import streamlit as st
from datetime import datetime
from db import get_properties,create_inspection,add_media,UPLOAD_DIR
from utils import save_upload,health_score
st.title('📋 Field Agent — Inspection Console')
st.caption('GPS and evidence controls are simulated in this browser MVP; native mobile GPS enforcement comes in V2.')
props=get_properties(1)
selected_code=st.selectbox('Assigned property',[item['property_code'] for item in props])
prop=next(item for item in props if item['property_code']==selected_code)
st.subheader(prop['name'])
st.write(prop['address'])
with st.form('inspection'):
    st.markdown('### 1. Location verification')
    lat=st.number_input('Captured latitude',value=float(prop['latitude']),format='%.6f')
    lon=st.number_input('Captured longitude',value=float(prop['longitude']),format='%.6f')
    accuracy=st.number_input('GPS accuracy (m)',value=8.0,min_value=0.1)
    st.markdown('### 2. Inspection checklist')
    boundary=st.selectbox('Boundary',['CLEAR','REVIEW','CONCERN'])
    access=st.selectbox('Access',['ACCESSIBLE','INACCESSIBLE'])
    construction=st.selectbox('Construction activity',['NONE','NEW_ACTIVITY','UNKNOWN'])
    vegetation=st.selectbox('Vegetation',['LOW','MODERATE','HIGH'])
    notes=st.text_area('Agent observations')
    uploads=st.file_uploader('Capture/upload evidence',type=['jpg','jpeg','png','webp','mp4'],accept_multiple_files=True)
    submit=st.form_submit_button('Complete inspection')
if submit:
    score=health_score(boundary,access,construction,vegetation)
    finding='Potential physical change detected; human review required.' if construction=='NEW_ACTIVITY' else 'No material change indicated by checklist.'
    iid=create_inspection(prop['id'],2,{'scheduled_at':datetime.now().isoformat(),'started_at':datetime.now().isoformat(),'completed_at':datetime.now().isoformat(),'gps_lat':lat,'gps_long':lon,'gps_accuracy':accuracy,'boundary_status':boundary,'access_status':access,'construction_status':construction,'vegetation_status':vegetation,'notes':notes,'ai_summary':finding,'health_score':score})
    for u in uploads or []:
        path,digest=save_upload(u,UPLOAD_DIR)
        add_media(iid,'video' if u.type.startswith('video') else 'photo',u.name,path,digest,finding)
    st.success(f'Inspection {iid} submitted for human review. Health score: {score}/100')