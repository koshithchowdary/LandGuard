import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

BASE = Path(__file__).parent
DB_PATH = BASE / 'data' / 'landguard.db'
UPLOAD_DIR = BASE / 'data' / 'uploads'
DB_PATH.parent.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

SCHEMA = '''
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE, role TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS properties (
 id INTEGER PRIMARY KEY AUTOINCREMENT, property_code TEXT UNIQUE NOT NULL, owner_id INTEGER NOT NULL,
 name TEXT NOT NULL, property_type TEXT NOT NULL, address TEXT NOT NULL, district TEXT, mandal TEXT,
 village TEXT, survey_number TEXT, extent TEXT, latitude REAL, longitude REAL, monitoring_plan TEXT,
 status TEXT DEFAULT 'MONITORED', health_score INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(owner_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS inspections (
 id INTEGER PRIMARY KEY AUTOINCREMENT, property_id INTEGER NOT NULL, agent_id INTEGER NOT NULL,
 scheduled_at TEXT, started_at TEXT, completed_at TEXT, gps_lat REAL, gps_long REAL, gps_accuracy REAL,
 boundary_status TEXT, access_status TEXT, construction_status TEXT, vegetation_status TEXT,
 notes TEXT, ai_summary TEXT, health_score INTEGER, review_status TEXT DEFAULT 'PENDING',
 FOREIGN KEY(property_id) REFERENCES properties(id), FOREIGN KEY(agent_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS media (
 id INTEGER PRIMARY KEY AUTOINCREMENT, inspection_id INTEGER NOT NULL, media_type TEXT, filename TEXT,
 stored_path TEXT, captured_at TEXT, gps_lat REAL, gps_long REAL, sha256 TEXT, ai_finding TEXT,
 FOREIGN KEY(inspection_id) REFERENCES inspections(id)
);
CREATE TABLE IF NOT EXISTS service_requests (
 id INTEGER PRIMARY KEY AUTOINCREMENT, property_id INTEGER NOT NULL, owner_id INTEGER NOT NULL,
 request_type TEXT NOT NULL, priority TEXT NOT NULL, description TEXT, status TEXT DEFAULT 'OPEN', created_at TEXT DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(property_id) REFERENCES properties(id), FOREIGN KEY(owner_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS alerts (
 id INTEGER PRIMARY KEY AUTOINCREMENT, property_id INTEGER NOT NULL, inspection_id INTEGER,
 severity TEXT, title TEXT, description TEXT, status TEXT DEFAULT 'OPEN', created_at TEXT DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(property_id) REFERENCES properties(id), FOREIGN KEY(inspection_id) REFERENCES inspections(id)
);
'''

def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with conn() as c:
        c.executescript(SCHEMA)

def seed_demo_data():
    with conn() as c:
        if c.execute('SELECT COUNT(*) FROM users').fetchone()[0]: return
        cur=c.execute("INSERT INTO users(name,email,role) VALUES(?,?,?)", ('Ravi Demo','ravi@example.com','customer'))
        owner = cur.lastrowid
        cur=c.execute("INSERT INTO users(name,email,role) VALUES(?,?,?)", ('Srinivas Field Agent','agent@landguard.demo','agent'))
        agent = cur.lastrowid
        c.execute("INSERT INTO users(name,email,role) VALUES(?,?,?)", ('LANDGUARD Admin','ops@landguard.demo','admin'))
        props = [
            ('LG-NEL-000124', owner, 'Nellore Open Plot', 'Open Plot', 'Dhanalakshmi Puram, Nellore, Andhra Pradesh', 'Nellore','Nellore Rural','Nellore','124/2','500 sq yards',14.4426,79.9865,'Guardian',94),
            ('LG-HYD-000207', owner, 'Hyderabad Villa', 'Residential', 'Narsingi, Hyderabad, Telangana', 'Hyderabad','Gandipet','Narsingi','207/A','240 sq yards',17.3850,78.3400,'Watch',88),
        ]
        for p in props:
            c.execute('''INSERT INTO properties(property_code,owner_id,name,property_type,address,district,mandal,village,survey_number,extent,latitude,longitude,monitoring_plan,health_score) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', p)
        p1 = c.execute("SELECT id FROM properties WHERE property_code='LG-NEL-000124'").fetchone()['id']
        p2 = c.execute("SELECT id FROM properties WHERE property_code='LG-HYD-000207'").fetchone()['id']
        now = datetime.now()
        c.execute('''INSERT INTO inspections(property_id,agent_id,scheduled_at,started_at,completed_at,gps_lat,gps_long,gps_accuracy,boundary_status,access_status,construction_status,vegetation_status,notes,ai_summary,health_score,review_status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (p1,agent,(now-timedelta(days=2)).isoformat(),(now-timedelta(days=2,hours=-1)).isoformat(),(now-timedelta(days=2)).isoformat(),14.4427,79.9866,8.0,'CLEAR','ACCESSIBLE','NONE','MODERATE','No visible boundary concern.','No material change detected in demo inspection.',94,'APPROVED'))
        c.execute('''INSERT INTO inspections(property_id,agent_id,scheduled_at,completed_at,gps_lat,gps_long,gps_accuracy,boundary_status,access_status,construction_status,vegetation_status,notes,ai_summary,health_score,review_status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (p2,agent,(now-timedelta(days=10)).isoformat(),(now-timedelta(days=10)).isoformat(),17.3851,78.3401,10.0,'REVIEW','ACCESSIBLE','NEW_ACTIVITY','LOW','Structure-like change flagged for review.','Potential physical change detected; human review required.',88,'PENDING'))
        c.execute("INSERT INTO alerts(property_id,inspection_id,severity,title,description) VALUES(?,?,?,?,?)", (p2,2,'MEDIUM','Potential physical change','Current inspection indicates possible new structure-like activity. This is an observation, not a legal finding.'))
        c.commit()

def get_properties(owner_id=1):
    with conn() as c: return c.execute('SELECT * FROM properties WHERE owner_id=? ORDER BY id', (owner_id,)).fetchall()

def get_property(pid):
    with conn() as c: return c.execute('SELECT * FROM properties WHERE id=?',(pid,)).fetchone()

def get_inspections(pid):
    with conn() as c: return c.execute('SELECT i.*, u.name agent_name FROM inspections i JOIN users u ON u.id=i.agent_id WHERE property_id=? ORDER BY id DESC',(pid,)).fetchall()

def create_service_request(property_id, owner_id, request_type, priority, description):
    with conn() as c:
        c.execute('INSERT INTO service_requests(property_id,owner_id,request_type,priority,description) VALUES(?,?,?,?,?)',(property_id,owner_id,request_type,priority,description)); c.commit()

def create_inspection(property_id, agent_id, payload):
    with conn() as c:
        cur=c.execute('''INSERT INTO inspections(property_id,agent_id,scheduled_at,started_at,completed_at,gps_lat,gps_long,gps_accuracy,boundary_status,access_status,construction_status,vegetation_status,notes,ai_summary,health_score,review_status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (property_id,agent_id,payload['scheduled_at'],payload['started_at'],payload['completed_at'],payload['gps_lat'],payload['gps_long'],payload['gps_accuracy'],payload['boundary_status'],payload['access_status'],payload['construction_status'],payload['vegetation_status'],payload['notes'],payload['ai_summary'],payload['health_score'],'PENDING'))
        iid=cur.lastrowid
        c.execute('UPDATE properties SET health_score=? WHERE id=?',(payload['health_score'],property_id)); c.commit(); return iid

def add_media(inspection_id, media_type, filename, stored_path, sha256, ai_finding):
    with conn() as c:
        c.execute('INSERT INTO media(inspection_id,media_type,filename,stored_path,captured_at,sha256,ai_finding) VALUES(?,?,?,?,?,?,?)',(inspection_id,media_type,filename,stored_path,datetime.now().isoformat(),sha256,ai_finding)); c.commit()

def get_open_alerts():
    with conn() as c: return c.execute('''SELECT a.*,p.property_code,p.name FROM alerts a JOIN properties p ON p.id=a.property_id WHERE a.status='OPEN' ORDER BY a.id DESC''').fetchall()

def get_open_requests():
    with conn() as c: return c.execute('''SELECT r.*,p.property_code,p.name FROM service_requests r JOIN properties p ON p.id=r.property_id WHERE r.status='OPEN' ORDER BY r.id DESC''').fetchall()