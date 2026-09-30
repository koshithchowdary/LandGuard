import streamlit as st
from db import get_properties
st.title('🏠 Customer Dashboard')
st.caption('Independent property monitoring, evidence and alerts.')
props=get_properties(1)
cols=st.columns(2)
for idx,p in enumerate(props):
    with cols[idx%2]:
        status='🟢 MONITORED' if p['health_score']>=90 else '🟡 REVIEW'
        st.subheader(p['name'])
        st.write(f"**{status}**  ·  `{p['property_code']}`")
        a,b,c=st.columns(3)
        a.metric('Health',f"{p['health_score']}/100")
        b.metric('Plan',p['monitoring_plan'])
        c.metric('Area',p['extent'])
        st.caption(p['address'])
        st.progress(p['health_score']/100)
        st.divider()
st.info('Demo note: this MVP uses seeded sample properties. Customer authentication and payments are intentionally deferred until pilot validation.')