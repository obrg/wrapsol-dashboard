import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
from io import BytesIO
import re

st.set_page_config(page_title="Wrapsol Dashboard", page_icon="🔆", layout="wide")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
.stApp { background-color: #F8F9F9 !important; }

/* ── Force all text dark ── */
*, *::before, *::after,
p, span, div, label, li, td, th, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stText { color: #1a1a1a !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] section,
[data-testid="stSidebar"] .block-container {
    background-color: #FFFFFF !important;
}
[data-testid="stSidebar"] { border-right: 2px solid #EAEAEA !important; }
[data-testid="stSidebar"] label {
    font-size: 0.7rem !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 1.3px !important;
    color: #707A79 !important;
}

/* ── Every input surface — light mode ── */
div[data-baseweb="input"],
div[data-baseweb="base-input"],
div[data-baseweb="input"] > div,
div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div > div,
div[data-testid="stTextInput"] > div,
div[data-testid="stTextInput"] > div > div,
div[data-testid="stSelectbox"] > div > div {
    background-color: #FFFFFF !important;
    border-color: #EAEAEA !important;
    border-radius: 8px !important;
    color: #1a1a1a !important;
}
input, textarea {
    background-color: #FFFFFF !important;
    color: #1a1a1a !important;
    border-color: #EAEAEA !important;
    caret-color: #FCD118 !important;
}
input::placeholder, textarea::placeholder {
    color: #b0b8b7 !important; opacity: 1 !important;
}
div[data-baseweb="input"]:focus-within,
div[data-baseweb="select"]:focus-within {
    border-color: #FCD118 !important;
    box-shadow: 0 0 0 2px rgba(252,209,24,0.18) !important;
}

/* ── Date input — force white ── */
div[data-testid="stDateInput"] div[data-baseweb="input"],
div[data-testid="stDateInput"] div[data-baseweb="base-input"],
div[data-testid="stDateInput"] div[data-baseweb="input"] > div,
div[data-testid="stDateInput"] input {
    background-color: #FFFFFF !important;
    color: #1a1a1a !important;
    border-color: #EAEAEA !important;
}
div[data-baseweb="calendar"],
div[data-baseweb="datepicker"],
div[data-baseweb="calendar"] > div,
div[class*="CalendarWrapper"],
div[class*="StyledCalendarContainer"],
div[class*="stDateInputPopover"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #EAEAEA !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1) !important;
    color: #1a1a1a !important;
}
div[data-baseweb="calendar"] *,
div[data-baseweb="datepicker"] * { color: #1a1a1a !important; background-color: transparent !important; }
div[data-baseweb="calendar"] button,
div[data-baseweb="calendar"] td { color: #1a1a1a !important; }
div[data-baseweb="calendar"] button:hover { background-color: #F8F9F9 !important; border-radius: 50% !important; }
div[data-baseweb="calendar"] [aria-selected="true"],
div[data-baseweb="calendar"] button[aria-selected="true"] {
    background-color: #FCD118 !important;
    color: #1a1a1a !important;
    border-radius: 50% !important;
}
div[data-testid="stDateInputPopoverContent"],
div[data-testid="stDateInputPopoverContent"] * {
    background-color: #FFFFFF !important;
    color: #1a1a1a !important;
}

/* ── Multiselect ── */
div[data-testid="stMultiSelect"] > div,
div[data-testid="stMultiSelect"] > div > div {
    background-color: #FFFFFF !important;
    border-color: #EAEAEA !important;
    border-radius: 8px !important;
}
span[data-baseweb="tag"], div[data-baseweb="tag"] {
    background-color: #F0F1F1 !important;
    border: 1px solid #EAEAEA !important;
    border-radius: 6px !important;
}
span[data-baseweb="tag"] *, div[data-baseweb="tag"] * { color: #1a1a1a !important; }
div[data-testid="stMultiSelect"] svg,
div[data-testid="stSelectbox"] svg,
div[data-testid="stDateInput"] svg,
div[data-baseweb="select"] svg,
div[data-baseweb="input"] svg {
    fill: #707A79 !important; color: #707A79 !important; stroke: none !important;
}

/* ── Dropdown popup ── */
div[data-baseweb="popover"] > div,
ul[data-baseweb="menu"],
div[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
    border: 1px solid #EAEAEA !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
}
li[role="option"], li[data-baseweb="menu-item"] {
    background-color: #FFFFFF !important; color: #1a1a1a !important;
}
li[role="option"]:hover, li[data-baseweb="menu-item"]:hover { background-color: #F8F9F9 !important; }
li[aria-selected="true"] { background-color: rgba(252,209,24,0.12) !important; }

/* ── st.metric overrides ── */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #EAEAEA;
    border-left: 4px solid #FCD118;
    border-radius: 14px;
    padding: 16px 18px !important;
}
div[data-testid="stMetricLabel"] > div { font-size: 0.65rem !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 1.4px !important; color: #9ba5a4 !important; }
div[data-testid="stMetricValue"] > div { font-size: 1.75rem !important; font-weight: 800 !important; color: #1a1a1a !important; }
div[data-testid="stMetricDelta"] > div { font-size: 0.82rem !important; font-weight: 700 !important; }
div[data-testid="stMetricDelta"][data-direction=""] > div { color: #9ba5a4 !important; }

/* ── Transactions special card ── */
.txn-card {
    background: #FFFFFF;
    border: 1px solid #EAEAEA;
    border-radius: 14px;
    padding: 16px 18px;
    border-left: 4px solid #FCD118;
}
.txn-title { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.4px; color: #9ba5a4 !important; margin-bottom: 6px; }
.txn-total { font-size: 1.75rem; font-weight: 800; color: #1a1a1a !important; line-height: 1; margin-bottom: 12px; }
.txn-divider { height: 1px; background: #EAEAEA; margin-bottom: 10px; }
.txn-row { display: flex; justify-content: space-between; gap: 8px; }
.txn-sub { flex: 1; }
.txn-sub-lbl { font-size: 0.58rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #b0b8b7 !important; margin-bottom: 2px; }
.txn-sub-val { font-size: 1.1rem; font-weight: 800; color: #1a1a1a !important; }

/* ── Download buttons ── */
[data-testid="stDownloadButton"] button {
    background-color: #FFFFFF !important; color: #1a1a1a !important;
    border: 1.5px solid #EAEAEA !important; border-radius: 8px !important; font-weight: 600 !important;
}
[data-testid="stDownloadButton"] button:hover {
    border-color: #FCD118 !important; background-color: rgba(252,209,24,0.06) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F8F9F9; }
::-webkit-scrollbar-thumb { background: #EAEAEA; border-radius: 3px; }

/* ── Layout ── */
.ws-logo { font-weight: 800; font-size: 1.45rem; color: #1a1a1a !important; padding: 4px 0 14px; border-bottom: 3px solid #FCD118; margin-bottom: 20px; display: inline-block; }
.ws-logo span { color: #FCD118 !important; }
.page-title { font-weight: 800; font-size: 1.85rem; color: #1a1a1a !important; letter-spacing: -0.5px; }
.page-sub { font-size: 0.85rem; color: #707A79 !important; margin-bottom: 1.2rem; }
.sec { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.8px; color: #707A79 !important; margin-bottom: 10px; padding-bottom: 7px; border-bottom: 1px solid #EAEAEA; }
.ws-hr { height: 2px; background: linear-gradient(to right, #FCD118, #EAEAEA); border: none; margin: 6px 0 20px; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Config ─────────────────────────────────────────────────────────────────────
SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQMxwkcaP3FDKRk1iWxqhnvreBpJ-PbimDPGdE8KiXGj0ixRTveQFoyOn5vKyZq1sQU-_oxUzZhnD7h/pub?gid=541577724&single=true&output=csv"
)

DATE_COL    = "Transaction Date"
STORE_COL   = "Store Name"
DEVICE_COL  = "Device No"
CAT_COL     = "Category"
BRAND_COL   = "Brand"
MODEL_COL   = "Model"
PRODUCT_COL = "Product Name"
PLT_COL     = "PLT Code"

WS_COLORS = ["#FCD118","#c8ab00","#707A79","#9ba5a4","#e6c200","#4a5352","#fde066","#c0c8c7"]
CL = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Plus Jakarta Sans', color='#4a4a4a', size=11),
    margin=dict(l=8,r=8,t=36,b=8),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=11, color='#4a4a4a')),
    colorway=WS_COLORS,
)
AX  = dict(showgrid=True,  gridcolor='#EAEAEA', zeroline=False, tickfont=dict(size=10, color='#707A79'))
AXF = dict(showgrid=False, zeroline=False,       tickfont=dict(size=10, color='#707A79'))
CHINESE_RE = re.compile(r'[\u4e00-\u9fff]+')

# ── Load ───────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)  # refresh every 5 minutes
def load_data(url):
    df = pd.read_csv(url)
    df = df.map(lambda x: CHINESE_RE.sub('', str(x)).strip() if pd.notna(x) else x)
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors='coerce')
    df['_date'] = df[DATE_COL].dt.date
    df['_hour'] = df[DATE_COL].dt.hour
    df['_brand_model'] = (df[BRAND_COL].fillna('') + ' ' + df[MODEL_COL].fillna('')).str.strip()
    return df

try:
    df = load_data(SHEET_CSV_URL)
except Exception as e:
    st.error(f"❌ Could not load data from Google Sheets: {e}")
    st.stop()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="ws-logo">WRAP<span>SOL</span></div>', unsafe_allow_html=True)
    st.markdown("**Filters**"); st.write("")

    week_options = ["All time", "This week", "Last week", "2 weeks ago", "3 weeks ago", "4 weeks ago"]
    week_filter = st.selectbox("Quick Week Filter", week_options)

    min_d, max_d = df['_date'].min(), df['_date'].max()
    date_range = st.date_input(
        "Date Range" + (" (overridden)" if week_filter != "All time" else ""),
        value=(min_d, max_d), min_value=min_d, max_value=max_d,
        disabled=(week_filter != "All time"),
    )

    store_q = st.text_input("Search Store", placeholder="Type store name…")
    stores_all = sorted(df[STORE_COL].dropna().unique())
    if store_q:
        stores_all = [s for s in stores_all if store_q.lower() in str(s).lower()]
    sel_stores = st.multiselect("Stores", stores_all, default=list(stores_all))

    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"📅 {date.today().strftime('%d %B %Y')}")

# ── Resolve date window ────────────────────────────────────────────────────────
latest = df['_date'].max()

if week_filter != "All time":
    week_offsets = {"This week": 0, "Last week": 1, "2 weeks ago": 2, "3 weeks ago": 3, "4 weeks ago": 4}
    offset = week_offsets[week_filter]
    resolved_end   = latest - timedelta(weeks=offset)
    resolved_start = resolved_end - timedelta(days=6)
else:
    resolved_start = date_range[0] if len(date_range) == 2 else min_d
    resolved_end   = date_range[1] if len(date_range) == 2 else max_d

# ── Apply filters ──────────────────────────────────────────────────────────────
f = df.copy()
f = f[(f['_date'] >= resolved_start) & (f['_date'] <= resolved_end)]
if sel_stores: f = f[f[STORE_COL].isin(sel_stores)]

# ── Week-over-week helper ──────────────────────────────────────────────────────
def wk_pct(df_in, col=None):
    latest_d = df_in['_date'].max() if not df_in.empty else date.today()
    tw_s = latest_d - timedelta(days=6)
    lw_e = tw_s - timedelta(days=1)
    lw_s = lw_e - timedelta(days=6)
    tw = df_in[(df_in['_date'] >= tw_s) & (df_in['_date'] <= latest_d)]
    lw = df_in[(df_in['_date'] >= lw_s) & (df_in['_date'] <= lw_e)]
    tv = len(tw)       if col is None else tw[col].nunique()
    lv = len(lw)       if col is None else lw[col].nunique()
    pct = ((tv - lv) / lv * 100) if lv > 0 else None
    return tv, pct

def fmt_delta(pct):
    if pct is None:
        return None
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"

# ── Compute week/month transaction counts ─────────────────────────────────────
today_d    = latest
week_start = today_d - timedelta(days=6)
month_start = today_d.replace(day=1)

txn_week  = len(f[f['_date'] >= week_start])
txn_month = len(f[f['_date'] >= month_start])

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">Operations Dashboard</div>', unsafe_allow_html=True)
active_label = f"Week: {resolved_start.strftime('%d %b')} → {resolved_end.strftime('%d %b %Y')}" if week_filter != "All time" else f"{resolved_start.strftime('%d %b')} → {resolved_end.strftime('%d %b %Y')}"
st.markdown(f'<div class="page-sub"><b>{len(f):,}</b> transactions &nbsp;·&nbsp; {active_label}</div>', unsafe_allow_html=True)
st.markdown('<hr class="ws-hr">', unsafe_allow_html=True)

# ── KPI Row 1 ─────────────────────────────────────────────────────────────────
k0, k1, k2, k3, k4 = st.columns(5)

with k0:
    _, tw_pct = wk_pct(f)
    st.markdown(f"""
    <div class="txn-card">
        <div class="txn-title">Transactions</div>
        <div class="txn-total">{len(f):,}</div>
        <div class="txn-divider"></div>
        <div class="txn-row">
            <div class="txn-sub">
                <div class="txn-sub-lbl">This Week</div>
                <div class="txn-sub-val">{txn_week:,}</div>
            </div>
            <div class="txn-sub">
                <div class="txn-sub-lbl">This Month</div>
                <div class="txn-sub-val">{txn_month:,}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

metric_defs_r1 = [
    (k1, "Active Stores",  f[STORE_COL].nunique(),   STORE_COL),
    (k2, "Brands",         f[BRAND_COL].nunique(),   BRAND_COL),
    (k3, "Products",       f[PRODUCT_COL].nunique(), PRODUCT_COL),
    (k4, "Models",         f['_brand_model'].nunique(), '_brand_model'),
]
for col, lbl, total, wk_col in metric_defs_r1:
    _, pct = wk_pct(f, wk_col)
    with col:
        st.metric(label=lbl, value=f"{total:,}", delta=fmt_delta(pct))

st.markdown("<br>", unsafe_allow_html=True)

# ── KPI Row 2 ─────────────────────────────────────────────────────────────────
k5, k6, k7, k8, k9 = st.columns(5)

days_active = f['_date'].nunique()
days_total  = max((f['_date'].max() - f['_date'].min()).days + 1, 1) if not f.empty else 1
avg_day     = round(len(f) / days_total, 1)

tw_s2 = latest - timedelta(days=6)
lw_e2 = tw_s2 - timedelta(days=1)
lw_s2 = lw_e2 - timedelta(days=6)
tw_avg = round(len(f[f['_date'] >= tw_s2]) / 7, 1)
lw_cnt = len(f[(f['_date'] >= lw_s2) & (f['_date'] <= lw_e2)])
lw_avg = round(lw_cnt / 7, 1)
avg_pct = ((tw_avg - lw_avg) / lw_avg * 100) if lw_avg > 0 else None

metric_defs_r2 = [
    (k5, "PLT Codes",   f[PLT_COL].nunique(),  PLT_COL),
    (k6, "Days Active", days_active,            '_date'),
    (k7, "Avg / Day",   avg_day,                None),
    (k8, "Stores",      f[STORE_COL].nunique(), STORE_COL),
    (k9, "Categories",  f[CAT_COL].nunique(),   CAT_COL),
]
for col, lbl, total, wk_col in metric_defs_r2:
    if lbl == "Avg / Day":
        with col:
            st.metric(label=lbl, value=f"{avg_day}", delta=fmt_delta(avg_pct))
    else:
        _, pct = wk_pct(f, wk_col)
        with col:
            st.metric(label=lbl, value=f"{total:,}", delta=fmt_delta(pct))

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row 1 ───────────────────────────────────────────────────────────────
c1, c2 = st.columns([1.6, 1])

with c1:
    st.markdown('<div class="sec">📈 Transactions Over Time</div>', unsafe_allow_html=True)
    daily = f.groupby('_date').size().reset_index(name='Count')
    daily.columns = ['Date', 'Count']
    fig1 = go.Figure(go.Scatter(
        x=daily['Date'], y=daily['Count'], mode='lines+markers',
        line=dict(color='#FCD118', width=3),
        marker=dict(color='#FCD118', size=5, line=dict(color='#fff', width=1.5)),
        fill='tozeroy', fillcolor='rgba(252,209,24,0.12)',
    ))
    fig1.update_layout(**CL, height=280); fig1.update_xaxes(**AXF); fig1.update_yaxes(**AX)
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown('<div class="sec">🏪 Top Stores</div>', unsafe_allow_html=True)
    sc = f[STORE_COL].value_counts().head(10).reset_index()
    sc.columns = ['Store', 'Count']
    fig2 = go.Figure(go.Bar(
        x=sc['Count'], y=sc['Store'], orientation='h',
        marker=dict(color=sc['Count'], colorscale=[[0,'#EAEAEA'],[1,'#FCD118']], line=dict(width=0)),
    ))
    fig2.update_layout(**CL, height=280); fig2.update_xaxes(**AX); fig2.update_yaxes(**AXF, autorange='reversed')
    st.plotly_chart(fig2, use_container_width=True)

# ── Charts Row 2 ───────────────────────────────────────────────────────────────
c3, c4, c5 = st.columns(3)

with c3:
    st.markdown('<div class="sec">🧩 Top Models</div>', unsafe_allow_html=True)
    mc = f['_brand_model'].value_counts().head(8).reset_index()
    mc.columns = ['Model', 'Count']
    fig3 = go.Figure(go.Pie(
        labels=mc['Model'], values=mc['Count'], hole=0.52,
        marker=dict(colors=WS_COLORS, line=dict(color='#fff', width=2)),
        textfont=dict(size=10, color='#4a4a4a'),
    ))
    fig3.update_layout(**CL, height=270,
        annotations=[dict(text='Models', x=0.5, y=0.5, showarrow=False,
                          font=dict(size=12, color='#707A79', family='Plus Jakarta Sans'))])
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.markdown('<div class="sec">📂 Categories</div>', unsafe_allow_html=True)
    cc = f[CAT_COL].value_counts().reset_index()
    cc.columns = ['Category', 'Count']
    clrs = (WS_COLORS * (len(cc)//len(WS_COLORS)+1))[:len(cc)]
    fig4 = go.Figure(go.Bar(
        x=cc['Category'], y=cc['Count'],
        marker=dict(color=clrs, line=dict(width=0)),
        text=cc['Count'], textposition='outside', textfont=dict(size=10, color='#4a4a4a'),
    ))
    fig4.update_layout(**CL, height=270); fig4.update_xaxes(**AXF, tickangle=-30); fig4.update_yaxes(**AX)
    st.plotly_chart(fig4, use_container_width=True)

with c5:
    st.markdown('<div class="sec">🏷️ Brands</div>', unsafe_allow_html=True)
    bc = f[BRAND_COL].value_counts().head(8).reset_index()
    bc.columns = ['Brand', 'Count']
    fig5 = go.Figure(go.Pie(
        labels=bc['Brand'], values=bc['Count'], hole=0.52,
        marker=dict(colors=WS_COLORS, line=dict(color='#fff', width=2)),
        textfont=dict(size=10, color='#4a4a4a'),
    ))
    fig5.update_layout(**CL, height=270,
        annotations=[dict(text='Brands', x=0.5, y=0.5, showarrow=False,
                          font=dict(size=12, color='#707A79', family='Plus Jakarta Sans'))])
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row 3 ───────────────────────────────────────────────────────────────
c6, c7 = st.columns([1, 1.2])

with c6:
    st.markdown('<div class="sec">🕐 Transactions by Hour</div>', unsafe_allow_html=True)
    hr = f.groupby('_hour').size().reset_index(name='Count')
    hr.columns = ['Hour', 'Count']
    fig6 = go.Figure(go.Bar(
        x=hr['Hour'], y=hr['Count'],
        marker=dict(color=hr['Count'], colorscale=[[0,'#EAEAEA'],[1,'#FCD118']], line=dict(width=0)),
    ))
    fig6.update_layout(**CL, height=260)
    fig6.update_xaxes(**AXF, tickvals=list(range(0,24)), ticktext=[f"{h:02d}:00" for h in range(24)], tickangle=-45)
    fig6.update_yaxes(**AX)
    st.plotly_chart(fig6, use_container_width=True)

with c7:
    st.markdown('<div class="sec">📦 Top Products</div>', unsafe_allow_html=True)
    pc = f[PRODUCT_COL].value_counts().head(10).reset_index()
    pc.columns = ['Product', 'Count']
    fig7 = go.Figure(go.Bar(
        x=pc['Count'], y=pc['Product'], orientation='h',
        marker=dict(color='#707A79', line=dict(width=0)),
        text=pc['Count'], textposition='outside', textfont=dict(size=10, color='#4a4a4a'),
    ))
    fig7.update_layout(**CL, height=260); fig7.update_xaxes(**AX); fig7.update_yaxes(**AXF, autorange='reversed')
    st.plotly_chart(fig7, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Data Table ─────────────────────────────────────────────────────────────────
st.markdown('<div class="sec">📋 Transaction Log</div>', unsafe_allow_html=True)

all_wanted = [DATE_COL, STORE_COL, DEVICE_COL, CAT_COL, BRAND_COL, MODEL_COL, PRODUCT_COL, PLT_COL]
display_cols = [c for c in all_wanted if c in f.columns]

if f.empty:
    st.info("No transactions found for the selected filters.")
elif not display_cols:
    st.dataframe(f.reset_index(drop=True), use_container_width=True, height=380)
else:
    st.dataframe(f[display_cols].reset_index(drop=True), use_container_width=True, height=380)

st.markdown("<br>", unsafe_allow_html=True)

# ── Export ─────────────────────────────────────────────────────────────────────
export_df = f[display_cols] if display_cols else f
dl1, dl2, _ = st.columns([1,1,3])
with dl1:
    st.download_button("⬇️ Export CSV",
        data=export_df.to_csv(index=False).encode(),
        file_name=f"{date.today().strftime('%Y%m%d')}_wrapsol_log.csv",
        mime='text/csv', use_container_width=True)
with dl2:
    buf = BytesIO(); export_df.to_excel(buf, index=False)
    st.download_button("⬇️ Export Excel",
        data=buf.getvalue(),
        file_name=f"{date.today().strftime('%Y%m%d')}_wrapsol_log.xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        use_container_width=True)