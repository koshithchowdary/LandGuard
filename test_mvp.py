from pathlib import Path
from db import init_db, seed_demo_data, get_properties, get_inspections, get_open_alerts, create_service_request

DB = Path(__file__).parent / 'data' / 'landguard.db'
if DB.exists(): DB.unlink()
init_db(); seed_demo_data()
props = get_properties(1)
assert len(props) == 2
assert props[0]['property_code'].startswith('LG-')
assert len(get_inspections(props[0]['id'])) == 1
assert len(get_open_alerts()) == 1
create_service_request(props[0]['id'], 1, 'Routine inspection', 'Low', 'Test request')
print('LANDGUARD MVP smoke test: PASS')