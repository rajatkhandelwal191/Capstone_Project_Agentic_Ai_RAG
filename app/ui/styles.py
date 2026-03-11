import streamlit as st


def apply_global_styles():
    st.markdown(
        """
<style>
:root {
  --bg-main-1: #020617;
  --bg-main-2: #0f172a;
  --bg-main-3: #111827;
  --panel: rgba(15, 23, 42, 0.72);
  --panel-2: rgba(30, 41, 59, 0.74);
  --border: rgba(148, 163, 184, 0.32);
  --text: #e2e8f0;
  --muted: #cbd5e1;
  --accent: #22d3ee;
  --accent-2: #f59e0b;
}

.stApp {
  background:
    radial-gradient(circle at 0% 0%, rgba(34, 211, 238, 0.09), transparent 34%),
    radial-gradient(circle at 100% 0%, rgba(245, 158, 11, 0.08), transparent 30%),
    linear-gradient(135deg, var(--bg-main-1), var(--bg-main-2) 48%, var(--bg-main-3));
  color: var(--text);
}

h1, h2, h3, h4, h5, h6, p, li, label, span, div {
  color: var(--text);
}

[data-testid="stSidebar"] {
  background:
    linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(17, 24, 39, 0.96));
  border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
  color: #e5e7eb;
}

.hero-card {
  background: linear-gradient(130deg, #0f172a, #1e293b 45%, #0b1120);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(2, 6, 23, 0.45);
  padding: 20px 22px;
}

.hero-card h3 {
  margin: 0 0 10px 0;
  font-size: 1.55rem;
}

.hero-card p {
  margin: 0;
  color: var(--muted);
  line-height: 1.45;
}

.detail-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px 16px;
}

.detail-card h4 {
  margin: 0 0 8px 0;
}

.detail-card p {
  margin: 0;
  color: var(--muted);
}

.chip-wrap {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid rgba(34, 211, 238, 0.4);
  background: rgba(34, 211, 238, 0.12);
  color: #a5f3fc;
  font-size: 12px;
}

.chip-warn {
  border-color: rgba(245, 158, 11, 0.45);
  background: rgba(245, 158, 11, 0.12);
  color: #fde68a;
}

.stInfo, .stWarning, .stSuccess, .stError {
  border-radius: 10px;
}

[data-testid="stButton"] > button,
.stButton > button {
  min-height: 48px;
  padding: 0.62rem 1rem;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.2px;
  color: #f8fafc;
  border: 1px solid rgba(34, 211, 238, 0.55);
  border-radius: 12px;
  background: linear-gradient(135deg, #1e293b, #0f172a);
  box-shadow: 0 6px 16px rgba(2, 6, 23, 0.4);
}

[data-testid="stButton"] > button:hover,
.stButton > button:hover {
  border-color: rgba(34, 211, 238, 0.95);
  background: linear-gradient(135deg, #243447, #0f172a);
  transform: translateY(-1px);
}

[data-testid="stButton"] > button:focus,
.stButton > button:focus {
  outline: 2px solid rgba(34, 211, 238, 0.9);
  outline-offset: 1px;
}

.stTabs [role="tablist"] {
  gap: 10px;
}

.stTabs [role="tab"] {
  min-height: 44px;
  padding: 0.4rem 0.95rem;
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 10px 10px 0 0;
  background: rgba(15, 23, 42, 0.6);
  color: #e2e8f0;
  font-size: 1rem;
  font-weight: 700;
}

.stTabs [role="tab"][aria-selected="true"] {
  border-color: rgba(34, 211, 238, 0.8);
  color: #a5f3fc;
  background: rgba(8, 47, 73, 0.56);
}

[data-testid="stMetric"] {
  background: var(--panel-2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 8px 10px;
}

[data-testid="stMetric"] * {
  color: var(--text) !important;
}

div[data-testid="stCodeBlock"] pre {
  border: 1px solid var(--border);
  border-radius: 10px;
}
</style>
        """,
        unsafe_allow_html=True,
    )
