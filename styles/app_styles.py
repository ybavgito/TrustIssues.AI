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

/* Fix all container backgrounds - NO BLACK! */
div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"],
.element-container,
[data-testid="stExpander"],
.stContainer,
section[data-testid="stSidebar"],
.st-emotion-cache-1y4p8pa {{
    background-color: transparent !important;
}}

/* Ensure expanders have white background */
[data-testid="stExpander"] > div {{
    background-color: {COLORS['surface']} !important;
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

/* Fix file uploader button visibility - all possible selectors */
[data-testid="stFileUploader"] button,
.stFileUploader button,
.stFileUploader section button,
button[kind="secondary"] {{
    background-color: {COLORS['primary']} !important;
    color: white !important;
    border: 1px solid {COLORS['primary']} !important;
    padding: 8px 16px !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
}}

[data-testid="stFileUploader"] button:hover,
.stFileUploader button:hover,
.stFileUploader section button:hover {{
    background-color: {COLORS['primary_dark']} !important;
    border-color: {COLORS['primary_dark']} !important;
}}

/* Ensure text inside button is white */
[data-testid="stFileUploader"] button span,
.stFileUploader button span {{
    color: white !important;
}}

/* File uploader drag area */
.stFileUploader section > div {{
    border: 2px dashed {COLORS['border']} !important;
    border-radius: 8px !important;
    background-color: {COLORS['surface']} !important;
}}

.stFileUploader section > div:hover {{
    border-color: {COLORS['primary']} !important;
    background-color: {COLORS['background']} !important;
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

/* Fix expander header text visibility */
.streamlit-expanderHeader p,
.streamlit-expanderHeader div,
.streamlit-expanderHeader span,
[data-testid="stMarkdownContainer"] p,
[data-testid="stExpander"] p,
[data-testid="stExpander"] span,
[data-testid="stExpander"] div {{
    color: {COLORS['text']} !important;
    background-color: transparent !important;
}}

/* Expander content area */
.streamlit-expanderContent {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-top: none;
    border-radius: 0 0 8px 8px;
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

/* Target specific Streamlit emotion-cache classes that cause black backgrounds */
[class*="emotion-cache"] {{
    background-color: transparent !important;
}}

/* Re-apply specific backgrounds where needed */
.stApp,
.main {{
    background-color: {COLORS['background']} !important;
}}

.streamlit-expanderHeader,
.streamlit-expanderContent {{
    background-color: {COLORS['surface']} !important;
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

