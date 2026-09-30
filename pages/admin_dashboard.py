import streamlit as st
from db import get_open_alerts,get_open_requests,get_properties
st.title('🛠️ Operations Dashboard')
props=get_properties(1)
alerts=get_open_alerts(); requests=get_open_requests()
a,b,c=st.columns(3)
a.metric('Properties',len(props)); b.metric('Open alerts',len(alerts)); c.metric('Open requests',len(requests))
st.subheader('🚨 Alerts')
for x in alerts:
    st.error(f"**{x['severity']} · {x['property_code']}** — {x['title']}\n\n{x['description']}")
st.subheader('📝 Service requests')
for x in requests:
    st.warning(f"**{x['priority']} · {x['property_code']}** — {x['request_type']}\n\n{x['description'] or 'No description'}")
st.subheader('Property portfolio')
for p in props:
    st.write(f"`{p['property_code']}` · {p['name']} · Health **{p['health_score']}/100** · {p['monitoring_plan']}")