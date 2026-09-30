import hashlib
from pathlib import Path
from datetime import datetime

def save_upload(uploaded_file, upload_dir: Path):
    data = uploaded_file.getvalue()
    digest = hashlib.sha256(data).hexdigest()
    safe = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{digest[:10]}_{uploaded_file.name.replace(' ','_')}"
    path = upload_dir / safe
    path.write_bytes(data)
    return str(path), digest

def health_score(boundary, access, construction, vegetation):
    score = 100
    score -= {'REVIEW':10,'CONCERN':20}.get(boundary,0)
    score -= {'INACCESSIBLE':10}.get(access,0)
    score -= {'NEW_ACTIVITY':8,'UNKNOWN':4}.get(construction,0)
    score -= {'HIGH':5,'MODERATE':2}.get(vegetation,0)
    return max(0, min(100, score))