"""
Consistent styling for TrustIssues.AI
Single source of truth for all CSS across the application
"""

# Professional Color Palette
COLORS = {
    'primary': '#2563eb',      # Professional blue
    'primary_dark': '#1e40af',
    'primary_light': '#3b82f6',
    'secondary': '#10b981',    # Green accent
    'danger': '#dc2626',       # Red
    'warning': '#f59e0b',      # Orange
    'success': '#10b981',      # Green
    'background': '#f9fafb',   # Subtle off-white
    'surface': '#ffffff',      # Pure white for cards
    'text': '#111827',         # Dark text
    'text_secondary': '#6b7280', # Gray text
    'border': '#e5e7eb',       # Light border
}

# Base CSS that applies to all pages
BASE_CSS = f"""
<style>
/* Hide Streamlit branding */
#MainMenu {{visibility: hidden;}}
header {{visibility: hidden;}}
footer {{visibility: hidden;}}

/* Professional background */
.main {{
    background-color: {COLORS['background']} !important;
}}

.stApp {{
    background-color: {COLORS['background']} !important;
}}

/* Professional typography */
h1, h2, h3, h4, h5, h6 {{
    color: {COLORS['text']} !important;
    font-weight: 600;
}}

p, span, label, div, .stMarkdown {{
    color: {COLORS['text']} !important;
}}

.element-container, .stMarkdown, .stText {{
    color: {COLORS['text']} !important;
}}

/* Cards */
.card {{
    background: {COLORS['surface']};
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-bottom: 16px;
    border: 1px solid {COLORS['border']};
}}

/* Professional header bar */
.header-bar {{
    background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_dark']});
    color: white;
    padding: 24px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
}}

.header-bar h1 {{
    color: white !important;
    margin: 0;
    font-size: 28px;
}}

.header-bar p {{
    color: rgba(255,255,255,0.95) !important;
    margin: 4px 0 0 0;
    font-size: 14px;
}}

/* Professional buttons */
.stButton > button {{
    border-radius: 8px;
    font-weight: 500;
    padding: 10px 20px;
    border: none;
    transition: all 0.2s;
    background: {COLORS['primary']} !important;
    color: white !important;
}}

.stButton > button:hover {{
    background: {COLORS['primary_dark']} !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    transform: translateY(-1px);
}}

.stButton > button[kind="secondary"] {{
    background: {COLORS['surface']} !important;
    color: {COLORS['text']} !important;
    border: 1px solid {COLORS['border']} !important;
}}

.stButton > button[kind="secondary"]:hover {{
    background: {COLORS['background']} !important;
    border-color: {COLORS['primary']} !important;
}}

/* Input fields */
.stTextInput > div > div > input {{
    border-radius: 8px;
    border: 1px solid {COLORS['border']};
    padding: 8px 12px;
}}

.stTextInput > div > div > input:focus {{
    border-color: {COLORS['primary']};
    box-shadow: 0 0 0 1px {COLORS['primary']};
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    border-bottom: 1px solid {COLORS['border']};
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: 8px 8px 0 0;
    color: {COLORS['text_secondary']};
    padding: 12px 24px;
    font-weight: 500;
}}

.stTabs [aria-selected="true"] {{
    background-color: {COLORS['surface']};
    color: {COLORS['primary']} !important;
    border-bottom: 2px solid {COLORS['primary']};
}}

/* File uploader */
.stFileUploader {{
    border-radius: 8px;
}}

/* Metrics */
.metric-card {{
    background: {COLORS['surface']};
    border-radius: 8px;
    padding: 16px;
    border: 1px solid {COLORS['border']};
    text-align: center;
}}

/* Status badges */
.badge {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}}

.badge-success {{
    background: #dcfce7;
    color: #166534;
}}

.badge-warning {{
    background: #fef3c7;
    color: #92400e;
}}

.badge-danger {{
    background: #fee2e2;
    color: #991b1b;
}}

.badge-info {{
    background: #dbeafe;
    color: #1e40af;
}}

/* Risk indicators */
.risk-low {{
    color: {COLORS['success']};
    font-weight: 600;
}}

.risk-medium {{
    color: {COLORS['warning']};
    font-weight: 600;
}}

.risk-high {{
    color: {COLORS['danger']};
    font-weight: 600;
}}

/* Expander */
.streamlit-expanderHeader {{
    border-radius: 8px;
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
}}

/* Select box */
.stSelectbox > div > div {{
    border-radius: 8px;
}}

/* Progress bar */
.stProgress > div > div {{
    background-color: {COLORS['primary']};
}}

/* Sidebar */
.css-1d391kg {{
    background-color: {COLORS['surface']};
}}

/* Remove extra padding */
.block-container {{
    padding-top: 2rem;
    padding-bottom: 2rem;
}}
</style>
"""

def get_base_css():
    """Return the base CSS for all pages"""
    return BASE_CSS

def get_page_config(title, icon="🛡️", layout="wide"):
    """Standard page configuration"""
    return {
        "page_title": f"{title} - TrustIssues.AI",
        "page_icon": icon,
        "layout": layout,
        "initial_sidebar_state": "collapsed"
    }

