import streamlit as st
import time
from typing import List, Dict, Optional
import requests
import json
import pandas as pd

from src.storage.csv_storage import CSVStorage
from src.storage.json_storage import JSONStorage

# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(
    page_title="Product Catalog Scraper",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛍️ Product Catalog Scraper")
st.markdown("Extract structured product data from e-commerce websites with balanced scraping technology.")

# -----------------------------
# Backend Selection
# -----------------------------
st.sidebar.header("🔌 Backend Connection")

backend_mode = st.sidebar.radio(
    "Select Backend",
    options=["Hosted (HuggingFace)", "Local Server"],
    help="Choose between hosted API or local development server"
)

if backend_mode == "Hosted (HuggingFace)":
    HF_API_BASE = "https://gouriikarus3d-product-catalogue-ai.hf.space"
    st.sidebar.success("🌐 Using hosted backend")
else:
    custom_url = st.sidebar.text_input(
        "Local Server URL",
        value="http://localhost:7860",
        help="Enter your local API server URL"
    )
    HF_API_BASE = custom_url
    st.sidebar.info(f"🏠 Using local backend: {custom_url}")

# Test connection button
if st.sidebar.button("🔍 Test Connection", use_container_width=True):
    with st.sidebar:
        with st.spinner("Testing connection..."):
            try:
                response = requests.get(f"{HF_API_BASE}/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Connection successful!")
                    st.json(data)
                else:
                    st.error(f"❌ Connection failed (Status: {response.status_code})")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")

st.sidebar.markdown("---")

# -----------------------------
# Check Backend Features
# -----------------------------
@st.cache_data(ttl=300)
def get_backend_features(api_base: str):
    """Get available features from backend"""
    try:
        response = requests.get(f"{api_base}/features", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"google_sheets": {"enabled": False}}

backend_features = get_backend_features(HF_API_BASE)
google_sheets_available = backend_features.get("google_sheets", {}).get("enabled", False)

# -----------------------------
# Sidebar – Configuration (FORM)
# -----------------------------
st.sidebar.header("⚙️ Scraper Settings")

with st.sidebar.form("scraper_form"):
    url = st.text_input(
        "Target Website URL",
        placeholder="https://example.com/products",
        help="Enter the full URL including https://"
    )

    st.markdown("### 🎯 Scraping Mode")
    strictness = st.selectbox(
        "Strictness Level",
        options=["balanced", "lenient", "strict"],
        index=0,
        help="""
        • Lenient: High recall - finds all products (may include false positives)
        • Balanced: Good precision + recall (RECOMMENDED)
        • Strict: High precision - very clean results (may miss some products)
        """
    )
    
    # Show info about selected strictness
    strictness_info = {
        "lenient": "🔍 **Lenient Mode**: Catches all products, some false positives may occur",
        "balanced": "⚖️ **Balanced Mode**: Optimal precision and recall (recommended)",
        "strict": "✨ **Strict Mode**: Very clean results, may miss some edge cases"
    }
    st.info(strictness_info[strictness])

    st.markdown("### 📊 Crawling Parameters")
    max_pages = st.slider("Max Pages", 10, 300, 50, 10)
    max_depth = st.slider("Max Crawl Depth", 1, 5, 3)
    delay = st.slider("Crawl Delay (seconds)", 0.1, 5.0, 0.5, 0.1)

    st.markdown("### 💾 Export Options")
    export_formats = st.multiselect(
        "Export Formats",
        options=["json", "csv", "csv_prices", "quotation"],
        default=["json"],
        help="""
        • json: Complete product data in JSON format
        • csv: Basic CSV with core product fields
        • csv_prices: CSV with detailed price information
        • quotation: JSON template formatted for quotations
        """
    )

    output_file = st.text_input(
        "Output filename (base name)",
        value="product_catalog",
        help="Base filename for exports (extensions will be added automatically)"
    )

    # Google Sheets Integration
    st.markdown("### 📊 Google Sheets Integration")
    
    if google_sheets_available:
        enable_sheets = st.checkbox(
            "Upload to Google Sheets",
            value=False,
            help="Automatically upload results to Google Sheets after scraping"
        )
        
        sheets_id = None
        if enable_sheets:
            sheets_id = st.text_input(
                "Spreadsheet ID (optional)",
                placeholder="Leave empty to create new spreadsheet",
                help="Provide an existing spreadsheet ID to update it, or leave empty to create new"
            )
            st.info("💡 New spreadsheets will be created in your service account's Drive")
    else:
        enable_sheets = False
        sheets_id = None
        st.warning("📊 Google Sheets not configured on this backend")
        
        with st.expander("ℹ️ How to enable Google Sheets"):
            st.markdown("""
            **For administrators:**
            
            To enable Google Sheets integration:
            1. Set up a Google Cloud service account
            2. Download credentials JSON
            3. For HuggingFace: Add as `GOOGLE_SHEETS_CREDS_JSON` secret
            4. For Local: Save as `credentials.json` in project root
            
            See `GOOGLE_SHEETS_SETUP.md` for detailed instructions.
            """)

    run_button = st.form_submit_button(
        "🚀 Start Scraping",
        type="primary",
        use_container_width=True
    )

st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 About")
st.sidebar.info(
    "**Balanced Scraper v2.1**\n\n"
    "This tool uses a balanced approach combining lenient and strict methods "
    "to extract product information with optimal accuracy.\n\n"
    "**Features:**\n"
    "- Multiple strictness levels\n"
    "- Real-time progress tracking\n"
    "- Multiple export formats\n"
    "- Google Sheets integration\n"
    "- Customization options extraction\n\n"
    "**Backend Options:**\n"
    "- Hosted: Production HuggingFace deployment\n"
    "- Local: Development server (localhost)"
)

# -----------------------------
# HF API Client
# -----------------------------

class HFAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def health_check(self) -> Dict:
        """Check if API is available and return health info"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return {"status": "healthy", "data": response.json()}
            else:
                return {"status": "unhealthy", "error": f"Status code: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}

    def start_scrape(self, url, max_pages, max_depth, crawl_delay, export_formats, 
                     strictness, google_sheets_upload=False, google_sheets_id=None):
        """Start a new scraping job with strictness parameter and optional Google Sheets upload"""
        payload = {
            "url": url,
            "max_pages": max_pages,
            "max_depth": max_depth,
            "crawl_delay": crawl_delay,
            "export_formats": export_formats,
            "strictness": strictness,
            "google_sheets_upload": google_sheets_upload,
            "google_sheets_id": google_sheets_id
        }
        try:
            r = self.session.post(f"{self.base_url}/scrape", json=payload, timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to start scraping job: {str(e)}")
            raise

    def get_job_status(self, job_id):
        """Get status of a scraping job"""
        try:
            r = self.session.get(f"{self.base_url}/jobs/{job_id}", timeout=5)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to get job status: {str(e)}")
            raise

    def download_results(self, job_id, fmt):
        """Download results for a completed job"""
        try:
            r = self.session.get(f"{self.base_url}/download/{job_id}/{fmt}", timeout=30)
            r.raise_for_status()
            return r.content
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to download results: {str(e)}")
            raise

    def upload_to_sheets(self, job_id, spreadsheet_id=None, spreadsheet_title="Product Catalog", 
                        include_prices=True):
        """Upload completed job to Google Sheets"""
        payload = {
            "job_id": job_id,
            "spreadsheet_id": spreadsheet_id,
            "spreadsheet_title": spreadsheet_title,
            "include_prices": include_prices
        }
        try:
            r = self.session.post(f"{self.base_url}/google-sheets/upload", json=payload, timeout=30)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to upload to Google Sheets: {str(e)}")
            raise

    def get_scraper_info(self):
        """Get information about scraper capabilities"""
        try:
            r = self.session.get(f"{self.base_url}/info", timeout=5)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException:
            return None

# -----------------------------
# HF API Scraping with Polling
# -----------------------------
def scrape_with_hf_api(api_client, url, max_pages, max_depth, crawl_delay, 
                       export_formats, strictness, google_sheets_upload, google_sheets_id,
                       status_placeholder, progress_bar):
    """Execute scraping job and poll for completion"""
    
    sheets_msg = " + Google Sheets" if google_sheets_upload else ""
    status_placeholder.info(f"🚀 Submitting scraping request (strictness: **{strictness}**{sheets_msg})...")
    progress_bar.progress(5)

    try:
        job_response = api_client.start_scrape(
            url, max_pages, max_depth, crawl_delay, export_formats, strictness,
            google_sheets_upload, google_sheets_id
        )
    except Exception as e:
        st.error(f"❌ Failed to submit scraping job: {str(e)}")
        return None, None

    job_id = job_response.get("job_id")
    if not job_id:
        st.error("❌ No job ID returned from API")
        return None, None
    
    st.info(f"📋 Job ID: `{job_id}` | Mode: **{strictness}**")

    stage_progress = {
        "pending": 10,
        "initializing": 15,
        "crawling": 50,
        "exporting": 75,
        "google_sheets_upload": 85,
        "running": 50,
        "completed": 100,
        "failed": 0
    }
    max_polls = 300  # 5 minutes with 1 second intervals

    for poll_count in range(max_polls):
        try:
            job = api_client.get_job_status(job_id)
            status = job.get("status", "unknown")
            message = job.get("message", "")
            progress_info = job.get("progress", {})

            # Calculate progress
            if progress_info and "stage" in progress_info:
                stage = progress_info.get("stage", "")
                current_progress = stage_progress.get(stage, stage_progress.get(status, 50))
            else:
                current_progress = stage_progress.get(status, 50)
            
            progress_bar.progress(current_progress)
            
            # Enhanced status display
            status_html = f"""
            **Status:** {status.title()}  
            **Message:** {message}  
            **Strictness:** {strictness.title()}
            """
            
            if progress_info:
                stage = progress_info.get("stage", "")
                if stage:
                    stage_display = stage.replace("_", " ").title()
                    status_html += f"  \n**Stage:** {stage_display}"
            
            status_placeholder.markdown(status_html)

            if status == "completed":
                progress_bar.progress(100)
                return job, job_id
            
            if status == "failed":
                st.error(f"❌ Job failed: {message}")
                
                # Suggest trying different strictness level
                if "No products found" in message and strictness != "lenient":
                    st.warning("💡 Try using **lenient** mode for higher recall")
                
                return None, None

            time.sleep(100)
            
        except Exception as e:
            st.warning(f"⚠️ Error polling job status (attempt {poll_count + 1}): {str(e)}")
            time.sleep(200)
            continue

    st.error("⏱️ Timeout waiting for job completion")
    return None, None

# -----------------------------
# Main Execution (ONLY ON SUBMIT)
# -----------------------------
if run_button:
    if not url or not url.startswith(("http://", "https://")):
        st.error("⚠️ Please enter a valid URL starting with http:// or https://")
        st.stop()
    
    if not export_formats:
        st.error("⚠️ Please select at least one export format")
        st.stop()

    # Initialize API client with selected backend
    api_client = HFAPIClient(HF_API_BASE)

    # Only check health when actually running a job
    with st.spinner(f"Checking API availability ({backend_mode})..."):
        health_result = api_client.health_check()
        
        if health_result["status"] != "healthy":
            st.error(f"❌ Cannot connect to backend: {health_result.get('error', 'Unknown error')}")
            
            if backend_mode == "Local Server":
                st.warning("""
                **Troubleshooting Local Server:**
                1. Make sure your local API server is running
                2. Check if it's accessible at the correct URL
                3. Verify the port number is correct
                4. Try running: `python app.py` or `uvicorn app:app --reload`
                """)
            else:
                st.warning("The hosted backend might be temporarily unavailable. Try again later or use Local Server mode.")
            
            st.stop()

    health_data = health_result.get("data", {})
    st.success(f"✅ Connected to backend ({backend_mode})")
    
    # Show backend info
    with st.expander("🔍 Backend Information", expanded=False):
        st.json(health_data)
    
    # Show scraper info if available
    scraper_info = api_client.get_scraper_info()
    if scraper_info:
        st.info(f"📊 Scraper Version: **{scraper_info.get('version', 'unknown')}** | Type: **{scraper_info.get('scraper_type', 'unknown')}**")

    # Initialize progress tracking
    progress_bar = st.progress(0)
    status_placeholder = st.empty()

    # Execute scraping job
    job_result, job_id = scrape_with_hf_api(
        api_client, url, max_pages, max_depth, delay,
        export_formats, strictness, enable_sheets, sheets_id,
        status_placeholder, progress_bar
    )

    if not job_result or not job_id:
        st.stop()

    # -----------------------------
    # Download and Parse Results
    # -----------------------------
    result_info = job_result.get("result", {})
    available_files = result_info.get("files", {})
    total_products = result_info.get("total_products", 0)
    google_sheets_info = result_info.get("google_sheets", {})
    
    # Download JSON for preview (if available)
    catalog = []
    if "json" in available_files:
        try:
            json_data = api_client.download_results(job_id, "json")
            catalog_json = json.loads(json_data)
            
            # Handle different JSON structures
            if isinstance(catalog_json, list):
                catalog = catalog_json
            elif isinstance(catalog_json, dict) and "products" in catalog_json:
                catalog = catalog_json["products"]
            else:
                catalog = []
                
        except json.JSONDecodeError as e:
            st.error(f"❌ Failed to parse JSON: {str(e)}")
        except Exception as e:
            st.warning(f"⚠️ Could not load preview data: {str(e)}")

    if total_products == 0:
        st.warning(f"⚠️ No products found with **{strictness}** mode")
        
        # Provide suggestions based on current strictness
        if strictness == "strict":
            st.info("💡 Try **balanced** or **lenient** mode for higher recall")
        elif strictness == "balanced":
            st.info("💡 Try **lenient** mode to catch more products (may include false positives)")
        
        st.stop()

    # Display result summary
    st.success(f"✅ Successfully scraped **{total_products}** products using **{strictness}** mode!")

    # Google Sheets Success Message
    if google_sheets_info.get("uploaded"):
        sheets_url = google_sheets_info.get("url")
        st.success(f"📊 **Uploaded to Google Sheets!**")
        st.markdown(f"**🔗 [Open Spreadsheet]({sheets_url})**")
        st.code(sheets_url, language=None)
    elif enable_sheets and not google_sheets_info.get("uploaded"):
        error_msg = google_sheets_info.get("error", "Unknown error")
        st.warning(f"⚠️ Google Sheets upload failed: {error_msg}")

    # -----------------------------
    # Results Preview
    # -----------------------------
    st.subheader("📋 Results Preview")
    
    # Show statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Products", total_products)
    with col2:
        st.metric("Strictness Mode", strictness.title())
    with col3:
        products_with_customizations = sum(1 for p in catalog if p.get("customizations"))
        st.metric("With Customizations", products_with_customizations)
    with col4:
        backend_display = "☁️ Hosted" if backend_mode == "Hosted (HuggingFace)" else "🏠 Local"
        st.metric("Backend", backend_display)
    
    # Show preview of products (if available)
    if catalog:
        preview_data = catalog[:5]
        
        st.markdown("#### 🔍 First 5 Products")
        for i, product in enumerate(preview_data, 1):
            product_name = product.get("name") or product.get("product_name") or f"Product {i}"
            with st.expander(f"{i}. {product_name}", expanded=(i == 1)):
                st.json(product)
    else:
        st.info("Preview not available - download files to view results")

    # -----------------------------
    # Download Buttons for ALL Available Files
    # -----------------------------
    st.subheader("💾 Download Results")
    
    # Map format codes to user-friendly names and file extensions
    format_info = {
        "json": {
            "label": "📥 Download JSON",
            "mime": "application/json",
            "extension": ".json",
            "description": "Complete product data in JSON format"
        },
        "csv": {
            "label": "📥 Download CSV (Basic)",
            "mime": "text/csv",
            "extension": ".csv",
            "description": "Basic CSV with core product fields"
        },
        "csv_prices": {
            "label": "📥 Download CSV (With Prices)",
            "mime": "text/csv",
            "extension": "_with_prices.csv",
            "description": "CSV with detailed price information"
        },
        "quotation": {
            "label": "📥 Download Quotation Template",
            "mime": "application/json",
            "extension": "_quotation_template.json",
            "description": "JSON template formatted for quotations"
        }
    }
    
    # Create download buttons for each available file
    download_count = 0
    for fmt, file_path in available_files.items():
        if fmt in format_info:
            info = format_info[fmt]
            
            try:
                # Download the file content
                file_content = api_client.download_results(job_id, fmt)
                
                # Create filename
                filename = f"{output_file}{info['extension']}"
                
                # Create download button
                st.download_button(
                    label=info["label"],
                    data=file_content,
                    file_name=filename,
                    mime=info["mime"],
                    help=info["description"],
                    use_container_width=True,
                    key=f"download_{fmt}"
                )
                download_count += 1
                
            except Exception as e:
                st.error(f"❌ Failed to prepare {fmt.upper()} download: {str(e)}")
    
    if download_count == 0:
        st.warning("⚠️ No downloadable files available")
    else:
        st.success(f"✅ {download_count} file(s) ready for download")
    
    # Post-scrape Google Sheets Upload Option
    if not enable_sheets and google_sheets_available and total_products > 0:
        st.markdown("---")
        st.markdown("### 📊 Upload to Google Sheets")
        
        with st.form("sheets_upload_form"):
            st.info("You can still upload these results to Google Sheets!")
            
            post_sheets_id = st.text_input(
                "Spreadsheet ID (optional)",
                placeholder="Leave empty to create new spreadsheet",
                help="Provide an existing spreadsheet ID or leave empty to create new"
            )
            
            post_sheets_title = st.text_input(
                "Spreadsheet Title",
                value=f"Product Catalog - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                help="Title for the new spreadsheet (if creating new)"
            )
            
            include_prices = st.checkbox("Include prices", value=True)
            
            upload_button = st.form_submit_button(
                "📊 Upload to Google Sheets",
                use_container_width=True
            )
            
            if upload_button:
                with st.spinner("Uploading to Google Sheets..."):
                    try:
                        sheets_result = api_client.upload_to_sheets(
                            job_id=job_id,
                            spreadsheet_id=post_sheets_id if post_sheets_id else None,
                            spreadsheet_title=post_sheets_title,
                            include_prices=include_prices
                        )
                        
                        if sheets_result.get("success"):
                            st.success("✅ Successfully uploaded to Google Sheets!")
                            sheets_url = sheets_result.get("url")
                            st.markdown(f"**🔗 [Open Spreadsheet]({sheets_url})**")
                            st.code(sheets_url, language=None)
                        else:
                            st.error("❌ Failed to upload to Google Sheets")
                    except Exception as e:
                        st.error(f"❌ Upload failed: {str(e)}")
    
    # Show available files info
    with st.expander("📂 Available Files Details", expanded=False):
        st.json(available_files)
    
    # Show tips based on results
    st.markdown("---")
    st.markdown("### 💡 Tips")
    
    if strictness == "lenient" and total_products > 100:
        st.info("You're using **lenient** mode with many results. Consider using **balanced** or **strict** mode for cleaner data.")
    elif strictness == "strict" and total_products < 10:
        st.info("You're using **strict** mode with few results. Consider using **balanced** or **lenient** mode to find more products.")
    else:
        st.success(f"**{strictness.title()}** mode appears to be working well for this website!")
    
    # Show backend-specific tips
    if backend_mode == "Local Server":
        st.info("🏠 Using local backend - great for development and testing!")
    
    # Show format-specific tips
    if len(export_formats) > 1:
        st.info(f"📊 Multiple formats exported: {', '.join(export_formats)}")