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

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="header-container">
    <div class="header-title">
        <div class="header-text">
            <h1>Product Catalog Scraper</h1>
            <p>AI-powered data extraction</p>
        </div>
    </div>
    <div class="backend-status">
        <span class="status-dot" style="background-color: #28a745;"></span>
        Backend Online
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Backend Configuration Options
# -----------------------------
BACKEND_OPTIONS = {
    "Local": "http://localhost:7860",
    "LAM Sales": "https://gouriikarus3d-lam-sales.hf.space",
    "Catalogue AI": "https://gouriikarus3d-catalog-ai.hf.space/"
    # "Product Catalogue AI": "https://gouriikarus3d-product-catalogue-ai.hf.space"
}

# -----------------------------
# Backend Feature Detection
# -----------------------------
@st.cache_data(ttl=60)
def get_backend_features(api_base: str):
    try:
        r = requests.get(f"{api_base}/features", timeout=5)
        if r.status_code == 200:
            return {"available": True, **r.json()}
    except:
        pass
    return {"available": False, "google_sheets": {"enabled": False}}

# -----------------------------
# Initialize Session State
# -----------------------------
if 'scraping_started' not in st.session_state:
    st.session_state.scraping_started = False
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'job_status' not in st.session_state:
    st.session_state.job_status = None
if 'progress_pct' not in st.session_state:
    st.session_state.progress_pct = 0
if 'poll_count' not in st.session_state:
    st.session_state.poll_count = 0
if 'backend_url' not in st.session_state:
    st.session_state.backend_url = BACKEND_OPTIONS["LAM Sales"]

# -----------------------------
# Sidebar – Scraper Settings
# -----------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-section-header">🌐 Website URL</div>', unsafe_allow_html=True)
    url = st.text_input(
        "Target Website URL",
        placeholder="https://example.com/products",
        label_visibility="collapsed"
    )
    
    # AI Recommendation Section - Always Visible - OUTSIDE FORM
    st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-header">🧠 AI Recommendation</div>', unsafe_allow_html=True)
    
    recommend_intent = st.text_area(
        "What do you want to extract?",
        value="Extract the product information, price and customizations",
        height=80,
        help="Describe your extraction goal in natural language"
    )
    
    get_recommendation_btn = st.button(
        "🚀 Get AI Recommendation",
        use_container_width=True,
        help="Let Gemini analyze the site and recommend optimal crawler/scraper combination"
    )
    
    if get_recommendation_btn:
        if url and recommend_intent:
            st.info("💡 AI will analyze the site and suggest the best strategy")
        elif not url:
            st.warning("⚠️ Please enter a website URL first")
        elif not recommend_intent:
            st.warning("⚠️ Please describe what you want to extract")
    
    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
    
    # Manual Configuration - INSIDE FORM
    with st.form("scraper_form"):
        st.markdown('<div class="sidebar-section-header">⚙️ Manual Configuration</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section-header">⚙️ Backend Selection</div>', unsafe_allow_html=True)
        
        # Determine current index for the radio button
        current_index = 0
        for idx, (key, url_val) in enumerate(BACKEND_OPTIONS.items()):
            if url_val == st.session_state.backend_url:
                current_index = idx
                break
        
        selected_backend = st.radio(
            "Backend",
            options=list(BACKEND_OPTIONS.keys()),
            index=current_index,
            label_visibility="collapsed",
            help="Local: localhost:7860\nLAM Sales: HF Space optimized for LAM model\nProduct Catalogue AI: HF Space for all models"
        )
        
        # Update backend URL
        new_backend_url = BACKEND_OPTIONS[selected_backend]
        if new_backend_url != st.session_state.backend_url:
            st.session_state.backend_url = new_backend_url
            # Clear cache when switching backends
            get_backend_features.clear()
        
        # Show backend status
        backend_features = get_backend_features(st.session_state.backend_url)
        backend_status = backend_features.get("available", False)
        if backend_status:
            st.success(f"✅ Connected to {selected_backend}")
        else:
            st.warning(f"⚠️ Cannot connect to {selected_backend}")
            if selected_backend == "Local":
                st.caption("Make sure the backend is running: `uvicorn app:app --port 7860`")
        
        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
        
        # Get google sheets availability from current backend
        google_sheets_available = backend_features.get("google_sheets", {}).get("enabled", False)

        st.markdown('<div class="sidebar-section-header" style="margin-top: 1.5rem;">🔍 Crawler Selection</div>', unsafe_allow_html=True)
        
        crawler_options = {
            "Web Crawler": "web",
            "AI Crawler (Legacy)": "ai",
            "Unified Crawler (Recommended)": "unified"
        }
        
        crawler_display = st.radio(
            "Crawler Type",
            options=list(crawler_options.keys()),
            index=2,  # Default to Unified
            label_visibility="collapsed",
            help="Web: Traditional crawling with classification\nAI: Legacy Gemini-powered crawler\nUnified: Discover + AI filter (recommended)"
        )
        crawler = crawler_options[crawler_display]
        
        # Crawler descriptions
        # crawler_descriptions = {
        #     "Web Crawler": "🌐 Traditional: Crawls pages and classifies using rule-based signals (fast, reliable for standard sites)",
        #     "AI Crawler (Legacy)": "🤖 Legacy AI: Uses Jina + Gemini for page classification (requires Jina API)",
        #     "Unified Crawler (Recommended)": "✨ Best Choice: Discovers all URLs then uses Gemini to filter by intent (no Jina required, more reliable)"
        # }
        # st.info(crawler_descriptions[crawler_display])
        
        st.markdown('<div class="sidebar-section-header" style="margin-top: 1.5rem;">⚙️ Scraper Selection</div>', unsafe_allow_html=True)
        
        scraper_options = {
            "Static (HTML Parsing)": "static",
            "LAM (Gemini + Playwright)": "lam",
            "AI (AI Extraction)": "ai",
            "Auto (Intelligent Routing)": "auto"
        }
        
        scraper_display = st.radio(
            "Scraper Type",
            options=list(scraper_options.keys()),
            index=3,  # Default to Auto
            label_visibility="collapsed",
            help="Static: Fast HTML parsing\nLAM: Gemini-guided interactive extraction for configurators\nAI: AI-powered semantic extraction\nAuto: Intelligent routing based on content type"
        )
        scraper = scraper_options[scraper_display]
        
        # Scraper descriptions
        scraper_descriptions = {
            "Static (HTML Parsing)": "⚡ Fast: Extracts data from HTML using Jina AI (works on most sites)",
            "LAM (Gemini + Playwright)": "🎯 Interactive: Uses Gemini + Playwright to navigate configurators and extract variants",
            "AI (AI Extraction)": "🧠 Semantic: AI-powered extraction with deep content understanding",
            "Auto (Intelligent Routing)": "🤖 Smart: Analyzes each URL and routes to optimal scraper (LAM/Static/AI) automatically"
        }
        st.info(scraper_descriptions[scraper_display])
        
        # Force AI option (only for LAM scraper)
        force_ai = False
        if scraper == "lam":
            force_ai = st.checkbox(
                "Force AI Extraction",
                value=False,
                help="Force Gemini AI extraction even for static sites (no fallback to static extraction)"
            )
            if force_ai:
                st.caption("⚡ AI-only mode: No fallback to static extraction")
        
        # Result Optimization
        st.markdown('<div class="sidebar-section-header" style="margin-top: 1.5rem;">🎯 Post-Processing</div>', unsafe_allow_html=True)
        optimize_results = st.checkbox(
            "Optimize Results",
            value=True,
            help="Use AI to remove duplicates and filter out invalid entries (questions, FAQs, generic text)"
        )
        if optimize_results:
            st.caption("✨ AI will clean results before export")
        
        # User Intent (REQUIRED for AI/unified crawler or auto scraper, optional for LAM/AI scraper)
        user_intent = None
        intent_required = crawler in ["ai", "unified"] or scraper == "auto"
        intent_recommended = scraper in ["lam", "ai"]
        
        if intent_required or intent_recommended:
            intent_label = "🎯 Extraction Intent" + (" (Required)" if intent_required else " (Recommended)")
            st.markdown(f'<div class="sidebar-section-header" style="margin-top: 1.5rem;">{intent_label}</div>', unsafe_allow_html=True)
            
            # Default intent based on combination
            if crawler in ["ai", "unified"]:
                default_intent = "Extract the product information, price and customizations"
            elif scraper == "auto":
                default_intent = "Extract the product information, price and customizations"
            elif scraper == "lam":
                default_intent = "Extract the product information, price and customizations"
            else:
                default_intent = "Extract the product information, price and customizations"
            
            user_intent = st.text_area(
                "User Intent",
                value=default_intent,
                height=100,
                label_visibility="collapsed",
                help="Describe what you want to extract. Be specific about what to include and exclude."
            )
            
            if intent_required:
                if scraper == "auto":
                    st.caption("🔍 Auto scraper requires intent for intelligent routing")
                else:
                    st.caption("🔍 AI/Unified crawler requires intent to filter pages")
            if crawler in ["ai", "unified"]:
                st.caption("💡 Examples: 'Extract RV projects', 'Find luxury homes with pricing', 'Collect industrial case studies'")
            elif scraper == "auto":
                st.caption("💡 Describe what to extract - the system will route each URL to the best scraper")
            elif scraper == "lam":
                st.caption("💡 Be specific: mention what to extract and what to ignore")

        st.markdown('<div class="sidebar-section-header" style="margin-top: 1.5rem;">🎯 Scraping Strictness</div>', unsafe_allow_html=True)
        
        strictness_options = {
            "Lenient": "lenient",
            "Balanced": "balanced",
            "Strict": "strict"
        }
        
        strictness_display = st.radio(
            "Strictness Level",
            options=list(strictness_options.keys()),
            index=1,
            label_visibility="collapsed",
            help="Lenient: Captures more products, may include noise\nBalanced: Optimal balance of coverage and accuracy\nStrict: High precision, may miss some products"
        )
        strictness = strictness_options[strictness_display]
        
        # Description based on selection
        strictness_descriptions = {
            "Lenient": "Captures more products, may include some noise",
            "Balanced": "Optimal balance of coverage and accuracy",
            "Strict": "High precision, may miss some products"
        }
        st.caption(strictness_descriptions[strictness_display])

        st.markdown('<div class="sidebar-section-header" style="margin-top: 1.5rem;">📊 Crawling Controls</div>', unsafe_allow_html=True)
        
        max_pages = st.slider("Max Pages", 10, 300, 25, 10)
        max_depth = st.slider("Max Depth", 1, 5, 3)
        delay = st.slider("Delay", 0.1, 5.0, 0.5, 0.1, format="%.1fs")

        st.markdown('<div class="sidebar-section-header" style="margin-top: 1.5rem;">📄 Export Format</div>', unsafe_allow_html=True)
        st.caption("JSON export is enabled by default")

        export_formats = ["json"]

        st.markdown('<div class="sidebar-section-header" style="margin-top: 1.5rem;">📊 Google Sheets</div>', unsafe_allow_html=True)
        
        if google_sheets_available:
            enable_sheets = st.toggle("Enable Google Sheets Upload", value=True)
            if enable_sheets:
                st.caption("Results will be exported to your connected Google Sheet")
                st.markdown("[📊 Open Google Sheet](https://docs.google.com/spreadsheets/d/1SrD1nYSuHEIF8i8n8Xs3mg3f8KviYgm0TbYC1AbhquQ/edit?gid=0#gid=0)")
            sheets_id = None
        else:
            enable_sheets = False
            sheets_id = None
            st.warning("⚠️ Google Sheets not enabled on backend")

        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        run_button = st.form_submit_button(
            "▶️ Start Scraping",
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
    
    def recommend(self, url: str, intent: str):
        """Get AI-powered recommendation from master.py"""
        r = self.session.post(
            f"{self.base_url}/recommend",
            json={"url": url, "intent": intent},
            timeout=30
        )
        r.raise_for_status()
        return r.json()

# -----------------------------
# Main Content Area
# -----------------------------

# Create a placeholder for the main content
main_content = st.empty()

if not st.session_state.scraping_started:
    # Empty State using native Streamlit
    with main_content.container():
        st.markdown("<div style='text-align: center; padding: 4rem 2rem;'>", unsafe_allow_html=True)
        
        # Icon and title
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style='text-align: center;'>
                <div style='width: 80px; height: 80px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
                     border-radius: 20px; display: inline-flex; align-items: center; justify-content: center; 
                     color: white; font-size: 40px; margin-bottom: 1.5rem;'>
                    ✨
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("# Ready to Extract Products")
            st.markdown("""
            <p style='color: #6b7280; font-size: 1rem; line-height: 1.5;'>
                Configure your scraping parameters in the sidebar and click "Start Scraping" 
                to extract structured product data from any e-commerce website.
            </p>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <p style='margin-top: 1rem;'>
                <a href='#' style='color: #3b82f6; text-decoration: none; font-weight: 500;'>
                    ← Configure settings to get started
                </a>
            </p>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Run Scraper
# -----------------------------
if run_button:
    if not url.startswith(("http://", "https://")):
        st.error("⚠️ Please enter a valid URL starting with http:// or https://")
        st.stop()

    if not export_formats:
        st.error("⚠️ Please select at least one export format")
        st.stop()

    # Clear the empty state and mark scraping as started
    st.session_state.scraping_started = True
    main_content.empty()
    
    api = HFAPIClient(st.session_state.backend_url)

    with st.spinner("Checking backend availability..."):
        try:
            api.health()
        except Exception as e:
            st.error(f"❌ Backend unavailable: {str(e)}")
            st.stop()
    
    # Step 0: Get AI Recommendation (if enabled)
    if get_recommendation and recommend_intent:
        st.info("🧠 Getting AI-powered recommendation from Master Flow Recommender...")
        
        try:
            # Call /recommend endpoint
            recommend_payload = {
                "url": url,
                "intent": recommend_intent
            }
            
            response = api.session.post(
                f"{api.base_url}/recommend",
                json=recommend_payload,
                timeout=30
            )
            response.raise_for_status()
            recommendation_result = response.json()
            
            if recommendation_result.get("success"):
                rec = recommendation_result.get("recommendation", {})
                
                # Display recommendation
                st.success("✅ Recommendation received!")
                
                with st.expander("📋 View AI Recommendation", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Crawler", rec.get("crawler", "N/A").upper())
                    with col2:
                        st.metric("Scraper", rec.get("scraper", "N/A").upper())
                    with col3:
                        st.metric("Strictness", rec.get("strictness", "N/A").upper())
                    
                    if rec.get("reasoning"):
                        st.markdown("**Reasoning:**")
                        for key, value in rec.get("reasoning", {}).items():
                            st.markdown(f"- **{key}**: {value}")
                
                # Apply recommendation
                crawler = rec.get("crawler", crawler)
                scraper = rec.get("scraper", scraper)
                strictness = rec.get("strictness", strictness)
                user_intent = recommend_intent  # Use the recommendation intent
                
                # Apply exploration config if available
                exploration_config = rec.get("exploration_config", {})
                if exploration_config.get("max_pages"):
                    max_pages = exploration_config.get("max_pages", max_pages)
                if exploration_config.get("max_depth"):
                    max_depth = exploration_config.get("max_depth", max_depth)
                
                st.info(f"🚀 Proceeding with recommended configuration: {crawler} crawler + {scraper} scraper")
            else:
                st.warning("⚠️ Could not get recommendation, using manual configuration")
        
        except Exception as e:
            st.warning(f"⚠️ Recommendation failed: {str(e)}")
            st.info("Proceeding with manual configuration...")

    payload = {
        "url": url,
        "max_pages": max_pages,
        "max_depth": max_depth,
        "crawl_delay": delay,
        "export_formats": export_formats,
        "strictness": strictness,
        "crawler": crawler,
        "scraper": scraper,
        "force_ai": force_ai,
        "intent": user_intent,
        "optimize": optimize_results,
        "google_sheets_upload": enable_sheets,
        "google_sheets_id": sheets_id
    }

    st.info("🚀 Submitting scraping job...")
    job = api.start_scrape(payload)
    job_id = job.get("job_id")

    if not job_id:
        st.error("❌ No job ID returned")
        st.stop()
    
    st.session_state.job_id = job_id
    st.session_state.progress_pct = 5
    st.session_state.poll_count = 0
    
    # Trigger immediate rerun to start polling
    st.rerun()

# -----------------------------
# Job Status Polling (Non-blocking)
# -----------------------------
if st.session_state.scraping_started and st.session_state.job_id:
    api = HFAPIClient(st.session_state.backend_url)
    
    # Poll the backend for current status
    try:
        job = api.job_status(st.session_state.job_id)
        status = job.get("status")
        message = job.get("message", "")
        
        st.session_state.job_status = job
        st.session_state.poll_count += 1
        
        # Calculate progress percentage based on actual backend stages
        if status == "pending":
            st.session_state.progress_pct = 5
        elif status == "running":
            # Try to extract progress from message
            if "Crawling" in message or "Discovering" in message:
                # Crawling phase: 10-40%
                try:
                    if "[" in message and "/" in message:
                        # Extract current/total from message like "[3/10]"
                        parts = message.split("[")[1].split("]")[0].split("/")
                        current = int(parts[0])
                        total = int(parts[1])
                        st.session_state.progress_pct = 10 + int((current / total) * 30)
                    else:
                        # Gradually increase if no specific progress
                        st.session_state.progress_pct = min(st.session_state.progress_pct + 2, 40)
                except:
                    st.session_state.progress_pct = min(st.session_state.progress_pct + 2, 40)
            elif "Scraping product" in message or "Product Summary" in message:
                # Scraping phase: 40-70%
                st.session_state.progress_pct = min(max(st.session_state.progress_pct + 1, 40), 70)
            elif "Uploading" in message or "Google Sheets" in message:
                # Upload phase: 70-85%
                st.session_state.progress_pct = min(max(st.session_state.progress_pct + 2, 70), 85)
            elif "Exporting" in message or "files" in message:
                # Export phase: 85-95%
                st.session_state.progress_pct = min(max(st.session_state.progress_pct + 2, 85), 95)
            else:
                # General running - gradual increase
                st.session_state.progress_pct = min(st.session_state.progress_pct + 1, 90)
        elif status == "exporting":
            st.session_state.progress_pct = 95
        elif status == "completed":
            st.session_state.progress_pct = 100
        elif status == "failed":
            st.session_state.progress_pct = 0
        
        # Display job status
        status_emoji = {
            "pending": "⏳",
            "running": "🔄",
            "exporting": "📦",
            "completed": "✅",
            "failed": "❌"
        }.get(status, "🔄")
        
        status_display = status.replace("_", " ").title()
        
        # Header with status badge
        col_left, col_right = st.columns([3, 1])
        with col_left:
            st.markdown("### Job Status")
        with col_right:
            if status == "completed":
                st.success(f"{status_emoji} {status_display}")
            elif status == "failed":
                st.error(f"{status_emoji} {status_display}")
            else:
                st.info(f"{status_emoji} {status_display}")
        
        # Progress section
        st.markdown(f"**Progress: {st.session_state.progress_pct}%**")
        print(st.session_state.progress_pct)
        st.progress(int(st.session_state.progress_pct))

        
        # Current activity
        st.markdown("**Current Activity**")
        activity_msg = message if message else f"Scraping started (strictness: {strictness})"
        st.markdown(f"• {activity_msg}")
        
        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
        
        # Check if job is complete
        if status == "completed":
            # Job completed - show results
            result = job.get("result", {})
            files = result.get("files", {})
            total = result.get("total_products", 0)
            pages_crawled = result.get("pages_crawled", 0)
            duration = result.get("duration", "N/A")

            st.success("✅ Scraping completed successfully!")
            
            # Metrics Row using Streamlit native metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Products Scraped",
                    value=total,
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="Pages Crawled",
                    value=pages_crawled,
                    delta=None
                )
            
            with col3:
                st.metric(
                    label="Duration",
                    value=duration,
                    delta=None
                )
            
            with col4:
                st.metric(
                    label="Strictness",
                    value=strictness,
                    delta=None
                )

            st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

            # Results Section Header
            st.markdown("### 📥 Results Ready")
            st.caption(f"{len(files)} file(s) available for download")
            
            # Show Google Sheets link if enabled
            if enable_sheets:
                st.markdown("[📊 View in Google Sheets](https://docs.google.com/spreadsheets/d/1SrD1nYSuHEIF8i8n8Xs3mg3f8KviYgm0TbYC1AbhquQ/edit?gid=0#gid=0)")
                st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

            # Download Files
            format_meta = {
                "json": ("application/json", ".json", "📄", "JSON Export"),
                "csv": ("text/csv", ".csv", "📊", "CSV Export"),
                "csv_prices": ("text/csv", "_with_prices.csv", "💰", "Prices CSV"),
                "quotation": ("application/json", "_quotation.json", "📋", "Quotation")
            }

            for fmt in files:
                if fmt in format_meta:
                    mime, ext, icon, label = format_meta[fmt]
                    
                    try:
                        content = api.download(st.session_state.job_id, fmt)
                        file_size = len(content) / 1024  # KB
                        file_size_str = f"{file_size:.1f} KB" if file_size < 1024 else f"{file_size/1024:.1f} MB"
                        filename = f"products_{st.session_state.job_id[:8]}{ext}"
                        
                        # Create a clean download row
                        col_info, col_button = st.columns([3, 1])
                        
                        with col_info:
                            st.markdown(f"**{icon} {label}**")
                            st.caption(f"{filename} • {file_size_str}")
                        
                        with col_button:
                            st.download_button(
                                label="📥 Download",
                                data=content,
                                file_name=filename,
                                mime=mime,
                                use_container_width=True,
                                key=f"download_{fmt}"
                            )
                        
                        st.markdown("<div style='margin-bottom: 0.75rem;'></div>", unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Failed to download {fmt}: {str(e)}")
            
            # Don't rerun anymore - job is done
            
        elif status == "failed":
            st.error("❌ Job failed. Please try again.")
            
        else:
            # Job still in progress - check timeout
            if st.session_state.poll_count < 300:
                # Wait 2 seconds and rerun
                time.sleep(2)
                st.rerun()
            else:
                st.error("⏱️ Job polling timeout. The job may still be running on the backend.")
                
    except Exception as e:
        st.error(f"❌ Error polling job status: {str(e)}")
        st.session_state.scraping_started = False