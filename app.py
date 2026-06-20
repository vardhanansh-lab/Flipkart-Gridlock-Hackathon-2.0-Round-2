"""
GRIDLOCK — Predictive Illegal-Parking Enforcement System
Flipkart Gridlock Hackathon · Round 2 Prototype
Team: Last Mile Legends

Streamlit dashboard: predicts tomorrow's top-5% illegal-parking hotspots in
Bengaluru and ranks them by traffic-flow impact into a deployable patrol queue.
"""
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import datetime as dt

st.set_page_config(page_title="GRIDLOCK · Parking Enforcement Intelligence",
                   page_icon="🛰️", layout="wide", initial_sidebar_state="collapsed")

# ---------- THEME (dark, dense, Linear/Stripe-style) ----------
st.markdown("""
<style>
  .stApp { background:#0a0b0f; color:#e6e7eb; }
  #MainMenu,footer,header {visibility:hidden;}
  .block-container{padding-top:1.2rem;padding-bottom:1rem;max-width:1500px;}
  h1,h2,h3,h4{color:#f4f5f7;font-family:'Inter',system-ui,sans-serif;letter-spacing:-.02em;}
  .kpi{background:linear-gradient(160deg,#14161d,#0e1015);border:1px solid #1f2230;
       border-radius:14px;padding:16px 18px;}
  .kpi .v{font-size:30px;font-weight:700;color:#fff;line-height:1;}
  .kpi .l{font-size:11px;color:#7c8190;text-transform:uppercase;letter-spacing:.08em;margin-top:6px;}
  .kpi .d{font-size:11px;color:#34d399;margin-top:4px;}
  .qrow{background:#0e1015;border:1px solid #1b1e2a;border-left:3px solid var(--c);
        border-radius:10px;padding:10px 14px;margin-bottom:7px;}
  .qrow:hover{border-color:#2a2e3e;background:#12141b;}
  .rank{font-size:13px;color:#7c8190;font-weight:600;}
  .cell{font-size:14px;font-weight:600;color:#f4f5f7;font-family:ui-monospace,monospace;}
  .meta{font-size:11px;color:#868b99;}
  .score{font-size:20px;font-weight:700;color:#fff;float:right;}
  .pill{display:inline-block;font-size:10px;padding:2px 7px;border-radius:20px;
        background:#1a1d28;color:#9aa0b0;margin-right:5px;}
  .pill.hot{background:#3b1418;color:#f87171;}
  .pill.art{background:#2a1f08;color:#fbbf24;}
  .sec{font-size:12px;color:#7c8190;text-transform:uppercase;letter-spacing:.1em;
       margin:4px 0 10px;font-weight:600;}
  .badge{background:#0c1f17;border:1px solid #14402e;color:#34d399;font-size:11px;
         padding:3px 10px;border-radius:20px;font-weight:600;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load():
    df = pd.read_csv("dashboard_predictions.csv")
    df = df.dropna(subset=["lat","lon"])
    return df.sort_values("priority_score", ascending=False).reset_index(drop=True)

df = load()
tomorrow = (dt.date.today()+dt.timedelta(days=1)).strftime("%a, %d %b %Y")

# ---------- HEADER ----------
c1,c2 = st.columns([0.72,0.28])
with c1:
    st.markdown("# 🛰️ GRIDLOCK")
    st.markdown("**Predictive Illegal-Parking Enforcement Intelligence** · Bengaluru City Traffic Police")
with c2:
    st.markdown(f"<div style='text-align:right;padding-top:18px'>"
                f"<span class='badge'>● LIVE FORECAST</span><br>"
                f"<span class='meta'>Patrol plan for &nbsp;<b style='color:#e6e7eb'>{tomorrow}</b></span></div>",
                unsafe_allow_html=True)
st.markdown("<hr style='border-color:#1a1d28;margin:12px 0 18px'>", unsafe_allow_html=True)

# ---------- CONTROLS ----------
fc1,fc2,fc3 = st.columns([0.4,0.3,0.3])
with fc1:
    topk = st.slider("Patrol capacity (cells to deploy)", 10, 60, 20, 5)
with fc2:
    view = st.selectbox("Rank by", ["Enforcement Priority (impact-weighted)",
                                     "Raw hotspot probability"])
with fc3:
    show_heavy = st.checkbox("Flag freight corridors", value=True)

rank_col = "priority_score" if view.startswith("Enforcement") else "hotspot_prob"
ranked = df.sort_values(rank_col, ascending=False).reset_index(drop=True)
sel = ranked.head(topk).copy()

# ---------- KPIs ----------
k1,k2,k3,k4 = st.columns(4)
kpis = [
    (f"{topk}", "Cells flagged tomorrow", "top-priority targets"),
    ("0.945", "Model AUC (top-5% hotspots)", "±0.018 · 3-fold CV"),
    (f"{int(sel['total_viol'].sum()):,}", "Violations in flagged zones", "historical load"),
    (f"{(sel['heavy_share']>0.5).sum()}", "Freight-corridor cells", "high flow-impact"),
]
for col,(v,l,d) in zip([k1,k2,k3,k4],kpis):
    col.markdown(f"<div class='kpi'><div class='v'>{v}</div><div class='l'>{l}</div>"
                 f"<div class='d'>{d}</div></div>", unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# ---------- SPLIT: MAP | QUEUE ----------
mcol, qcol = st.columns([0.5,0.5])

with mcol:
    st.markdown("<div class='sec'>Predicted Hotspot Map · Bengaluru</div>", unsafe_allow_html=True)
    sel["radius"] = 120 + sel[rank_col]/sel[rank_col].max()*380
    sel["r"]=240; sel["g"]=(180*(1-sel[rank_col]/sel[rank_col].max())).astype(int); sel["b"]=60
    layer = pdk.Layer("ScatterplotLayer", data=sel,
        get_position="[lon,lat]", get_radius="radius",
        get_fill_color="[r,g,b,160]", get_line_color="[255,120,80,200]",
        line_width_min_pixels=1, pickable=True, stroked=True)
    rest = ranked.iloc[topk:]
    base = pdk.Layer("ScatterplotLayer", data=rest,
        get_position="[lon,lat]", get_radius=60,
        get_fill_color="[90,95,110,70]", pickable=False)
    view_state = pdk.ViewState(latitude=float(sel["lat"].mean()),
        longitude=float(sel["lon"].mean()), zoom=10.6, pitch=35)
    st.pydeck_chart(pdk.Deck(layers=[base,layer], initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={"html":"<b>{gh6}</b><br/>Priority: {priority_score}<br/>"
                 "Peak hour: {peak_hour}:00<br/>Hist. violations: {total_viol}",
                 "style":{"backgroundColor":"#14161d","color":"#e6e7eb","fontSize":"12px"}}),
        use_container_width=True)
    st.markdown("<span class='meta'>🔴 Red intensity = enforcement priority · "
                "grey = lower-priority cells · hover for detail</span>", unsafe_allow_html=True)

with qcol:
    st.markdown("<div class='sec'>Patrol Deployment Queue · ranked by impact</div>", unsafe_allow_html=True)
    qbox = st.container(height=560)
    with qbox:
        for i,row in sel.iterrows():
            mx = sel[rank_col].max()
            c = "#f87171" if row[rank_col]>0.66*mx else "#fbbf24" if row[rank_col]>0.33*mx else "#60a5fa"
            hot = "<span class='pill hot'>HIGH RISK</span>" if row["hotspot_prob"]>0.9 else ""
            art = "<span class='pill art'>FREIGHT</span>" if (show_heavy and row["heavy_share"]>0.5) else ""
            loc = str(row.get("location","")).strip()[:34] or "—"
            st.markdown(f"""<div class='qrow' style='--c:{c}'>
              <span class='score'>{row['priority_score']:.0f}</span>
              <span class='rank'>#{i+1}</span> &nbsp;<span class='cell'>{row['gh6']}</span><br/>
              {hot}{art}
              <span class='meta'>peak {int(row['peak_hour'])}:00 · {int(row['total_viol']):,} hist · {loc}</span>
            </div>""", unsafe_allow_html=True)

# ---------- FOOTER STRIP ----------
st.markdown("<hr style='border-color:#1a1d28;margin:16px 0 10px'>", unsafe_allow_html=True)
st.markdown(
  "<span class='meta'><b style='color:#e6e7eb'>How it works:</b> "
  "LightGBM spatio-temporal forecaster predicts each cell's hotspot probability for "
  "tomorrow (AUC 0.945, top-5% definition), then an impact layer weights it by road "
  "criticality (throughput + freight share) → <b style='color:#34d399'>Enforcement "
  "Priority Score</b>. Trained on 298K real Bengaluru violation records (Jan–May).</span>",
  unsafe_allow_html=True)
