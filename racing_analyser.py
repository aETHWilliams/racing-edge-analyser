"""
Racing Edge Analyser — PuntingForm API v2
Live odds scraped from TAB.com.au (public, no auth required)
pip install streamlit requests pandas numpy plotly
streamlit run racing_analyser.py
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, date
from typing import Optional, Dict, List
import json
import re
import time

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Racing Edge",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── PREMIUM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@300;400;500&family=Playfair+Display:wght@700;800&display=swap');

:root {
  /* Core palette — deep navy / brass / cream */
  --ink:#0d0f14;
  --ink-2:#1a1e2a;
  --ink-3:#252b3b;
  --slate:#3a4256;
  --steel:#5a6480;
  --mist:#8b95aa;
  --fog:#b8bfcc;
  --silver:#d6dae3;
  --ghost:#eef0f5;
  --snow:#f7f8fb;
  --white:#ffffff;

  /* Accent — brass / gold */
  --brass:#c9a44a;
  --brass-l:#e8d49a;
  --brass-ll:#fdf6e3;
  --brass-dark:#8c6f2a;

  /* Accent — sapphire */
  --sap:#2255cc;
  --sap-mid:#3b6fe0;
  --sap-l:#d0dcf8;
  --sap-ll:#eef2fd;

  /* Semantic */
  --go:#1a8c4e;
  --go-l:#d4f0e2;
  --go-m:#6dd49a;
  --stop:#c0392b;
  --stop-l:#fde8e6;
  --stop-m:#f0938a;
  --warn:#b06a00;
  --warn-l:#fef3d6;
  --warn-m:#f5c96b;
  --info:#1a6ea8;
  --info-l:#d6ecf8;

  --r:5px;--r2:9px;--r3:14px;--r4:22px;
  --sh:0 1px 4px rgba(13,15,20,.07),0 1px 2px rgba(13,15,20,.05);
  --sh2:0 4px 20px rgba(13,15,20,.1),0 1px 6px rgba(13,15,20,.06);
  --sh3:0 8px 40px rgba(34,85,204,.15),0 2px 10px rgba(34,85,204,.08);
}

html,body,[data-testid="stAppViewContainer"]{
  font-family:'DM Sans',sans-serif!important;
  background:var(--snow)!important;
  color:var(--ink)!important;
  font-size:14px;
}

/* ── SIDEBAR ── */
[data-testid="stHeader"]{background:transparent!important;}
[data-testid="stSidebar"]{
  background:var(--ink-2)!important;
  border-right:1px solid var(--ink-3)!important;
}
[data-testid="stSidebar"]>div{padding-top:0!important;}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stDateInput label{
  color:var(--fog)!important;font-size:.72rem!important;
  font-weight:500!important;letter-spacing:.04em!important;
  text-transform:uppercase!important;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] select{
  background:var(--ink-3)!important;
  border:1px solid var(--slate)!important;
  border-radius:var(--r)!important;
  color:var(--silver)!important;
  font-family:'DM Mono',monospace!important;
}
[data-testid="stSidebar"] [data-baseweb="select"]>div{
  background:var(--ink-3)!important;
  border:1px solid var(--slate)!important;
}
[data-testid="stSidebar"] [data-baseweb="select"]*{color:var(--silver)!important;}
[data-testid="stSidebar"] [data-testid="stAlert"]{display:none;}

/* ── INPUTS ── */
.stTextInput input,.stNumberInput input,.stTextArea textarea{
  background:var(--white)!important;
  border:1px solid var(--silver)!important;
  border-radius:var(--r)!important;
  color:var(--ink)!important;
  font-family:'DM Mono',monospace!important;
  font-size:.82rem!important;
  transition:border .15s;
}
.stTextInput input:focus,.stNumberInput input:focus{
  border-color:var(--sap)!important;
  box-shadow:0 0 0 3px rgba(34,85,204,.1)!important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{
  background:var(--white)!important;
  border-bottom:2px solid var(--silver)!important;
  gap:0!important;padding:0!important;
  box-shadow:var(--sh);
}
.stTabs [data-baseweb="tab"]{
  background:transparent!important;
  color:var(--steel)!important;
  font-family:'DM Sans',sans-serif!important;
  font-size:.82rem!important;font-weight:500!important;
  padding:15px 22px!important;
  border:none!important;border-bottom:2px solid transparent!important;
  margin-bottom:-2px!important;letter-spacing:.02em;
}
.stTabs [aria-selected="true"]{
  color:var(--ink)!important;
  border-bottom:2px solid var(--brass)!important;
  font-weight:700!important;
}
.stTabs [data-testid="stTabPanel"]{
  background:var(--snow)!important;padding-top:28px!important;
}

/* ── BUTTONS ── */
.stButton>button{
  background:var(--ink)!important;color:var(--white)!important;
  border:none!important;border-radius:var(--r2)!important;
  font-family:'DM Sans',sans-serif!important;
  font-weight:600!important;font-size:.8rem!important;
  padding:.55rem 1.25rem!important;letter-spacing:.02em;
  box-shadow:0 2px 8px rgba(13,15,20,.25)!important;
  transition:all .18s ease!important;
}
.stButton>button:hover{
  background:var(--ink-3)!important;
  transform:translateY(-1px)!important;
  box-shadow:0 4px 16px rgba(13,15,20,.3)!important;
}
[data-testid="stSidebar"] .stButton>button{
  background:linear-gradient(135deg,var(--brass-dark),var(--brass))!important;
  color:var(--ink)!important;width:100%!important;padding:.65rem!important;
  font-weight:700!important;
}
[data-testid="stSidebar"] .stButton>button:hover{
  filter:brightness(1.08)!important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"]{
  border:1px solid var(--silver)!important;
  border-radius:var(--r2)!important;overflow:hidden!important;
  box-shadow:var(--sh)!important;
}
[data-testid="stDataFrame"] th{
  background:var(--ghost)!important;color:var(--slate)!important;
  font-family:'DM Sans',sans-serif!important;
  font-size:.65rem!important;font-weight:700!important;
  letter-spacing:.1em!important;text-transform:uppercase!important;
  border-bottom:2px solid var(--silver)!important;padding:11px 14px!important;
}
[data-testid="stDataFrame"] td{
  color:var(--ink)!important;border-bottom:1px solid var(--ghost)!important;
  font-family:'DM Mono',monospace!important;font-size:.77rem!important;
  padding:9px 14px!important;
}
[data-testid="stDataFrame"] tr:hover td{background:var(--sap-ll)!important;}

/* ── EXPANDERS ── */
.streamlit-expanderHeader{
  background:var(--white)!important;border:1px solid var(--silver)!important;
  border-radius:var(--r2)!important;color:var(--ink)!important;
  font-family:'DM Sans',sans-serif!important;font-size:.86rem!important;
  font-weight:600!important;box-shadow:var(--sh)!important;
  padding:14px 18px!important;transition:background .15s;
}
.streamlit-expanderHeader:hover{background:var(--ghost)!important;}
.streamlit-expanderContent{
  background:var(--white)!important;border:1px solid var(--silver)!important;
  border-top:none!important;border-radius:0 0 var(--r2) var(--r2)!important;
  padding:20px!important;
}
[data-testid="stAlert"]{border-radius:var(--r2)!important;font-size:.82rem!important;}

/* ── CUSTOM COMPONENTS ── */
.brand-header{
  background:linear-gradient(160deg,var(--ink) 0%,var(--ink-3) 100%);
  margin:-1rem -1rem 0;padding:24px 20px 22px;
  border-bottom:1px solid rgba(201,164,74,.3);
}
.brand-logo{
  font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:800;
  color:var(--white);letter-spacing:-.01em;display:flex;align-items:center;gap:10px;
}
.brand-sub{
  font-family:'DM Mono',monospace;font-size:.58rem;color:rgba(255,255,255,.4);
  letter-spacing:.16em;margin-top:5px;text-transform:uppercase;
}
.brand-version{
  display:inline-block;margin-top:10px;padding:2px 10px;
  background:rgba(201,164,74,.2);border:1px solid rgba(201,164,74,.4);
  border-radius:99px;font-family:'DM Mono',monospace;
  font-size:.58rem;color:var(--brass-l);letter-spacing:.08em;
}
.sb-section{
  font-size:.62rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  color:var(--slate);margin:22px 0 10px;padding-top:18px;
  border-top:1px solid var(--ink-3);
}
.sb-section:first-of-type{border-top:none;margin-top:18px;}
.status-ok{
  font-size:.72rem;color:#4ade80;font-family:'DM Mono',monospace;
  display:flex;align-items:center;gap:6px;margin-top:5px;
}
.status-ok::before{content:'●';font-size:.5rem;animation:pulse 2s infinite;}
.status-err{
  font-size:.72rem;color:#f87171;font-family:'DM Mono',monospace;
  display:flex;align-items:center;gap:6px;margin-top:5px;
}
.status-err::before{content:'●';font-size:.5rem;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}

.page-header{
  display:flex;align-items:flex-end;justify-content:space-between;
  border-bottom:2px solid var(--silver);padding-bottom:18px;margin-bottom:32px;
}
.page-title{
  font-family:'Playfair Display',serif;font-size:1.7rem;font-weight:700;
  color:var(--ink);letter-spacing:-.02em;line-height:1;
}
.page-eyebrow{
  font-family:'DM Mono',monospace;font-size:.62rem;color:var(--mist);
  letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px;
}

.metric-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(145px,1fr));gap:14px;margin-bottom:28px;}
.metric-card{
  background:var(--white);border:1px solid var(--silver);
  border-radius:var(--r2);padding:18px 20px;box-shadow:var(--sh);
  position:relative;overflow:hidden;
}
.metric-card::after{
  content:'';position:absolute;bottom:0;left:0;right:0;height:3px;
  background:var(--silver);
}
.metric-card.c-blue::after{background:var(--sap);}
.metric-card.c-green::after{background:var(--go);}
.metric-card.c-red::after{background:var(--stop);}
.metric-card.c-brass::after{background:var(--brass);}
.metric-lbl{font-size:.62rem;font-weight:700;color:var(--mist);letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px;}
.metric-val{font-family:'DM Mono',monospace;font-size:1.55rem;font-weight:700;color:var(--ink);line-height:1;}
.metric-val.c-blue{color:var(--sap);}
.metric-val.c-green{color:var(--go);}
.metric-val.c-red{color:var(--stop);}
.metric-val.c-brass{color:var(--brass-dark);}
.metric-sub{font-family:'DM Mono',monospace;font-size:.65rem;color:var(--mist);margin-top:5px;}

.pill{display:inline-flex;align-items:center;padding:2px 10px;border-radius:99px;font-size:.63rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;line-height:1.9;}
.pill-ink{background:var(--ink);color:var(--silver);}
.pill-blue{background:var(--sap-ll);color:var(--sap);border:1px solid var(--sap-l);}
.pill-green{background:var(--go-l);color:var(--go);border:1px solid var(--go-m);}
.pill-red{background:var(--stop-l);color:var(--stop);border:1px solid var(--stop-m);}
.pill-amber{background:var(--warn-l);color:var(--warn);border:1px solid var(--warn-m);}
.pill-muted{background:var(--ghost);color:var(--steel);border:1px solid var(--silver);}
.pill-brass{background:var(--brass-ll);color:var(--brass-dark);border:1px solid var(--brass-l);}

.alert{border-radius:var(--r2);padding:12px 16px;font-size:.82rem;margin:8px 0;line-height:1.65;}
.alert-blue{background:var(--info-l);border-left:3px solid var(--info);color:var(--info);}
.alert-green{background:var(--go-l);border-left:3px solid var(--go);color:var(--go);}
.alert-red{background:var(--stop-l);border-left:3px solid var(--stop);color:var(--stop);}
.alert-amber{background:var(--warn-l);border-left:3px solid var(--warn);color:var(--warn);}
.alert-brass{background:var(--brass-ll);border-left:3px solid var(--brass);color:var(--brass-dark);}

.card{background:var(--white);border:1px solid var(--silver);border-radius:var(--r2);padding:22px 24px;box-shadow:var(--sh);margin-bottom:14px;}
.card-sm{background:var(--ghost);border:1px solid var(--silver);border-radius:var(--r);padding:10px 14px;margin-bottom:7px;}
.card-blue{background:var(--sap-ll);border:1px solid var(--sap-l);border-radius:var(--r2);padding:16px 20px;margin-bottom:14px;}
.card-green{background:var(--go-l);border:1px solid var(--go-m);border-radius:var(--r2);padding:16px 20px;margin-bottom:14px;}
.card-brass{background:var(--brass-ll);border:1px solid var(--brass-l);border-radius:var(--r2);padding:16px 20px;margin-bottom:14px;}
.card-dark{background:var(--ink);border:1px solid var(--ink-3);border-radius:var(--r2);padding:18px 20px;margin-bottom:14px;}

/* MARKET TABLE */
.mkt-wrap{background:var(--white);border:1px solid var(--silver);border-radius:var(--r2);overflow:hidden;box-shadow:var(--sh);}
.mkt-table{width:100%;border-collapse:collapse;font-size:.8rem;}
.mkt-table th{
  background:var(--ghost);color:var(--slate);
  font-size:.62rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
  padding:12px 16px;text-align:left;border-bottom:2px solid var(--silver);white-space:nowrap;
}
.mkt-table td{
  padding:11px 16px;border-bottom:1px solid var(--ghost);
  font-family:'DM Mono',monospace;font-size:.77rem;color:var(--ink);vertical-align:middle;
}
.mkt-table tr:last-child td{border-bottom:none;}
.mkt-table tr:hover td{background:var(--sap-ll);}
.mkt-table .val-row td{background:rgba(26,140,78,.04);}
.mkt-table .fav-row td{background:rgba(34,85,204,.03);}
.mkt-horse{font-family:'DM Sans',sans-serif;font-weight:700;font-size:.88rem;color:var(--ink);}
.mkt-badge{display:inline-block;padding:1px 7px;border-radius:3px;font-size:.58rem;font-weight:700;margin-left:6px;text-transform:uppercase;letter-spacing:.06em;}
.badge-fav{background:var(--sap-ll);color:var(--sap);}
.badge-val{background:var(--go-l);color:var(--go);}
.badge-live{background:var(--warn-l);color:var(--warn);}
.edge-pos{color:var(--go);font-weight:700;}
.edge-neg{color:var(--stop);}
.edge-neu{color:var(--mist);}
.prob-bar{height:4px;border-radius:2px;background:var(--silver);overflow:hidden;margin-top:5px;}
.prob-fill{height:4px;border-radius:2px;}

/* SPEEDMAP */
.tempo-banner{
  display:flex;align-items:center;gap:16px;
  background:var(--white);border:1px solid var(--silver);
  border-radius:var(--r2);padding:16px 20px;margin-bottom:16px;box-shadow:var(--sh);
}
.smap-row{
  display:flex;align-items:center;gap:14px;
  padding:10px 16px;background:var(--white);border:1px solid var(--silver);
  border-radius:var(--r);margin-bottom:6px;box-shadow:var(--sh);
}
.smap-pos{font-size:.7rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;width:82px;flex-shrink:0;}
.smap-horses{font-family:'DM Mono',monospace;font-size:.78rem;color:var(--ink-3);flex:1;}
.smap-cnt{font-family:'DM Mono',monospace;font-size:.68rem;color:var(--mist);width:24px;text-align:right;}

/* FACTOR BARS */
.factor-row{display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid var(--ghost);}
.factor-name{font-size:.72rem;color:var(--steel);width:100px;flex-shrink:0;font-weight:500;}
.factor-bar{flex:1;height:4px;border-radius:2px;background:var(--silver);}
.factor-fill{height:4px;border-radius:2px;}
.factor-score{font-family:'DM Mono',monospace;font-size:.65rem;color:var(--ink-3);width:52px;text-align:right;flex-shrink:0;}

/* GATE ROWS */
.gate-row{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--ghost);}
.gate-lbl{font-size:.82rem;color:var(--ink-3);flex:1;font-weight:500;}
.gate-detail{font-family:'DM Mono',monospace;font-size:.7rem;color:var(--steel);}

/* STAKE CARD */
.stake-card{
  background:linear-gradient(135deg,var(--ink-2) 0%,var(--ink-3) 100%);
  border:1px solid var(--brass-dark);
  border-radius:var(--r2);padding:20px 22px;margin-bottom:12px;
  box-shadow:0 4px 20px rgba(13,15,20,.35);
}
.stake-lbl{font-size:.66rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--brass-l);margin-bottom:8px;}
.stake-amount{font-family:'DM Mono',monospace;font-size:2.4rem;font-weight:700;color:var(--white);line-height:1;}
.stake-detail{font-family:'DM Mono',monospace;font-size:.72rem;color:rgba(255,255,255,.65);margin-top:7px;}

/* BET BANNER */
.bet-banner{
  background:linear-gradient(135deg,var(--go),#22a862);
  border-radius:var(--r2);padding:14px 18px;margin-bottom:12px;
}
.bet-banner-title{font-size:.82rem;font-weight:700;color:var(--white);margin-bottom:3px;}
.bet-banner-sub{font-size:.74rem;color:rgba(255,255,255,.85);}

/* RACE / MEETING ROWS */
.race-row{display:flex;align-items:center;justify-content:space-between;padding:11px 0;border-bottom:1px solid var(--ghost);}
.race-row:last-child{border-bottom:none;}
.race-num{font-family:'DM Mono',monospace;font-size:.9rem;font-weight:700;color:var(--sap);width:30px;flex-shrink:0;}
.race-name{font-size:.9rem;font-weight:600;color:var(--ink);}
.race-meta{font-family:'DM Mono',monospace;font-size:.66rem;color:var(--mist);margin-top:3px;}

.section-hdr{
  font-size:.63rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase;
  color:var(--mist);border-bottom:1px solid var(--silver);
  padding-bottom:8px;margin:28px 0 16px;
}

.dl-label{font-size:.63rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--mist);margin-bottom:4px;}
.dl-value{font-family:'DM Mono',monospace;font-size:1.0rem;color:var(--ink);font-weight:600;}
.dl-value.c-green{color:var(--go);}
.dl-value.c-red{color:var(--stop);}
.dl-value.c-blue{color:var(--sap);}
.dl-value.c-brass{color:var(--brass-dark);}

.debug-box{
  background:var(--ink);border:1px solid var(--ink-3);border-radius:var(--r);
  padding:12px 14px;font-family:'DM Mono',monospace;font-size:.72rem;
  color:var(--mist);white-space:pre-wrap;max-height:300px;overflow-y:auto;
}
.empty-state{text-align:center;padding:70px 20px;color:var(--mist);}
.empty-icon{font-size:2.8rem;margin-bottom:14px;opacity:.6;}
.empty-title{font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;color:var(--slate);margin-bottom:7px;}
.empty-sub{font-size:.84rem;color:var(--mist);line-height:1.7;}

/* LIVE PRICE BADGE */
.live-price{
  display:inline-flex;align-items:center;gap:5px;
  font-family:'DM Mono',monospace;font-size:.82rem;font-weight:700;
  color:var(--ink);
}
.live-dot{width:6px;height:6px;border-radius:50%;background:#22c55e;animation:pulse 2s infinite;flex-shrink:0;}

hr{border:none;border-top:1px solid var(--ghost);margin:26px 0;}
.prob-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.prob-cell{background:var(--ghost);border:1px solid var(--silver);border-radius:var(--r);padding:11px 14px;}
.prob-cell-blue{background:var(--sap-ll);border:1px solid var(--sap-l);border-radius:var(--r);padding:11px 14px;}

/* Odds update flash */
@keyframes flash{0%{background:rgba(201,164,74,.35)}100%{background:transparent}}
.price-updated{animation:flash .8s ease-out;}
</style>
""", unsafe_allow_html=True)


# ─── SESSION STATE ────────────────────────────────────────────────────────────
DEFAULTS = {
    "api_key": "", "meetings": [], "selected_race": None, "runners": [],
    "ratings": {}, "pf_ratings": {}, "sectionals": {},
    "past_form_by_horse": {}, "bet_log": [],
    "bank": 1000.0, "starting_bank": 1000.0,
    "staking_method": "Quarter Kelly", "kelly_fraction": 0.25,
    "flat_pct": 2.0, "level_stake": 20.0, "max_stake_pct": 5.0,
    "min_odds": 2.0, "max_odds": 50.0, "min_rating": 50,
    "min_edge": 3.0, "min_tj_a2e": 0.8,
    "notes": {},
    "_api_log": [],
    "_live_prices": {},
    "_live_prices_ts": None,
    "_live_source": "",
    "_model_reasoning": {},
    "fetch_status": "", "fetch_count": 0,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── API LAYER ────────────────────────────────────────────────────────────────
BASE_URL = "https://api.puntingform.com.au/v2"

def pf_date(d: date) -> str:
    import platform
    fmt = "%#d-%b-%Y" if platform.system() == "Windows" else "%-d-%b-%Y"
    return d.strftime(fmt)

def _log_api(url: str, params: dict, status: int, note: str = ""):
    safe = {k: v for k, v in params.items() if k != "apiKey"}
    st.session_state["_api_log"].append({
        "url": url, "params": safe, "status": status,
        "note": note, "ts": datetime.now().strftime("%H:%M:%S"),
    })
    st.session_state["_api_log"] = st.session_state["_api_log"][-40:]

def pf_get(endpoint: str, params: dict = {}, silent: bool = False) -> Optional[dict]:
    if not st.session_state.api_key:
        return None
    p = dict(params)
    p["apiKey"] = st.session_state.api_key
    url = f"{BASE_URL}/{endpoint}"
    try:
        r = requests.get(url, params=p, timeout=20)
        _log_api(url, p, r.status_code, "" if r.ok else r.text[:200])
        if r.status_code == 400:
            if not silent:
                try: msg = r.json().get("error", r.text[:120])
                except: msg = r.text[:120]
                st.error(f"API 400 — {endpoint}: {msg}")
            return None
        if r.status_code == 401:
            st.error("API 401: Invalid or expired API key.")
            return None
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        _log_api(url, p, -1, "TIMEOUT")
        if not silent: st.error(f"Timeout on {endpoint}")
    except Exception as e:
        _log_api(url, p, -1, str(e))
        if not silent: st.error(f"Error on {endpoint}: {e}")
    return None

def safe_float(v, d: float = 0.0) -> float:
    try: return float(v)
    except: return d

def safe_int(v, d: int = 0) -> int:
    try: return int(v)
    except: return d


# ─── LIVE PRICE SCRAPING ──────────────────────────────────────────────────────
SCRAPE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-AU,en;q=0.9",
    "Referer": "https://www.tab.com.au/",
}

def _normalise_horse_name(name: str) -> str:
    """Lowercase, strip punctuation for fuzzy matching."""
    return re.sub(r"[^a-z0-9 ]", "", name.lower().strip())

def scrape_tab_prices(track_name: str, race_number: int, race_date: date) -> dict:
    """
    Fetch live win prices from the TAB.com.au racing API (public JSON endpoint).
    Returns dict: {normalised_horse_name: price}
    Falls back to Betfair SP data from PuntingForm if TAB fails.
    """
    prices = {}
    source = ""

    # --- Attempt 1: TAB API (public, no auth) ---
    # TAB uses a slug like "2025-01-01/R1/thoroughbred" with venue code
    try:
        date_str = race_date.strftime("%Y-%m-%d")
        # TAB venue search
        venue_url = "https://api.tab.com.au/v1/tab-info-service/racing/dates/{}/meetings".format(date_str)
        r = requests.get(venue_url, headers=SCRAPE_HEADERS, timeout=8)
        if r.ok:
            data = r.json()
            meetings = data.get("meetings", [])
            # Find matching meeting
            track_norm = _normalise_horse_name(track_name)
            matched_meeting = None
            for m in meetings:
                m_name = _normalise_horse_name(m.get("meetingName","") or m.get("venueName",""))
                if track_norm in m_name or m_name in track_norm:
                    matched_meeting = m
                    break
            if matched_meeting:
                # Get race detail
                meeting_id = matched_meeting.get("meetingId","")
                race_url = "https://api.tab.com.au/v1/tab-info-service/racing/dates/{}/meetings/{}/races/{}".format(
                    date_str, meeting_id, race_number)
                r2 = requests.get(race_url, headers=SCRAPE_HEADERS, timeout=8)
                if r2.ok:
                    rdata = r2.json()
                    for runner in rdata.get("runners", []):
                        name = runner.get("runnerName","")
                        win_odds = runner.get("fixedOdds", {}).get("returnWin", 0)
                        if not win_odds:
                            win_odds = runner.get("parimutuel", {}).get("returnWin", 0)
                        if name and win_odds and float(win_odds) > 1.0:
                            prices[_normalise_horse_name(name)] = float(win_odds)
                    if prices:
                        source = "TAB.com.au live"
    except Exception:
        pass

    # --- Attempt 2: Betfair Exchange via TAB API alternate endpoint ---
    if not prices:
        try:
            date_str = race_date.strftime("%Y-%m-%d")
            url = f"https://api.tab.com.au/v1/tab-info-service/racing/dates/{date_str}/meetings"
            params = {"jurisdiction": "QLD"}
            r = requests.get(url, headers=SCRAPE_HEADERS, params=params, timeout=8)
            if r.ok:
                data = r.json()
                meetings_list = data.get("meetings", [])
                track_norm = _normalise_horse_name(track_name)
                for m in meetings_list:
                    m_name = _normalise_horse_name(m.get("meetingName","") or "")
                    if track_norm in m_name or m_name in track_norm:
                        for race in m.get("races", []):
                            if race.get("raceNumber") == race_number:
                                for runner in race.get("runners", []):
                                    name = runner.get("runnerName","")
                                    price = safe_float(runner.get("fixedOdds",{}).get("returnWin",0))
                                    if not price:
                                        price = safe_float(runner.get("parimutuel",{}).get("returnWin",0))
                                    if name and price > 1.0:
                                        prices[_normalise_horse_name(name)] = price
                        if prices:
                            source = "TAB.com.au (embedded)"
                            break
        except Exception:
            pass

    # --- Attempt 3: Sky Racing / Racing and Sports public API ---
    if not prices:
        try:
            date_str = race_date.strftime("%Y-%m-%d")
            url = f"https://www.racingandpunting.com.au/api/race/{date_str}/{_normalise_horse_name(track_name).replace(' ', '-')}/{race_number}"
            r = requests.get(url, headers=SCRAPE_HEADERS, timeout=8)
            if r.ok:
                data = r.json()
                for runner in data.get("horses", data.get("runners", [])):
                    name = runner.get("horse_name","") or runner.get("name","")
                    price = safe_float(runner.get("fixed_win","") or runner.get("win_price","") or 0)
                    if name and price > 1.0:
                        prices[_normalise_horse_name(name)] = price
                if prices:
                    source = "RacingAndPunting"
        except Exception:
            pass

    return prices, source


def get_live_price(horse_name: str) -> Optional[float]:
    """Look up a horse's live price from the cached scrape."""
    live = st.session_state.get("_live_prices", {})
    if not live:
        return None
    norm = _normalise_horse_name(horse_name)
    # Exact match
    if norm in live:
        return live[norm]
    # Partial match — handle "(NZ)" suffixes etc.
    for k, v in live.items():
        if norm[:8] in k or k[:8] in norm:
            return v
    return None


def refresh_live_prices(race: dict, race_date_obj: date):
    """Trigger a live price scrape for the current race."""
    track = race.get("_meetingName","")
    rnum = safe_int(race.get("raceNumber") or race.get("number") or 1)
    with st.spinner("Fetching live odds..."):
        prices, source = scrape_tab_prices(track, rnum, race_date_obj)
    st.session_state["_live_prices"] = prices
    st.session_state["_live_prices_ts"] = datetime.now()
    st.session_state["_live_source"] = source
    return prices, source


def get_best_price(runner: dict) -> float:
    """Return live price if available, else fall back to SP / fixed odds."""
    name = get_runner_name(runner)
    live = get_live_price(name)
    if live and live > 1.0:
        return live
    # Fallback chain
    for field in ("fixedOddsWin", "fixedWin", "priceSP", "price", "sp"):
        v = safe_float(runner.get(field, 0))
        if v > 1.01:
            return v
    return 0.0


def price_source_label(runner: dict) -> str:
    name = get_runner_name(runner)
    live = get_live_price(name)
    if live and live > 1.0:
        return "live"
    return "sp"


# ─── PAYLOAD EXTRACTION ───────────────────────────────────────────────────────
def extract_runners_from_payload(data) -> list:
    if not data:
        return []
    payload = data.get("payLoad", data) if isinstance(data, dict) else data
    if isinstance(payload, list):
        if payload and isinstance(payload[0], dict):
            first = payload[0]
            if any(k in first for k in ("name","runnerName","horseName","horseId","runnerId","HorseId","RunnerID")):
                return payload
            for race in payload:
                for rkey in ("runners","fields","horses"):
                    runners = race.get(rkey, [])
                    if runners and isinstance(runners, list):
                        return runners
        return payload
    if isinstance(payload, dict):
        for key in ("fields", "runners", "horses", "payLoad"):
            val = payload.get(key)
            if isinstance(val, list) and val:
                first = val[0]
                if isinstance(first, dict) and any(
                    k in first for k in ("name","runnerName","horseName","horseId","runnerId","HorseId","RunnerID","barrier","barrierNumber")
                ):
                    return val
        for key, val in payload.items():
            if isinstance(val, list) and val and isinstance(val[0], dict):
                return val
    return []


def extract_meetings_list(data) -> list:
    if not data:
        return []
    if isinstance(data, list):
        return data
    payload = data.get("payLoad", data) if isinstance(data, dict) else data
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("meetings", "meetingList", "meetingsList", "data"):
            val = payload.get(key)
            if isinstance(val, list) and val:
                return val
        for val in payload.values():
            if isinstance(val, list) and val:
                return val
    return []


def extract_races_from_meeting(data) -> list:
    if not data:
        return []
    payload = data.get("payLoad", data) if isinstance(data, dict) else data
    if isinstance(payload, list):
        if payload and isinstance(payload[0], dict):
            first = payload[0]
            for rkey in ("races","raceList","Races"):
                races = first.get(rkey, [])
                if races:
                    return races
            if any(k in first for k in ("raceNumber","raceName","number","name","raceNo")):
                return payload
    if isinstance(payload, dict):
        for key in ("races", "raceList", "Races"):
            val = payload.get(key)
            if isinstance(val, list) and val:
                return val
        for val in payload.values():
            if isinstance(val, list) and val:
                return val
    return []


def get_race_id(obj: dict) -> str:
    for f in ["raceId","RaceId","race_id","raceID","id"]:
        v = obj.get(f)
        if v and str(v).strip() not in ("","0","null","None"):
            return str(v).strip()
    return ""

def get_horse_id(obj: dict) -> str:
    for f in ["horseId","HorseId","horse_id","runnerId","RunnerID","horseid","runnerNumber"]:
        v = obj.get(f)
        if v and str(v).strip() not in ("","0","null","None"):
            return str(v).strip()
    name = obj.get("name") or obj.get("runnerName") or obj.get("horseName") or ""
    return str(name).strip() or ""

def get_meeting_name(obj: dict) -> str:
    track = obj.get("track") or {}
    return (track.get("name") if isinstance(track, dict) else None) or \
           obj.get("meetingName") or obj.get("venueName") or obj.get("trackName") or \
           obj.get("name") or "Unknown"

def get_meeting_state(obj: dict) -> str:
    track = obj.get("track") or {}
    state = (track.get("state") if isinstance(track, dict) else None) or \
            obj.get("state") or obj.get("meetingState") or ""
    return str(state).upper().strip()

def get_runner_name(obj: dict) -> str:
    return (obj.get("name") or obj.get("runnerName") or obj.get("horseName") or
            obj.get("horse") or obj.get("Horse") or "Unknown")


# ─── MEETINGS ────────────────────────────────────────────────────────────────
def fetch_meetings_fast(d: date) -> list:
    ds = pf_date(d)
    data = pf_get("form/meetingslist", {"meetingDate": ds})
    if not data:
        return []
    meetings = extract_meetings_list(data)
    enriched = []
    for m in meetings:
        m["_name"]  = get_meeting_name(m)
        m["_state"] = get_meeting_state(m)
        m["_date"]  = ds
        m["_races_loaded"] = False
        m["races"]  = []
        enriched.append(m)
    return enriched


def fetch_races_for_meeting(m: dict, d: date) -> list:
    ds   = pf_date(d)
    name = m.get("_name", "")
    mid  = str(m.get("meetingId") or m.get("id") or "")
    data = None
    if mid and mid not in ("0", ""):
        data = pf_get("form/meeting", {"meetingId": mid}, silent=True)
    if not data and name:
        data = pf_get("form/meeting", {"meetingDate": ds, "track": name}, silent=True)
    if not data:
        return []
    races = extract_races_from_meeting(data)
    for race in races:
        race.setdefault("_meetingName",  name)
        race.setdefault("_meetingState", m.get("_state",""))
        race.setdefault("_meetingDate",  ds)
        race.setdefault("_meetingId",    mid)
        race.setdefault("_dateObj",      d)
    return races


# ─── RUNNERS ────────────────────────────────────────────────────────────────
def fetch_race_field(race: dict) -> tuple:
    ds    = race.get("_meetingDate", "")
    track = race.get("_meetingName", "")
    rnum  = str(race.get("raceNumber") or race.get("number") or race.get("raceNo") or "1")
    rid   = get_race_id(race)
    debug = {"attempts": [], "raw_samples": []}

    def _try(endpoint, params, label):
        data = pf_get(endpoint, params, silent=True)
        runners = extract_runners_from_payload(data) if data else []
        debug["attempts"].append({
            "label": label, "endpoint": endpoint,
            "params": {k:v for k,v in params.items() if k!="apiKey"},
            "got_data": data is not None, "runners_found": len(runners),
            "top_keys": list(data.keys())[:8] if isinstance(data, dict) else (
                list(data[0].keys())[:8] if isinstance(data, list) and data and isinstance(data[0], dict) else []),
        })
        if data and not runners:
            debug["raw_samples"].append({"label": label, "sample": str(data)[:500]})
        return runners

    if rid:
        runners = _try("form/fields", {"raceId": rid}, f"fields?raceId={rid}")
        if runners: return runners, debug
    if ds and track and rnum:
        runners = _try("form/fields", {"meetingDate": ds, "track": track, "raceNumber": rnum},
                       f"fields?date={ds}&track={track}&raceNum={rnum}")
        if runners: return runners, debug
    if rid:
        runners = _try("form/form", {"raceId": rid}, f"form?raceId={rid}")
        if runners: return runners, debug
    if ds and track and rnum:
        runners = _try("form/form", {"meetingDate": ds, "track": track, "raceNumber": rnum},
                       f"form?date={ds}&track={track}&raceNum={rnum}")
        if runners: return runners, debug

    mid = race.get("_meetingId", "")
    if mid:
        data = pf_get("form/meeting", {"meetingId": mid}, silent=True)
    elif ds and track:
        data = pf_get("form/meeting", {"meetingDate": ds, "track": track}, silent=True)
    else:
        data = None

    if data:
        races = extract_races_from_meeting(data)
        for r in races:
            r_num = str(r.get("raceNumber") or r.get("number") or r.get("raceNo") or "")
            if r_num == rnum:
                for rkey in ("runners","fields","horses"):
                    embedded = r.get(rkey, [])
                    if embedded:
                        debug["attempts"].append({"label": f"meeting embed rnum={rnum}", "runners_found": len(embedded)})
                        return embedded, debug

    return [], debug


def fetch_form_for_race(race: dict) -> list:
    ds    = race.get("_meetingDate", "")
    track = race.get("_meetingName", "")
    rnum  = str(race.get("raceNumber") or race.get("number") or "1")
    rid   = get_race_id(race)
    # Only call with raceId if we have a valid non-zero one
    if rid and rid not in ("0", ""):
        data = pf_get("form/form", {"raceId": rid}, silent=True)
        rows = extract_runners_from_payload(data) if data else []
        if rows: return rows
    # Always try by date+track+raceNumber (silent to suppress 400 noise)
    if ds and track and rnum:
        data = pf_get("form/form", {"meetingDate": ds, "track": track, "raceNumber": rnum}, silent=True)
        rows = extract_runners_from_payload(data) if data else []
        if rows: return rows
    return []


def fetch_pf_ratings(race: dict) -> dict:
    ds    = race.get("_meetingDate", "")
    track = race.get("_meetingName", "")
    rnum  = str(race.get("raceNumber") or race.get("number") or "1")
    rid   = get_race_id(race)
    data = None
    if rid:
        data = pf_get("ratings/meetingratings", {"raceId": rid}, silent=True)
    if not data and ds and track:
        data = pf_get("ratings/meetingratings", {"meetingDate": ds, "track": track, "raceNumber": rnum}, silent=True)
    rows = extract_runners_from_payload(data) if data else []
    result = {}
    for row in rows:
        hid = get_horse_id(row)
        if hid: result[hid] = row
    return result


def fetch_sectionals(race: dict) -> dict:
    ds    = race.get("_meetingDate", "")
    track = race.get("_meetingName", "")
    rnum  = str(race.get("raceNumber") or race.get("number") or "1")
    rid   = get_race_id(race)
    data = None
    if rid:
        data = pf_get("ratings/meetingsectionals", {"raceId": rid}, silent=True)
    if not data and ds and track:
        data = pf_get("ratings/meetingsectionals", {"meetingDate": ds, "track": track, "raceNumber": rnum}, silent=True)
    rows = extract_runners_from_payload(data) if data else []
    result = {}
    for row in rows:
        hid = get_horse_id(row)
        if hid: result[hid] = row
    return result


# ─── RATING ENGINE ───────────────────────────────────────────────────────────
FACTOR_WEIGHTS = {
    "closing_speed": 24, "speed_rating": 16, "recent_form": 12,
    "class_differential": 9, "in_running_luck": 8, "pace_dynamics": 7,
    "weight_penalty": 5, "barrier_position": 4, "jt_combination": 6,
    "track_record": 5, "distance_record": 4,
}
MAX_SCORE = sum(FACTOR_WEIGHTS.values())
FACTOR_LBLS = {
    "closing_speed": "Closing Speed", "speed_rating": "Speed Rating",
    "recent_form": "Recent Form", "class_differential": "Class",
    "in_running_luck": "Unlucky", "pace_dynamics": "Pace Fit",
    "weight_penalty": "Weight", "barrier_position": "Barrier",
    "jt_combination": "J+T Combo", "track_record": "Track",
    "distance_record": "Distance",
}
TROUBLE_KEYWORDS = [
    ("no clear run",4.0),("held up",3.5),("blocked",3.5),("checked",3.0),
    ("traffic",3.0),("steadied",2.5),("interfered with",2.5),("interfered",2.0),
    ("bumped",2.0),("hampered",2.5),("crowded",2.0),("slow start",2.0),
    ("wide throughout",2.0),("wide",1.5),("stumbled",1.5),("lost ground",1.5),
    ("difficult run",2.0),("lack of room",3.0),
]

def _sectional_score(runner, past, secs):
    hid = get_horse_id(runner)
    sec = secs.get(hid, {})
    pf_sec = safe_float(sec.get("sectionalRating") or sec.get("closing600Rating") or 0)
    if pf_sec > 0:
        return round(min(max((pf_sec-60)/50*24,0),24),2)
    scores=[]
    for run in past[:7]:
        cs=safe_float(run.get("closingSectional") or run.get("closing600") or run.get("last600") or 0)
        if 0<cs<45:
            scores.append(max(0,min(24,(37-cs)/3.5*24))); continue
        pos=safe_float(run.get("finishingPosition",10))
        field=max(safe_float(run.get("numberOfRunners",10)),1)
        margin=safe_float(run.get("marginBeaten",20))
        scores.append(min(max(0,(1-(pos-1)/field))*16+max(0,(1-margin/12))*8 if pos!=1 else max(0,(1-(pos-1)/field))*16+8,24))
    if not scores:
        return round(min(max(safe_float(runner.get("winPct",0))/100*20,4),18),2)
    wts=[1.4,1.2,1.0,0.85,0.7,0.55,0.45][:len(scores)]
    return round(min(max(sum(s*w for s,w in zip(scores,wts))/sum(wts),0),24),2)

def _speed_score(runner, past):
    raw=safe_float(runner.get("speedRating") or runner.get("pfSpeedRating") or 0)
    if raw<=0:
        positions=[safe_float(r.get("finishingPosition",99)) for r in past[:5]]
        best=min(positions,default=8)
        field=max(safe_float((past[0] if past else {}).get("numberOfRunners",10)),1)
        return round(min(max(16*(1-(best-1)/field)*0.8,1),14),2)
    cls=safe_float(runner.get("raceClass") or 0)
    cls_adj=5 if cls>=95 else 3 if cls>=85 else 1 if cls>=75 else 0 if cls>=60 else -2 if cls<45 else 0
    going=(runner.get("going") or runner.get("trackCondition") or "").lower()
    going_adj=-4 if "heavy" in going else -2.5 if "soft" in going else -1.5 if "slow" in going else 0
    recency_pen=0
    if past:
        s=str(past[0].get("raceDate") or past[0].get("date") or "")[:10]
        try:
            ld=datetime.strptime(s,"%Y-%m-%d").date()
            days=(date.today()-ld).days
            recency_pen=-2 if days>90 else -1 if days>60 else 0
        except: pass
    return round(min(max((raw+cls_adj+going_adj+recency_pen-55)/65*16,0),16),2)

def _form_score(runner, past):
    if not past: return 5.0
    score=0.0; wts=[3.0,2.4,1.9,1.5,1.1,0.8,0.6]
    for i,run in enumerate(past[:7]):
        w=wts[i] if i<len(wts) else 0.4
        pos=safe_float(run.get("finishingPosition",99))
        field=max(safe_float(run.get("numberOfRunners",10)),1)
        if pos==1: score+=w*1.0
        elif pos==2: score+=w*0.72
        elif pos==3: score+=w*0.5
        elif pos<=max(4,field*0.4): score+=w*0.22
    lp=safe_float(past[0].get("finishingPosition",99))
    if lp==1: score+=1.8
    elif lp<=2: score+=1.0
    elif lp<=3: score+=0.5
    if len(past)<=2: score=score*0.7+12*0.3
    return round(min(max(score,0),12),2)

def _class_score(runner, past):
    cur=safe_float(runner.get("raceClass") or 0)
    if not past: return 4.5
    prev=[safe_float(r.get("raceClass",0)) for r in past[:5] if r.get("raceClass")]
    if not prev or cur==0: return 4.5
    return round(min(max(4.5+(sum(prev)/len(prev)-cur)*0.2,0),9),2)

def _unlucky_score(past):
    if not past: return 4.0
    score=4.0
    for i,run in enumerate(past[:4]):
        rm=1.4 if i==0 else 1.1 if i==1 else 0.9 if i==2 else 0.7
        comment=(run.get("raceComment") or run.get("comments") or "").lower()
        for kw,val in TROUBLE_KEYWORDS:
            if kw in comment: score+=val*rm*0.6; break
        if safe_float(run.get("positionAfterTurn") or 0)>=7 and safe_float(run.get("finishingPosition",99))<=3:
            score+=1.0*rm
    return round(min(max(score,0),8),2)

def _pace_score(runner, past, tempo="MODERATE"):
    pace_pos=safe_int(runner.get("pacePosition",3))
    score=3.5
    if tempo=="HOT": score+= 2.0 if pace_pos>=4 else 0.5 if pace_pos==3 else -1.5
    elif tempo=="SOFT": score+= 2.0 if pace_pos<=2 else 0.2 if pace_pos==3 else -1.0
    elif tempo=="GENUINE": score+= 0.5 if pace_pos==3 else 0
    for run in past[:4]:
        pe=safe_float(run.get("positionEarly") or run.get("firstPosition") or 5)
        pf_p=safe_float(run.get("finishingPosition",10))
        if pe>=5 and pf_p<=3: score+=0.6
        if pe<=2 and pf_p<=2: score+=0.4
    return round(min(max(score,0),7),2)

def _weight_score(runner):
    w=safe_float(runner.get("weightTotal") or runner.get("weightCarried") or runner.get("handicapWeight") or 57)
    dist=safe_float(runner.get("distance") or runner.get("raceDistance") or 1200)
    base=max(0,5-(w-54)*0.6)
    mult=1.4 if dist>=2400 else 1.2 if dist>=2000 else 1.1 if dist>=1600 else 0.9 if dist<=1100 else 1.0
    return round(min(max(base*mult,0),5),2)

def _barrier_score(runner):
    b=safe_float(runner.get("barrierNumber") or runner.get("barrier") or 8)
    dist=safe_float(runner.get("distance") or runner.get("raceDistance") or 1200)
    track=(runner.get("_meetingName") or runner.get("meetingName") or "").lower()
    if b<=0: return 2.0
    scale=0.38 if dist<=1400 else 0.28 if dist<=1800 else 0.18
    base=max(0,4-(b-1)*scale)
    if "flemington" in track and dist<=1400:
        base=(base*1.4) if b<=4 else (base*0.6)
    elif "caulfield" in track and dist<=1200:
        base=(base*1.25) if b<=5 else (base*0.8)
    elif "eagle farm" in track or "doomben" in track:
        base=(base*1.2) if b<=5 else (base*0.85)
    return round(min(max(base,0),4),2)

def _jt_score(runner):
    combo=runner.get("trainerJockeyA2E_Career") or {}
    runs=safe_float(combo.get("runners",0))
    if runs<5: return 3.0
    sr=safe_float(combo.get("strikeRate",0))/100
    a2e=safe_float(combo.get("a2E",0))
    plce=safe_float(combo.get("placeRate",0))/100
    score=(a2e*0.5+sr*0.3+plce*0.2)*6
    conf=min(1.0,runs/30)
    return round(min(max(score*conf+3.0*(1-conf),0),6),2)

def _track_score(runner, past):
    tr=runner.get("trackRecord") or {}
    ts=safe_float(tr.get("starts",0)); tw=safe_float(tr.get("firsts",0))
    tp=safe_float(tr.get("seconds",0))+safe_float(tr.get("thirds",0))
    if ts>=3:
        score=(tw/ts*0.65+(tw+tp)/ts*0.35)*5
        conf=min(1.0,ts/12)
        return round(min(max(score*conf+2.5*(1-conf),0),5),2)
    return 2.5

def _distance_score(runner, past):
    dr=runner.get("distanceRecord") or {}
    ds2=safe_float(dr.get("starts",0)); dw=safe_float(dr.get("firsts",0))
    dp=safe_float(dr.get("seconds",0))+safe_float(dr.get("thirds",0))
    if ds2>=3:
        score=(dw/ds2*0.65+(dw+dp)/ds2*0.35)*4
        conf=min(1.0,ds2/10)
        return round(min(max(score*conf+2.0*(1-conf),0),4),2)
    return 2.0

def rate_runner(runner, past=[], secs={}, tempo="MODERATE"):
    br={
        "closing_speed":      _sectional_score(runner,past,secs),
        "speed_rating":       _speed_score(runner,past),
        "recent_form":        _form_score(runner,past),
        "class_differential": _class_score(runner,past),
        "in_running_luck":    _unlucky_score(past),
        "pace_dynamics":      _pace_score(runner,past,tempo),
        "weight_penalty":     _weight_score(runner),
        "barrier_position":   _barrier_score(runner),
        "jt_combination":     _jt_score(runner),
        "track_record":       _track_score(runner,past),
        "distance_record":    _distance_score(runner,past),
    }
    br["composite"]=round(sum(br.values()),2)
    br["pct"]=round(br["composite"]/MAX_SCORE*100,1)
    return br


# ─── MARKET FRAMING ──────────────────────────────────────────────────────────
def frame_market(runners):
    priced=[(r, get_best_price(r)) for r in runners]
    priced=[(r,p) for r,p in priced if p>1.01]
    if len(priced)<2: return {}
    raw_sum=sum(1/p for _,p in priced)
    out={}
    for r,sp in priced:
        hid=get_horse_id(r); raw=1/sp; true=raw/raw_sum
        out[hid]={"sp":sp,"raw_pct":round(raw*100,2),"true_pct":round(true*100,2),
                  "fair_odds":round(1/true,2),"overround":round(raw_sum*100,1),
                  "source": price_source_label(r)}
    return out

def compute_model_prob(runner, rating, pf_r={}, past=[]):
    """
    Returns a raw (un-normalised) score for this runner.
    We purposely keep it proportional to winning probability rather than
    anchoring to an absolute %, because softmax normalisation in
    normalise_field() will handle the field-level constraint.
    """
    signals, weights = [], []

    # 1. PF AI model price — strongest signal when available
    pf_px = safe_float(pf_r.get("pfAiPrice") or pf_r.get("modelPrice") or 0)
    if pf_px > 1.0:
        signals.append(1.0 / pf_px)
        weights.append(5.0)

    # 2. Composite rating → softmax-ready score
    #    Use exponential transform so differences in rating are amplified
    #    (avoids the longshot bias of linear scaling)
    rat_pct = rating.get("pct", 50) / 100.0 if rating else 0.5
    # Scale: exp(rating * 3) keeps favourites appropriately dominant
    rat_signal = np.exp(rat_pct * 3.0)
    signals.append(rat_signal / np.exp(3.0))   # normalise against max=1
    weights.append(2.5)

    # 3. Career win% — calibrated form signal
    cw = safe_float(runner.get("winPct", 0)) / 100.0
    if cw > 0:
        signals.append(cw)
        weights.append(2.0)

    # 4. Track & distance records
    tr = runner.get("trackRecord") or {}
    ts = safe_float(tr.get("starts", 0)); tw2 = safe_float(tr.get("firsts", 0))
    if ts >= 3:
        signals.append(tw2 / ts)
        weights.append(1.5)

    dr = runner.get("distanceRecord") or {}
    ds2 = safe_float(dr.get("starts", 0)); dw = safe_float(dr.get("firsts", 0))
    if ds2 >= 3:
        signals.append(dw / ds2)
        weights.append(1.3)

    # 5. J+T A2E — only if statistically significant
    tj = runner.get("trainerJockeyA2E_Career") or {}
    tj_sr = safe_float(tj.get("strikeRate", 0)) / 100.0
    tj_a2e = safe_float(tj.get("a2E", 0))
    tj_runs = safe_float(tj.get("runners", 0))
    if tj_runs >= 15 and tj_a2e > 0:
        # A2E > 1.0 means J+T combo outperforms market expectations
        # Map: A2E=1.0→ neutral, A2E=1.5→ boost, A2E=0.5→ discount
        signals.append(min(tj_sr * tj_a2e, 0.6))
        weights.append(1.5)

    # 6. Days since last run — fitness curve
    days_penalty = 0.0
    if past:
        s = str(past[0].get("raceDate") or past[0].get("date") or "")[:10]
        try:
            ld = datetime.strptime(s, "%Y-%m-%d").date()
            days = (date.today() - ld).days
            if 14 <= days <= 21:
                days_penalty = 0.04     # peak fitness window — boost
            elif days <= 7:
                days_penalty = 0.01     # very recent — slight risk of fatigue
            elif days > 100:
                days_penalty = -0.06    # lengthy absence — discount
            elif days > 60:
                days_penalty = -0.03
        except:
            pass

    # 7. "Puncture" angle — last start beaten early, potential bounce-back
    #    Identifies horses that led/pressed but faded (ran too fast early)
    puncture_boost = 0.0
    if past and len(past) >= 1:
        last = past[0]
        ls_pos = safe_float(last.get("finishingPosition", 99))
        ls_early = safe_float(last.get("positionEarly") or last.get("firstPosition") or 0)
        ls_comment = (last.get("raceComment") or last.get("comments") or "").lower()
        # Was in top 3 early but finished 5+? → possible puncture
        if 0 < ls_early <= 3 and ls_pos >= 5:
            puncture_boost = 0.05
        # Comment clues
        puncture_keywords = ["tired", "weakened", "gave way", "peaked", "flattened", "not run on"]
        if any(k in ls_comment for k in puncture_keywords):
            puncture_boost = max(puncture_boost, 0.04)

    # 8. Weight impact — penalise heavy carriers in sprint/middle distances
    w_carried = safe_float(runner.get("weightTotal") or runner.get("weightCarried") or
                           runner.get("handicapWeight") or 57)
    dist = safe_float(runner.get("distance") or runner.get("raceDistance") or 1200)
    weight_penalty = 0.0
    if w_carried > 58 and dist >= 1200:
        # Each kg over 58 costs ~0.6% probability in relevant distances
        weight_penalty = -(w_carried - 58) * 0.006

    # Aggregate
    if not signals:
        base = 0.05
    else:
        total_w = sum(weights)
        base = sum(s * w for s, w in zip(signals, weights)) / total_w

    final = max(0.005, min(0.95, base + days_penalty + puncture_boost + weight_penalty))
    return round(final, 5), {
        "pf_signal": round(1.0/pf_px, 4) if pf_px > 1 else None,
        "rat_signal": round(rat_pct, 3),
        "career_win": round(cw, 3),
        "tj_a2e": round(tj_a2e, 2),
        "tj_runs": int(tj_runs),
        "days_penalty": round(days_penalty, 3),
        "puncture_boost": round(puncture_boost, 3),
        "weight_penalty": round(weight_penalty, 3),
        "base": round(base, 4),
        "final_raw": round(final, 5),
    }


def normalise_field(runners, ratings, pf_ratings, past_all={}):
    """
    True softmax normalisation:  p_h = exp(R_h) / Σ exp(R_i)
    This ensures probabilities sum to 1 and respects field-level competition.
    Returns both probs and per-runner reasoning dicts.
    """
    raw_scores, reasoning = {}, {}
    for r in runners:
        hid = get_horse_id(r)
        prob, reason = compute_model_prob(
            r,
            ratings.get(hid, {}),
            pf_ratings.get(hid, {}),
            past_all.get(hid, [])
        )
        raw_scores[hid] = prob
        reasoning[hid] = reason

    # Softmax over raw scores — use log-space for numerical stability
    scores_arr = np.array(list(raw_scores.values()), dtype=float)
    # Subtract max for numerical stability
    scores_arr = scores_arr - scores_arr.max()
    exp_arr = np.exp(scores_arr * 4.0)   # scale=4 keeps spread tight enough
    softmax_arr = exp_arr / exp_arr.sum()

    hids = list(raw_scores.keys())
    probs = {hid: round(float(p), 5) for hid, p in zip(hids, softmax_arr)}

    # Store reasoning in session state for display
    st.session_state["_model_reasoning"] = reasoning
    return probs


def compute_ev_metrics(model_prob: float, sp: float) -> dict:
    """
    Core EV equation:  EV = (P_win × net_profit) - (P_loss × stake)
    Assuming stake = $1:  EV = P_win × (sp-1) - P_loss × 1
    Also compute Kelly fraction and A/E-style diagnostics.
    """
    if sp <= 1.0 or model_prob <= 0:
        return {"ev": 0, "ev_pct": 0, "kelly_f": 0, "fair_odds": 0, "overlay_pct": 0}
    ev = model_prob * (sp - 1) - (1 - model_prob)
    fair_odds = round(1.0 / model_prob, 2)
    overlay_pct = round((sp - fair_odds) / fair_odds * 100, 1)   # how much above fair value
    kelly_f = max(0, (model_prob * (sp - 1) - (1 - model_prob)) / (sp - 1))
    return {
        "ev": round(ev, 4),
        "ev_pct": round(ev * 100, 1),
        "kelly_f": round(kelly_f, 4),
        "fair_odds": fair_odds,
        "overlay_pct": overlay_pct,
    }


def assess_value(model_prob, true_mkt_pct, sp, rating_pct, tj_a2e, min_rating, min_edge, min_tj_a2e):
    mkt = true_mkt_pct / 100.0
    edge = model_prob - mkt
    edge_pct = round(edge * 100, 1)
    ev_metrics = compute_ev_metrics(model_prob, sp)
    ev_unit = ev_metrics["ev"]
    overlay = ev_metrics["overlay_pct"]

    gates = {
        "edge":   edge > (min_edge / 100),
        "rating": rating_pct >= min_rating,
        "tj":     tj_a2e >= min_tj_a2e,
        "odds":   st.session_state.min_odds <= sp <= st.session_state.max_odds,
        "ev":     ev_unit > 0,   # NEW: must be +EV per dollar
    }
    bet = all(gates.values())
    reasons = []
    if not gates["edge"]:   reasons.append(f"Edge {edge_pct}% < min {min_edge}%")
    if not gates["rating"]: reasons.append(f"Rating {rating_pct}% < min {min_rating}%")
    if not gates["tj"]:     reasons.append(f"J+T A2E {round(tj_a2e,2)} < min {min_tj_a2e}")
    if not gates["odds"]:   reasons.append(f"Price ${sp} outside ${st.session_state.min_odds}–${st.session_state.max_odds}")
    if not gates["ev"]:     reasons.append(f"EV negative ({ev_metrics['ev_pct']:+.1f}%)")
    return {
        "bet": bet, "gates": gates,
        "edge_pct": edge_pct,
        "model_pct": round(model_prob * 100, 1),
        "market_pct": round(mkt * 100, 1),
        "ev_unit": round(ev_unit, 3),
        "ev_pct": ev_metrics["ev_pct"],
        "overlay_pct": overlay,
        "kelly_f": ev_metrics["kelly_f"],
        "fair_odds": ev_metrics["fair_odds"],
        "reasons": reasons,
    }


def detect_angles(runner: dict, past: list, tempo_info: dict, secs: dict) -> list:
    """
    Returns a list of angle dicts: {"label", "detail", "strength": 1-3}
    strength 3 = strong positive, 1 = mild
    """
    angles = []
    hid = get_horse_id(runner)
    name = get_runner_name(runner)
    dist = safe_float(runner.get("distance") or runner.get("raceDistance") or 1200)

    if not past:
        return angles

    last = past[0]
    ls_pos = safe_float(last.get("finishingPosition", 99))
    ls_early = safe_float(last.get("positionEarly") or last.get("firstPosition") or 0)
    ls_comment = (last.get("raceComment") or last.get("comments") or "").lower()
    ls_dist = safe_float(last.get("raceDistance") or 0)

    # 1. PUNCTURE ANGLE — ran fast early, tired, racing back to soft tempo
    if 0 < ls_early <= 3 and ls_pos >= 5:
        tempo = tempo_info.get("tempo", "MODERATE")
        if tempo in ("SOFT", "MODERATE"):
            angles.append({
                "label": "Puncture Bounce",
                "detail": f"Led/pressed last start (pos {int(ls_early)}) but faded to {int(ls_pos)}. Today's {tempo.lower()} tempo suits — can roll forward unchallenged.",
                "strength": 3,
                "icon": "🔁"
            })
        else:
            angles.append({
                "label": "Puncture (Hot Pace Risk)",
                "detail": f"Pressed last start and tired. Today's HOT tempo may repeat the pattern — watch sectionals.",
                "strength": 1,
                "icon": "⚠️"
            })

    # 2. UNLUCKY LAST START
    trouble_found = []
    for kw, _ in TROUBLE_KEYWORDS[:8]:
        if kw in ls_comment:
            trouble_found.append(kw)
            break
    if trouble_found and ls_pos >= 4:
        angles.append({
            "label": "Unlucky Last Start",
            "detail": f"Comment mentions '{trouble_found[0]}' — finished {int(ls_pos)}{['st','nd','rd'][int(ls_pos)-1] if int(ls_pos)<=3 else 'th'}. Hidden merit warrants upgrade.",
            "strength": 2,
            "icon": "🍀"
        })

    # 3. DISTANCE DROP — stepping back from longer race
    if ls_dist > 0 and dist < ls_dist * 0.88:
        angles.append({
            "label": "Distance Drop",
            "detail": f"Steps back from {int(ls_dist)}m to {int(dist)}m — typically suits on-pace runners with tactical speed.",
            "strength": 2,
            "icon": "📏"
        })

    # 4. WEIGHT RELIEF
    w_now = safe_float(runner.get("weightTotal") or runner.get("weightCarried") or 57)
    w_last = safe_float(last.get("weightCarried") or 0)
    if w_last > 0 and w_now < w_last - 1.5:
        angles.append({
            "label": "Weight Relief",
            "detail": f"Carries {w_now}kg today vs {w_last}kg last start — {round(w_last-w_now,1)}kg lighter. Meaningful advantage at {int(dist)}m.",
            "strength": 2 if (w_last - w_now) >= 3 else 1,
            "icon": "⚖️"
        })

    # 5. FRESH HORSE — first-up after 60+ day spell with good record
    s = str(last.get("raceDate") or last.get("date") or "")[:10]
    try:
        ld = datetime.strptime(s, "%Y-%m-%d").date()
        days = (date.today() - ld).days
        if days > 60:
            tr = runner.get("trackRecord") or {}
            # Check if trainer has a strong first-up record (approximate via career win%)
            cw = safe_float(runner.get("winPct", 0))
            if cw >= 20:
                angles.append({
                    "label": f"Fresh Runner ({days}d spell)",
                    "detail": f"Off a {days}-day break. Career win% of {cw:.0f}% suggests horse returns fit — watch market drift for trainer confidence.",
                    "strength": 2 if days < 120 else 1,
                    "icon": "💤"
                })
        elif 14 <= days <= 21:
            angles.append({
                "label": "Peak Fitness Window",
                "detail": f"Runs {days} days since last start — sits in the optimal 14–21 day fitness cycle.",
                "strength": 1,
                "icon": "✅"
            })
    except:
        pass

    # 6. SECTIONAL CLOSER — strong closing speed, suits hot pace
    sec_d = secs.get(hid, {})
    sec_rtg = safe_float(sec_d.get("sectionalRating") or sec_d.get("closing600Rating") or 0)
    if sec_rtg > 80 and tempo_info.get("tempo") == "HOT":
        angles.append({
            "label": "Elite Closer in Hot Pace",
            "detail": f"Sectional rating {sec_rtg:.0f} — top-tier closing speed. HOT tempo setup is ideal.",
            "strength": 3,
            "icon": "🚀"
        })

    return angles


# ─── SPEEDMAP ────────────────────────────────────────────────────────────────
PACE_POSITIONS={1:"Leader",2:"On Pace",3:"Midfield",4:"Back",5:"Rear"}
PACE_COLORS={"Leader":"var(--stop)","On Pace":"var(--warn)","Midfield":"var(--sap-mid)",
              "Back":"var(--mist)","Rear":"var(--mist)"}

def assign_pace_positions(runners):
    for r in runners:
        if not r.get("pacePosition"):
            b=safe_float(r.get("barrierNumber") or r.get("barrier") or 8)
            r["pacePosition"]=1 if b<=3 else 2 if b<=6 else 3 if b<=10 else 4
    return runners

def classify_tempo(runners):
    leaders=[r for r in runners if safe_int(r.get("pacePosition",3))==1]
    on_pace=[r for r in runners if safe_int(r.get("pacePosition",3))==2]
    n=len(leaders)
    if n>=3: return {"tempo":"HOT","pill":"pill-red","desc":"Multiple leaders — burn-up likely. Favours closers.","strategy":"Back midfield-to-rear runners with closing ability."}
    elif n==2: return {"tempo":"GENUINE","pill":"pill-amber","desc":"Two leaders — honest tempo. All running styles viable.","strategy":"Slight lean toward on-pace runners."}
    elif n==1 and len(on_pace)<=1: return {"tempo":"SOFT","pill":"pill-blue","desc":"Single uncontested leader — significant front-runner advantage.","strategy":"Favour the leader and nearest pursuer (draw ≤5)."}
    else: return {"tempo":"MODERATE","pill":"pill-muted","desc":"Balanced dynamics — no dominant pace factor.","strategy":"Rate on ability and class."}


# ─── STAKING ─────────────────────────────────────────────────────────────────
def kelly_criterion(bank, prob, odds, fraction):
    b=odds-1
    if b<=0 or prob<=0 or prob>=1: return 0.0
    return bank*fraction*max((b*prob-(1-prob))/b,0)

def compute_stake(bank, model_prob, sp, method, kf, flat_pct, level_amt, max_pct):
    edge=model_prob-(1/sp if sp>1 else 0)
    if method=="Quarter Kelly":  stake=kelly_criterion(bank,model_prob,sp,0.25)
    elif method=="Half Kelly":   stake=kelly_criterion(bank,model_prob,sp,0.50)
    elif method=="Full Kelly":   stake=kelly_criterion(bank,model_prob,sp,1.0)
    elif method=="Flat %":       stake=bank*flat_pct/100 if edge>0 else 0
    elif method=="Level":        stake=level_amt if edge>0 else 0
    else: stake=0
    stake=min(round(stake,2),round(bank*max_pct/100,2))
    if stake<=0: return {"stake":0,"ev":0,"ev_pct":0,"pct_bank":0,"roi_required":0}
    ev=round((model_prob*(sp-1)-(1-model_prob))*stake,2)
    return {"stake":stake,"ev":ev,"ev_pct":round(ev/stake*100,1) if stake else 0,
            "pct_bank":round(stake/bank*100,1) if bank else 0,
            "roi_required":round((1/model_prob-1)*100,1)}


# ─── BET LOG ─────────────────────────────────────────────────────────────────
def add_bet(horse, race, stake, odds, edge_pct, model_pct):
    st.session_state.bet_log.append({"dt":datetime.now().strftime("%d/%m %H:%M"),
        "horse":horse,"race":race,"stake":round(stake,2),"odds":odds,
        "edge":edge_pct,"model_pct":model_pct,"result":"Pending","pl":0.0})

def settle(idx, result):
    b=st.session_state.bet_log[idx]
    pl=b["stake"]*(b["odds"]-1) if result=="Won" else -b["stake"]
    st.session_state.bet_log[idx].update({"result":result,"pl":round(pl,2)})
    st.session_state.bank=round(st.session_state.bank+pl,2)

def bankroll_stats():
    settled=[b for b in st.session_state.bet_log if b["result"]!="Pending"]
    if not settled: return {}
    staked=sum(b["stake"] for b in settled); pl=sum(b["pl"] for b in settled)
    winners=[b for b in settled if b["result"]=="Won"]
    run=peak=0; dds=[]
    for b in settled:
        run+=b["pl"]; peak=max(peak,run); dds.append(run-peak)
    return {"n":len(settled),"winners":len(winners),"sr":round(len(winners)/len(settled)*100,1),
            "staked":round(staked,2),"pl":round(pl,2),"roi":round(pl/staked*100,1) if staked else 0,
            "avg_odds":round(sum(b["odds"] for b in settled)/len(settled),2),
            "max_dd":round(min(dds),2),"bank":round(st.session_state.bank,2),
            "peak":round(st.session_state.starting_bank+peak,2)}


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand-header">
      <div class="brand-logo">🏇 Racing Edge</div>
      <div class="brand-sub">PuntingForm API v2 · Live Odds</div>
      <span class="brand-version">v3.0.0</span>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sb-section">API Connection</div>', unsafe_allow_html=True)
    try: secret_key = st.secrets.get("PUNTINGFORM_API_KEY","")
    except: secret_key=""

    api_key=st.text_input("API Key",type="password",
        value=st.session_state.api_key or secret_key,
        placeholder="Paste PuntingForm API key...")
    if api_key!=st.session_state.api_key:
        st.session_state.api_key=api_key
        st.session_state.meetings=[]

    if st.session_state.api_key:
        st.markdown('<div class="status-ok">Connected</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-err">No key entered</div>',unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Race Selection</div>',unsafe_allow_html=True)
    race_date=st.date_input("Date",value=date.today())

    AU_STATES=["NSW","VIC","QLD","SA","WA","TAS","NT","ACT"]
    state_filter=st.multiselect("Filter by State",AU_STATES,placeholder="All states")

    fetch_clicked=st.button("🔍  Fetch Meetings",use_container_width=True)

    if fetch_clicked:
        if not st.session_state.api_key:
            st.error("Enter API key first.")
        else:
            with st.spinner(f"Fetching {pf_date(race_date)}..."):
                meetings=fetch_meetings_fast(race_date)
            st.session_state.meetings=meetings
            st.session_state.fetch_count=len(meetings)
            st.session_state.fetch_status="ok" if meetings else "empty"

    if st.session_state.fetch_status=="ok":
        n=st.session_state.fetch_count
        st.markdown(
            f'<div style="background:rgba(26,140,78,.1);border:1px solid rgba(26,140,78,.3);border-radius:8px;padding:10px 14px;margin-top:8px">'
            f'<div style="color:#4ade80;font-family:\'DM Mono\',monospace;font-size:.78rem;font-weight:600">'
            f'✓ {n} meeting{"s" if n!=1 else ""} loaded</div>'
            f'<div style="color:#86efac;font-family:\'DM Mono\',monospace;font-size:.66rem;margin-top:2px">{pf_date(race_date)}</div>'
            f'</div>',unsafe_allow_html=True)
    elif st.session_state.fetch_status=="empty":
        st.markdown(
            '<div style="background:rgba(176,106,0,.1);border:1px solid rgba(176,106,0,.3);border-radius:8px;padding:10px 14px;margin-top:8px">'
            '<div style="color:#fb923c;font-family:\'DM Mono\',monospace;font-size:.78rem">⚠ No meetings found</div>'
            '</div>',unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Staking</div>',unsafe_allow_html=True)
    st.session_state.bank=st.number_input("Bankroll ($)",value=float(st.session_state.bank),step=50.0,min_value=1.0)
    if st.session_state.starting_bank==1000.0 and st.session_state.bank!=1000.0:
        st.session_state.starting_bank=st.session_state.bank
    st.session_state.staking_method=st.selectbox("Method",
        ["Quarter Kelly","Half Kelly","Full Kelly","Flat %","Level"],
        index=["Quarter Kelly","Half Kelly","Full Kelly","Flat %","Level"].index(st.session_state.staking_method))
    if st.session_state.staking_method=="Flat %":
        st.session_state.flat_pct=st.slider("% of Bank",0.5,10.0,st.session_state.flat_pct,0.5)
    elif st.session_state.staking_method=="Level":
        st.session_state.level_stake=st.number_input("Fixed Stake ($)",value=st.session_state.level_stake,step=5.0)
    st.session_state.max_stake_pct=st.slider("Max Stake % of Bank",1.0,20.0,st.session_state.max_stake_pct,0.5)

    st.markdown('<div class="sb-section">Bet Filters</div>',unsafe_allow_html=True)
    st.session_state.min_odds=st.number_input("Min Odds",value=st.session_state.min_odds,step=0.5,min_value=1.01)
    st.session_state.max_odds=st.number_input("Max Odds",value=st.session_state.max_odds,step=5.0)
    st.session_state.min_rating=st.slider("Min Rating %",0,100,st.session_state.min_rating)
    st.session_state.min_edge=st.slider("Min Edge %",0.0,20.0,st.session_state.min_edge,0.5)
    st.session_state.min_tj_a2e=st.slider("Min J+T A2E",0.0,2.5,st.session_state.min_tj_a2e,0.1)

    if st.session_state.bet_log:
        bpct=st.session_state.bank/st.session_state.starting_bank*100 if st.session_state.starting_bank else 100
        clr="#4ade80" if bpct>=100 else "#fb923c" if bpct>=85 else "#f87171"
        st.markdown(
            f'<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:14px 16px;margin-top:14px">'
            f'<div style="font-family:\'DM Mono\',monospace;font-size:.62rem;color:#64748b;text-transform:uppercase;letter-spacing:.1em;margin-bottom:7px">Bankroll</div>'
            f'<div style="font-family:\'DM Mono\',monospace;font-size:1.5rem;font-weight:700;color:#f1f5f9">${st.session_state.bank:.0f}</div>'
            f'<div style="font-family:\'DM Mono\',monospace;font-size:.72rem;color:{clr};margin-top:4px">{bpct-100:+.1f}% vs start</div>'
            f'</div>',unsafe_allow_html=True)


# ─── TABS ─────────────────────────────────────────────────────────────────────
TAB_RACES, TAB_ANALYSIS, TAB_STAKING, TAB_BANKROLL, TAB_DEBUG = st.tabs([
    "🏟  Meetings & Races","📊  Race Analysis","💰  Staking & Bets","📈  Bankroll","🔧  Debug"
])


# ════════════════════════════════════════════════════════════════
# TAB 1 — MEETINGS & RACES
# ════════════════════════════════════════════════════════════════
with TAB_RACES:
    st.markdown("""<div class="page-header"><div>
      <div class="page-eyebrow">Today's Card</div>
      <div class="page-title">Meetings & Races</div>
    </div></div>""",unsafe_allow_html=True)

    if not st.session_state.api_key:
        st.markdown('<div class="alert alert-amber">Enter your PuntingForm API key in the sidebar to begin.</div>',unsafe_allow_html=True)
    elif not st.session_state.meetings:
        st.markdown("""<div class="empty-state">
          <div class="empty-icon">🏇</div>
          <div class="empty-title">No meetings loaded</div>
          <div class="empty-sub">Select a date and click "Fetch Meetings" in the sidebar.</div>
        </div>""",unsafe_allow_html=True)

    meetings=st.session_state.meetings
    if meetings:
        total_loaded=sum(len(m.get("races",[])) for m in meetings if m.get("_races_loaded"))
        st.markdown(
            f'<div class="card-brass" style="display:flex;align-items:center;gap:28px;margin-bottom:22px">'
            f'<div><div class="dl-label">Meetings</div><div class="dl-value c-brass">{len(meetings)}</div></div>'
            f'<div style="width:1px;height:32px;background:var(--brass-l)"></div>'
            f'<div><div class="dl-label">Date</div><div class="dl-value c-brass" style="font-size:.9rem">{pf_date(race_date)}</div></div>'
            f'<div style="width:1px;height:32px;background:var(--brass-l)"></div>'
            f'<div><div class="dl-label">Races loaded</div><div class="dl-value c-brass">{total_loaded}</div></div>'
            f'</div>',unsafe_allow_html=True)

        state_pill_map={"NSW":"pill-blue","VIC":"pill-blue","QLD":"pill-brass",
                        "SA":"pill-green","WA":"pill-green","TAS":"pill-muted",
                        "NT":"pill-amber","ACT":"pill-muted"}

        for mi, meeting in enumerate(meetings):
            name  = meeting.get("_name","Unknown")
            state = meeting.get("_state","")
            cond  = meeting.get("trackCondition") or meeting.get("going") or ""

            if state_filter and state.upper() not in [s.upper() for s in state_filter]:
                continue

            state_pill=state_pill_map.get(state.upper(),"pill-muted")
            races_loaded=meeting.get("_races_loaded",False)
            races=meeting.get("races",[])
            n_races=len(races)
            exp_label=f"{name}  ·  {state}  {'·  ' + str(n_races) + ' races' if races_loaded else '(click to load)'}"

            with st.expander(exp_label,expanded=False):
                if not races_loaded:
                    with st.spinner(f"Loading races for {name}..."):
                        races=fetch_races_for_meeting(meeting, race_date)
                        meeting["races"]=races
                        meeting["_races_loaded"]=True
                        st.session_state.meetings[mi]=meeting
                    if not races:
                        st.markdown(f'<div class="alert alert-red">No races returned for {name}. Check Debug tab for API log.</div>',unsafe_allow_html=True)
                        continue

                meta_html=(f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;'
                           f'padding-bottom:14px;border-bottom:1px solid var(--ghost)">'
                           f'<span class="pill {state_pill}">{state}</span>')
                if cond: meta_html+=f'<span class="pill pill-muted">{cond}</span>'
                meta_html+=f'<span class="pill pill-ink">{len(races)} races</span></div>'
                st.markdown(meta_html,unsafe_allow_html=True)

                valid_races=[r for r in races if r.get("raceName") or r.get("raceNumber") or r.get("number")]
                if not valid_races:
                    st.markdown('<div class="alert alert-amber">Race list returned but no races have names or numbers. Check Debug tab.</div>',unsafe_allow_html=True)
                    continue

                for race in valid_races:
                    rnum=race.get("raceNumber") or race.get("number") or "?"
                    rname=race.get("raceName") or race.get("name") or f"Race {rnum}"
                    rdist=race.get("raceDistance") or race.get("distance") or "?"
                    rtime=race.get("startTime") or race.get("raceTime") or ""
                    rcls=race.get("raceClass") or race.get("class") or ""
                    rid=get_race_id(race)
                    time_str=""
                    if rtime:
                        try:
                            t=str(rtime)
                            t=t.split("T")[1][:5] if "T" in t else t[:5]
                            time_str=t
                        except: time_str=str(rtime)[:5]

                    c1,c2=st.columns([8,1])
                    with c1:
                        st.markdown(
                            f'<div class="race-row">'
                            f'<div class="race-num">R{rnum}</div>'
                            f'<div style="flex:1;margin-left:12px">'
                            f'<div class="race-name">{rname}</div>'
                            f'<div class="race-meta">'
                            f'{time_str + "  ·  " if time_str else ""}{rdist}m'
                            f'{("  ·  "+str(rcls)) if rcls else ""}'
                            f'{("  ·  #"+rid) if rid else ""}'
                            f'</div></div></div>',unsafe_allow_html=True)
                    with c2:
                        btn_key=f"load_{mi}_{rnum}_{rid}"
                        if st.button("Load",key=btn_key,use_container_width=True):
                            st.session_state.selected_race=race
                            st.session_state.runners=[]
                            st.session_state.ratings={}
                            st.session_state.pf_ratings={}
                            st.session_state.sectionals={}
                            st.session_state.past_form_by_horse={}
                            st.session_state["_live_prices"]={}
                            st.session_state["_live_prices_ts"]=None

                            with st.spinner(f"Loading runners for R{rnum} {name}..."):
                                runners, dbg=fetch_race_field(race)
                                st.session_state["_last_field_debug"]=dbg
                                if runners:
                                    st.session_state.runners=assign_pace_positions(runners)
                                    # Auto-fetch live prices
                                    prices, source = refresh_live_prices(race, race_date)
                                    n_prices = len(prices)
                                    price_msg = f" · {n_prices} live prices from {source}" if n_prices else " · Live prices unavailable (will use SP)"
                                    st.success(f"✓ {len(runners)} runners loaded{price_msg} — go to Race Analysis tab")
                                else:
                                    st.error("❌ No runners returned. See details below and check Debug tab.")
                                    for a in dbg.get("attempts",[]):
                                        status="✓" if a.get("runners_found",0)>0 else "✗"
                                        st.markdown(f'<div class="debug-box">{status} {a["label"]} → data={a.get("got_data","?")} runners={a.get("runners_found",0)} keys={a.get("top_keys",[])}</div>',unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# TAB 2 — RACE ANALYSIS
# ════════════════════════════════════════════════════════════════
with TAB_ANALYSIS:
    race=st.session_state.selected_race
    runners=st.session_state.runners

    if not race:
        st.markdown("""<div class="empty-state">
          <div class="empty-icon">📊</div>
          <div class="empty-title">No race selected</div>
          <div class="empty-sub">Go to Meetings & Races and click Load on any race.</div>
        </div>""",unsafe_allow_html=True)
        st.stop()

    if not runners:
        st.markdown('<div class="alert alert-amber">No runners loaded. Click Load on a race in the Meetings tab.</div>',unsafe_allow_html=True)
        st.stop()

    rname=race.get("raceName") or race.get("name") or "Race"
    rdist=race.get("raceDistance") or race.get("distance") or "?"
    rtrk=race.get("_meetingName") or race.get("meetingName") or ""
    rcond=race.get("trackCondition") or race.get("going") or ""
    rcls=race.get("raceClass") or ""
    rnum=race.get("raceNumber") or race.get("number") or "?"
    rid=get_race_id(race)
    rds=race.get("_meetingDate","")
    rdate_obj=race.get("_dateObj", race_date)

    # ── Race header ──
    live_ts=st.session_state.get("_live_prices_ts")
    live_src=st.session_state.get("_live_source","")
    live_age=""
    if live_ts:
        secs=(datetime.now()-live_ts).seconds
        live_age=f"{secs//60}m ago" if secs>=60 else f"{secs}s ago"

    header_right=""
    if live_ts:
        header_right=(f'<div style="text-align:right">'
                      f'<div class="live-price"><span class="live-dot"></span>Live odds · {live_src}</div>'
                      f'<div style="font-family:\'DM Mono\',monospace;font-size:.66rem;color:var(--mist);margin-top:3px">Updated {live_age}</div></div>')
    else:
        header_right='<span class="pill pill-amber">SP only</span>'

    cls_pill = f'<span class="pill pill-muted">{rcls}</span>' if rcls else ''
    cond_pill = f'<span class="pill pill-muted">{rcond}</span>' if rcond else ''
    st.markdown(
        f'<div class="page-header">'
        f'<div>'
        f'<div class="page-eyebrow">{rtrk} · {rds}</div>'
        f'<div class="page-title">Race {rnum} — {rname}</div>'
        f'<div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">'
        f'<span class="pill pill-ink">{len(runners)} runners</span>'
        f'<span class="pill pill-muted">{rdist}m</span>'
        f'{cls_pill}{cond_pill}'
        f'</div>'
        f'</div>'
        f'{header_right}'
        f'</div>',
        unsafe_allow_html=True)

    # ── Controls bar ──
    col_rate, col_odds, col_space = st.columns([2, 2, 6])
    with col_rate:
        run_ratings=st.button("⚡  Run Full Analysis",use_container_width=True)
    with col_odds:
        if st.button("🔄  Refresh Live Odds",use_container_width=True):
            prices, source = refresh_live_prices(race, rdate_obj)
            if prices:
                st.success(f"✓ {len(prices)} prices from {source}")
            else:
                st.warning("No live prices returned — check Debug. SP fallback active.")

    if run_ratings:
        ratings_new={}; pf_new={}; secs_new={}; past_by_hid={}
        prog=st.progress(0); status=st.empty()
        status.markdown('<div class="alert alert-blue">Fetching past form...</div>',unsafe_allow_html=True)
        past_rows=fetch_form_for_race(race)
        for row in past_rows:
            hid=get_horse_id(row)
            if hid: past_by_hid.setdefault(hid,[]).append(row)
        prog.progress(0.25)
        status.markdown('<div class="alert alert-blue">Fetching PF AI ratings...</div>',unsafe_allow_html=True)
        pf_new=fetch_pf_ratings(race)
        prog.progress(0.45)
        status.markdown('<div class="alert alert-blue">Fetching sectionals...</div>',unsafe_allow_html=True)
        secs_new=fetch_sectionals(race)
        prog.progress(0.60)
        tempo_str=classify_tempo(runners)["tempo"]
        status.markdown('<div class="alert alert-blue">Computing ratings...</div>',unsafe_allow_html=True)
        for i,runner in enumerate(runners):
            hid=get_horse_id(runner)
            ratings_new[hid or f"_idx{i}"]=rate_runner(runner,past_by_hid.get(hid,[]),secs_new,tempo_str)
            prog.progress(0.60+0.40*(i+1)/len(runners))
        st.session_state.ratings=ratings_new
        st.session_state.pf_ratings=pf_new
        st.session_state.sectionals=secs_new
        st.session_state.past_form_by_horse=past_by_hid
        prog.empty(); status.empty()
        msgs=[f"✓ Rated {len(runners)} runners"]
        if past_by_hid: msgs.append(f"{len(past_by_hid)} with past form")
        if pf_new: msgs.append(f"{len(pf_new)} PF AI ratings")
        if secs_new: msgs.append(f"{len(secs_new)} sectionals")
        if not pf_new: msgs.append("PF AI unavailable — check subscription tier")
        st.success("  ·  ".join(msgs))

    ratings=st.session_state.ratings
    pf_ratings=st.session_state.pf_ratings
    secs=st.session_state.sectionals
    past_all=st.session_state.past_form_by_horse
    mkt=frame_market(runners)
    tempo_info=classify_tempo(runners)
    field_probs=normalise_field(runners,ratings,pf_ratings,past_all) if ratings else {}

    # ══ SPEEDMAP ══
    st.markdown('<div class="section-hdr">Speedmap & Pace Dynamics</div>',unsafe_allow_html=True)
    tc={"HOT":"pill-red","GENUINE":"pill-amber","SOFT":"pill-blue","MODERATE":"pill-muted"}.get(tempo_info["tempo"],"pill-muted")
    st.markdown(
        f'<div class="tempo-banner">'
        f'<span class="pill {tc}" style="font-size:.72rem;padding:5px 14px;flex-shrink:0;font-weight:800">{tempo_info["tempo"]}</span>'
        f'<div><div style="font-size:.9rem;color:var(--ink-3);font-weight:600">{tempo_info["desc"]}</div>'
        f'<div style="font-size:.78rem;color:var(--steel);margin-top:3px">Strategy: {tempo_info["strategy"]}</div></div>'
        f'</div>',unsafe_allow_html=True)

    positions={1:[],2:[],3:[],4:[],5:[]}
    for r in runners:
        pp=safe_int(r.get("pacePosition",3))
        positions[min(max(pp,1),5)].append(get_runner_name(r))
    for pp,lbl in PACE_POSITIONS.items():
        horses=positions.get(pp,[])
        if not horses: continue
        color=PACE_COLORS.get(lbl,"var(--mist)")
        st.markdown(
            f'<div class="smap-row">'
            f'<div class="smap-pos" style="color:{color}">{lbl}</div>'
            f'<div class="smap-horses">{" · ".join(horses)}</div>'
            f'<div class="smap-cnt">{len(horses)}</div>'
            f'</div>',unsafe_allow_html=True)

    st.markdown('<hr>',unsafe_allow_html=True)

    # ══ MARKET TABLE ══
    st.markdown('<div class="section-hdr">Market Frame</div>',unsafe_allow_html=True)

    # Live price status banner
    live_prices=st.session_state.get("_live_prices",{})
    n_live=len(live_prices)
    if n_live>0:
        st.markdown(
            f'<div class="alert alert-green" style="display:flex;align-items:center;gap:8px">'
            f'<span class="live-dot" style="flex-shrink:0"></span>'
            f'<strong>{n_live} live prices loaded</strong> from {live_src}  ·  Edge calculated against de-vigged live market'
            f'</div>',unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="alert alert-amber">⚠ No live prices — showing SP fallback. Click "Refresh Live Odds" for current prices.</div>',
            unsafe_allow_html=True)

    if not mkt:
        st.markdown('<div class="alert alert-amber">No prices available yet. Click "Refresh Live Odds" or wait for prices to be published.</div>',unsafe_allow_html=True)
    else:
        sample=next(iter(mkt.values()))
        overround=sample["overround"]
        st.markdown(
            f'<div class="card-blue" style="font-size:.8rem;color:var(--sap);margin-bottom:16px;display:flex;align-items:center;gap:20px">'
            f'<div><span style="color:var(--mist)">Book overround</span> <strong style="color:var(--ink)">{overround}%</strong></div>'
            f'<div><span style="color:var(--mist)">True%</span> = de-vigged probability</div>'
            f'<div><span style="color:var(--mist)">Edge</span> = Model% minus True%</div>'
            f'</div>',unsafe_allow_html=True)

        sorted_by_sp=sorted(runners,key=lambda x: get_best_price(x) or 99)
        rows=""
        for rank,r in enumerate(sorted_by_sp):
            hid=get_horse_id(r); mf=mkt.get(hid)
            if not mf: continue
            name=get_runner_name(r)
            sp=mf["sp"]; raw=mf["raw_pct"]; true=mf["true_pct"]; fair=mf["fair_odds"]
            src=mf.get("source","sp")
            mp=field_probs.get(hid,0)
            pfr=pf_ratings.get(hid,{}); pf_px=safe_float(pfr.get("pfAiPrice") or 0)
            diff=round(mp*100-true,1) if mp else None
            is_val=diff is not None and diff>0
            edge_html="—"
            if diff is not None:
                cls="edge-pos" if diff>0 else "edge-neg" if diff<0 else "edge-neu"
                edge_html=f'<span class="{cls}">{("+" if diff>=0 else "")}{diff}%</span>'
            bar_w=min(int(true*3.5),100)
            bar_c="#1a8c4e" if is_val else "#2255cc"
            bar_html=f'<div class="prob-bar" style="width:60px"><div class="prob-fill" style="width:{bar_w}%;background:{bar_c}"></div></div>'
            badges=""
            if rank==0: badges+='<span class="mkt-badge badge-fav">Fav</span>'
            if is_val: badges+='<span class="mkt-badge badge-val">Value</span>'
            if src=="live": badges+='<span class="mkt-badge badge-live">Live</span>'
            pf_cell=f"${pf_px:.2f}" if pf_px>1 else "—"
            mp_cell=f"{mp*100:.1f}%" if mp else "—"
            row_cls="val-row" if is_val else ("fav-row" if rank==0 else "")
            rows+=(f'<tr class="{row_cls}">'
                   f'<td style="color:var(--mist);font-size:.72rem">{rank+1}</td>'
                   f'<td><span class="mkt-horse">{name}</span>{badges}</td>'
                   f'<td style="color:var(--sap);font-weight:700">${sp:.2f}</td>'
                   f'<td style="color:var(--steel)">{raw}%</td>'
                   f'<td><div style="display:flex;align-items:center;gap:8px"><span style="font-weight:600">{true}%</span>{bar_html}</div></td>'
                   f'<td style="color:var(--ink-3)">${fair:.2f}</td>'
                   f'<td style="color:var(--sap)">{pf_cell}</td>'
                   f'<td style="color:var(--sap-mid)">{mp_cell}</td>'
                   f'<td>{edge_html}</td></tr>')

        st.markdown(
            f'<div class="mkt-wrap"><table class="mkt-table">'
            f'<thead><tr><th>#</th><th>Horse</th><th>Price</th><th>Raw%</th>'
            f'<th>True%</th><th>Fair Odds</th><th>PF AI</th><th>Model%</th><th>Edge</th>'
            f'</tr></thead><tbody>{rows}</tbody></table></div>',unsafe_allow_html=True)

    st.markdown('<hr>',unsafe_allow_html=True)

    # ══ RUNNER CARDS ══
    st.markdown('<div class="section-hdr">Runner-by-Runner Analysis</div>',unsafe_allow_html=True)

    if ratings:
        summary_rows=[]
        for r in runners:
            hid=get_horse_id(r)
            name=get_runner_name(r)
            rtg=ratings.get(hid,{})
            mp=field_probs.get(hid,0)
            mf=mkt.get(hid,{})
            price=get_best_price(r)
            diff=round(mp*100-mf.get("true_pct",0),1) if mp and mf else None
            summary_rows.append({
                "Horse":name,
                "Barrier":r.get("barrierNumber") or r.get("barrier") or "?",
                "Rating":f"{rtg.get('pct',0):.1f}%",
                "Composite":f"{rtg.get('composite',0):.1f}",
                "Model%":f"{mp*100:.1f}%" if mp else "—",
                "Price":f"${price:.2f}" if price>0 else "—",
                "Edge":f"+{diff}%" if diff is not None and diff>0 else (f"{diff}%" if diff is not None else "—"),
                "Bet":"✓" if (diff is not None and diff>(st.session_state.min_edge/100) and rtg.get("pct",0)>=st.session_state.min_rating) else "",
            })
        summary_rows.sort(key=lambda x:float(x["Composite"].replace("—","0")),reverse=True)
        st.dataframe(pd.DataFrame(summary_rows),use_container_width=True,hide_index=True)
        st.markdown('<div style="margin-bottom:22px"></div>',unsafe_allow_html=True)

    def sort_key(r):
        hid=get_horse_id(r)
        return field_probs.get(hid,0) if field_probs else -safe_float(get_best_price(r) or 99)

    for rank,runner in enumerate(sorted(runners,key=sort_key,reverse=True),1):
        hid=get_horse_id(runner)
        name=get_runner_name(runner)
        barrier=runner.get("barrierNumber") or runner.get("barrier") or "?"
        jockey=(runner.get("jockey") or {}).get("fullName") or runner.get("jockeyName") or "—"
        trainer=(runner.get("trainer") or {}).get("fullName") or runner.get("trainerName") or "—"
        weight=runner.get("weightTotal") or runner.get("weightCarried") or runner.get("handicapWeight") or "—"
        age=runner.get("age") or runner.get("horseAge") or ""
        sex=runner.get("sex") or runner.get("horseSex") or ""
        price=get_best_price(runner)
        p_source=price_source_label(runner)
        pace_lbl=PACE_POSITIONS.get(safe_int(runner.get("pacePosition",3)),"Midfield")
        rating=ratings.get(hid)
        pfr=pf_ratings.get(hid,{})
        sec_d=secs.get(hid,{})
        mf=mkt.get(hid,{})
        mp=field_probs.get(hid,0)
        past=past_all.get(hid,[])
        tj=runner.get("trainerJockeyA2E_Career") or {}
        tj_a2e=safe_float(tj.get("a2E",0))
        tj_sr=safe_float(tj.get("strikeRate",0))
        tj_runs=safe_float(tj.get("runners",0))

        verdict=None
        if rating and mf and mp:
            verdict=assess_value(mp,mf["true_pct"],price,rating["pct"],tj_a2e,
                st.session_state.min_rating,st.session_state.min_edge,st.session_state.min_tj_a2e)

        sp_str=f"${price:.2f}" if price>0 else "N/A"
        src_str=f" ({'live' if p_source=='live' else 'SP'})" if price>0 else ""
        mp_str=f"  ·  Model {round(mp*100,1)}%" if mp else ""
        mkt_str=f"  ·  Mkt {mf.get('true_pct','?')}%" if mf else ""
        edge_str=f"  ·  Edge {'+' if verdict and verdict['edge_pct']>=0 else ''}{verdict['edge_pct']}%" if verdict else ""
        bet_flag="  ★ BET" if (verdict and verdict["bet"]) else ""
        exp_label=f"#{rank}  {name}   B{barrier}   {sp_str}{src_str}{mp_str}{mkt_str}{edge_str}{bet_flag}"
        is_expanded=rank<=2 or (verdict is not None and verdict["bet"])

        with st.expander(exp_label, expanded=is_expanded):
            col_left, col_right = st.columns([3,2], gap="medium")

            with col_left:
                pace_pill={"Leader":"pill-red","On Pace":"pill-amber","Midfield":"pill-blue","Back":"pill-muted","Rear":"pill-muted"}.get(pace_lbl,"pill-muted")
                meta_line='<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px">'
                meta_line+=f'<span class="pill pill-muted">B{barrier}</span>'
                meta_line+=f'<span class="pill {pace_pill}">{pace_lbl}</span>'
                if weight and str(weight)!="—": meta_line+=f'<span class="pill pill-muted">{weight}kg</span>'
                if age: meta_line+=f'<span class="pill pill-muted">{age}yo</span>'
                if sex: meta_line+=f'<span class="pill pill-muted">{sex}</span>'
                if p_source=="live": meta_line+=f'<span class="pill pill-green">Live ${price:.2f}</span>'
                meta_line+="</div>"
                st.markdown(meta_line, unsafe_allow_html=True)

                st.markdown(
                    f'<div style="display:grid;grid-template-columns:auto auto;gap:4px 20px;'
                    f'font-size:.84rem;color:var(--ink-3);margin-bottom:16px;line-height:2">'
                    f'<span style="color:var(--mist);font-size:.65rem;text-transform:uppercase;letter-spacing:.07em;font-weight:700">Jockey</span>'
                    f'<span style="font-weight:600">{jockey}</span>'
                    f'<span style="color:var(--mist);font-size:.65rem;text-transform:uppercase;letter-spacing:.07em;font-weight:700">Trainer</span>'
                    f'<span style="font-weight:600">{trainer}</span>'
                    f'</div>', unsafe_allow_html=True)

                cw=safe_float(runner.get("winPct",0)); cp=safe_float(runner.get("placePct",0))
                tr2=runner.get("trackRecord") or {}
                ts=safe_float(tr2.get("starts",0)); tw=safe_float(tr2.get("firsts",0))
                ts2=safe_float(tr2.get("seconds",0)); tt=safe_float(tr2.get("thirds",0))
                dr=runner.get("distanceRecord") or {}
                ds2=safe_float(dr.get("starts",0)); dw=safe_float(dr.get("firsts",0))
                ds3=safe_float(dr.get("seconds",0)); dt=safe_float(dr.get("thirds",0))
                tsr=round(tw/ts*100,1) if ts>0 else 0; tplr=round((tw+ts2+tt)/ts*100,1) if ts>0 else 0
                dsr=round(dw/ds2*100,1) if ds2>0 else 0; dplr=round((dw+ds3+dt)/ds2*100,1) if ds2>0 else 0

                st.markdown(
                    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px">'
                    +f'<div class="card-sm"><div class="dl-label">Career Win%</div><div class="dl-value {"c-green" if cw>20 else ""}">{cw:.1f}%</div></div>'
                    +f'<div class="card-sm"><div class="dl-label">Career Place%</div><div class="dl-value">{cp:.1f}%</div></div>'
                    +f'<div class="card-sm"><div class="dl-label">Track {int(ts)} starts</div><div class="dl-value {"c-green" if tsr>20 else ""}">{tsr}%W {tplr}%P</div></div>'
                    +f'<div class="card-sm"><div class="dl-label">Distance {int(ds2)} starts</div><div class="dl-value {"c-green" if dsr>20 else ""}">{dsr}%W {dplr}%P</div></div>'
                    +'</div>', unsafe_allow_html=True)

                if tj_runs>=5:
                    a2e_col="c-green" if tj_a2e>=1.1 else "c-red" if tj_a2e<0.8 else ""
                    st.markdown(
                        f'<div class="card-sm" style="margin-bottom:16px">'
                        f'<div class="dl-label" style="margin-bottom:8px">J+T Combination — {int(tj_runs)} runs</div>'
                        f'<div style="display:flex;gap:24px;font-family:\'DM Mono\',monospace;font-size:.84rem">'
                        f'<div>SR <span style="font-weight:700">{tj_sr:.1f}%</span></div>'
                        f'<div>A2E <span class="dl-value {a2e_col}" style="font-size:.9rem">{tj_a2e:.2f}</span></div>'
                        f'</div></div>', unsafe_allow_html=True)

                pf_px=safe_float(pfr.get("pfAiPrice") or pfr.get("modelPrice") or 0)
                pf_rank=pfr.get("pfAiRank") or pfr.get("rank")
                if pf_px>1 or pf_rank:
                    pf_val=price>0 and pf_px>price
                    st.markdown(
                        f'<div class="card-blue" style="margin-bottom:16px">'
                        f'<div class="dl-label" style="margin-bottom:10px;color:var(--sap)">PF AI Model</div>'
                        f'<div style="display:flex;gap:24px;flex-wrap:wrap">'
                        +(f'<div><div class="dl-label">AI Price</div><div class="dl-value c-blue" style="font-size:1.15rem">${pf_px:.2f}</div></div>' if pf_px>1 else "")
                        +(f'<div><div class="dl-label">AI Rank</div><div class="dl-value c-blue">#{pf_rank}</div></div>' if pf_rank else "")
                        +f'</div>'
                        +(f'<div style="font-size:.72rem;color:var(--go);margin-top:8px;font-weight:600">AI price > market — value signal</div>' if pf_val else "")
                        +f'</div>', unsafe_allow_html=True)

                sec_rtg=safe_float(sec_d.get("sectionalRating") or sec_d.get("closing600Rating") or 0)
                sec_600=safe_float(sec_d.get("averageClosing600") or sec_d.get("avg600") or 0)
                if sec_rtg>0 or sec_600>0:
                    st.markdown(
                        f'<div class="card-sm" style="margin-bottom:16px">'
                        f'<div class="dl-label" style="margin-bottom:8px">Sectionals</div>'
                        f'<div style="display:flex;gap:24px;font-family:\'DM Mono\',monospace;font-size:.84rem">'
                        +(f'<div>Rating <span style="color:var(--sap);font-weight:700">{sec_rtg:.1f}</span></div>' if sec_rtg>0 else "")
                        +(f'<div>Avg 600m <span style="color:var(--sap);font-weight:700">{sec_600:.2f}s</span></div>' if sec_600>0 else "")
                        +f'</div></div>', unsafe_allow_html=True)

                if rating:
                    r_pct=rating["pct"]
                    r_col="var(--go)" if r_pct>=65 else "var(--warn)" if r_pct>=45 else "var(--stop)"
                    st.markdown(
                        f'<div class="dl-label" style="margin-bottom:7px">Composite Rating</div>'
                        f'<div style="display:flex;align-items:baseline;gap:10px;margin-bottom:8px">'
                        f'<span style="font-family:\'DM Mono\',monospace;font-size:2rem;font-weight:700;color:{r_col}">{rating["composite"]}</span>'
                        f'<span style="font-family:\'DM Mono\',monospace;font-size:.72rem;color:var(--mist)">/ {MAX_SCORE}  ({r_pct}%)</span>'
                        f'</div>'
                        f'<div class="prob-bar" style="margin-bottom:18px"><div class="prob-fill" style="width:{r_pct}%;background:{r_col}"></div></div>',
                        unsafe_allow_html=True)
                    for fkey,fmax in FACTOR_WEIGHTS.items():
                        val=rating.get(fkey,0); pct=int(val/fmax*100) if fmax else 0
                        bc="#1a8c4e" if pct>=65 else "#2255cc" if pct>=35 else "#c0392b"
                        st.markdown(
                            f'<div class="factor-row">'
                            f'<span class="factor-name">{FACTOR_LBLS[fkey]}</span>'
                            f'<div class="factor-bar"><div class="factor-fill" style="width:{pct}%;background:{bc}"></div></div>'
                            f'<span class="factor-score">{val:.1f}/{fmax}</span></div>',
                            unsafe_allow_html=True)

                if past:
                    st.markdown('<div class="dl-label" style="margin-top:18px;margin-bottom:10px">Recent Form</div>',unsafe_allow_html=True)
                    form_html='<div style="display:flex;gap:6px;flex-wrap:wrap">'
                    for run in past[:6]:
                        pos=safe_int(run.get("finishingPosition",0))
                        trk=(run.get("meetingName") or "")[:3].upper()
                        dst=safe_int(run.get("raceDistance") or 0)
                        box_c="#1a8c4e" if pos==1 else "#2255cc" if pos<=3 else "#6b7280" if pos<=5 else "#c0392b"
                        form_html+=(f'<div style="text-align:center;background:var(--ghost);border:1px solid var(--silver);'
                                    f'border-radius:var(--r);padding:7px 12px;min-width:44px">'
                                    f'<div style="font-family:\'DM Mono\',monospace;font-size:1.1rem;font-weight:700;color:{box_c}">{pos}</div>'
                                    f'<div style="font-size:.58rem;color:var(--mist);margin-top:2px">{trk}</div>'
                                    f'<div style="font-size:.58rem;color:var(--mist)">{dst}m</div></div>')
                    form_html+='</div>'
                    st.markdown(form_html, unsafe_allow_html=True)

                nk=f"{hid}_{rid}"
                note=st.text_area("Notes",value=st.session_state.notes.get(nk,""),
                    key=f"note_{hid}_{rank}",height=56,placeholder="Add race-day notes...")
                st.session_state.notes[nk]=note

            with col_right:
                if not rating and not mf:
                    st.markdown('<div class="alert alert-blue">Click "Run Full Analysis" to compute ratings.</div>',unsafe_allow_html=True)
                elif price<=1:
                    st.markdown('<div class="alert alert-amber">No price available yet.</div>',unsafe_allow_html=True)
                else:
                    # ── Betting Angles ──
                    angles = detect_angles(runner, past, tempo_info, secs)
                    if angles:
                        ang_html = '<div style="margin-bottom:16px"><div class="dl-label" style="margin-bottom:8px">Betting Angles</div>'
                        for ang in angles:
                            s = ang["strength"]
                            bg = "var(--go-l)" if s==3 else "var(--warn-l)" if s==2 else "var(--ghost)"
                            bd = "var(--go-m)" if s==3 else "var(--warn-m)" if s==2 else "var(--silver)"
                            tc = "var(--go)" if s==3 else "var(--warn)" if s==2 else "var(--steel)"
                            stars = "★"*s + "☆"*(3-s)
                            ang_html += (
                                f'<div style="background:{bg};border:1px solid {bd};border-radius:var(--r);padding:10px 12px;margin-bottom:6px">'
                                f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">'
                                f'<span style="font-size:.76rem;font-weight:700;color:{tc}">{ang["icon"]} {ang["label"]}</span>'
                                f'<span style="font-family:\'DM Mono\',monospace;font-size:.66rem;color:{tc}">{stars}</span>'
                                f'</div>'
                                f'<div style="font-size:.76rem;color:var(--ink-3);line-height:1.55">{ang["detail"]}</div>'
                                f'</div>'
                            )
                        ang_html += '</div>'
                        st.markdown(ang_html, unsafe_allow_html=True)

                    # ── Probability & EV breakdown ──
                    if mf and mp:
                        tp=mf["true_pct"]; rp=mf["raw_pct"]; fair=mf["fair_odds"]; mp_p=round(mp*100,1)
                        diff=round(mp_p-tp,1); dc="var(--go)" if diff>0 else "var(--stop)"
                        src_badge=f'<span class="mkt-badge badge-live" style="font-size:.6rem">{"LIVE" if mf.get("source")=="live" else "SP"}</span>'
                        ev_m = compute_ev_metrics(mp, price)
                        ev_c_inner = "var(--go)" if ev_m["ev"]>0 else "var(--stop)"
                        overlay_c = "var(--go)" if ev_m["overlay_pct"]>0 else "var(--stop)"
                        st.markdown(
                            f'<div class="card" style="margin-bottom:16px">'
                            f'<div class="dl-label" style="margin-bottom:14px;font-weight:700">Probability & EV {src_badge}</div>'
                            f'<div class="prob-grid">'
                            f'<div class="prob-cell-blue"><div class="dl-label">Market Price</div><div class="dl-value c-blue" style="font-size:1.2rem">${price:.2f}</div></div>'
                            f'<div class="prob-cell-blue"><div class="dl-label">Fair Odds</div><div class="dl-value" style="font-size:1.2rem">${ev_m["fair_odds"]:.2f}</div></div>'
                            f'<div class="prob-cell"><div class="dl-label">True Mkt%</div><div class="dl-value" style="font-size:.95rem">{tp}%</div></div>'
                            f'<div class="prob-cell-blue"><div class="dl-label">Model%</div><div class="dl-value c-blue" style="font-size:.95rem;font-weight:700">{mp_p}%</div></div>'
                            f'<div class="prob-cell-blue"><div class="dl-label">Edge</div><div style="font-family:\'DM Mono\',monospace;font-size:.95rem;font-weight:700;color:{dc}">{"+" if diff>=0 else ""}{diff}%</div></div>'
                            f'<div class="prob-cell-blue"><div class="dl-label">Overlay</div><div style="font-family:\'DM Mono\',monospace;font-size:.95rem;font-weight:700;color:{overlay_c}">{ev_m["overlay_pct"]:+.1f}%</div></div>'
                            f'</div>'
                            f'<div style="margin-top:12px;display:flex;gap:16px;flex-wrap:wrap">'
                            f'<div><div class="dl-label">EV per $1</div><div style="font-family:\'DM Mono\',monospace;font-size:1rem;font-weight:700;color:{ev_c_inner}">{ev_m["ev_pct"]:+.1f}¢</div></div>'
                            f'<div><div class="dl-label">Kelly%</div><div style="font-family:\'DM Mono\',monospace;font-size:1rem;font-weight:700">{round(ev_m["kelly_f"]*100,1)}%</div></div>'
                            f'<div><div class="dl-label">Book</div><div style="font-family:\'DM Mono\',monospace;font-size:1rem">{mf["overround"]}%</div></div>'
                            f'</div></div>', unsafe_allow_html=True)

                    # ── Model reasoning ──
                    reason = st.session_state.get("_model_reasoning", {}).get(hid)
                    if reason:
                        r_parts = []
                        if reason.get("pf_signal"):
                            r_parts.append(f'PF AI implied {round(reason["pf_signal"]*100,1)}%')
                        r_parts.append(f'Rating {round(reason["rat_signal"]*100,1)}%')
                        if reason.get("career_win",0)>0:
                            r_parts.append(f'Career win {round(reason["career_win"]*100,1)}%')
                        if reason.get("tj_a2e",0)>0 and reason.get("tj_runs",0)>=15:
                            r_parts.append(f'J+T A2E {reason["tj_a2e"]:.2f} ({reason["tj_runs"]} runs)')
                        adjustments = []
                        if reason.get("days_penalty",0)!=0:
                            dp = reason["days_penalty"]
                            adjustments.append((f'Fitness {"+" if dp>0 else ""}{round(dp*100,1)}%', dp>0))
                        if reason.get("puncture_boost",0)>0:
                            adjustments.append((f'Puncture bounce +{round(reason["puncture_boost"]*100,1)}%', True))
                        if reason.get("weight_penalty",0)<0:
                            adjustments.append((f'Weight penalty {round(reason["weight_penalty"]*100,1)}%', False))
                        reason_html = (
                            '<div class="card-sm" style="margin-bottom:16px">'
                            '<div class="dl-label" style="margin-bottom:8px">Model Inputs</div>'
                            '<div style="font-size:.75rem;color:var(--steel);line-height:1.8">'
                        )
                        for p in r_parts:
                            reason_html += f'<div>· {p}</div>'
                        if adjustments:
                            reason_html += '<div style="margin-top:5px;padding-top:5px;border-top:1px solid var(--silver)">'
                            for (a_txt, positive) in adjustments:
                                col = "var(--go)" if positive else "var(--stop)"
                                reason_html += f'<div style="color:{col}">▸ {a_txt}</div>'
                            reason_html += '</div>'
                        reason_html += (
                            f'<div style="margin-top:6px;padding-top:6px;border-top:1px solid var(--silver);'
                            f'color:var(--mist)">Raw: {reason.get("final_raw",0):.4f} → softmax normalised</div>'
                            f'</div></div>'
                        )
                        st.markdown(reason_html, unsafe_allow_html=True)

                    if verdict:
                        g=verdict["gates"]
                        def gp(ok): return ("pill-green","Pass") if ok else ("pill-red","Fail")
                        g1c,g1t=gp(g["edge"]); g2c,g2t=gp(g["rating"]); g3c,g3t=gp(g["tj"])
                        g4c,g4t=gp(g["odds"]); g5c,g5t=gp(g.get("ev",False))
                        gate_detail={
                            "edge":f"Edge {'+' if verdict['edge_pct']>=0 else ''}{verdict['edge_pct']}% vs min {st.session_state.min_edge}%",
                            "rating":f"Rating {rating['pct'] if rating else '?'}% vs min {st.session_state.min_rating}%",
                            "tj":f"A2E {tj_a2e:.2f} vs min {st.session_state.min_tj_a2e}",
                            "odds":f"${price:.2f}  range ${st.session_state.min_odds}–${st.session_state.max_odds}",
                            "ev":f"EV {verdict['ev_pct']:+.1f}¢ per $1 staked",
                        }
                        st.markdown(
                            f'<div class="card" style="margin-bottom:16px">'
                            f'<div class="dl-label" style="margin-bottom:14px;font-weight:700">Value Gates (5)</div>'
                            +"".join([
                                f'<div class="gate-row"><span class="pill {pc}" style="width:44px;justify-content:center;flex-shrink:0;font-size:.6rem">{pt}</span>'
                                f'<span class="gate-lbl">{lbl}</span><span class="gate-detail">{gate_detail[gk]}</span></div>'
                                for gk,(pc,pt),lbl in [
                                    ("edge",(g1c,g1t),"Edge"),
                                    ("rating",(g2c,g2t),"Rating"),
                                    ("tj",(g3c,g3t),"J+T A2E"),
                                    ("odds",(g4c,g4t),"Odds range"),
                                    ("ev",(g5c,g5t),"+EV"),
                                ]
                            ])
                            +f'</div>', unsafe_allow_html=True)

                        if verdict["bet"]:
                            rec=compute_stake(st.session_state.bank,mp,price,st.session_state.staking_method,
                                st.session_state.kelly_fraction,st.session_state.flat_pct,
                                st.session_state.level_stake,st.session_state.max_stake_pct)
                            ev_c2="#4ade80" if rec["ev"]>=0 else "#f87171"
                            st.markdown(
                                f'<div class="stake-card">'
                                f'<div class="stake-lbl">{st.session_state.staking_method}</div>'
                                f'<div class="stake-amount">${rec["stake"]:.2f}</div>'
                                f'<div class="stake-detail" style="color:{ev_c2}">EV ${rec["ev"]:+.2f}  ·  {rec["ev_pct"]:+.1f}%  ·  {rec["pct_bank"]}% of bank</div>'
                                f'<div class="stake-detail">Break-even: {rec["roi_required"]:.1f}% ROI  ·  Kelly f* = {round(verdict["kelly_f"]*100,2)}%</div>'
                                f'</div>', unsafe_allow_html=True)
                            top_angle = max(angles, key=lambda a: a["strength"]) if angles else None
                            banner_sub = top_angle["label"] + " — " + top_angle["detail"][:80] + "…" if top_angle else "Positive edge versus de-vigged market probability"
                            st.markdown(
                                f'<div class="bet-banner"><div class="bet-banner-title">★ BET — All five gates pass</div>'
                                f'<div class="bet-banner-sub">{banner_sub}</div></div>',
                                unsafe_allow_html=True)
                            if st.button(f"📋  Log — {name}",key=f"log_{hid}_{rank}"):
                                add_bet(name,f"{rtrk} R{rnum}",rec["stake"],price,verdict["edge_pct"],verdict["model_pct"])
                                st.success(f"✓ Logged: {name} ${rec['stake']:.2f} @ ${price}")
                        else:
                            st.markdown(f'<div class="alert alert-red">No bet — {"  ·  ".join(verdict["reasons"])}</div>',unsafe_allow_html=True)



# ════════════════════════════════════════════════════════════════
# TAB 3 — STAKING & BETS
# ════════════════════════════════════════════════════════════════
with TAB_STAKING:
    st.markdown("""<div class="page-header"><div>
      <div class="page-eyebrow">Discipline & Records</div>
      <div class="page-title">Staking & Bet Log</div>
    </div></div>""",unsafe_allow_html=True)

    st.markdown('<div class="section-hdr">Staking Methods</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    for col,title,pill_c,body in [
        (c1,"Kelly Criterion","pill-blue","Mathematically optimal — stake is proportional to edge.<br><br><code>f* = (bp − q) / b</code><br><br><strong>Quarter Kelly (recommended)</strong> retains ~75% of theoretical growth rate while dramatically reducing variance."),
        (c2,"Flat Percentage","pill-muted","Fixed % of current bank per bet. Naturally scales down in losing runs and up in winning runs.<br><br>Simpler than Kelly. Does not account for edge size."),
        (c3,"Level Stakes","pill-muted","Fixed dollar amount per bet. Easiest for tracking ROI cleanly.<br><br>Does not protect bank in drawdowns. Best for evaluating model performance in isolation."),
    ]:
        col.markdown(f'<div class="card"><div style="margin-bottom:12px"><span class="pill {pill_c}">{title}</span></div><div style="font-size:.81rem;color:var(--ink-3);line-height:1.9">{body}</div></div>',unsafe_allow_html=True)

    bpct=st.session_state.bank/st.session_state.starting_bank*100 if st.session_state.starting_bank else 100
    if bpct<70:
        st.markdown(f'<div class="alert alert-red">⚠ Stop-loss triggered — bank at {bpct:.1f}% of starting balance. Halve all stakes until bank recovers above 85%.</div>',unsafe_allow_html=True)
    elif bpct<85:
        st.markdown(f'<div class="alert alert-amber">Bank at {bpct:.1f}% of start — consider reducing stake sizes.</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-hdr">Bet Log</div>',unsafe_allow_html=True)
    log=st.session_state.bet_log
    if not log:
        st.markdown('<div class="alert alert-blue">No bets logged yet. Qualifying bets appear here after clicking "Log" in the Analysis tab.</div>',unsafe_allow_html=True)
    else:
        settled=[b for b in log if b["result"]!="Pending"]; pending=[b for b in log if b["result"]=="Pending"]
        if settled:
            s_pl=sum(b["pl"] for b in settled); s_stk=sum(b["stake"] for b in settled)
            s_roi=round(s_pl/s_stk*100,1) if s_stk else 0; s_wins=sum(1 for b in settled if b["result"]=="Won")
            pl_c="var(--go)" if s_pl>=0 else "var(--stop)"
            st.markdown(f'<div style="display:flex;gap:10px;margin-bottom:18px;flex-wrap:wrap">'
                        f'<span style="padding:4px 12px;border-radius:99px;background:var(--ghost);border:1px solid var(--silver);font-size:.72rem">{len(settled)} settled</span>'
                        f'<span style="padding:4px 12px;border-radius:99px;background:var(--ghost);border:1px solid var(--silver);font-size:.72rem">{len(pending)} pending</span>'
                        f'<span style="padding:4px 12px;border-radius:99px;background:var(--ghost);border:1px solid var(--silver);font-size:.72rem;color:{pl_c}">P/L ${s_pl:+.2f}</span>'
                        f'<span style="padding:4px 12px;border-radius:99px;background:var(--ghost);border:1px solid var(--silver);font-size:.72rem">ROI {s_roi:+.1f}%</span>'
                        f'<span style="padding:4px 12px;border-radius:99px;background:var(--ghost);border:1px solid var(--silver);font-size:.72rem">{s_wins}/{len(settled)} wins</span>'
                        f'</div>',unsafe_allow_html=True)

        df_log=pd.DataFrame(log)
        st.dataframe(df_log[["dt","horse","race","stake","odds","edge","model_pct","result","pl"]].rename(columns={
            "dt":"Time","horse":"Horse","race":"Race","stake":"Stake $","odds":"Odds",
            "edge":"Edge %","model_pct":"Model %","result":"Result","pl":"P/L $"}),
            use_container_width=True,hide_index=True)

        pending_idx=[(i,b) for i,b in enumerate(log) if b["result"]=="Pending"]
        if pending_idx:
            st.markdown('<div class="section-hdr">Settle Pending Bets</div>',unsafe_allow_html=True)
            for idx,bet in pending_idx:
                c1,c2,c3,c4=st.columns([5,1,1,1])
                with c1:
                    st.markdown(f'<div style="padding:10px 0;font-family:\'DM Mono\',monospace;font-size:.8rem">'
                                f'<span style="color:var(--sap);font-weight:700">{bet["horse"]}</span>&nbsp;&nbsp;'
                                f'<span style="color:var(--steel)">${bet["stake"]:.2f} @ {bet["odds"]}</span></div>',unsafe_allow_html=True)
                with c2:
                    if st.button("Won",key=f"won_{idx}"): settle(idx,"Won"); st.rerun()
                with c3:
                    if st.button("Lost",key=f"lst_{idx}"): settle(idx,"Lost"); st.rerun()
                with c4:
                    if st.button("Void",key=f"vd_{idx}"): settle(idx,"Void"); st.rerun()

        if st.button("Clear All Bets",type="secondary"):
            st.session_state.bet_log=[]; st.rerun()


# ════════════════════════════════════════════════════════════════
# TAB 4 — BANKROLL
# ════════════════════════════════════════════════════════════════
with TAB_BANKROLL:
    st.markdown("""<div class="page-header"><div>
      <div class="page-eyebrow">Performance Tracking</div>
      <div class="page-title">Bankroll</div>
    </div></div>""",unsafe_allow_html=True)

    stats=bankroll_stats()
    if not stats:
        st.markdown("""<div class="empty-state"><div class="empty-icon">📈</div>
          <div class="empty-title">No settled bets yet</div>
          <div class="empty-sub">Results appear here after settling bets in the Staking tab.</div>
        </div>""",unsafe_allow_html=True)
    else:
        pl_c="c-green" if stats["pl"]>=0 else "c-red"; roi_c="c-green" if stats["roi"]>=0 else "c-red"
        st.markdown(
            f'<div class="metric-grid">'
            f'<div class="metric-card c-blue"><div class="metric-lbl">Bank</div><div class="metric-val c-blue">${stats["bank"]:.0f}</div><div class="metric-sub">Start: ${st.session_state.starting_bank:.0f}</div></div>'
            f'<div class="metric-card {"c-green" if stats["pl"]>=0 else "c-red"}"><div class="metric-lbl">Total P/L</div><div class="metric-val {pl_c}">{("+" if stats["pl"]>=0 else "")}${stats["pl"]:.2f}</div></div>'
            f'<div class="metric-card {"c-green" if stats["roi"]>=0 else "c-red"}"><div class="metric-lbl">ROI</div><div class="metric-val {roi_c}">{("+" if stats["roi"]>=0 else "")}{stats["roi"]:.1f}%</div><div class="metric-sub">On ${stats["staked"]:.0f} staked</div></div>'
            f'<div class="metric-card c-brass"><div class="metric-lbl">Strike Rate</div><div class="metric-val c-brass">{stats["sr"]:.1f}%</div><div class="metric-sub">{stats["winners"]}/{stats["n"]} wins</div></div>'
            f'<div class="metric-card"><div class="metric-lbl">Avg Odds</div><div class="metric-val">{stats["avg_odds"]:.2f}</div></div>'
            f'<div class="metric-card c-red"><div class="metric-lbl">Max Drawdown</div><div class="metric-val c-red">−${abs(stats["max_dd"]):.2f}</div></div>'
            f'</div>',unsafe_allow_html=True)

        settled=[b for b in st.session_state.bet_log if b["result"]!="Pending"]
        if settled:
            st.markdown('<div class="section-hdr">Cumulative P/L</div>',unsafe_allow_html=True)
            pl_vals=[0]+list(pd.Series([b["pl"] for b in settled]).cumsum())
            fig=go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(len(pl_vals))),y=pl_vals,mode="lines+markers",
                line=dict(color="#2255cc",width=2.5),
                marker=dict(size=5,color=["#1a8c4e" if v>=0 else "#c0392b" for v in pl_vals]),
                fill="tozeroy",fillcolor="rgba(34,85,204,0.07)"))
            fig.add_hline(y=0,line_dash="dash",line_color="#d6dae3",line_width=1.5)
            fig.update_layout(
                paper_bgcolor="white",plot_bgcolor="white",
                margin=dict(t=10,b=10,l=10,r=10),
                xaxis=dict(title="Bet #",gridcolor="#f7f8fb",color="#8b95aa",tickfont=dict(family="DM Mono")),
                yaxis=dict(title="P/L ($)",gridcolor="#f7f8fb",color="#8b95aa",tickfont=dict(family="DM Mono")),
                height=320,showlegend=False,
                font=dict(family="DM Sans, sans-serif"))
            st.plotly_chart(fig,use_container_width=True)

        col_a,col_b=st.columns(2)
        with col_a:
            if st.button("Reset Bankroll & Log",type="secondary"):
                st.session_state.bet_log=[]; st.session_state.bank=st.session_state.starting_bank; st.rerun()
        with col_b:
            new_start=st.number_input("Set Starting Bank",value=st.session_state.starting_bank,step=100.0)
            if st.button("Update Starting Bank"):
                st.session_state.starting_bank=new_start; st.rerun()


# ════════════════════════════════════════════════════════════════
# TAB 5 — DEBUG
# ════════════════════════════════════════════════════════════════
with TAB_DEBUG:
    st.markdown("""<div class="page-header"><div>
      <div class="page-eyebrow">Diagnostics</div>
      <div class="page-title">API Debug</div>
    </div></div>""",unsafe_allow_html=True)

    st.markdown(f'**Date format:** `{pf_date(race_date)}`')

    # Live price diagnostics
    st.markdown('<div class="section-hdr">Live Price Scrape Status</div>',unsafe_allow_html=True)
    live_prices=st.session_state.get("_live_prices",{})
    live_ts=st.session_state.get("_live_prices_ts")
    live_src=st.session_state.get("_live_source","")
    if live_prices:
        st.markdown(f'<div class="alert alert-green">✓ {len(live_prices)} prices cached from {live_src} at {live_ts.strftime("%H:%M:%S") if live_ts else "?"}</div>',unsafe_allow_html=True)
        with st.expander("Show cached live prices"):
            for k,v in sorted(live_prices.items()):
                st.markdown(f'<div class="debug-box">{k}  →  ${v:.2f}</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert alert-amber">No live prices cached. Load a race and click "Refresh Live Odds".</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-hdr">API Call Log</div>',unsafe_allow_html=True)
    api_log=st.session_state.get("_api_log",[])
    if not api_log:
        st.markdown('<div class="alert alert-blue">No API calls yet.</div>',unsafe_allow_html=True)
    else:
        for entry in reversed(api_log[-20:]):
            status=entry["status"]
            color="#1a8c4e" if status==200 else "#c0392b" if status>=400 else "#b06a00"
            st.markdown(
                f'<div class="debug-box">'
                f'<span style="color:{color};font-weight:700">[{status}]</span>'
                f' <span style="color:#d6dae3">{entry["ts"]}</span>'
                f'  <span style="color:#6fa3f5">{entry["url"].replace(BASE_URL,"")}</span>'
                f'<br>params: {json.dumps(entry["params"])}'
                +(f'<br><span style="color:#f87171">{entry["note"]}</span>' if entry.get("note") else "")
                +f'</div>',unsafe_allow_html=True)

    dbg=st.session_state.get("_last_field_debug")
    if dbg:
        st.markdown('<div class="section-hdr">Last Runner-Fetch Attempts</div>',unsafe_allow_html=True)
        for a in dbg.get("attempts",[]):
            ok=a.get("runners_found",0)>0
            color="#1a8c4e" if ok else "#c0392b"
            st.markdown(
                f'<div class="debug-box">'
                f'<span style="color:{color};font-weight:700">{"✓" if ok else "✗"}</span>'
                f' <span style="color:#d6dae3">{a["label"]}</span>'
                f'  runners_found=<span style="color:{"#4ade80" if ok else "#f87171"}">{a.get("runners_found",0)}</span>'
                f'  top_keys={a.get("top_keys",[])} </div>',unsafe_allow_html=True)
        for s in dbg.get("raw_samples",[]):
            st.markdown(f'**Raw — {s["label"]}:**')
            st.markdown(f'<div class="debug-box">{s["sample"]}</div>',unsafe_allow_html=True)

    if st.button("Clear debug log"):
        st.session_state["_api_log"]=[]; st.session_state["_last_field_debug"]=None; st.rerun()

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:52px 0 28px;
  font-family:'DM Mono',monospace;font-size:.6rem;color:var(--silver);
  letter-spacing:.18em;text-transform:uppercase;border-top:1px solid var(--ghost);margin-top:32px">
  Racing Edge  ·  Research & Analysis Only  ·  Gamble Responsibly  ·  1800 858 858  ·  18+
</div>
""", unsafe_allow_html=True)
