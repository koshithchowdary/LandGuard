import streamlit as st
from db import get_properties,create_service_request
st.title('📝 Request Inspection')
props=get_properties(1)
with st.form('request'):
    prop=st.selectbox('Property',[p['property_code'] for p in props])
    req=st.selectbox('Request type',['Routine inspection','Emergency inspection','Boundary observation','Maintenance coordination'])
    priority=st.select_slider('Priority',['Low','Medium','High'])
    desc=st.text_area('What do you need checked?')
    submitted=st.form_submit_button('Submit request')
if submitted:
    p=next(p for p in props if p['property_code']==prop)
    create_service_request(p['id'],1,req,priority,desc)
    st.success('Request submitted to LANDGUARD Operations.')