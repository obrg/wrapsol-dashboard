import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
from io import BytesIO
import re
import os

os.environ["STREAMLIT_THEME_BASE"]                       = "light"
os.environ["STREAMLIT_THEME_PRIMARY_COLOR"]              = "#FCD118"
os.environ["STREAMLIT_THEME_BACKGROUND_COLOR"]           = "#F8F9F9"
os.environ["STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR"] = "#FFFFFF"
os.environ["STREAMLIT_THEME_TEXT_COLOR"]                 = "#1a1a1a"
os.environ["STREAMLIT_THEME_FONT"]                       = "sans serif"

st.set_page_config(page_title="Wrapsol Dashboard", page_icon="🔆", layout="wide")

# ── Translations ───────────────────────────────────────────────────────────────
TR = {
    "en": {
        "title": "Operations Dashboard",
        "cuts": "Cuts",
        "this_week": "This Week",
        "last_week": "Last Week",
        "this_month": "This Month",
        "last_90": "Last 90 Days",
        "all_time": "All Time",
        "avg_day": "Avg / Day",
        "days_active": "Days Active",
        "stores": "Stores",
        "brands": "Brands",
        "categories": "Categories",
        "filters": "Filters",
        "quick_week": "Quick Period",
        "date_range": "Date Range",
        "search_store": "Search Store",
        "search_placeholder": "Type store name…",
        "stores_label": "Stores",
        "refresh": "🔄 Refresh Data",
        "no_data": "No cuts found for the selected filters.",
        "log_title": "✂️ Cuts Log",
        "export_csv": "⬇️ Export CSV",
        "export_excel": "⬇️ Export Excel",
        "chart_cuts_time": "📈 Cuts Over Time",
        "chart_top_stores": "🏪 Top Stores",
        "chart_top_models": "🧩 Top Models",
        "chart_categories": "📂 Categories",
        "chart_brands": "🏷️ Top Brands",
        "chart_by_hour": "🕐 Cuts by Hour",
        "week_opts": ["All time", "This week", "Last week", "2 weeks ago", "3 weeks ago", "4 weeks ago"],
        "sub_line": "cuts",
        "language": "Language",
    },
    "tr": {
        "title": "Operasyon Paneli",
        "cuts": "Kesimler",
        "this_week": "Bu Hafta",
        "last_week": "Geçen Hafta",
        "this_month": "Bu Ay",
        "last_90": "Son 90 Gün",
        "all_time": "Tüm Zamanlar",
        "avg_day": "Günlük Ort.",
        "days_active": "Aktif Gün",
        "stores": "Mağazalar",
        "brands": "Markalar",
        "categories": "Kategoriler",
        "filters": "Filtreler",
        "quick_week": "Hızlı Dönem",
        "date_range": "Tarih Aralığı",
        "search_store": "Mağaza Ara",
        "search_placeholder": "Mağaza adı yazın…",
        "stores_label": "Mağazalar",
        "refresh": "🔄 Veriyi Yenile",
        "no_data": "Seçili filtreler için kesim bulunamadı.",
        "log_title": "✂️ Kesim Kaydı",
        "export_csv": "⬇️ CSV İndir",
        "export_excel": "⬇️ Excel İndir",
        "chart_cuts_time": "📈 Zamana Göre Kesimler",
        "chart_top_stores": "🏪 Üst Mağazalar",
        "chart_top_models": "🧩 Üst Modeller",
        "chart_categories": "📂 Kategoriler",
        "chart_brands": "🏷️ Üst Markalar",
        "chart_by_hour": "🕐 Saate Göre Kesimler",
        "week_opts": ["Tüm zamanlar", "Bu hafta", "Geçen hafta", "2 hafta önce", "3 hafta önce", "4 hafta önce"],
        "sub_line": "kesim",
        "language": "Dil",
    },
}

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

/* ── Every input surface ── */
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

/* ── Date input ── */
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
div[data-testid="stMetricLabel"] > div {
    font-size: 0.65rem !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 1.4px !important;
    color: #9ba5a4 !important;
}
div[data-testid="stMetricValue"] > div { font-size: 1.75rem !important; font-weight: 800 !important; color: #1a1a1a !important; }
div[data-testid="stMetricDelta"] > div { font-size: 0.82rem !important; font-weight: 700 !important; }
div[data-testid="stMetricDelta"][data-direction=""] > div { color: #9ba5a4 !important; }

/* ── Cuts expanded card ── */
.cuts-card {
    background: #FFFFFF;
    border: 1px solid #EAEAEA;
    border-radius: 14px;
    padding: 18px 20px 14px;
    border-left: 4px solid #FCD118;
}
.cuts-title {
    font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.4px; color: #9ba5a4 !important; margin-bottom: 4px;
}
.cuts-total {
    font-size: 1.75rem; font-weight: 800; color: #1a1a1a !important;
    line-height: 1; margin-bottom: 14px;
}
.cuts-divider { height: 1px; background: #EAEAEA; margin-bottom: 12px; }
.cuts-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px 6px;
}
.cuts-sub {}
.cuts-sub-lbl {
    font-size: 0.55rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; color: #b0b8b7 !important; margin-bottom: 2px;
}
.cuts-sub-val { font-size: 1.05rem; font-weight: 800; color: #1a1a1a !important; }
.cuts-delta-pos { font-size: 0.7rem; font-weight: 700; color: #22c55e !important; }
.cuts-delta-neg { font-size: 0.7rem; font-weight: 700; color: #ef4444 !important; }
.cuts-delta-neu { font-size: 0.7rem; font-weight: 700; color: #9ba5a4 !important; }

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
STORE_COL   = "store name"
DEVICE_COL  = "Device No"
CAT_COL     = "Category"
BRAND_COL   = "Brand"
MODEL_COL   = "Model"

WS_COLORS = ["#FCD118","#c8ab00","#707A79","#9ba5a4","#e6c200","#4a5352","#fde066","#c0c8c7","#b89e00","#5a6463"]

CL = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Plus Jakarta Sans', color='#4a4a4a', size=11),
    margin=dict(l=8,r=8,t=36,b=8),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=11, color='#4a4a4a')),
    colorway=WS_COLORS,
)
AX   = dict(showgrid=True,  gridcolor='#EAEAEA', zeroline=False, tickfont=dict(size=10, color='#707A79'))
AXF  = dict(showgrid=False, zeroline=False,       tickfont=dict(size=10, color='#707A79'))
AXF9 = dict(showgrid=False, zeroline=False,       tickfont=dict(size=9,  color='#707A79'))
CHINESE_RE = re.compile(r'[\u4e00-\u9fff]+')

# ── Load ───────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
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

# ── Language selector (sidebar top) ───────────────────────────────────────────
with st.sidebar:
    lang = st.selectbox("🌐 Language / Dil", ["English", "Türkçe"], label_visibility="collapsed")
    L = TR["tr"] if lang == "Türkçe" else TR["en"]

    st.markdown('<div class="ws-logo">WRAP<span>SOL</span></div>', unsafe_allow_html=True)
    st.markdown(f"**{L['filters']}**"); st.write("")

    week_opts = L["week_opts"]
    week_filter = st.selectbox(L["quick_week"], week_opts)

    min_d, max_d = df['_date'].min(), df['_date'].max()
    override = week_filter != week_opts[0]
    date_range = st.date_input(
        L["date_range"] + (" (overridden)" if override else ""),
        value=(min_d, max_d), min_value=min_d, max_value=max_d,
        disabled=override,
    )

    store_q = st.text_input(L["search_store"], placeholder=L["search_placeholder"])
    stores_all = sorted(df[STORE_COL].dropna().unique())
    if store_q:
        stores_all = [s for s in stores_all if store_q.lower() in str(s).lower()]
    sel_stores = st.multiselect(L["stores_label"], stores_all, default=list(stores_all))

    st.markdown("---")
    if st.button(L["refresh"], use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"📅 {date.today().strftime('%d %B %Y')}")

# ── Resolve date window ────────────────────────────────────────────────────────
latest = df['_date'].max()

if override:
    week_offsets = {w: i for i, w in enumerate(week_opts)}
    offset = week_offsets.get(week_filter, 0)
    resolved_end   = latest - timedelta(weeks=offset)
    resolved_start = resolved_end - timedelta(days=6)
else:
    resolved_start = date_range[0] if len(date_range) == 2 else min_d
    resolved_end   = date_range[1] if len(date_range) == 2 else max_d

# ── Apply filters ──────────────────────────────────────────────────────────────
f = df.copy()
f = f[(f['_date'] >= resolved_start) & (f['_date'] <= resolved_end)]
if sel_stores:
    f = f[f[STORE_COL].isin(sel_stores)]

# ── Helpers ────────────────────────────────────────────────────────────────────
def cuts_in(df_in, start, end=None):
    if end is None:
        return len(df_in[df_in['_date'] >= start])
    return len(df_in[(df_in['_date'] >= start) & (df_in['_date'] <= end)])

def delta_html(cur, prev):
    if prev == 0 or prev is None:
        return f'<span class="cuts-delta-neu">—</span>'
    pct = (cur - prev) / prev * 100
    sign = "+" if pct >= 0 else ""
    cls = "cuts-delta-pos" if pct >= 0 else "cuts-delta-neg"
    arrow = "▲" if pct >= 0 else "▼"
    return f'<span class="{cls}">{arrow} {sign}{pct:.1f}%</span>'

def wk_pct(df_in, col=None):
    latest_d = df_in['_date'].max() if not df_in.empty else date.today()
    tw_s = latest_d - timedelta(days=6)
    lw_e = tw_s - timedelta(days=1)
    lw_s = lw_e - timedelta(days=6)
    tw = df_in[(df_in['_date'] >= tw_s) & (df_in['_date'] <= latest_d)]
    lw = df_in[(df_in['_date'] >= lw_s) & (df_in['_date'] <= lw_e)]
    tv = len(tw)  if col is None else tw[col].nunique()
    lv = len(lw)  if col is None else lw[col].nunique()
    pct = ((tv - lv) / lv * 100) if lv > 0 else None
    return tv, pct

def fmt_delta(pct):
    if pct is None: return None
    return f"{'+'if pct>=0 else ''}{pct:.1f}%"

# ── Cuts breakdown ─────────────────────────────────────────────────────────────
today_d      = latest
tw_start     = today_d - timedelta(days=6)
lw_end       = tw_start - timedelta(days=1)
lw_start     = lw_end - timedelta(days=6)
month_start  = today_d.replace(day=1)
prev_month_end   = month_start - timedelta(days=1)
prev_month_start = prev_month_end.replace(day=1)
d90_start    = today_d - timedelta(days=89)
prev90_start = d90_start - timedelta(days=90)
prev90_end   = d90_start - timedelta(days=1)

cuts_total      = len(f)
cuts_this_week  = cuts_in(f, tw_start)
cuts_last_week  = cuts_in(f, lw_start, lw_end)
cuts_this_month = cuts_in(f, month_start)
cuts_prev_month = cuts_in(f, prev_month_start, prev_month_end)
cuts_90         = cuts_in(f, d90_start)
cuts_prev_90    = cuts_in(f, prev90_start, prev90_end)
days_total      = max((f['_date'].max() - f['_date'].min()).days + 1, 1) if not f.empty else 1
avg_day         = round(len(f) / days_total, 1)
days_active     = f['_date'].nunique()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="page-title">{L["title"]}</div>', unsafe_allow_html=True)
active_label = f"{resolved_start.strftime('%d %b')} → {resolved_end.strftime('%d %b %Y')}"
st.markdown(f'<div class="page-sub"><b>{len(f):,}</b> {L["sub_line"]} &nbsp;·&nbsp; {active_label}</div>', unsafe_allow_html=True)
st.markdown('<hr class="ws-hr">', unsafe_allow_html=True)

# ── KPI Row 1: Cuts expanded card + secondary metrics ─────────────────────────
k0, k1, k2, k3 = st.columns([1.6, 1, 1, 1])

with k0:
    st.markdown(f"""
    <div class="cuts-card">
        <div class="cuts-title">{L['cuts']}</div>
        <div class="cuts-total">{cuts_total:,}</div>
        <div class="cuts-divider"></div>
        <div class="cuts-grid">
            <div class="cuts-sub">
                <div class="cuts-sub-lbl">{L['this_week']}</div>
                <div class="cuts-sub-val">{cuts_this_week:,}</div>
                {delta_html(cuts_this_week, cuts_last_week)}
            </div>
            <div class="cuts-sub">
                <div class="cuts-sub-lbl">{L['last_week']}</div>
                <div class="cuts-sub-val">{cuts_last_week:,}</div>
            </div>
            <div class="cuts-sub">
                <div class="cuts-sub-lbl">{L['this_month']}</div>
                <div class="cuts-sub-val">{cuts_this_month:,}</div>
                {delta_html(cuts_this_month, cuts_prev_month)}
            </div>
            <div class="cuts-sub">
                <div class="cuts-sub-lbl">{L['last_90']}</div>
                <div class="cuts-sub-val">{cuts_90:,}</div>
                {delta_html(cuts_90, cuts_prev_90)}
            </div>
            <div class="cuts-sub">
                <div class="cuts-sub-lbl">{L['all_time']}</div>
                <div class="cuts-sub-val">{len(df):,}</div>
            </div>
            <div class="cuts-sub">
                <div class="cuts-sub-lbl">{L['avg_day']}</div>
                <div class="cuts-sub-val">{avg_day}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

_, tw_pct_stores = wk_pct(f, STORE_COL)
_, tw_pct_brands = wk_pct(f, BRAND_COL)
_, tw_pct_cats   = wk_pct(f, CAT_COL)

with k1:
    st.metric(label=L["stores"],     value=f"{f[STORE_COL].nunique():,}", delta=fmt_delta(tw_pct_stores))
with k2:
    st.metric(label=L["brands"],     value=f"{f[BRAND_COL].nunique():,}", delta=fmt_delta(tw_pct_brands))
with k3:
    st.metric(label=L["categories"], value=f"{f[CAT_COL].nunique():,}",  delta=fmt_delta(tw_pct_cats))

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row 1 ───────────────────────────────────────────────────────────────
c1, c2 = st.columns([1.6, 1])

with c1:
    st.markdown(f'<div class="sec">{L["chart_cuts_time"]}</div>', unsafe_allow_html=True)
    daily = f.groupby('_date').size().reset_index(name='Count')
    daily.columns = ['Date', 'Count']
    fig1 = go.Figure(go.Scatter(
        x=daily['Date'], y=daily['Count'], mode='lines+markers',
        line=dict(color='#FCD118', width=3),
        marker=dict(color='#FCD118', size=5, line=dict(color='#fff', width=1.5)),
        fill='tozeroy', fillcolor='rgba(252,209,24,0.12)',
    ))
    fig1.update_layout(**CL, height=280)
    fig1.update_xaxes(**AXF)
    fig1.update_yaxes(**AX)
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown(f'<div class="sec">{L["chart_top_stores"]}</div>', unsafe_allow_html=True)
    sc = f[STORE_COL].value_counts().head(10).reset_index()
    sc.columns = ['Store', 'Count']
    # gradient from gray to yellow
    n = len(sc)
    bar_colors = [f"rgba(252,209,24,{0.35 + 0.65*(i/(max(n-1,1)))})" for i in range(n)][::-1]
    fig2 = go.Figure(go.Bar(
        x=sc['Count'], y=sc['Store'], orientation='h',
        marker=dict(color=bar_colors, line=dict(width=0)),
        text=sc['Count'], textposition='outside',
        textfont=dict(size=10, color='#4a4a4a'),
    ))
    fig2.update_layout(**CL, height=280)
    fig2.update_xaxes(**AX)
    fig2.update_yaxes(**AXF, autorange='reversed')
    st.plotly_chart(fig2, use_container_width=True)

# ── Charts Row 2 ───────────────────────────────────────────────────────────────
c3, c4, c5 = st.columns(3)

with c3:
    st.markdown(f'<div class="sec">{L["chart_top_models"]}</div>', unsafe_allow_html=True)
    mc = f['_brand_model'].value_counts().head(10).reset_index()
    mc.columns = ['Model', 'Count']
    # sort ascending so largest bar is at top
    mc = mc.sort_values('Count', ascending=True)
    n = len(mc)
    bar_colors_m = [f"rgba(252,209,24,{0.3 + 0.7*(i/(max(n-1,1)))})" for i in range(n)]
    fig3 = go.Figure(go.Bar(
        x=mc['Count'], y=mc['Model'], orientation='h',
        marker=dict(color=bar_colors_m, line=dict(width=0)),
        text=mc['Count'], textposition='outside',
        textfont=dict(size=9, color='#4a4a4a'),
    ))
    fig3.update_layout(**CL, height=290)
    fig3.update_xaxes(**AX)
    fig3.update_yaxes(**AXF9)
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.markdown(f'<div class="sec">{L["chart_categories"]}</div>', unsafe_allow_html=True)
    cc = f[CAT_COL].value_counts().reset_index()
    cc.columns = ['Category', 'Count']
    clrs = (WS_COLORS * (len(cc)//len(WS_COLORS)+1))[:len(cc)]
    fig4 = go.Figure(go.Bar(
        x=cc['Category'], y=cc['Count'],
        marker=dict(color=clrs, line=dict(width=0)),
        text=cc['Count'], textposition='outside',
        textfont=dict(size=10, color='#4a4a4a'),
    ))
    fig4.update_layout(**CL, height=290)
    fig4.update_xaxes(**AXF, tickangle=-30)
    fig4.update_yaxes(**AX)
    st.plotly_chart(fig4, use_container_width=True)

with c5:
    st.markdown(f'<div class="sec">{L["chart_brands"]}</div>', unsafe_allow_html=True)
    bc = f[BRAND_COL].value_counts().head(10).reset_index()
    bc.columns = ['Brand', 'Count']
    bc = bc.sort_values('Count', ascending=True)
    n = len(bc)
    bar_colors_b = [f"rgba(112,122,121,{0.3 + 0.7*(i/(max(n-1,1)))})" for i in range(n)]
    fig5 = go.Figure(go.Bar(
        x=bc['Count'], y=bc['Brand'], orientation='h',
        marker=dict(color=bar_colors_b, line=dict(width=0)),
        text=bc['Count'], textposition='outside',
        textfont=dict(size=9, color='#4a4a4a'),
    ))
    fig5.update_layout(**CL, height=290)
    fig5.update_xaxes(**AX)
    fig5.update_yaxes(**AXF9)
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Chart Row 3: Cuts by Hour ──────────────────────────────────────────────────
st.markdown(f'<div class="sec">{L["chart_by_hour"]}</div>', unsafe_allow_html=True)
hr = f.groupby('_hour').size().reset_index(name='Count')
hr.columns = ['Hour', 'Count']
# fill missing hours with 0
all_hours = pd.DataFrame({'Hour': range(24)})
hr = all_hours.merge(hr, on='Hour', how='left').fillna(0)
hr['Count'] = hr['Count'].astype(int)
max_count = hr['Count'].max() if hr['Count'].max() > 0 else 1
bar_colors_h = [f"rgba(252,209,24,{0.2 + 0.8*(v/max_count)})" for v in hr['Count']]
fig6 = go.Figure(go.Bar(
    x=hr['Hour'], y=hr['Count'],
    marker=dict(color=bar_colors_h, line=dict(width=0)),
    text=hr['Count'].where(hr['Count']>0, other=''),
    textposition='outside', textfont=dict(size=9, color='#4a4a4a'),
))
fig6.update_layout(**CL, height=240)
fig6.update_xaxes(**AXF, tickvals=list(range(24)), ticktext=[f"{h:02d}:00" for h in range(24)], tickangle=-45)
fig6.update_yaxes(**AX)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Data Table ─────────────────────────────────────────────────────────────────
st.markdown(f'<div class="sec">{L["log_title"]}</div>', unsafe_allow_html=True)

display_cols = [c for c in [DATE_COL, STORE_COL, DEVICE_COL, CAT_COL, BRAND_COL, MODEL_COL] if c in f.columns]

if f.empty:
    st.info(L["no_data"])
else:
    st.dataframe(f[display_cols].reset_index(drop=True), use_container_width=True, height=380)

st.markdown("<br>", unsafe_allow_html=True)

# ── Export ─────────────────────────────────────────────────────────────────────
export_df = f[display_cols] if display_cols else f
dl1, dl2, _ = st.columns([1,1,3])
with dl1:
    st.download_button(L["export_csv"],
        data=export_df.to_csv(index=False).encode(),
        file_name=f"{date.today().strftime('%Y%m%d')}_wrapsol_cuts.csv",
        mime='text/csv', use_container_width=True)
with dl2:
    buf = BytesIO()
    export_df.to_excel(buf, index=False)
    st.download_button(L["export_excel"],
        data=buf.getvalue(),
        file_name=f"{date.today().strftime('%Y%m%d')}_wrapsol_cuts.xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        use_container_width=True)
