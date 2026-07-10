"""Wrapsol Operations Dashboard.

Reads the combined cuts dataset published as CSV from Google Sheets and renders
a dark, bilingual (EN/TR) operations dashboard.

Every periodic KPI is anchored to the END of the selected window (`anchor`),
never to today or the dataset's global max — so looking at a historical period
shows that period's momentum, not zeros. All deltas compare EQUAL-LENGTH spans
(last 7 days vs the 7 before; month-to-date vs the same day-span of the prior
month), because a partial-vs-full comparison always reads as a fake drop.
"""

import re
from datetime import date, timedelta
from io import BytesIO

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Wrapsol Dashboard", page_icon="✂️", layout="wide")

# ── Column constants ───────────────────────────────────────────────────────────
SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQMxwkcaP3FDKRk1iWxqhnvreBpJ-PbimDPGdE8KiXGj0ixRTveQFoyOn5vKyZq1sQU-_oxUzZhnD7h/pub?gid=541577724&single=true&output=csv"
)

DATE_COL   = "Transaction Date"
STORE_COL  = "store name"
DEVICE_COL = "Device No"
CAT_COL    = "Category"
BRAND_COL  = "Brand"
MODEL_COL  = "Model"

# ── Palette (light mode) ───────────────────────────────────────────────────────
# Categorical slots from the validated reference palette; the 5-slot pie order
# passes all-pairs CVD (worst ΔE 16.6) on white. Aqua and yellow sit below 3:1
# contrast on white, so every chart using them carries visible labels (the
# relief rule). Brand gold (#FCD118) stays UI chrome only.
BLUE    = "#2a78d6"
AQUA    = "#1baf7a"
YELLOW  = "#eda100"
VIOLET  = "#4a3aa7"
ORANGE  = "#eb6834"
OTHER_GRAY = "#898781"  # neutral "Other" slice — not an identity color
PIE_COLORS = [BLUE, AQUA, YELLOW, VIOLET, ORANGE, OTHER_GRAY]

INK     = "#16150f"
MUTED   = "#6b6a63"
MUTED_2 = "#98968e"
GRID    = "#e8e7e1"
SURFACE = "#ffffff"
GREEN   = "#006300"
RED     = "#d03b3b"

CHINESE_RE = re.compile(r"[一-鿿]+")

# ── Translations ───────────────────────────────────────────────────────────────
TR = {
    "en": {
        "title": "Operations Dashboard",
        "sub_cuts": "cuts",
        "data_through": "Data through",
        "filters": "Filters",
        "quick_period": "Quick Period",
        "date_range": "Date Range",
        "overridden": "(overridden)",
        "stores_label": "Stores",
        "stores_ph": "All stores — pick to narrow",
        "stores_help": "Leave empty to include every store.",
        "stores_search_label": "Search stores",
        "stores_search_ph": "Type to filter the list below (Turkish letters supported)",
        "refresh": "🔄 Refresh Data",
        "week_opts": ["All time", "Latest 7 days", "1 week back", "2 weeks back", "3 weeks back", "4 weeks back"],
        "cuts": "Cuts (selected period)",
        "last7": "Last 7 Days",
        "prev7": "Prev 7 Days",
        "mtd": "Month to Date",
        "all_time": "All Time",
        "avg_active": "Avg / Active Day",
        "days_active": "Days Active",
        "stores": "Active Stores",
        "devices": "Active Devices",
        "brands": "Brands",
        "models": "Models",
        "peak_day": "Peak Day",
        "peak_hour": "Peak Hour",
        "vs_prev7": "vs prev 7 days",
        "vs_prev_month": "vs same span last month",
        "chart_daily": "Cuts Over Time · with 7-day average",
        "chart_stores": "Top Stores",
        "chart_hour": "Cuts by Hour",
        "chart_dow": "Cuts by Weekday",
        "chart_models": "Top Models",
        "chart_brands": "Brand Share",
        "chart_cats": "Categories",
        "other": "Other",
        "leaderboard": "Store Leaderboard",
        "lb_store": "Store",
        "lb_cuts": "Cuts",
        "lb_share": "Share",
        "lb_last7": "Last 7d",
        "lb_prev7": "Prev 7d",
        "lb_delta": "Δ 7d",
        "log_title": "Cuts Log",
        "export_csv": "⬇️ Export CSV",
        "export_excel": "⬇️ Export Excel",
        "no_data": "No cuts found for the selected filters.",
        "no_data_at_all": "No data loaded — check the Google Sheet connection.",
        "bad_dates": "row(s) had unreadable dates and were excluded.",
        "dupes": "duplicate row(s) removed.",
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
    "tr": {
        "title": "Operasyon Paneli",
        "sub_cuts": "kesim",
        "data_through": "Veri tarihi",
        "filters": "Filtreler",
        "quick_period": "Hızlı Dönem",
        "date_range": "Tarih Aralığı",
        "overridden": "(devre dışı)",
        "stores_label": "Mağazalar",
        "stores_ph": "Tüm mağazalar — daraltmak için seçin",
        "stores_help": "Tüm mağazalar için boş bırakın.",
        "stores_search_label": "Mağaza ara",
        "stores_search_ph": "Aşağıdaki listeyi daraltmak için yazın",
        "refresh": "🔄 Veriyi Yenile",
        "week_opts": ["Tüm zamanlar", "Son 7 gün", "1 hafta önce", "2 hafta önce", "3 hafta önce", "4 hafta önce"],
        "cuts": "Kesimler (seçili dönem)",
        "last7": "Son 7 Gün",
        "prev7": "Önceki 7 Gün",
        "mtd": "Ay Başından Beri",
        "all_time": "Tüm Zamanlar",
        "avg_active": "Aktif Gün Ort.",
        "days_active": "Aktif Gün",
        "stores": "Aktif Mağazalar",
        "devices": "Aktif Cihazlar",
        "brands": "Markalar",
        "models": "Modeller",
        "peak_day": "En Yoğun Gün",
        "peak_hour": "En Yoğun Saat",
        "vs_prev7": "önceki 7 güne göre",
        "vs_prev_month": "geçen ayın aynı dönemine göre",
        "chart_daily": "Zamana Göre Kesimler · 7 günlük ortalama",
        "chart_stores": "En İyi Mağazalar",
        "chart_hour": "Saate Göre Kesimler",
        "chart_dow": "Günlere Göre Kesimler",
        "chart_models": "En Çok Kesilen Modeller",
        "chart_brands": "Marka Payı",
        "chart_cats": "Kategoriler",
        "other": "Diğer",
        "leaderboard": "Mağaza Sıralaması",
        "lb_store": "Mağaza",
        "lb_cuts": "Kesim",
        "lb_share": "Pay",
        "lb_last7": "Son 7g",
        "lb_prev7": "Önceki 7g",
        "lb_delta": "Δ 7g",
        "log_title": "Kesim Kaydı",
        "export_csv": "⬇️ CSV İndir",
        "export_excel": "⬇️ Excel İndir",
        "no_data": "Seçili filtreler için kesim bulunamadı.",
        "no_data_at_all": "Veri yüklenemedi — Google Sheet bağlantısını kontrol edin.",
        "bad_dates": "satırın tarihi okunamadı ve hariç tutuldu.",
        "dupes": "yinelenen satır kaldırıldı.",
        "weekdays": ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"],
    },
}

MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "tr": ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"],
}


def fmt_d(d, lang, with_year=False):
    """02 Tem / 02 Jul (2026) — localized short date."""
    s = f"{d.day:02d} {MONTHS[lang][d.month - 1]}"
    return f"{s} {d.year}" if with_year else s


# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

html, body, [class*="css"], .stApp, [data-testid="stSidebar"] * , .stMarkdown, button, input, select {
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}
/* the blanket font rule above must not override Streamlit's icon font,
   or icons render as their ligature names ("keyboard_double_arrow_left") */
[data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded' !important;
}
.stApp { background: radial-gradient(1100px 500px at 12% -8%, rgba(252,209,24,0.07), transparent 60%), #f7f7f4 !important; }

[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e8e7e1; }
[data-testid="stSidebar"] label {
    font-size: 0.68rem !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 1.1px !important;
    color: #6b6a63 !important;
}
[data-testid="stHeader"] { background: transparent !important; }

.ws-logo { font-weight: 800; font-size: 1.3rem; color: #16150f; padding: 2px 0 12px; border-bottom: 2px solid #FCD118; margin-bottom: 18px; display: inline-block; }
.ws-logo span { color: #c98500; }

.page-title { font-weight: 800; font-size: 1.8rem; color: #16150f; letter-spacing: -0.5px; }
.page-sub { font-size: 0.85rem; color: #6b6a63; margin-bottom: 1.1rem; }
.page-sub b { color: #16150f; }

.sec { font-size: 0.66rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.6px; color: #6b6a63; margin: 4px 0 10px; padding-bottom: 7px; border-bottom: 1px solid #e8e7e1; }

/* stat tiles */
.tile {
    background: #ffffff; border: 1px solid #e8e7e1; border-top: 2px solid #d6d5cd;
    border-radius: 13px; padding: 15px 17px 13px; height: 100%;
    box-shadow: 0 1px 2px rgba(20,20,15,0.04);
}
.tile.gold { border-top-color: #FCD118; }
.tile-lbl { font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #98968e; margin-bottom: 5px; }
.tile-val { font-size: 1.6rem; font-weight: 700; color: #16150f; line-height: 1.05; font-family: 'JetBrains Mono', monospace; }
.tile-val small { font-size: 0.85rem; color: #98968e; font-weight: 600; }
.tile-delta { font-size: 0.72rem; font-weight: 700; margin-top: 5px; font-family: 'JetBrains Mono', monospace; }
.tile-delta .ctx { color: #98968e; font-weight: 500; font-family: 'Plus Jakarta Sans', sans-serif; }
.d-pos { color: #006300; } .d-neg { color: #d03b3b; } .d-neu { color: #98968e; }

.cuts-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 9px 10px; margin-top: 12px; padding-top: 12px; border-top: 1px solid #e8e7e1; }
.cuts-sub-lbl { font-size: 0.56rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #98968e; margin-bottom: 2px; }
.cuts-sub-val { font-size: 1.02rem; font-weight: 700; color: #16150f; font-family: 'JetBrains Mono', monospace; }
.cuts-sub-val .tile-delta { display: inline; margin-left: 5px; font-size: 0.68rem; }

/* store multiselect: compact chips, small dropdown text */
[data-testid="stSidebar"] span[data-baseweb="tag"] {
    height: auto !important; padding: 1px 7px !important; border-radius: 6px !important;
    background-color: #fff6d6 !important; border: 1px solid #efe3ae !important;
}
[data-testid="stSidebar"] span[data-baseweb="tag"] * {
    font-size: 0.62rem !important; line-height: 1.5 !important; color: #16150f !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"] input { font-size: 0.72rem !important; }
li[role="option"], li[role="option"] * { font-size: 0.72rem !important; }

[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid #e8e7e1; }

[data-testid="stDownloadButton"] button {
    background-color: #ffffff !important; color: #16150f !important;
    border: 1px solid #e8e7e1 !important; border-radius: 9px !important; font-weight: 600 !important;
}
[data-testid="stDownloadButton"] button:hover { border-color: #FCD118 !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f7f7f4; }
::-webkit-scrollbar-thumb { background: #d6d5cd; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Load ───────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df = df.map(lambda x: CHINESE_RE.sub("", str(x)).strip() if pd.notna(x) else x)

    n_raw = len(df)
    # The sheet grows by appended exports that can overlap; exact repeats are
    # not new cuts. Rows can share a Transaction No while differing in other
    # columns, so dedup on the full row rather than the id alone.
    df = df.drop_duplicates()
    n_dupes = n_raw - len(df)

    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    n_bad_dates = int(df[DATE_COL].isna().sum())
    df = df.dropna(subset=[DATE_COL]).reset_index(drop=True)

    # The two plotter vendors export different casing ("Samsung" vs "SAMSUNG",
    # "Galaxy A17 5G" vs "GALAXY A17 5G"), which splits one brand/model into
    # two. Merge case-insensitively, displaying each group's most common
    # spelling (keeps "OPPO"/"realme" as branded).
    for col in (BRAND_COL, MODEL_COL, CAT_COL):
        if col in df.columns:
            canon = df.groupby(df[col].str.casefold())[col].agg(lambda s: s.mode().iat[0])
            df[col] = df[col].str.casefold().map(canon)

    df["_date"] = df[DATE_COL].dt.date
    df["_hour"] = df[DATE_COL].dt.hour
    df["_dow"] = df[DATE_COL].dt.dayofweek
    df["_brand_model"] = (df[BRAND_COL].fillna("") + " " + df[MODEL_COL].fillna("")).str.strip()
    return df, n_dupes, n_bad_dates


if "refresh_token" not in st.session_state:
    st.session_state["refresh_token"] = 0

# Google's publish-to-web CSV export is itself cached on Google's side for a
# few minutes, independent of our own @st.cache_data ttl. Clearing our cache
# alone can still hand back the same stale CSV, so the "Refresh" button also
# appends a changing query param — Google's cache is keyed on the full URL,
# so a new param forces a fresh export instead of a cached one.
fetch_url = f"{SHEET_CSV_URL}&_cb={st.session_state['refresh_token']}"

try:
    df, n_dupes, n_bad_dates = load_data(fetch_url)
except Exception as e:
    st.error(f"❌ Could not load data from Google Sheets: {e}")
    st.stop()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    lang_choice = st.selectbox("🌐 Language / Dil", ["English", "Türkçe"], label_visibility="collapsed")
    lang = "tr" if lang_choice == "Türkçe" else "en"
    L = TR[lang]

    st.markdown('<div class="ws-logo">WRAP<span>SOL</span></div>', unsafe_allow_html=True)

    if df.empty:
        st.error(L["no_data_at_all"])
        st.stop()

    week_opts = L["week_opts"]
    week_filter = st.selectbox(L["quick_period"], week_opts)
    override = week_filter != week_opts[0]

    min_d, max_d = df["_date"].min(), df["_date"].max()
    date_range = st.date_input(
        L["date_range"] + (" " + L["overridden"] if override else ""),
        value=(min_d, max_d), min_value=min_d, max_value=max_d,
        disabled=override,
    )

    # Empty selection = all stores. The multiselect's own built-in typeahead
    # lowercases with plain JS/Python casing rules, which mishandle Turkish
    # dotted/dotless I (İ.lower() != "i", so typing "iletişim" matches none
    # of the "İletişim" stores). Filter the option list ourselves with a
    # Turkish-aware fold instead of relying on the widget's search box.
    stores_all = sorted(df[STORE_COL].dropna().unique())

    def _tr_fold(s: str) -> str:
        return s.replace("İ", "i").replace("I", "ı").lower()

    store_query = st.text_input(
        L["stores_search_label"], value="", placeholder=L["stores_search_ph"],
    )
    if store_query.strip():
        q = _tr_fold(store_query.strip())
        matches = [s for s in stores_all if q in _tr_fold(s)]
    else:
        matches = stores_all

    # Keep already-selected stores in the option list even when the current
    # query filters them out, so typing a new search term can't silently
    # drop a prior selection (and Streamlit doesn't reject it as an option
    # no longer present in the widget's `options`).
    prior_sel = st.session_state.get("sel_stores", [])
    store_options = sorted(set(matches) | set(prior_sel))

    sel_stores = st.multiselect(
        L["stores_label"], store_options, default=[],
        placeholder=L["stores_ph"], help=L["stores_help"], key="sel_stores",
    )

    st.markdown("---")
    if st.button(L["refresh"], width='stretch'):
        st.cache_data.clear()
        st.session_state["refresh_token"] += 1
        st.rerun()

    last_ts = df[DATE_COL].max()
    st.caption(f"📅 {L['data_through']}: {fmt_d(last_ts.date(), lang, with_year=True)} {last_ts.strftime('%H:%M')}")
    if n_dupes:
        st.caption(f"🧹 {n_dupes:,} {L['dupes']}")
    if n_bad_dates:
        st.caption(f"⚠️ {n_bad_dates:,} {L['bad_dates']}")

# ── Resolve window ─────────────────────────────────────────────────────────────
latest = df["_date"].max()

if override:
    # week_opts[1] = latest 7 days → offset 0 (the old dict built from
    # enumerate() included "All time" at index 0 and shifted every quick
    # period one week into the past).
    offset = week_opts.index(week_filter) - 1
    resolved_end = latest - timedelta(weeks=offset)
    resolved_start = resolved_end - timedelta(days=6)
else:
    resolved_start = date_range[0] if len(date_range) == 2 else min_d
    resolved_end = date_range[1] if len(date_range) == 2 else max_d

# base: store filter only (KPI momentum, leaderboard trends, all-time)
# sel:  store filter + date window (everything the page displays as "selected")
# An empty multiselect means "all stores" (the widget's placeholder says so).
base = df[df[STORE_COL].isin(sel_stores)] if sel_stores else df
sel = base[(base["_date"] >= resolved_start) & (base["_date"] <= resolved_end)]

# ── Period math (all anchored to resolved_end, equal-length comparisons) ──────
anchor = resolved_end


def count_between(data, start, end):
    return int(((data["_date"] >= start) & (data["_date"] <= end)).sum())


def nunique_between(data, col, start, end):
    m = (data["_date"] >= start) & (data["_date"] <= end)
    return data.loc[m, col].nunique()


l7_s, l7_e = anchor - timedelta(days=6), anchor
p7_s, p7_e = anchor - timedelta(days=13), anchor - timedelta(days=7)

mtd_s = anchor.replace(day=1)
prev_month_end = mtd_s - timedelta(days=1)
pm_s = prev_month_end.replace(day=1)
# same day-span of the previous month, clamped to its length
pm_e = min(pm_s + timedelta(days=(anchor - mtd_s).days), prev_month_end)

cuts_l7 = count_between(base, l7_s, l7_e)
cuts_p7 = count_between(base, p7_s, p7_e)
cuts_mtd = count_between(base, mtd_s, anchor)
cuts_pm_span = count_between(base, pm_s, pm_e)

days_active = sel["_date"].nunique()
avg_active = round(len(sel) / days_active, 1) if days_active else 0.0

daily_all = sel.groupby("_date").size() if not sel.empty else pd.Series(dtype=int)
peak_day = daily_all.idxmax() if not daily_all.empty else None
peak_day_n = int(daily_all.max()) if not daily_all.empty else 0
hourly_all = sel.groupby("_hour").size() if not sel.empty else pd.Series(dtype=int)
peak_hour = int(hourly_all.idxmax()) if not hourly_all.empty else None
peak_hour_n = int(hourly_all.max()) if not hourly_all.empty else 0


def pct(cur, prev):
    if prev == 0:
        return None
    return (cur - prev) / prev * 100


def delta_html(p, ctx=""):
    if p is None:
        return f'<div class="tile-delta d-neu">— <span class="ctx">{ctx}</span></div>'
    cls = "d-pos" if p >= 0 else "d-neg"
    arrow = "▲" if p >= 0 else "▼"
    return f'<div class="tile-delta {cls}">{arrow} {p:+.1f}% <span class="ctx">{ctx}</span></div>'


def tile(label, value, delta="", gold=False):
    return (
        f'<div class="tile{" gold" if gold else ""}">'
        f'<div class="tile-lbl">{label}</div>'
        f'<div class="tile-val">{value}</div>{delta}</div>'
    )


# nunique deltas: last 7 vs prev 7 (activity breadth, not totals)
stores_now = sel[STORE_COL].nunique()
stores_pct = pct(nunique_between(base, STORE_COL, l7_s, l7_e), nunique_between(base, STORE_COL, p7_s, p7_e))
devices_now = sel[DEVICE_COL].nunique()
devices_pct = pct(nunique_between(base, DEVICE_COL, l7_s, l7_e), nunique_between(base, DEVICE_COL, p7_s, p7_e))
brands_now = sel[BRAND_COL].nunique()
models_now = sel["_brand_model"].nunique()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="page-title">{L["title"]}</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="page-sub"><b>{len(sel):,}</b> {L["sub_cuts"]} &nbsp;·&nbsp; '
    f'{fmt_d(resolved_start, lang)} → {fmt_d(resolved_end, lang, with_year=True)}</div>',
    unsafe_allow_html=True,
)

# ── KPI row 1: cuts card + breadth tiles ──────────────────────────────────────
k0, k1, k2, k3, k4 = st.columns([1.7, 1, 1, 1, 1])

with k0:
    st.markdown(
        f"""<div class="tile gold">
        <div class="tile-lbl">{L['cuts']}</div>
        <div class="tile-val">{len(sel):,}</div>
        <div class="cuts-grid">
            <div><div class="cuts-sub-lbl">{L['last7']}</div>
                <div class="cuts-sub-val">{cuts_l7:,}</div>
                {delta_html(pct(cuts_l7, cuts_p7), L['vs_prev7'])}</div>
            <div><div class="cuts-sub-lbl">{L['prev7']}</div>
                <div class="cuts-sub-val">{cuts_p7:,}</div></div>
            <div><div class="cuts-sub-lbl">{L['mtd']}</div>
                <div class="cuts-sub-val">{cuts_mtd:,}</div>
                {delta_html(pct(cuts_mtd, cuts_pm_span), L['vs_prev_month'])}</div>
            <div><div class="cuts-sub-lbl">{L['all_time']}</div>
                <div class="cuts-sub-val">{len(base):,}</div></div>
        </div></div>""",
        unsafe_allow_html=True,
    )

# two stacked tiles per column, so the columns match the tall cuts card
GAP = "<div style='height:10px'></div>"
with k1:
    st.markdown(
        tile(L["stores"], f"{stores_now:,}", delta_html(stores_pct, L["vs_prev7"]))
        + GAP
        + tile(L["avg_active"], f"{avg_active:,}"),
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        tile(L["devices"], f"{devices_now:,}", delta_html(devices_pct, L["vs_prev7"]))
        + GAP
        + tile(L["days_active"], f"{days_active:,}"),
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        tile(L["brands"], f"{brands_now:,}")
        + GAP
        + tile(L["peak_day"], f"{fmt_d(peak_day, lang)} <small>({peak_day_n:,})</small>" if peak_day else "—"),
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        tile(L["models"], f"{models_now:,}")
        + GAP
        + tile(L["peak_hour"], f"{peak_hour:02d}:00 <small>({peak_hour_n:,})</small>" if peak_hour is not None else "—"),
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

# ── Plotly base style ──────────────────────────────────────────────────────────
CL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color=MUTED, size=11),
    margin=dict(l=8, r=8, t=10, b=8),
    hoverlabel=dict(bgcolor="#ffffff", bordercolor=GRID, font=dict(color=INK, size=12)),
    showlegend=False,
)
AX  = dict(showgrid=True, gridcolor=GRID, zeroline=False, tickfont=dict(size=10, color=MUTED))
AXF = dict(showgrid=False, zeroline=False, tickfont=dict(size=10, color=MUTED))
PC  = {"displayModeBar": False}


def hbar(series, color=BLUE, height=280, hovername="cuts"):
    """Ranked horizontal bar — one hue (nominal categories), end labels."""
    s = series.iloc[::-1]  # largest on top after autorange reversal below
    fig = go.Figure(go.Bar(
        x=s.values, y=[str(i) for i in s.index], orientation="h",
        marker=dict(color=color, line=dict(width=0)),
        text=[f"{v:,}" for v in s.values], textposition="outside",
        textfont=dict(size=10, color=MUTED, family="JetBrains Mono"),
        cliponaxis=False,
        hovertemplate="%{y}: %{x:,} " + hovername + "<extra></extra>",
    ))
    fig.update_layout(**CL, height=height, bargap=0.35)
    # headroom so outside end labels never clip at the plot edge
    fig.update_xaxes(**AX, range=[0, float(s.max()) * 1.18] if len(s) else None)
    fig.update_yaxes(**AXF)
    return fig


if sel.empty:
    st.info(L["no_data"])
else:
    # ── Row 1: daily trend + top stores ───────────────────────────────────────
    c1, c2 = st.columns([1.65, 1])

    with c1:
        st.markdown(f'<div class="sec">{L["chart_daily"]}</div>', unsafe_allow_html=True)
        full_range = pd.date_range(resolved_start, resolved_end, freq="D").date
        daily = daily_all.reindex(full_range, fill_value=0)
        roll = daily.rolling(7, min_periods=1).mean()
        fig = go.Figure()
        fig.add_bar(
            x=list(daily.index), y=daily.values,
            marker=dict(color=BLUE, line=dict(width=0)),
            hovertemplate="%{x|%d %b}: %{y:,}<extra></extra>",
        )
        fig.add_scatter(
            x=list(roll.index), y=roll.values, mode="lines",
            line=dict(color=MUTED_2, width=2),
            hovertemplate="7d avg: %{y:.1f}<extra></extra>",
        )
        fig.update_layout(**CL, height=290, bargap=0.4)
        fig.update_xaxes(**AXF)
        fig.update_yaxes(**AX)
        st.plotly_chart(fig, width='stretch', config=PC)

    with c2:
        st.markdown(f'<div class="sec">{L["chart_stores"]}</div>', unsafe_allow_html=True)
        sc = sel[STORE_COL].value_counts().head(10)
        st.plotly_chart(hbar(sc, height=290), width='stretch', config=PC)

    # ── Row 2: hour, weekday, categories ──────────────────────────────────────
    c3, c4, c5 = st.columns([1.3, 1, 0.8])

    with c3:
        st.markdown(f'<div class="sec">{L["chart_hour"]}</div>', unsafe_allow_html=True)
        hr = hourly_all.reindex(range(24), fill_value=0)
        fig = go.Figure(go.Bar(
            x=[f"{h:02d}" for h in hr.index], y=hr.values,
            marker=dict(color=AQUA, line=dict(width=0)),
            hovertemplate="%{x}:00 — %{y:,}<extra></extra>",
        ))
        fig.update_layout(**CL, height=250, bargap=0.3)
        fig.update_xaxes(**AXF, tickangle=0)
        fig.update_yaxes(**AX)
        st.plotly_chart(fig, width='stretch', config=PC)

    with c4:
        st.markdown(f'<div class="sec">{L["chart_dow"]}</div>', unsafe_allow_html=True)
        dow = sel.groupby("_dow").size().reindex(range(7), fill_value=0)
        fig = go.Figure(go.Bar(
            x=L["weekdays"], y=dow.values,
            marker=dict(color=VIOLET, line=dict(width=0)),
            hovertemplate="%{x}: %{y:,}<extra></extra>",
        ))
        fig.update_layout(**CL, height=250, bargap=0.35)
        fig.update_xaxes(**AXF)
        fig.update_yaxes(**AX)
        st.plotly_chart(fig, width='stretch', config=PC)

    with c5:
        st.markdown(f'<div class="sec">{L["chart_cats"]}</div>', unsafe_allow_html=True)
        cc = sel[CAT_COL].value_counts()
        st.plotly_chart(hbar(cc, color=YELLOW, height=250), width='stretch', config=PC)

    # ── Row 3: models + brand share ───────────────────────────────────────────
    c6, c7 = st.columns([1.2, 1])
    with c6:
        st.markdown(f'<div class="sec">{L["chart_models"]}</div>', unsafe_allow_html=True)
        mc = sel["_brand_model"].value_counts().head(10)
        st.plotly_chart(hbar(mc, color=ORANGE, height=300), width='stretch', config=PC)
    with c7:
        st.markdown(f'<div class="sec">{L["chart_brands"]}</div>', unsafe_allow_html=True)
        bc = sel[BRAND_COL].value_counts()
        # part-to-whole reads at a glance only with few segments: top 5 + Other
        top = bc.head(5)
        other = int(bc.iloc[5:].sum())
        labels = list(top.index) + ([L["other"]] if other else [])
        values = list(top.values) + ([other] if other else [])
        fig = go.Figure(go.Pie(
            labels=labels, values=values, hole=0.55,
            sort=False, direction="clockwise",
            marker=dict(colors=PIE_COLORS[: len(labels) - 1] + [OTHER_GRAY] if other
                        else PIE_COLORS[: len(labels)],
                        line=dict(color="#ffffff", width=2)),
            textinfo="percent", textposition="auto",
            insidetextorientation="horizontal",
            insidetextfont=dict(size=11, color="#ffffff", family="JetBrains Mono"),
            outsidetextfont=dict(size=11, color=MUTED, family="JetBrains Mono"),
            hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
        ))
        fig.update_layout(
            **{**CL, "showlegend": True},
            height=300,
            legend=dict(orientation="v", x=1.02, y=0.5, font=dict(size=11, color=INK)),
            annotations=[dict(
                text=f"<b>{int(bc.sum()):,}</b>", showarrow=False,
                font=dict(size=18, color=INK, family="JetBrains Mono"),
            )],
        )
        st.plotly_chart(fig, width='stretch', config=PC)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Store leaderboard ─────────────────────────────────────────────────────
    st.markdown(f'<div class="sec">{L["leaderboard"]}</div>', unsafe_allow_html=True)

    lb = sel.groupby(STORE_COL).size().rename(L["lb_cuts"]).to_frame()
    lb[L["lb_share"]] = lb[L["lb_cuts"]] / lb[L["lb_cuts"]].sum()
    g_l7 = base[(base["_date"] >= l7_s) & (base["_date"] <= l7_e)].groupby(STORE_COL).size()
    g_p7 = base[(base["_date"] >= p7_s) & (base["_date"] <= p7_e)].groupby(STORE_COL).size()
    lb[L["lb_last7"]] = g_l7.reindex(lb.index, fill_value=0).astype(int)
    lb[L["lb_prev7"]] = g_p7.reindex(lb.index, fill_value=0).astype(int)
    lb[L["lb_delta"]] = [
        f"{(a - b) / b * 100:+.0f}%" if b > 0 else "—"
        for a, b in zip(lb[L["lb_last7"]], lb[L["lb_prev7"]])
    ]
    lb = lb.sort_values(L["lb_cuts"], ascending=False).reset_index().rename(columns={STORE_COL: L["lb_store"]})

    st.dataframe(
        lb, width='stretch', height=min(38 * (len(lb) + 1), 420), hide_index=True,
        column_config={
            L["lb_share"]: st.column_config.ProgressColumn(
                L["lb_share"], format="percent", min_value=0.0, max_value=1.0
            ),
        },
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Cuts log + export ─────────────────────────────────────────────────────
    st.markdown(f'<div class="sec">{L["log_title"]}</div>', unsafe_allow_html=True)
    display_cols = [c for c in [DATE_COL, STORE_COL, DEVICE_COL, CAT_COL, BRAND_COL, MODEL_COL] if c in sel.columns]
    log = sel.sort_values(DATE_COL, ascending=False)[display_cols].reset_index(drop=True)
    st.dataframe(log, width='stretch', height=380)

    dl1, dl2, _ = st.columns([1, 1, 3])
    with dl1:
        st.download_button(
            L["export_csv"], data=log.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{date.today().strftime('%Y%m%d')}_wrapsol_cuts.csv",
            mime="text/csv", width='stretch',
        )
    with dl2:
        buf = BytesIO()
        log.to_excel(buf, index=False)
        st.download_button(
            L["export_excel"], data=buf.getvalue(),
            file_name=f"{date.today().strftime('%Y%m%d')}_wrapsol_cuts.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch',
        )
