import os
import streamlit as st
import requests
from typing import Any

st.set_page_config(page_title="KisanMind (Streamlit)", layout="centered")

API_BASE = os.environ.get("STREAMLIT_API_BASE") or "http://localhost:8000"

st.title("KisanMind — Streamlit")
st.markdown("A lightweight Streamlit frontend for the KisanMind backend. Provide a public image URL and a location, then run the pipeline.")

with st.form("query_form"):
    image_url = st.text_input("Crop image URL (public)")
    location = st.text_input("Location (city)")
    crop_type = st.text_input("Crop type (optional)")
    language = st.selectbox("Language", ["en", "ur", "hi", "pa"], index=0)
    message = st.text_area("Farmer message (optional)", value="Describe the problem or question here...")
    submit = st.form_submit_button("Run KisanMind")

if submit:
    if not image_url and not message:
        st.error("Please provide at least an image URL or a message describing the issue.")
    else:
        payload = {
            "message": message or "",
            "image_url": image_url or None,
            "crop_type": crop_type or None,
            "location": location or None,
            "language": language,
        }

        st.info("Sending request to backend /query endpoint...")
        try:
            r = requests.post(f"{API_BASE}/query", json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
        except requests.RequestException as e:
            st.exception(e)
            st.stop()

        st.success("Done — showing results")
        # Plan
        plan = data.get("plan")
        if plan:
            st.subheader("Orchestrator Plan")
            st.json(plan)

        results = data.get("agent_results", {})

        # Crop doctor
        if "crop_doctor" in results:
            st.subheader("Diagnosis")
            diag = results["crop_doctor"]
            if isinstance(diag, dict):
                st.write(diag.get("disease", "unknown"))
                if diag.get("confidence") is not None:
                    try:
                        conf = float(diag.get("confidence"))
                        st.write(f"Confidence: {conf * 100:.0f}%")
                    except Exception:
                        st.write(f"Confidence: {diag.get('confidence')}")
                st.write(diag.get("description", ""))
            else:
                st.write(diag)

        # Weather
        if "weather" in results:
            st.subheader("Weather Advisory")
            st.json(results["weather"])

        # Treatment
        if "treatment" in results:
            st.subheader("Treatment Recommendations")
            tr = results["treatment"]
            if isinstance(tr, dict):
                st.write("Organic:", tr.get("organic"))
                st.write("Chemical:", tr.get("chemical"))
                st.write("Precautions:")
                st.write(tr.get("precautions"))
            else:
                st.write(tr)

        # Supplier
        if "supplier" in results:
            st.subheader("Supplier Finder")
            st.json(results["supplier"])

        # Raw dump
        st.subheader("Raw agent results")
        st.json(results)

st.markdown("---")
st.caption("Note: For privacy, this demo accepts public image URLs. To enable secure uploads, add a backend /upload endpoint that accepts files and stores them securely.")
