import streamlit as st
from db import get_properties, init_db, seed_demo_data
from monitoring.providers import provider_status
from monitoring.notifications import channel_status
from monitoring.store import get_check_history, get_preferences, init_monitoring_store, log_check, save_preferences

st.title("Land Monitoring")
st.caption("Manage monitoring preferences and view the connector audit trail.")
init_db()
seed_demo_data()
init_monitoring_store()
props = get_properties(owner_id=1)
if not props:
    st.info("No properties found.")
    st.stop()
labels = [p["property_code"] + " — " + p["name"] for p in props]
label = st.selectbox("Property", labels)
prop = props[labels.index(label)]
pid = int(prop["id"])
pref = get_preferences(pid)
with st.form("monitoring_preferences"):
    physical = st.checkbox("Physical / satellite monitoring", bool(pref["physical_enabled"]))
    government = st.checkbox("Government-record monitoring", bool(pref["government_enabled"]))
    email = st.checkbox("Email alerts", bool(pref["alert_email"]))
    sms = st.checkbox("SMS alerts", bool(pref["alert_sms"]))
    whatsapp = st.checkbox("WhatsApp alerts", bool(pref["alert_whatsapp"]))
    if st.form_submit_button("Save preferences"):
        save_preferences(pid, physical_enabled=physical, government_enabled=government,
                         alert_email=email, alert_sms=sms, alert_whatsapp=whatsapp)
        st.success("Preferences saved locally. No provider or alert delivery is activated.")

st.warning("Live monitoring is not active: approved source access and provider integrations are still required.")
for item in provider_status():
    with st.container(border=True):
        st.markdown("**" + item["display_name"] + "** · " + item["state"])
        st.write("Status: " + item["status"])
        st.write(item["note"])
        st.markdown("[Official portal](" + item["portal_url"] + ")")

if st.button("Log government source unavailable"):
    log_check(pid, "government_records", "source_unavailable",
              "No approved API/feed connected; whether records changed is unknown.")
    st.warning("Logged as source unavailable, not as no change.")

st.subheader("History")
history = get_check_history(pid)
if not history:
    st.caption("No checks recorded yet.")
for item in history:
    with st.container(border=True):
        st.markdown("**" + item["source_type"] + "** · " + item["status"])
        st.write(item["summary"])
        st.caption(item["checked_at"])

st.subheader("Notification readiness")
for channel in channel_status():
    status = "Configured but not delivery-tested" if channel["configured"] else "Not configured"
    st.write("- **" + channel["channel"].upper() + "** — " + status)
st.caption("No messages are sent from this page. Scheduling, live source checks and delivery integrations remain future work.")
