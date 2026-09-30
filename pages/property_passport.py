import streamlit as st
from db import get_properties
props=get_properties(1)
if not props: st.stop()
selected=st.selectbox('Property', [p['property_code'] for p in props])
p=next(p for p in props if p['property_code']==selected)
st.title('📘 Property Passport')
st.caption('A structured digital record of the property and its monitoring history.')
a,b,c,d=st.columns(4)
a.metric('Health',f"{p['health_score']}/100")
b.metric('Type',p['property_type'])
c.metric('Extent',p['extent'])
d.metric('Monitoring',p['monitoring_plan'])
st.subheader(p['name'])
st.write(p['address'])
left,right=st.columns(2)
with left:
    st.markdown('### Property identity')
    st.json({'Property ID':p['property_code'],'Survey Number':p['survey_number'],'Village':p['village'],'Mandal':p['mandal'],'District':p['district']})
with right:
    st.markdown('### Location')
    st.map({'lat':[p['latitude']],'lon':[p['longitude']]})
st.warning('LANDGUARD monitoring status is an operational observation. It is not a title certificate, legal opinion, valuation, or guarantee against encroachment.')