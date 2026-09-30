import streamlit as st
from db import init_db, seed_demo_data

st.set_page_config(page_title='LANDGUARD', page_icon='🛡️', layout='wide')
init_db(); seed_demo_data()

if 'role' not in st.session_state:
    st.session_state.role = 'Customer'

st.sidebar.markdown('## 🛡️ LANDGUARD')
st.sidebar.caption('Your property. Watched locally.')
st.session_state.role = st.sidebar.selectbox('Demo role', ['Customer', 'Field Agent', 'Admin'], index=['Customer','Field Agent','Admin'].index(st.session_state.role))
st.sidebar.divider()
st.sidebar.info('MVP demo • Data is stored locally in SQLite.\n\nAI findings are advisory and require human review.')

customer_pages = [
    st.Page('pages/customer_dashboard.py', title='Dashboard', icon='🏠'),
    st.Page('pages/property_passport.py', title='Property Passport', icon='📘'),
    st.Page('pages/inspection_history.py', title='Inspection History', icon='📸'),
    st.Page('pages/service_request.py', title='Request Inspection', icon='📝'),
]
agent_pages = [st.Page('pages/agent_tasks.py', title='My Inspections', icon='📋')]
admin_pages = [st.Page('pages/admin_dashboard.py', title='Operations', icon='🛠️')]

if st.session_state.role == 'Customer':
    pages = customer_pages
elif st.session_state.role == 'Field Agent':
    pages = agent_pages
else:
    pages = admin_pages

pg = st.navigation(pages)
pg.run()