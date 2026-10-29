import streamlit as st
from monitoring.providers import provider_status
from monitoring.notifications import channel_status

st.title("🛰️ Land Monitoring")
st.caption("Track physical plot changes and government-record changes as separate services.")

st.warning(
    "Government record monitoring is not live yet. Telangana Bhu Bharati and AP MeeBhoomi/Webland "
    "require approved access before LandGuard can run automated checks."
)

left, right = st.columns(2)
with left:
    st.subheader("🛰️ Physical plot monitoring")
    st.write(
        "Designed for licensed satellite imagery comparisons to flag possible new construction, "
        "fencing or visible disturbance. Image refresh depends on provider coverage, satellite passes, "
        "cloud conditions and resolution—not a guaranteed daily schedule."
    )
    st.info("Status: provider not connected")
with right:
    st.subheader("🏛️ Government-record monitoring")
    st.write(
        "Designed to compare authorized records or change feeds for changes to relevant fields such as "
        "record status, extent or mutation status. Failed checks remain visibly unavailable."
    )
    st.info("Status: government access pending")

st.subheader("Connector status")
for item in provider_status():
    with st.container(border=True):
        st.markdown(f"**{item['display_name']}** · {item['state']}")
        st.write(f"Status: `{item['status']}`")
        st.write(item["note"])
        st.markdown(f"[Open official portal]({item['portal_url']})")

st.subheader("Notification setup")
for channel in channel_status():
    status = "Configuration detected (delivery still needs implementation/testing)" if channel["configured"] else "Not configured"
    st.write(f"- **{channel['channel'].upper()}** — {status}")

st.caption(
    "This screen describes intended product capabilities and current connector readiness. "
    "It does not claim that a live source was checked or that an alert channel has sent a message."
)
