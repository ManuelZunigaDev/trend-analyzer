import streamlit as st
 
 
def inject_css() -> None:
    """Inyecta el CSS global con el tema oscuro editorial."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');
 
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
 
    .stApp { background: #0c0e14; color: #e8e8f0; }
 
    [data-testid="stSidebar"] {
                

        background: #111320;
        border-right: 1px solid #1e2235;
    }
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stSelectbox select {
        background: #1a1e30;
        border: 1px solid #2a2f48;
        color: #e8e8f0;
        border-radius: 8px;
                
    }
    .hero {
        padding: 2.5rem 0 1.5rem;
        border-bottom: 1px solid #1e2235;
        margin-bottom: 2rem;
                

    }
    .hero h1 {
        font-family: 'Syne', sans-serif;
                
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #e8e8f0 30%, #6c7aff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero p { color: #6b7280; font-size: 1rem; font-weight: 300; margin-top: 0.4rem; }
 
    .metric-card {
        flex: 1; min-width: 160px;
        background: #111320;
        border: 1px solid #1e2235;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        position: relative; overflow: hidden;
    }
    .metric-label {
        font-size: 0.72rem; font-weight: 500;
        letter-spacing: 0.12em; text-transform: uppercase;
        color: #6b7280; margin-bottom: 0.4rem;
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 2rem; font-weight: 700;
        color: #e8e8f0; line-height: 1;
    }
    .metric-delta { font-size: 0.78rem; margin-top: 0.3rem; }
    .delta-up   { color: #34d399; }
    .delta-down { color: #f87171; }
    .delta-flat { color: #6b7280; }
 
    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem; font-weight: 700;
        letter-spacing: 0.05em; text-transform: uppercase;
        color: #6c7aff; margin: 2rem 0 1rem;
    }
    .chart-box {
        background: #111320;
        border: 1px solid #1e2235;
        border-radius: 14px;
        padding: 1rem; margin-bottom: 1.5rem;
    }
    [data-testid="stDataFrame"] { background: #111320 !important; border-radius: 12px; }
 
    .stDownloadButton button {
        background: linear-gradient(135deg, #6c7aff, #a78bfa) !important;
        color: #fff !important; border: none !important;
        border-radius: 8px !important;
        font-family: 'Syne', sans-serif; font-weight: 700;
        padding: 0.5rem 1.2rem; transition: opacity 0.2s;
    }
    .stDownloadButton button:hover { opacity: 0.85 !important; }
 
    .kw-tag {
        display: inline-block; padding: 0.2rem 0.7rem;
        border-radius: 99px; font-size: 0.78rem;
        font-weight: 500; margin-right: 0.3rem;
    }
    .empty-state { text-align: center; padding: 4rem 2rem; color: #6b7280; }
    .empty-state h3 {
        font-family: 'Syne', sans-serif;
        font-size: 1.4rem; color: #9ca3af; margin-bottom: 0.5rem;
    }
    .insight-box {
        background: #111320; border: 1px solid #1e2235;
        border-left: 3px solid #6c7aff;
        border-radius: 10px; padding: 1rem 1.2rem;
        margin-bottom: 0.6rem; font-size: 0.9rem;
        color: #c4c4d4; line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)