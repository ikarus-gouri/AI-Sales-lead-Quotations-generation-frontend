import streamlit as st
import time
from typing import Dict
import requests
import json
from datetime import datetime

# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(
    page_title="Product Catalog Scraper",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛍️ Product Catalog Scraper")
st.markdown(
    "Extract structured product data from e-commerce websites using a **hosted AI scraping backend**."
)

# -----------------------------
# Hosted Backend Configuration
# -----------------------------
st.sidebar.header("🔌 Backend Connection")

HF_API_BASE = "https://gouriikarus3d-product-catalogue-ai.hf.space"
st.sidebar.success("🌐 Connected to HuggingFace hosted backend")

if st.sidebar.button("🔍 Test Connection", use_container_width=True):
    with st.sidebar:
        with st.spinner("Testing connection..."):
            try:
                r = requests.get(f"{HF_API_BASE}/health", timeout=5)
                if r.status_code == 200:
                    st.success("✅ Backend reachable")
                    st.json(r.json())
                else:
                    st.error(f"❌ Status code: {r.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")

st.sidebar.markdown("---")

# -----------------------------
# Backend Feature Detection
# -----------------------------
@st.cache_data(ttl=300)
def get_backend_features(api_base: str):
    try:
        r = requests.get(f"{api_base}/features", timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {"google_sheets": {"enabled": False}}

backend_features = get_backend_features(HF_API_BASE)
google_sheets_available = backend_features.get("google_sheets", {}).get("enabled", False)

# -----------------------------
# Sidebar – Scraper Settings
# -----------------------------
st.sidebar.header("⚙️ Scraper Settings")

with st.sidebar.form("scraper_form"):
    url = st.text_input(
        "Target Website URL",
        placeholder="https://example.com/products"
    )

    st.markdown("### 🎯 Scraping Mode")
    strictness = st.selectbox(
        "Strictness Level",
        ["balanced", "lenient", "strict"],
        index=0
    )

    st.info({
        "lenient": "🔍 High recall – may include noise",
        "balanced": "⚖️ Best precision + recall (recommended)",
        "strict": "✨ Cleanest output – may miss some products"
    }[strictness])

    st.markdown("### 📊 Crawling Limits")
    max_pages = st.slider("Max Pages", 10, 300, 50, 10)
    max_depth = st.slider("Max Depth", 1, 5, 3)
    delay = st.slider("Crawl Delay (seconds)", 0.1, 5.0, 0.5, 0.1)

    st.markdown("### 💾 Export Formats")
    export_formats = st.multiselect(
        "Select formats",
        ["json", "csv", "csv_prices", "quotation"],
        default=["json"]
    )

    output_file = st.text_input(
        "Output filename",
        value="product_catalog"
    )

    st.markdown("### 📊 Google Sheets")
    if google_sheets_available:
        enable_sheets = st.checkbox("Upload to Google Sheets")
        sheets_id = (
            st.text_input("Spreadsheet ID (optional)")
            if enable_sheets else None
        )
    else:
        enable_sheets = False
        sheets_id = None
        st.warning("Google Sheets not enabled on backend")

    run_button = st.form_submit_button(
        "🚀 Start Scraping",
        use_container_width=True,
        type="primary"
    )

# -----------------------------
# HF API Client
# -----------------------------
class HFAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def health(self):
        r = self.session.get(f"{self.base_url}/health", timeout=5)
        r.raise_for_status()
        return r.json()

    def start_scrape(self, payload: Dict):
        r = self.session.post(f"{self.base_url}/scrape", json=payload, timeout=10)
        r.raise_for_status()
        return r.json()

    def job_status(self, job_id: str):
        r = self.session.get(f"{self.base_url}/jobs/{job_id}", timeout=5)
        r.raise_for_status()
        return r.json()

    def download(self, job_id: str, fmt: str):
        r = self.session.get(f"{self.base_url}/download/{job_id}/{fmt}", timeout=30)
        r.raise_for_status()
        return r.content

    def upload_sheets(self, payload: Dict):
        r = self.session.post(
            f"{self.base_url}/google-sheets/upload",
            json=payload,
            timeout=30
        )
        r.raise_for_status()
        return r.json()

# -----------------------------
# Run Scraper
# -----------------------------
if run_button:
    if not url.startswith(("http://", "https://")):
        st.error("⚠️ Enter a valid URL")
        st.stop()

    if not export_formats:
        st.error("⚠️ Select at least one export format")
        st.stop()

    api = HFAPIClient(HF_API_BASE)

    with st.spinner("Checking backend availability..."):
        try:
            api.health()
        except Exception as e:
            st.error(f"❌ Backend unavailable: {str(e)}")
            st.stop()

    payload = {
        "url": url,
        "max_pages": max_pages,
        "max_depth": max_depth,
        "crawl_delay": delay,
        "export_formats": export_formats,
        "strictness": strictness,
        "google_sheets_upload": enable_sheets,
        "google_sheets_id": sheets_id
    }

    st.info("🚀 Submitting scraping job...")
    job = api.start_scrape(payload)
    job_id = job.get("job_id")

    if not job_id:
        st.error("❌ No job ID returned")
        st.stop()

    progress = st.progress(0)
    status_box = st.empty()

    for _ in range(300):
        job = api.job_status(job_id)
        status = job.get("status")
        message = job.get("message", "")

        progress.progress({
            "pending": 10,
            "running": 50,
            "exporting": 80,
            "completed": 100,
            "failed": 0
        }.get(status, 50))

        status_box.markdown(f"**Status:** {status}\n\n{message}")

        if status == "completed":
            break
        if status == "failed":
            st.error("❌ Job failed")
            st.stop()

        time.sleep(2)

    st.success("✅ Scraping completed")

    result = job.get("result", {})
    files = result.get("files", {})
    total = result.get("total_products", 0)

    st.metric("Total Products", total)
    st.metric("Strictness", strictness.title())
    st.metric("Backend", "☁️ HuggingFace Hosted")

    # -----------------------------
    # Download Files
    # -----------------------------
    st.subheader("💾 Download Results")

    format_meta = {
        "json": ("application/json", ".json"),
        "csv": ("text/csv", ".csv"),
        "csv_prices": ("text/csv", "_with_prices.csv"),
        "quotation": ("application/json", "_quotation.json")
    }

    for fmt in files:
        if fmt in format_meta:
            mime, ext = format_meta[fmt]
            content = api.download(job_id, fmt)

            st.download_button(
                label=f"📥 Download {fmt.upper()}",
                data=content,
                file_name=f"{output_file}{ext}",
                mime=mime,
                use_container_width=True
            )
