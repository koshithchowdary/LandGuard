import streamlit as st
from db import get_properties, init_db, seed_demo_data
from monitoring.providers import provider_status
from monitoring.notifications import channel_status
from monitoring.store import (
    get_check_history, get_preferences, init_monitoring_store, log_check,
    save_owner_snapshot, save_preferences,
)

st.title("Land Monitoring")
st.caption("Your property. Watched locally. Track supplied record snapshots and source-check history.")
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

st.subheader("Monitoring preferences")
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
        st.success("Preferences saved locally. This does not activate source checks or message delivery.")

st.divider()
st.subheader("Record snapshot")
st.write(
    "Enter details from a document or official record you already have. LandGuard stores a "
    "normalized snapshot and compares it with the previous supplied snapshot. This is not a "
    "live government check, document authentication, or legal verification."
)
with st.form("owner_record_snapshot"):
    left, right = st.columns(2)
    with left:
        record_status = st.text_input("Record status", placeholder="e.g. Active")
        survey_number = st.text_input("Survey number", value=str(prop["survey_number"] or ""))
        subdivision_number = st.text_input("Subdivision number")
        extent = st.text_input("Extent", value=str(prop["extent"] or ""))
        recorded_owner_name = st.text_input("Recorded owner name")
    with right:
        mutation_status = st.text_input("Mutation status")
        record_date = st.text_input("Record date", placeholder="YYYY-MM-DD or as printed")
        parcel_id = st.text_input("Parcel / record ID")
    submitted = st.form_submit_button("Save and compare snapshot")
if submitted:
    record = {
        "record_status": record_status,
        "survey_number": survey_number,
        "subdivision_number": subdivision_number,
        "extent": extent,
        "recorded_owner_name": recorded_owner_name,
        "mutation_status": mutation_status,
        "record_date": record_date,
        "parcel_id": parcel_id,
    }
    try:
        result = save_owner_snapshot(pid, record)
        status = result["status"]
        if status == "baseline_created":
            st.success("Baseline created from the supplied details.")
        elif status == "source_changed":
            st.warning("Differences found between the supplied snapshots. Verify the original documents.")
            st.dataframe(result["changes"], use_container_width=True, hide_index=True)
        elif status == "no_change_observed":
            st.info("No differences observed between the supplied snapshots. This does not confirm current government status.")
        else:
            st.warning("The snapshot could not be compared.")
    except ValueError as exc:
        st.error(str(exc))

st.divider()
st.subheader("Government data connectors")
st.warning("Live government-record monitoring is not active. No approved API credentials or change feeds are configured.")
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

st.subheader("Monitoring history")
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
