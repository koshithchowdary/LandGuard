import streamlit as st
from db import get_properties,get_inspections
props=get_properties(1)
selected=st.selectbox('Property',[p['property_code'] for p in props])
p=next(p for p in props if p['property_code']==selected)
st.title('📸 Inspection History')
rows=get_inspections(p['id'])
for r in rows:
    with st.expander(f"{r['completed_at'][:10] if r['completed_at'] else 'Scheduled'} · {r['review_status']} · {r['health_score']}/100"):
        c1,c2=st.columns(2)
        c1.write(f"**Agent:** {r['agent_name']}\n\n**GPS:** {r['gps_lat']}, {r['gps_long']} ± {r['gps_accuracy']}m")
        c2.write(f"**Boundary:** {r['boundary_status']}\n\n**Construction:** {r['construction_status']}\n\n**Access:** {r['access_status']}\n\n**Vegetation:** {r['vegetation_status']}")
        st.info(r['ai_summary'] or 'No AI analysis available.')
        st.write(r['notes'])