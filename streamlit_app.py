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
# Custom CSS for Modern UI
# -----------------------------
# st.markdown("""
# <style>
#     /* Import Fonts */
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
#     /* Global Styles */
#     * {
#         font-family: 'Inter', sans-serif;
#     }
    
#     /* Hide Streamlit Branding */
#     #MainMenu {visibility: hidden;}
#     footer {visibility: hidden;}
#     header {visibility: hidden;}
    
#     /* Force Light Theme */
#     .stApp {
#         background: #f8f9fa !important;
#     }
    
#     /* Main Container */
#     .main {
#         background: #f8f9fa !important;
#         padding: 0;
#     }
    
#     .block-container {
#         padding-top: 2rem;
#         background: #f8f9fa !important;
#     }
    
#     /* Ensure all containers are light */
#     [data-testid="stAppViewContainer"] {
#         background: #f8f9fa !important;
#     }
    
#     [data-testid="stHeader"] {
#         background: transparent !important;
#     }
    
#     section[data-testid="stSidebar"] > div {
#         background: white !important;
#     }
    
#     /* Header Styling */
#     .header-container {
#         background: white;
#         padding: 1.5rem 2rem;
#         border-bottom: 1px solid #e5e7eb;
#         margin: -1rem -1rem 2rem -1rem;
#         display: flex;
#         align-items: center;
#         justify-content: space-between;
#     }
    
#     .header-title {
#         display: flex;
#         align-items: center;
#         gap: 0.75rem;
#     }
    
#     .header-icon {
#         width: 32px;
#         height: 32px;
#         background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
#         border-radius: 8px;
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         color: white;
#         font-size: 18px;
#     }
    
#     .header-text h1 {
#         font-size: 1.25rem;
#         font-weight: 600;
#         color: #111827;
#         margin: 0;
#         line-height: 1.2;
#     }
    
#     .header-text p {
#         font-size: 0.75rem;
#         color: #6b7280;
#         margin: 0;
#         font-weight: 400;
#     }
    
#     .backend-status {
#         display: flex;
#         align-items: center;
#         gap: 0.5rem;
#         font-size: 0.875rem;
#         color: #059669;
#         font-weight: 500;
#     }
    
#     .status-dot {
#         width: 8px;
#         height: 8px;
#         background: #10b981;
#         border-radius: 50%;
#         animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
#     }
    
#     @keyframes pulse {
#         0%, 100% {
#             opacity: 1;
#         }
#         50% {
#             opacity: 0.5;
#         }
#     }
    
#     /* Sidebar Styles */
#     [data-testid="stSidebar"] {
#         background: white;
#         padding: 1.5rem 1rem;
#     }
    
#     [data-testid="stSidebar"] > div:first-child {
#         background: white;
#     }
    
#     /* Section Headers in Sidebar */
#     .sidebar-section {
#         margin-bottom: 1.5rem;
#     }
    
#     .sidebar-section-header {
#         font-size: 0.75rem;
#         font-weight: 600;
#         color: #6b7280;
#         text-transform: uppercase;
#         letter-spacing: 0.05em;
#         margin-bottom: 0.75rem;
#         display: flex;
#         align-items: center;
#         gap: 0.5rem;
#     }
    
#     /* Input Labels */
#     .stTextInput > label,
#     .stSelectbox > label,
#     .stSlider > label,
#     .stRadio > label,
#     .stCheckbox > label,
#     .stMultiSelect > label {
#         color: #374151 !important;
#         font-weight: 500;
#         font-size: 0.875rem;
#     }
    
#     /* Input Styling */
#     .stTextInput > div > div > input {
#         border: 1px solid #e5e7eb;
#         border-radius: 8px;
#         padding: 0.625rem 0.875rem;
#         font-size: 0.875rem;
#         background: #f9fafb;
#         transition: all 0.2s;
#         color: #111827;
#     }
    
#     .stTextInput > div > div > input::placeholder {
#         color: #9ca3af;
#     }
    
#     .stTextInput > div > div > input:focus {
#         border-color: #3b82f6;
#         background: white;
#         box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
#     }
    
#     /* Ensure all text is dark and visible */
#     p, span, div, label {
#         color: #374151;
#     }
    
#     .stMarkdown p {
#         color: #374151;
#     }
    
#     /* Caption text */
#     .stCaption {
#         color: #6b7280 !important;
#     }
    
#     /* Select Box Styling */
#     .stSelectbox > div > div {
#         border: 1px solid #e5e7eb;
#         border-radius: 8px;
#         background: #f9fafb;
#         color: #111827;
#     }
    
#     .stSelectbox [data-baseweb="select"] {
#         color: #111827;
#     }
    
#     /* Slider Styling */
#     .stSlider > div > div > div {
#         background: #e5e7eb;
#     }
    
#     .stSlider > div > div > div > div {
#         background: #3b82f6;
#     }
    
#     .stSlider label {
#         color: #374151 !important;
#     }
    
#     .stSlider [data-testid="stTickBarMin"],
#     .stSlider [data-testid="stTickBarMax"] {
#         color: #6b7280 !important;
#     }
    
#     /* Radio Button Styling */
#     .stRadio > div {
#         gap: 0.5rem;
#     }
    
#     .stRadio > div > label {
#         background: white;
#         border: 2px solid #e5e7eb;
#         border-radius: 8px;
#         padding: 0.75rem 1rem;
#         cursor: pointer;
#         transition: all 0.2s;
#         display: flex;
#         align-items: center;
#         gap: 0.5rem;
#         color: #374151 !important;
#     }
    
#     .stRadio > div > label > div {
#         color: #374151 !important;
#     }
    
#     .stRadio > div > label:hover {
#         border-color: #3b82f6;
#         background: #f0f9ff;
#     }
    
#     .stRadio > div > label[data-checked="true"] {
#         border-color: #3b82f6;
#         background: #eff6ff;
#     }
    
#     /* Radio button labels */
#     .stRadio label p {
#         color: #374151 !important;
#         margin: 0;
#     }
    
#     /* Checkbox Styling */
#     .stCheckbox {
#         padding: 0.5rem 0;
#     }
    
#     .stCheckbox label {
#         color: #374151 !important;
#     }
    
#     .stCheckbox label span {
#         color: #374151 !important;
#     }
    
#     .stCheckbox label p {
#         color: #374151 !important;
#     }
    
#     /* Info/Warning Boxes */
#     .stAlert {
#         border-radius: 8px;
#         border: none;
#         padding: 0.75rem 1rem;
#         font-size: 0.875rem;
#     }
    
#     .stAlert p {
#         color: #374151 !important;
#     }
    
#     .stAlert [data-testid="stMarkdownContainer"] p {
#         color: #374151 !important;
#     }
    
#     /* Button Styling */
#     .stButton > button {
#         width: 100%;
#         background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
#         color: white;
#         border: none;
#         border-radius: 8px;
#         padding: 0.75rem 1.5rem;
#         font-weight: 600;
#         font-size: 0.875rem;
#         transition: all 0.2s;
#         box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
#     }
    
#     .stButton > button:hover {
#         background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
#         box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
#         transform: translateY(-1px);
#     }
    
#     .stButton > button:active {
#         transform: translateY(0);
#     }
    
#     /* Download Button */
#     .stDownloadButton > button {
#         width: 100%;
#         background: white;
#         color: #374151;
#         border: 1px solid #e5e7eb;
#         border-radius: 8px;
#         padding: 0.75rem 1rem;
#         font-weight: 500;
#         font-size: 0.875rem;
#         transition: all 0.2s;
#     }
    
#     .stDownloadButton > button:hover {
#         background: #f9fafb;
#         border-color: #d1d5db;
#     }
    
#     # /* Progress Bar */
#     # .stProgress > div > div {
#     #     background: #e5e7eb;
#     #     border-radius: 9999px;
#     #     height: 8px;
#     # }
    
#     # .stProgress > div > div > div {
#     #     background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
#     #     border-radius: 9999px;
#     # }
    
#     /* Metrics */
#     [data-testid="stMetricValue"] {
#         font-size: 1.875rem;
#         font-weight: 700;
#         color: #111827;
#     }
    
#     [data-testid="stMetricLabel"] {
#         font-size: 0.875rem;
#         font-weight: 500;
#         color: #6b7280;
#     }
    
#     /* Card Styling */
#     .status-card {
#         background: white;
#         border: 1px solid #e5e7eb;
#         border-radius: 12px;
#         padding: 1.5rem;
#         margin-bottom: 1.5rem;
#         box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
#     }
    
#     .metric-card {
#         background: white;
#         border: 1px solid #e5e7eb;
#         border-radius: 12px;
#         padding: 1.25rem;
#         text-align: center;
#         transition: all 0.2s;
#     }
    
#     .metric-card:hover {
#         box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
#         transform: translateY(-2px);
#     }
    
#     .metric-icon {
#         width: 48px;
#         height: 48px;
#         background: #eff6ff;
#         border-radius: 12px;
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         margin: 0 auto 1rem auto;
#         color: #3b82f6;
#         font-size: 24px;
#     }
    
#     .metric-value {
#         font-size: 2rem;
#         font-weight: 700;
#         color: #111827;
#         margin-bottom: 0.25rem;
#     }
    
#     .metric-label {
#         font-size: 0.875rem;
#         color: #6b7280;
#         font-weight: 500;
#     }
    
#     /* Empty State */
#     .empty-state {
#         text-align: center;
#         padding: 4rem 2rem;
#         background: white;
#         border-radius: 12px;
#         margin: 2rem;
#         border: 1px solid #e5e7eb;
#     }
    
#     .empty-state-icon {
#         width: 80px;
#         height: 80px;
#         background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
#         border-radius: 20px;
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         margin: 0 auto 1.5rem auto;
#         color: white;
#         font-size: 40px;
#     }
    
#     .empty-state-title {
#         font-size: 1.5rem;
#         font-weight: 700;
#         color: #111827;
#         margin-bottom: 0.5rem;
#     }
    
#     .empty-state-description {
#         font-size: 1rem;
#         color: #6b7280;
#         max-width: 500px;
#         margin: 0 auto;
#         line-height: 1.5;
#     }
    
#     .empty-state-link {
#         color: #3b82f6;
#         text-decoration: none;
#         font-weight: 500;
#         display: inline-flex;
#         align-items: center;
#         gap: 0.5rem;
#         margin-top: 1rem;
#         transition: all 0.2s;
#     }
    
#     .empty-state-link:hover {
#         color: #2563eb;
#     }
    
#     /* Job Status Card */
#     .job-status-header {
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#         margin-bottom: 1rem;
#     }
    
#     .job-status-title {
#         font-size: 1.125rem;
#         font-weight: 600;
#         color: #111827;
#     }
    
#     .job-status-badge {
#         display: inline-flex;
#         align-items: center;
#         gap: 0.5rem;
#         padding: 0.375rem 0.75rem;
#         background: #eff6ff;
#         color: #2563eb;
#         border-radius: 9999px;
#         font-size: 0.875rem;
#         font-weight: 500;
#     }
    
#     .job-status-badge.completed {
#         background: #d1fae5;
#         color: #059669;
#     }
    
#     .progress-section {
#         margin: 1.5rem 0;
#     }
    
#     .progress-label {
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#         margin-bottom: 0.5rem;
#         font-size: 0.875rem;
#         color: #6b7280;
#     }
    
#     .progress-percentage {
#         font-weight: 600;
#         color: #111827;
#     }
    
#     .activity-section {
#         background: #f9fafb;
#         border-radius: 8px;
#         padding: 1rem;
#         margin-top: 1rem;
#     }
    
#     .activity-title {
#         font-size: 0.75rem;
#         font-weight: 600;
#         color: #6b7280;
#         text-transform: uppercase;
#         letter-spacing: 0.05em;
#         margin-bottom: 0.5rem;
#     }
    
#     .activity-text {
#         font-size: 0.875rem;
#         color: #111827;
#         display: flex;
#         align-items: center;
#         gap: 0.5rem;
#     }
    
#     /* Results Section */
#     .results-header {
#         display: flex;
#         align-items: center;
#         gap: 0.75rem;
#         margin-bottom: 1.5rem;
#     }
    
#     .results-icon {
#         width: 40px;
#         height: 40px;
#         background: #d1fae5;
#         border-radius: 10px;
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         color: #059669;
#         font-size: 20px;
#     }
    
#     .results-title {
#         font-size: 1.125rem;
#         font-weight: 600;
#         color: #111827;
#     }
    
#     .results-subtitle {
#         font-size: 0.875rem;
#         color: #6b7280;
#     }
    
#     .download-item {
#         background: white;
#         border: 1px solid #e5e7eb;
#         border-radius: 8px;
#         padding: 1rem;
#         margin-bottom: 0.75rem;
#         display: flex;
#         align-items: center;
#         justify-content: space-between;
#         transition: all 0.2s;
#     }
    
#     .download-item:hover {
#         border-color: #3b82f6;
#         background: #f9fafb;
#     }
    
#     .download-info {
#         display: flex;
#         align-items: center;
#         gap: 0.75rem;
#     }
    
#     .download-icon {
#         width: 40px;
#         height: 40px;
#         background: #eff6ff;
#         border-radius: 8px;
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         color: #3b82f6;
#         font-size: 18px;
#     }
    
#     .download-details {
#         flex: 1;
#     }
    
#     .download-title {
#         font-size: 0.875rem;
#         font-weight: 600;
#         color: #111827;
#         margin-bottom: 0.125rem;
#     }
    
#     .download-meta {
#         font-size: 0.75rem;
#         color: #6b7280;
#     }
    
#     /* Multiselect Pills */
#     .stMultiSelect [data-baseweb="tag"] {
#         background: #eff6ff;
#         border: 1px solid #3b82f6;
#         border-radius: 6px;
#         color: #2563eb;
#         font-weight: 500;
#     }
    
#     .stMultiSelect input {
#         color: #111827 !important;
#     }
    
#     .stMultiSelect [data-baseweb="select"] {
#         color: #111827;
#     }
    
#     /* Form Labels - ensure all are dark */
#     label {
#         color: #374151 !important;
#     }
    
#     /* Streamlit native text */
#     .stMarkdown {
#         color: #374151;
#     }
    
#     /* Form Submit Button Override */
#     .stFormSubmitButton > button {
#         background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
#         color: white;
#         font-weight: 600;
#     }
    
#     /* Spacing Utilities */
#     .mb-1 { margin-bottom: 0.5rem; }
#     .mb-2 { margin-bottom: 1rem; }
#     .mb-3 { margin-bottom: 1.5rem; }
#     .mt-1 { margin-top: 0.5rem; }
#     .mt-2 { margin-top: 1rem; }
#     .mt-3 { margin-top: 1.5rem; }
    
#     /* Override any dark theme */
#     body {
#         background-color: #f8f9fa !important;
#     }
    
#     .main > div {
#         background-color: #f8f9fa !important;
#     }
    
#     /* Ensure no dark backgrounds anywhere */
#     div[data-testid="stVerticalBlock"] {
#         background-color: transparent !important;
#     }
    
#     div[data-testid="stHorizontalBlock"] {
#         background-color: transparent !important;
#     }
# </style>
# """, unsafe_allow_html=True)

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
# Hosted Backend Configuration
# -----------------------------
HF_API_BASE = "https://gouriikarus3d-product-catalogue-ai.hf.space"

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

# -----------------------------
# Sidebar – Scraper Settings
# -----------------------------
with st.sidebar:
    with st.form("scraper_form"):
        st.markdown('<div class="sidebar-section-header">🌐 Website URL</div>', unsafe_allow_html=True)
        url = st.text_input(
            "Target Website URL",
            placeholder="https://example.com/products",
            label_visibility="collapsed"
        )

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
            enable_sheets = st.toggle("Enable Google Sheets Upload", value=False)
            if enable_sheets:
                st.caption("Results will be exported to your connected Google Sheet")
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
    
    st.session_state.job_id = job_id
    st.session_state.progress_pct = 5
    st.session_state.poll_count = 0
    
    # Trigger immediate rerun to start polling
    st.rerun()

# -----------------------------
# Job Status Polling (Non-blocking)
# -----------------------------
if st.session_state.scraping_started and st.session_state.job_id:
    api = HFAPIClient(HF_API_BASE)
    
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