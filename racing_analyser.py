"""
Racing Edge Analyser — PuntingForm API v2
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

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Racing Edge",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap');
:root {
  --bg:#f8fafc;--bg2:#f1f5f9;--surface:#ffffff;--surface2:#f8fafc;
  --border:#e2e8f0;--border2:#cbd5e1;
  --blue:#1d4ed8;--blue-dark:#1e3a8a;--blue-mid:#3b82f6;
  --blue-l:#dbeafe;--blue-ll:#eff6ff;--blue-m:#bfdbfe;
  --teal:#0891b2;--teal-l:#cffafe;
  --text:#0f172a;--text2:#1e293b;--text3:#475569;--text4:#94a3b8;
  --green:#16a34a;--green-l:#dcfce7;--green-m:#86efac;
  --red:#dc2626;--red-l:#fee2e2;--red-m:#fca5a5;
  --amber:#d97706;--amber-l:#fef3c7;--amber-m:#fcd34d;
  --purple:#7c3aed;--purple-l:#ede9fe;
  --r:6px;--r2:10px;--r3:14px;--r4:20px;
  --sh:0 1px 3px rgba(15,23,42,.06),0 1px 2px rgba(15,23,42,.04);
  --sh2:0 4px 16px rgba(15,23,42,.08),0 2px 8px rgba(15,23,42,.04);
  --sh3:0 8px 32px rgba(29,78,216,.12),0 2px 8px rgba(29,78,216,.06);
}
html,body{font-family:'Inter',sans-serif;}
[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text);font-family:'Inter',sans-serif;font-size:14px;}
[data-testid="stHeader"]{background:transparent!important;}
[data-testid="stSidebar"]{background:#0f172a!important;border-right:1px solid #1e293b!important;}
[data-testid="stSidebar"]>div{padding-top:0!important;}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stDateInput label{color:#94a3b8!important;font-size:.78rem!important;font-weight:500!important;letter-spacing:.03em;}
[data-testid="stSidebar"] input,[data-testid="stSidebar"] select{background:#1e293b!important;border:1px solid #334155!important;border-radius:var(--r)!important;color:#f1f5f9!important;}
[data-testid="stSidebar"] [data-baseweb="select"]>div{background:#1e293b!important;border:1px solid #334155!important;}
[data-testid="stSidebar"] [data-baseweb="select"]*{color:#f1f5f9!important;}
[data-testid="stSidebar"] [data-testid="stAlert"]{display:none;}
.stTextInput input,.stNumberInput input,.stTextArea textarea{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:var(--r)!important;color:var(--text)!important;font-family:'JetBrains Mono',monospace!important;font-size:.82rem!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--surface)!important;border-bottom:2px solid var(--border)!important;gap:0!important;padding:0!important;box-shadow:var(--sh);}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--text3)!important;font-family:'Inter',sans-serif!important;font-size:.82rem!important;font-weight:500!important;padding:16px 24px!important;border:none!important;border-bottom:2px solid transparent!important;margin-bottom:-2px!important;}
.stTabs [aria-selected="true"]{color:var(--blue)!important;border-bottom:2px solid var(--blue)!important;font-weight:700!important;}
.stTabs [data-testid="stTabPanel"]{background:var(--bg)!important;padding-top:28px!important;}
.stButton>button{background:var(--blue)!important;color:#fff!important;border:none!important;border-radius:var(--r2)!important;font-family:'Inter',sans-serif!important;font-weight:600!important;font-size:.8rem!important;padding:.55rem 1.25rem!important;box-shadow:0 2px 8px rgba(29,78,216,.25)!important;transition:all .15s ease!important;}
.stButton>button:hover{background:var(--blue-dark)!important;transform:translateY(-1px)!important;}
[data-testid="stSidebar"] .stButton>button{background:linear-gradient(135deg,#1d4ed8,#3b82f6)!important;width:100%!important;padding:.65rem!important;}
[data-testid="stDataFrame"]{border:1px solid var(--border)!important;border-radius:var(--r2)!important;overflow:hidden!important;box-shadow:var(--sh)!important;}
[data-testid="stDataFrame"] th{background:#f8fafc!important;color:var(--blue-dark)!important;font-family:'Inter',sans-serif!important;font-size:.68rem!important;font-weight:700!important;letter-spacing:.08em!important;text-transform:uppercase!important;border-bottom:2px solid var(--border)!important;padding:11px 14px!important;}
[data-testid="stDataFrame"] td{color:var(--text)!important;border-bottom:1px solid var(--border)!important;font-family:'JetBrains Mono',monospace!important;font-size:.78rem!important;padding:9px 14px!important;}
[data-testid="stDataFrame"] tr:hover td{background:var(--blue-ll)!important;}
.streamlit-expanderHeader{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:var(--r2)!important;color:var(--text)!important;font-family:'Inter',sans-serif!important;font-size:.85rem!important;font-weight:600!important;box-shadow:var(--sh)!important;padding:14px 18px!important;}
.streamlit-expanderContent{background:var(--surface)!important;border:1px solid var(--border)!important;border-top:none!important;border-radius:0 0 var(--r2) var(--r2)!important;padding:16px!important;}
[data-testid="stAlert"]{border-radius:var(--r2)!important;font-size:.82rem!important;}
.page-hdr{display:flex;align-items:flex-end;justify-content:space-between;border-bottom:2px solid var(--border);padding-bottom:16px;margin-bottom:28px;}
.page-title{font-size:1.5rem;font-weight:800;color:var(--text);letter-spacing:-.03em;line-height:1;}
.page-sub{font-family:'JetBrains Mono',monospace;font-size:.68rem;color:var(--text4);letter-spacing:.06em;text-transform:uppercase;margin-top:6px;}
.sb-brand{background:linear-gradient(160deg,#0f172a 0%,#1e3a8a 100%);margin:-1rem -1rem 0;padding:24px 20px 20px;border-bottom:1px solid #1d4ed8;}
.sb-logo{font-size:1.25rem;font-weight:800;color:#fff;letter-spacing:-.03em;display:flex;align-items:center;gap:8px;}
.sb-sub{font-family:'JetBrains Mono',monospace;font-size:.58rem;color:rgba(255,255,255,.45);letter-spacing:.14em;margin-top:4px;text-transform:uppercase;}
.sb-version{display:inline-block;margin-top:8px;padding:2px 8px;background:rgba(59,130,246,.25);border:1px solid rgba(59,130,246,.4);border-radius:99px;font-family:'JetBrains Mono',monospace;font-size:.58rem;color:#93c5fd;letter-spacing:.08em;}
.sb-sec{font-size:.65rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#475569;margin:20px 0 10px;padding-top:16px;border-top:1px solid #1e293b;}
.sb-sec:first-of-type{border-top:none;margin-top:16px;}
.sb-status-ok{font-size:.72rem;color:#4ade80;font-family:'JetBrains Mono',monospace;display:flex;align-items:center;gap:5px;margin-top:4px;}
.sb-status-ok::before{content:'●';font-size:.6rem;}
.sb-status-err{font-size:.72rem;color:#f87171;font-family:'JetBrains Mono',monospace;display:flex;align-items:center;gap:5px;margin-top:4px;}
.sb-status-err::before{content:'●';font-size:.6rem;}
.metric-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px;margin-bottom:24px;}
.metric-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r2);padding:16px 18px;box-shadow:var(--sh);position:relative;overflow:hidden;}
.metric-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--border);}
.metric-card.blue::before{background:var(--blue);}
.metric-card.green::before{background:var(--green);}
.metric-card.red::before{background:var(--red);}
.metric-card.amber::before{background:var(--amber);}
.metric-label{font-size:.65rem;font-weight:700;color:var(--text4);letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px;}
.metric-value{font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;color:var(--text);line-height:1.1;}
.metric-value.blue{color:var(--blue);}
.metric-value.green{color:var(--green);}
.metric-value.red{color:var(--red);}
.metric-value.amber{color:var(--amber);}
.metric-sub{font-family:'JetBrains Mono',monospace;font-size:.65rem;color:var(--text4);margin-top:4px;}
.pill{display:inline-flex;align-items:center;padding:2px 9px;border-radius:99px;font-size:.65rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;line-height:1.8;}
.pill-blue{background:var(--blue-l);color:var(--blue);border:1px solid var(--blue-m);}
.pill-green{background:var(--green-l);color:var(--green);border:1px solid var(--green-m);}
.pill-red{background:var(--red-l);color:var(--red);border:1px solid var(--red-m);}
.pill-amber{background:var(--amber-l);color:var(--amber);border:1px solid var(--amber-m);}
.pill-muted{background:var(--surface2);color:var(--text3);border:1px solid var(--border);}
.pill-teal{background:var(--teal-l);color:var(--teal);border:1px solid #67e8f9;}
.pill-dark{background:#0f172a;color:#e2e8f0;border:1px solid #334155;}
.alert{border-radius:var(--r2);padding:12px 16px;font-size:.82rem;margin:8px 0;line-height:1.6;}
.alert-blue{background:var(--blue-ll);border-left:3px solid var(--blue);color:var(--blue-dark);}
.alert-green{background:var(--green-l);border-left:3px solid var(--green);color:#14532d;}
.alert-red{background:var(--red-l);border-left:3px solid var(--red);color:#7f1d1d;}
.alert-amber{background:var(--amber-l);border-left:3px solid var(--amber);color:#78350f;}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r2);padding:20px 22px;box-shadow:var(--sh);margin-bottom:12px;}
.card-sm{background:var(--surface2);border:1px solid var(--border);border-radius:var(--r);padding:10px 13px;margin-bottom:6px;}
.card-blue{background:var(--blue-ll);border:1px solid var(--blue-m);border-radius:var(--r2);padding:14px 18px;margin-bottom:12px;}
.card-green{background:var(--green-l);border:1px solid var(--green-m);border-radius:var(--r2);padding:14px 18px;margin-bottom:12px;}
.card-dark{background:#0f172a;border:1px solid #1e293b;border-radius:var(--r2);padding:16px 18px;margin-bottom:12px;}
.mkt-table{width:100%;border-collapse:collapse;font-size:.8rem;}
.mkt-table th{background:#f8fafc;color:#1e3a8a;font-size:.65rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:11px 14px;text-align:left;border-bottom:2px solid var(--border);white-space:nowrap;}
.mkt-table td{padding:10px 14px;border-bottom:1px solid var(--border);font-family:'JetBrains Mono',monospace;font-size:.77rem;color:var(--text);vertical-align:middle;}
.mkt-table tr:last-child td{border-bottom:none;}
.mkt-table tr:hover td{background:var(--blue-ll);}
.mkt-table .val-row td{background:rgba(22,163,74,.04);}
.mkt-table .fav-row td{background:rgba(29,78,216,.03);}
.mkt-horse{font-family:'Inter',sans-serif;font-weight:700;font-size:.86rem;color:var(--text);}
.mkt-fav{display:inline-block;padding:1px 7px;border-radius:3px;background:var(--blue-l);color:var(--blue);font-size:.58rem;font-weight:700;margin-left:5px;text-transform:uppercase;letter-spacing:.06em;}
.mkt-val{display:inline-block;padding:1px 7px;border-radius:3px;background:var(--green-l);color:var(--green);font-size:.58rem;font-weight:700;margin-left:5px;text-transform:uppercase;letter-spacing:.06em;}
.edge-pos{color:var(--green);font-weight:700;}
.edge-neg{color:var(--red);}
.edge-neu{color:var(--text4);}
.prob-bar{height:5px;border-radius:3px;background:var(--border);overflow:hidden;margin-top:4px;}
.prob-fill{height:5px;border-radius:3px;}
.comp-row{display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid var(--border);}
.comp-name{font-family:'JetBrains Mono',monospace;font-size:.66rem;color:var(--text3);width:90px;flex-shrink:0;}
.comp-score{font-family:'JetBrains Mono',monospace;font-size:.66rem;color:var(--text2);width:48px;text-align:right;flex-shrink:0;}
.comp-bar{flex:1;height:4px;border-radius:2px;background:var(--border);}
.comp-fill{height:4px;border-radius:2px;}
.smap-row{display:flex;align-items:center;gap:14px;padding:10px 16px;background:var(--surface);border:1px solid var(--border);border-radius:var(--r);margin-bottom:6px;box-shadow:var(--sh);}
.smap-pos{font-size:.72rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;width:80px;flex-shrink:0;}
.smap-horses{font-family:'JetBrains Mono',monospace;font-size:.78rem;color:var(--text2);flex:1;}
.smap-cnt{font-family:'JetBrains Mono',monospace;font-size:.68rem;color:var(--text4);width:24px;text-align:right;}
.gate-row{display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid var(--border);}
.gate-lbl{font-size:.8rem;color:var(--text2);flex:1;font-weight:500;}
.gate-detail{font-family:'JetBrains Mono',monospace;font-size:.7rem;color:var(--text4);}
.stake-card{background:linear-gradient(135deg,#1e3a8a 0%,#1d4ed8 100%);border-radius:var(--r2);padding:18px 20px;margin-bottom:10px;box-shadow:0 4px 20px rgba(29,78,216,.3);}
.stake-amount{font-family:'JetBrains Mono',monospace;font-size:2.2rem;font-weight:700;color:#fff;line-height:1;}
.stake-label{font-size:.7rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.6);margin-bottom:6px;}
.stake-detail{font-family:'JetBrains Mono',monospace;font-size:.72rem;color:rgba(255,255,255,.75);margin-top:6px;}
.race-row{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border);}
.race-row:last-child{border-bottom:none;}
.race-num{font-family:'JetBrains Mono',monospace;font-size:.85rem;font-weight:700;color:var(--blue);width:30px;flex-shrink:0;}
.race-info{flex:1;margin-left:12px;}
.race-name{font-size:.88rem;font-weight:600;color:var(--text);}
.race-meta{font-family:'JetBrains Mono',monospace;font-size:.68rem;color:var(--text4);margin-top:3px;}
.section-hdr{font-size:.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--text4);border-bottom:1px solid var(--border);padding-bottom:8px;margin:24px 0 16px;}
.dl-label{font-size:.66rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--text4);margin-bottom:4px;}
.dl-value{font-family:'JetBrains Mono',monospace;font-size:1.0rem;color:var(--text);font-weight:600;}
.dl-value.green{color:var(--green);}
.dl-value.red{color:var(--red);}
.dl-value.blue{color:var(--blue);}
.debug-box{background:#1e293b;border:1px solid #334155;border-radius:var(--r);padding:12px 14px;font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#94a3b8;white-space:pre-wrap;max-height:300px;overflow-y:auto;}
hr{border:none;border-top:1px solid var(--border);margin:24px 0;}
.prob-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.prob-cell{background:var(--surface2);border:1px solid var(--border);border-radius:var(--r);padding:10px 12px;}
.prob-cell-blue{background:var(--blue-ll);border:1px solid var(--blue-m);border-radius:var(--r);padding:10px 12px;}
.empty-state{text-align:center;padding:60px 20px;color:var(--text4);}
.empty-icon{font-size:3rem;margin-bottom:12px;}
.empty-title{font-size:1rem;font-weight:600;color:var(--text3);margin-bottom:6px;}
.empty-sub{font-size:.82rem;color:var(--text4);line-height:1.6;}
.bet-banner{background:linear-gradient(135deg,#14532d,#16a34a);border-radius:var(--r2);padding:14px 18px;margin-bottom:12px;}
.bet-banner-title{font-size:.8rem;font-weight:700;color:#fff;letter-spacing:.04em;text-transform:uppercase;margin-bottom:3px;}
.bet-banner-sub{font-size:.76rem;color:rgba(255,255,255,.8);}
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
    "_api_log": [],   # list of dicts: {url, status, keys}
    "fetch_status": "", "fetch_count": 0,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── API LAYER ────────────────────────────────────────────────────────────────
BASE_URL = "https://api.puntingform.com.au/v2"

def pf_date(d: date) -> str:
    """d-MMM-yyyy  e.g. 4-Apr-2026  (no leading zero — required by API)"""
    import platform
    fmt = "%#d-%b-%Y" if platform.system() == "Windows" else "%-d-%b-%Y"
    return d.strftime(fmt)

def _log_api(url: str, params: dict, status: int, note: str = ""):
    safe = {k: v for k, v in params.items() if k != "apiKey"}
    st.session_state["_api_log"].append({
        "url": url,
        "params": safe,
        "status": status,
        "note": note,
        "ts": datetime.now().strftime("%H:%M:%S"),
    })
    # Keep last 40 only
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

# ─── PAYLOAD EXTRACTION ───────────────────────────────────────────────────────
# The PuntingForm API wraps runners in many different shapes. This function
# tries every known nesting pattern before giving up.

def extract_runners_from_payload(data) -> list:
    """
    Try every known shape the fields/form endpoints return runners in:
      - top-level list
      - {"payLoad": [...]}
      - {"payLoad": {"fields": [...]}}
      - {"payLoad": {"runners": [...]}}
      - {"payLoad": {"horses": [...]}}
      - {"fields": [...]}
      - {"runners": [...]}
      - {"horses": [...]}
      - list-of-dicts where each dict has a "runners" key (meeting shape)
    Returns the first non-empty list found, else [].
    """
    if not data:
        return []

    # Unwrap payLoad if present
    payload = data.get("payLoad", data) if isinstance(data, dict) else data

    # Direct list
    if isinstance(payload, list):
        # Each item might be a runner directly, or a race-wrapper
        if payload and isinstance(payload[0], dict):
            # Check if first item looks like a runner (has name/horseId)
            first = payload[0]
            if any(k in first for k in ("name","runnerName","horseName","horseId","runnerId","HorseId","RunnerID")):
                return payload
            # Maybe it's a list of races — extract runners from first race
            for race in payload:
                for rkey in ("runners","fields","horses","runners"):
                    runners = race.get(rkey, [])
                    if runners and isinstance(runners, list):
                        return runners
        return payload

    if isinstance(payload, dict):
        # Try common runner list keys
        for key in ("fields", "runners", "horses", "runners", "payLoad"):
            val = payload.get(key)
            if isinstance(val, list) and val:
                first = val[0]
                if isinstance(first, dict) and any(
                    k in first for k in ("name","runnerName","horseName","horseId","runnerId","HorseId","RunnerID","barrier","barrierNumber")
                ):
                    return val
        # recurse one more level
        for key, val in payload.items():
            if isinstance(val, list) and val and isinstance(val[0], dict):
                return val

    return []


def extract_meetings_list(data) -> list:
    """Extract list of meeting objects from meetingslist response."""
    if not data:
        return []
    if isinstance(data, list):
        return data
    payload = data.get("payLoad", data) if isinstance(data, dict) else data
    if isinstance(payload, list):
        return payload
    # Sometimes wrapped in another key
    if isinstance(payload, dict):
        for key in ("meetings", "meetingList", "meetingsList", "data"):
            val = payload.get(key)
            if isinstance(val, list) and val:
                return val
        # Return values that are lists
        for val in payload.values():
            if isinstance(val, list) and val:
                return val
    return []


def extract_races_from_meeting(data) -> list:
    """Extract list of race objects from a meeting detail response."""
    if not data:
        return []
    payload = data.get("payLoad", data) if isinstance(data, dict) else data
    if isinstance(payload, list):
        if payload and isinstance(payload[0], dict):
            # Could be races directly, or meeting objects containing races
            first = payload[0]
            for rkey in ("races","raceList","Races"):
                races = first.get(rkey, [])
                if races:
                    return races
            # Already a list of races
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
    # Fall back to name if nothing else
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


# ─── MEETINGS — FAST (no per-meeting detail call) ────────────────────────────
def fetch_meetings_fast(d: date) -> list:
    """
    Step 1: just get the list of meetings (names, states, IDs).
    Does NOT fetch races — that happens lazily when user expands a meeting.
    """
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
    """
    Step 2: fetch races for a single meeting (called when user expands it).
    Tries meetingId first, then track name.
    """
    ds    = pf_date(d)
    name  = m.get("_name", "")
    mid   = str(m.get("meetingId") or m.get("id") or "")

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
def fetch_race_field(race: dict) -> tuple[list, dict]:
    """
    Fetch runners for one race.
    Returns (runners_list, debug_info_dict).
    Tries multiple endpoint + param combinations, logs all attempts.
    """
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
            "got_data": data is not None,
            "runners_found": len(runners),
            "top_keys": list(data.keys())[:8] if isinstance(data, dict) else (
                list(data[0].keys())[:8] if isinstance(data, list) and data and isinstance(data[0], dict) else []),
        })
        if data and not runners:
            # Store a sample of raw data to help diagnose
            debug["raw_samples"].append({"label": label, "sample": str(data)[:500]})
        return runners

    # Attempt 1: fields by raceId
    if rid:
        runners = _try("form/fields", {"raceId": rid}, f"fields?raceId={rid}")
        if runners: return runners, debug

    # Attempt 2: fields by date+track+raceNumber
    if ds and track and rnum:
        runners = _try("form/fields", {"meetingDate": ds, "track": track, "raceNumber": rnum},
                       f"fields?date={ds}&track={track}&raceNum={rnum}")
        if runners: return runners, debug

    # Attempt 3: form (past form endpoint also contains current field)
    if rid:
        runners = _try("form/form", {"raceId": rid}, f"form?raceId={rid}")
        if runners: return runners, debug

    if ds and track and rnum:
        runners = _try("form/form", {"meetingDate": ds, "track": track, "raceNumber": rnum},
                       f"form?date={ds}&track={track}&raceNum={rnum}")
        if runners: return runners, debug

    # Attempt 4: re-fetch meeting and pull race's embedded runners
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
                embedded = []
                for rkey in ("runners","fields","horses"):
                    embedded = r.get(rkey, [])
                    if embedded: break
                debug["attempts"].append({"label": f"meeting embed rnum={rnum}", "runners_found": len(embedded)})
                if embedded: return embedded, debug

    return [], debug


def fetch_form_for_race(race: dict) -> list:
    ds    = race.get("_meetingDate", "")
    track = race.get("_meetingName", "")
    rnum  = str(race.get("raceNumber") or race.get("number") or "1")
    rid   = get_race_id(race)

    if rid:
        data = pf_get("form/form", {"raceId": rid}, silent=True)
        rows = extract_runners_from_payload(data) if data else []
        if rows: return rows

    if ds and track and rnum:
        data = pf_get("form/form", {"meetingDate": ds, "track": track, "raceNumber": rnum})
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
    "closing_speed":      24,
    "speed_rating":       16,
    "recent_form":        12,
    "class_differential": 9,
    "in_running_luck":    8,
    "pace_dynamics":      7,
    "weight_penalty":     5,
    "barrier_position":   4,
    "jt_combination":     6,
    "track_record":       5,
    "distance_record":    4,
}
MAX_SCORE = sum(FACTOR_WEIGHTS.values())
FACTOR_LBLS = {
    "closing_speed":       "Closing Speed",
    "speed_rating":        "Speed Rating",
    "recent_form":         "Recent Form",
    "class_differential":  "Class",
    "in_running_luck":     "Unlucky",
    "pace_dynamics":       "Pace Fit",
    "weight_penalty":      "Weight",
    "barrier_position":    "Barrier",
    "jt_combination":      "J+T Combo",
    "track_record":        "Track",
    "distance_record":     "Distance",
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
        pos_score=max(0,(1-(pos-1)/field))*16
        margin_score=max(0,(1-margin/12))*8 if pos!=1 else 8
        scores.append(min(pos_score+margin_score,24))
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
    if tempo=="HOT":
        score+= 2.0 if pace_pos>=4 else 0.5 if pace_pos==3 else -1.5
    elif tempo=="SOFT":
        score+= 2.0 if pace_pos<=2 else 0.2 if pace_pos==3 else -1.0
    elif tempo=="GENUINE":
        score+= 0.5 if pace_pos==3 else 0
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
    dist=safe_float(runner.get("distance") or runner.get("raceDistance") or 1200)
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
    priced=[(r,safe_float(r.get("priceSP") or r.get("fixedOddsWin") or r.get("price") or 0)) for r in runners]
    priced=[(r,p) for r,p in priced if p>1.01]
    if len(priced)<2: return {}
    raw_sum=sum(1/p for _,p in priced)
    out={}
    for r,sp in priced:
        hid=get_horse_id(r); raw=1/sp; true=raw/raw_sum
        out[hid]={"sp":sp,"raw_pct":round(raw*100,2),"true_pct":round(true*100,2),
                  "fair_odds":round(1/true,2),"overround":round(raw_sum*100,1)}
    return out

def compute_model_prob(runner, rating, pf_r={}):
    signals,weights=[],[]
    pf_px=safe_float(pf_r.get("pfAiPrice") or pf_r.get("modelPrice") or 0)
    if pf_px>1.0: signals.append(1/pf_px); weights.append(4.5)
    rat_pct=rating.get("pct",50)/100 if rating else 0.5
    rat_prob=max(0.01,min(0.95,(rat_pct**1.5)*0.4))
    signals.append(rat_prob); weights.append(1.5)
    cw=safe_float(runner.get("winPct",0))/100
    if cw>0: signals.append(cw); weights.append(2.0)
    tr=runner.get("trackRecord") or {}
    ts=safe_float(tr.get("starts",0)); tw2=safe_float(tr.get("firsts",0))
    if ts>=3: signals.append(tw2/ts); weights.append(1.5)
    dr=runner.get("distanceRecord") or {}
    ds2=safe_float(dr.get("starts",0)); dw=safe_float(dr.get("firsts",0))
    if ds2>=3: signals.append(dw/ds2); weights.append(1.3)
    tj=runner.get("trainerJockeyA2E_Career") or {}
    tj_sr=safe_float(tj.get("strikeRate",0))/100
    if safe_float(tj.get("runners",0))>=10 and tj_sr>0: signals.append(tj_sr); weights.append(1.2)
    ls_pos=safe_float((runner.get("lastStart") or {}).get("finishingPosition",99))
    if ls_pos==1: signals.append(min(cw*2.5+0.05,0.5)); weights.append(0.8)
    elif ls_pos>=8: signals.append(max(cw*0.5,0.01)); weights.append(0.5)
    if not signals: return 0.05
    total_w=sum(weights)
    return min(max(round(sum(s*w for s,w in zip(signals,weights))/total_w,5),0.005),0.95)

def normalise_field(runners, ratings, pf_ratings):
    raw={get_horse_id(r): compute_model_prob(r,ratings.get(get_horse_id(r),{}),pf_ratings.get(get_horse_id(r),{})) for r in runners}
    total=sum(raw.values())
    if total<=0: return raw
    return {k:round(v/total,5) for k,v in raw.items()}

def assess_value(model_prob, true_mkt_pct, sp, rating_pct, tj_a2e, min_rating, min_edge, min_tj_a2e):
    mkt=true_mkt_pct/100
    edge=model_prob-mkt
    edge_pct=round(edge*100,1)
    ev_unit=model_prob*(sp-1)-(1-model_prob)
    gates={"edge":edge>(min_edge/100),"rating":rating_pct>=min_rating,"tj":tj_a2e>=min_tj_a2e,
           "odds":st.session_state.min_odds<=sp<=st.session_state.max_odds}
    bet=all(gates.values())
    reasons=[]
    if not gates["edge"]:   reasons.append(f"Edge {edge_pct}% < min {min_edge}%")
    if not gates["rating"]: reasons.append(f"Rating {rating_pct}% < min {min_rating}%")
    if not gates["tj"]:     reasons.append(f"J+T A2E {round(tj_a2e,2)} < min {min_tj_a2e}")
    if not gates["odds"]:   reasons.append(f"SP ${sp} outside ${st.session_state.min_odds}–${st.session_state.max_odds}")
    return {"bet":bet,"gates":gates,"edge_pct":edge_pct,"model_pct":round(model_prob*100,1),
            "market_pct":round(mkt*100,1),"ev_unit":round(ev_unit,3),"ev_pct":round(ev_unit*100,1),"reasons":reasons}


# ─── SPEEDMAP ────────────────────────────────────────────────────────────────
PACE_POSITIONS={1:"Leader",2:"On Pace",3:"Midfield",4:"Back",5:"Rear"}
PACE_COLORS={"Leader":"var(--red)","On Pace":"var(--amber)","Midfield":"var(--blue-mid)",
              "Back":"var(--text4)","Rear":"var(--text4)"}

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
    elif n==2: return {"tempo":"GENUINE","pill":"pill-amber","desc":"Two leaders — honest tempo. All styles viable.","strategy":"Slight lean toward on-pace runners."}
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
    <div class="sb-brand">
      <div class="sb-logo"><span>🏇</span> Racing Edge</div>
      <div class="sb-sub">PuntingForm API v2</div>
      <span class="sb-version">v2.2.0</span>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sb-sec">API Connection</div>', unsafe_allow_html=True)
    try: secret_key = st.secrets.get("PUNTINGFORM_API_KEY","")
    except: secret_key=""

    api_key=st.text_input("API Key",type="password",
        value=st.session_state.api_key or secret_key,
        placeholder="Paste PuntingForm API key...")
    if api_key!=st.session_state.api_key:
        st.session_state.api_key=api_key
        st.session_state.meetings=[]

    if st.session_state.api_key:
        st.markdown('<div class="sb-status-ok">Connected</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="sb-status-err">No key entered</div>',unsafe_allow_html=True)

    st.markdown('<div class="sb-sec">Race Selection</div>',unsafe_allow_html=True)
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
            f'<div style="background:#052e16;border:1px solid #166534;border-radius:8px;padding:10px 14px;margin-top:8px">'
            f'<div style="color:#4ade80;font-family:\'JetBrains Mono\',monospace;font-size:.78rem;font-weight:600">'
            f'✓ {n} meeting{"s" if n!=1 else ""} loaded</div>'
            f'<div style="color:#16a34a;font-family:\'JetBrains Mono\',monospace;font-size:.66rem;margin-top:2px">{pf_date(race_date)}</div>'
            f'</div>',unsafe_allow_html=True)
    elif st.session_state.fetch_status=="empty":
        st.markdown(
            '<div style="background:#422006;border:1px solid #78350f;border-radius:8px;padding:10px 14px;margin-top:8px">'
            '<div style="color:#fb923c;font-family:\'JetBrains Mono\',monospace;font-size:.78rem">⚠ No meetings found</div>'
            '</div>',unsafe_allow_html=True)

    st.markdown('<div class="sb-sec">Staking</div>',unsafe_allow_html=True)
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

    st.markdown('<div class="sb-sec">Bet Filters</div>',unsafe_allow_html=True)
    st.session_state.min_odds=st.number_input("Min Odds",value=st.session_state.min_odds,step=0.5,min_value=1.01)
    st.session_state.max_odds=st.number_input("Max Odds",value=st.session_state.max_odds,step=5.0)
    st.session_state.min_rating=st.slider("Min Rating %",0,100,st.session_state.min_rating)
    st.session_state.min_edge=st.slider("Min Edge %",0.0,20.0,st.session_state.min_edge,0.5)
    st.session_state.min_tj_a2e=st.slider("Min J+T A2E",0.0,2.5,st.session_state.min_tj_a2e,0.1)

    if st.session_state.bet_log:
        bpct=st.session_state.bank/st.session_state.starting_bank*100 if st.session_state.starting_bank else 100
        clr="#4ade80" if bpct>=100 else "#fb923c" if bpct>=85 else "#f87171"
        st.markdown(
            f'<div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:12px 14px;margin-top:12px">'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:.65rem;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">Bankroll</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:1.4rem;font-weight:700;color:#f1f5f9">${st.session_state.bank:.0f}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:.72rem;color:{clr};margin-top:3px">{bpct-100:+.1f}% vs start</div>'
            f'</div>',unsafe_allow_html=True)


# ─── TABS ─────────────────────────────────────────────────────────────────────
TAB_RACES, TAB_ANALYSIS, TAB_STAKING, TAB_BANKROLL, TAB_DEBUG = st.tabs([
    "🏟  Meetings & Races","📊  Race Analysis","💰  Staking & Bets","📈  Bankroll","🔧  Debug"
])


# ════════════════════════════════════════════════════════════════
# TAB 1: MEETINGS & RACES
# ════════════════════════════════════════════════════════════════
with TAB_RACES:
    st.markdown("""<div class="page-hdr"><div>
      <div class="page-title">Meetings & Races</div>
      <div class="page-sub">Expand a meeting to load its races, then click Load on a race</div>
    </div></div>""",unsafe_allow_html=True)

    if not st.session_state.api_key:
        st.markdown('<div class="alert alert-amber">Enter your PuntingForm API key in the sidebar to begin.</div>',unsafe_allow_html=True)
    elif not st.session_state.meetings:
        st.markdown("""<div class="empty-state">
          <div class="empty-icon">🏇</div>
          <div class="empty-title">No meetings loaded</div>
          <div class="empty-sub">Click "Fetch Meetings" in the sidebar.</div>
        </div>""",unsafe_allow_html=True)

    meetings=st.session_state.meetings
    if meetings:
        total_loaded=sum(len(m.get("races",[])) for m in meetings if m.get("_races_loaded"))
        st.markdown(
            f'<div class="card-blue" style="display:flex;align-items:center;gap:24px;margin-bottom:20px">'
            f'<div><div class="dl-label">Meetings</div><div class="dl-value blue">{len(meetings)}</div></div>'
            f'<div style="width:1px;height:32px;background:var(--blue-m)"></div>'
            f'<div><div class="dl-label">Date</div><div class="dl-value blue" style="font-size:.9rem">{pf_date(race_date)}</div></div>'
            f'<div style="width:1px;height:32px;background:var(--blue-m)"></div>'
            f'<div><div class="dl-label">Races loaded</div><div class="dl-value blue">{total_loaded}</div></div>'
            f'</div>',unsafe_allow_html=True)

        state_badge_map={"NSW":"pill-blue","VIC":"pill-blue","QLD":"pill-amber",
                         "SA":"pill-green","WA":"pill-teal","TAS":"pill-muted",
                         "NT":"pill-amber","ACT":"pill-muted"}

        for mi, meeting in enumerate(meetings):
            name  = meeting.get("_name","Unknown")
            state = meeting.get("_state","")
            cond  = meeting.get("trackCondition") or meeting.get("going") or ""

            if state_filter and state.upper() not in [s.upper() for s in state_filter]:
                continue

            state_badge=state_badge_map.get(state.upper(),"pill-muted")
            races_loaded=meeting.get("_races_loaded",False)
            races=meeting.get("races",[])
            n_races=len(races)
            exp_label=f"{name}  ·  {state}  {'·  ' + str(n_races) + ' races' if races_loaded else '(click to load races)'}"

            with st.expander(exp_label,expanded=False):
                if not races_loaded:
                    with st.spinner(f"Loading races for {name}..."):
                        races=fetch_races_for_meeting(meeting, race_date)
                        meeting["races"]=races
                        meeting["_races_loaded"]=True
                        # Update in session state
                        st.session_state.meetings[mi]=meeting
                    if not races:
                        st.markdown(f'<div class="alert alert-red">No races returned for {name}. Check Debug tab for API log.</div>',unsafe_allow_html=True)
                        continue

                meta_html=(f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;'
                           f'padding-bottom:12px;border-bottom:1px solid var(--border)">'
                           f'<span class="pill {state_badge}">{state}</span>')
                if cond: meta_html+=f'<span class="pill pill-muted">{cond}</span>'
                meta_html+=f'<span class="pill pill-dark">{len(races)} races</span></div>'
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
                            f'<div class="race-info">'
                            f'<div class="race-name">{rname}</div>'
                            f'<div class="race-meta">'
                            f'{time_str + "  ·  " if time_str else ""}{rdist}m'
                            f'{("  ·  "+str(rcls)) if rcls else ""}'
                            f'{("  ·  ID:"+rid) if rid else ""}'
                            f'</div></div></div>',unsafe_allow_html=True)
                    with c2:
                        btn_key=f"load_{mi}_{rnum}_{rid}"
                        if st.button("Load →",key=btn_key,use_container_width=True):
                            st.session_state.selected_race=race
                            st.session_state.runners=[]
                            st.session_state.ratings={}
                            st.session_state.pf_ratings={}
                            st.session_state.sectionals={}
                            st.session_state.past_form_by_horse={}

                            with st.spinner(f"Loading runners for R{rnum} {name}..."):
                                runners, dbg=fetch_race_field(race)
                                st.session_state["_last_field_debug"]=dbg
                                if runners:
                                    st.session_state.runners=assign_pace_positions(runners)
                                    st.success(f"✓ {len(runners)} runners loaded — go to Race Analysis tab")
                                else:
                                    # Show diagnostic immediately
                                    st.error("❌ No runners returned. See details below and check Debug tab.")
                                    attempts=dbg.get("attempts",[])
                                    for a in attempts:
                                        status="✓" if a.get("runners_found",0)>0 else "✗"
                                        st.markdown(
                                            f'<div class="debug-box">{status} {a["label"]} → '
                                            f'data={a.get("got_data","?")} runners={a.get("runners_found",0)} '
                                            f'keys={a.get("top_keys",[])}</div>',
                                            unsafe_allow_html=True)
                                    for s in dbg.get("raw_samples",[]):
                                        st.markdown(f'<div class="debug-box"><strong>{s["label"]}:</strong> {s["sample"]}</div>',unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# TAB 2: RACE ANALYSIS
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
        st.markdown('<div class="alert alert-amber">No runners loaded. Click Load on a race in the Meetings tab. Check the Debug tab if it keeps failing.</div>',unsafe_allow_html=True)
        st.stop()

    rname=race.get("raceName") or race.get("name") or "Race"
    rdist=race.get("raceDistance") or race.get("distance") or "?"
    rtrk=race.get("_meetingName") or race.get("meetingName") or ""
    rcond=race.get("trackCondition") or race.get("going") or ""
    rcls=race.get("raceClass") or ""
    rnum=race.get("raceNumber") or race.get("number") or "?"
    rid=get_race_id(race)
    rds=race.get("_meetingDate","")
    rprize=race.get("prizeMoney") or race.get("prize") or 0

    st.markdown(f"""<div class="page-hdr"><div>
      <div class="page-title">Race {rnum} — {rname}</div>
      <div class="page-sub">{rtrk}  ·  {rdist}m  ·  {rcls or "Open"}  ·  {rcond or "Cond TBC"}  ·  {rds}  ·  {len(runners)} runners</div>
    </div><span class="pill pill-dark">{len(runners)} runners</span></div>""",unsafe_allow_html=True)

    col_rate,col_info=st.columns([2,5])
    with col_rate:
        run_ratings=st.button("⚡  Run Full Analysis",use_container_width=True)
    with col_info:
        st.markdown('<div style="padding-top:9px;font-size:.8rem;color:var(--text3)">Fetches past form, PF ratings & sectionals. Rates all runners across 11 factors.</div>',unsafe_allow_html=True)

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
        if not pf_new: msgs.append("PF AI unavailable (subscription tier?)")
        st.success("  ·  ".join(msgs))

    ratings=st.session_state.ratings
    pf_ratings=st.session_state.pf_ratings
    secs=st.session_state.sectionals
    past_all=st.session_state.past_form_by_horse
    mkt=frame_market(runners)
    tempo_info=classify_tempo(runners)
    field_probs=normalise_field(runners,ratings,pf_ratings) if ratings else {}

    # ── SPEEDMAP ──
    st.markdown('<div class="section-hdr">Speedmap & Tempo</div>',unsafe_allow_html=True)
    tc={"HOT":"pill-red","GENUINE":"pill-amber","SOFT":"pill-blue","MODERATE":"pill-muted"}.get(tempo_info["tempo"],"pill-muted")
    st.markdown(
        f'<div class="card-blue" style="display:flex;align-items:center;gap:16px;margin-bottom:14px">'
        f'<span class="pill {tc}" style="font-size:.72rem;padding:4px 14px;flex-shrink:0">{tempo_info["tempo"]} PACE</span>'
        f'<div><div style="font-size:.88rem;color:var(--text2);font-weight:600">{tempo_info["desc"]}</div>'
        f'<div style="font-size:.77rem;color:var(--text3);margin-top:3px">Strategy: {tempo_info["strategy"]}</div></div>'
        f'</div>',unsafe_allow_html=True)

    positions={1:[],2:[],3:[],4:[],5:[]}
    for r in runners:
        pp=safe_int(r.get("pacePosition",3))
        positions[min(max(pp,1),5)].append(get_runner_name(r))
    for pp,lbl in PACE_POSITIONS.items():
        horses=positions.get(pp,[])
        if not horses: continue
        color=PACE_COLORS.get(lbl,"var(--text3)")
        st.markdown(
            f'<div class="smap-row">'
            f'<div class="smap-pos" style="color:{color}">{lbl}</div>'
            f'<div class="smap-horses">{" · ".join(horses)}</div>'
            f'<div class="smap-cnt">{len(horses)}</div>'
            f'</div>',unsafe_allow_html=True)

    st.markdown('<hr>',unsafe_allow_html=True)

    # ── MARKET FRAME ──
    st.markdown('<div class="section-hdr">Market Frame</div>',unsafe_allow_html=True)
    if not mkt:
        st.markdown('<div class="alert alert-amber">No SP prices yet — market frame unavailable. Prices are published closer to race time.</div>',unsafe_allow_html=True)
    else:
        sample=next(iter(mkt.values()))
        overround=sample["overround"]
        st.markdown(f'<div class="card-blue" style="font-size:.8rem;color:var(--blue-dark);margin-bottom:14px">'
                    f'Book overround: <strong>{overround}%</strong>  —  True% = de-vigged probability  ·  Edge = Model% minus True%</div>',
                    unsafe_allow_html=True)

        sorted_by_sp=sorted(runners,key=lambda x:safe_float(x.get("priceSP") or x.get("fixedOddsWin") or 99))
        rows=""
        for rank,r in enumerate(sorted_by_sp):
            hid=get_horse_id(r); mf=mkt.get(hid)
            if not mf: continue
            name=get_runner_name(r)
            sp=mf["sp"]; raw=mf["raw_pct"]; true=mf["true_pct"]; fair=mf["fair_odds"]
            mp=field_probs.get(hid,0)
            pfr=pf_ratings.get(hid,{}); pf_px=safe_float(pfr.get("pfAiPrice") or 0)
            diff=round(mp*100-true,1) if mp else None
            is_val=diff is not None and diff>0
            edge_html="—"
            if diff is not None:
                cls="edge-pos" if diff>0 else "edge-neg" if diff<0 else "edge-neu"
                edge_html=f'<span class="{cls}">{("+" if diff>=0 else "")}{diff}%</span>'
            bar_w=min(int(true*3.5),100)
            bar_c="#16a34a" if is_val else "#3b82f6"
            bar_html=f'<div class="prob-bar" style="width:60px"><div class="prob-fill" style="width:{bar_w}%;background:{bar_c}"></div></div>'
            badges=""
            if rank==0: badges+='<span class="mkt-fav">Fav</span>'
            if is_val: badges+='<span class="mkt-val">Value</span>'
            pf_cell=f"${pf_px:.2f}" if pf_px>1 else "—"
            mp_cell=f"{mp*100:.1f}%" if mp else "—"
            row_cls="val-row" if is_val else ("fav-row" if rank==0 else "")
            rows+=(f'<tr class="{row_cls}">'
                   f'<td style="color:var(--text4);font-size:.72rem">{rank+1}</td>'
                   f'<td><span class="mkt-horse">{name}</span>{badges}</td>'
                   f'<td style="color:var(--blue);font-weight:700">${sp:.2f}</td>'
                   f'<td style="color:var(--text3)">{raw}%</td>'
                   f'<td><div style="display:flex;align-items:center;gap:8px"><span style="font-weight:600">{true}%</span>{bar_html}</div></td>'
                   f'<td style="color:var(--text2)">${fair:.2f}</td>'
                   f'<td style="color:var(--blue)">{pf_cell}</td>'
                   f'<td style="color:var(--blue-mid)">{mp_cell}</td>'
                   f'<td>{edge_html}</td></tr>')

        st.markdown(
            f'<div class="card" style="padding:0;overflow:hidden"><table class="mkt-table">'
            f'<thead><tr><th>#</th><th>Horse</th><th>SP</th><th>Raw%</th>'
            f'<th>True%</th><th>Fair Odds</th><th>PF AI</th><th>Model%</th><th>Edge</th>'
            f'</tr></thead><tbody>{rows}</tbody></table></div>',unsafe_allow_html=True)

    st.markdown('<hr>',unsafe_allow_html=True)

    # ── RUNNER CARDS ──
    st.markdown('<div class="section-hdr">Runner-by-Runner Analysis</div>',unsafe_allow_html=True)

    if ratings:
        summary_rows=[]
        for r in runners:
            hid=get_horse_id(r)
            name=get_runner_name(r)
            rtg=ratings.get(hid,{})
            mp=field_probs.get(hid,0)
            mf=mkt.get(hid,{})
            price=safe_float(r.get("priceSP") or r.get("fixedOddsWin") or 0)
            diff=round(mp*100-mf.get("true_pct",0),1) if mp and mf else None
            summary_rows.append({"Horse":name,"Barrier":r.get("barrierNumber") or r.get("barrier") or "?",
                "Rating":f"{rtg.get('pct',0):.1f}%","Composite":f"{rtg.get('composite',0):.1f}",
                "Model%":f"{mp*100:.1f}%" if mp else "—","SP":f"${price:.2f}" if price>0 else "—",
                "Edge":f"+{diff}%" if diff is not None and diff>0 else (f"{diff}%" if diff is not None else "—"),
                "Bet":"✓" if (diff is not None and diff>(st.session_state.min_edge/100) and rtg.get("pct",0)>=st.session_state.min_rating) else "",})
        summary_rows.sort(key=lambda x:float(x["Composite"].replace("—","0")),reverse=True)
        st.dataframe(pd.DataFrame(summary_rows),use_container_width=True,hide_index=True)
        st.markdown('<div style="margin-bottom:20px"></div>',unsafe_allow_html=True)

    def sort_key(r):
        hid=get_horse_id(r)
        return field_probs.get(hid,0) if field_probs else -safe_float(r.get("priceSP") or 99)

    for rank,runner in enumerate(sorted(runners,key=sort_key,reverse=True),1):
        hid=get_horse_id(runner)
        name=get_runner_name(runner)
        barrier=runner.get("barrierNumber") or runner.get("barrier") or "?"
        jockey=(runner.get("jockey") or {}).get("fullName") or runner.get("jockeyName") or "—"
        trainer=(runner.get("trainer") or {}).get("fullName") or runner.get("trainerName") or "—"
        weight=runner.get("weightTotal") or runner.get("weightCarried") or runner.get("handicapWeight") or "—"
        age=runner.get("age") or runner.get("horseAge") or ""
        sex=runner.get("sex") or runner.get("horseSex") or ""
        price=safe_float(runner.get("priceSP") or runner.get("fixedOddsWin") or runner.get("price") or 0)
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
        mp_str=f"  ·  Model {round(mp*100,1)}%" if mp else ""
        mkt_str=f"  ·  Mkt {mf.get('true_pct','?')}%" if mf else ""
        edge_str=f"  ·  Edge {'+' if verdict and verdict['edge_pct']>=0 else ''}{verdict['edge_pct']}%" if verdict else ""
        bet_flag="  ✓ BET" if (verdict and verdict["bet"]) else ""
        exp_label=f"#{rank}  {name}   B{barrier}   {sp_str}{mp_str}{mkt_str}{edge_str}{bet_flag}"
        is_expanded=rank<=2 or (verdict is not None and verdict["bet"])

        with st.expander(exp_label,expanded=is_expanded):
            col_left,col_right=st.columns([3,2],gap="medium")

            with col_left:
                pace_pill={"Leader":"pill-red","On Pace":"pill-amber","Midfield":"pill-blue","Back":"pill-muted","Rear":"pill-muted"}.get(pace_lbl,"pill-muted")
                meta_line='<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px">'
                meta_line+=f'<span class="pill pill-muted">B{barrier}</span>'
                meta_line+=f'<span class="pill {pace_pill}">{pace_lbl}</span>'
                if weight and str(weight)!="—": meta_line+=f'<span class="pill pill-muted">{weight}kg</span>'
                if age: meta_line+=f'<span class="pill pill-muted">{age}yo</span>'
                if sex: meta_line+=f'<span class="pill pill-muted">{sex}</span>'
                meta_line+="</div>"
                st.markdown(meta_line,unsafe_allow_html=True)

                st.markdown(
                    f'<div style="font-size:.82rem;color:var(--text2);line-height:2.1;margin-bottom:14px">'
                    f'<span style="color:var(--text4);font-size:.65rem;text-transform:uppercase;letter-spacing:.07em;font-weight:700">Jockey</span>'
                    f'&nbsp;&nbsp;<span style="font-weight:600">{jockey}</span><br>'
                    f'<span style="color:var(--text4);font-size:.65rem;text-transform:uppercase;letter-spacing:.07em;font-weight:700">Trainer</span>'
                    f'&nbsp;&nbsp;<span style="font-weight:600">{trainer}</span></div>',
                    unsafe_allow_html=True)

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
                    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px">'
                    +f'<div class="card-sm"><div class="dl-label">Career Win%</div><div class="dl-value {"green" if cw>20 else ""}">{cw:.1f}%</div></div>'
                    +f'<div class="card-sm"><div class="dl-label">Career Place%</div><div class="dl-value">{cp:.1f}%</div></div>'
                    +f'<div class="card-sm"><div class="dl-label">Track W-P-T/{int(ts)}</div><div class="dl-value {"green" if tsr>20 else ""}">{tsr}%W {tplr}%P</div></div>'
                    +f'<div class="card-sm"><div class="dl-label">Distance W-P-T/{int(ds2)}</div><div class="dl-value {"green" if dsr>20 else ""}">{dsr}%W {dplr}%P</div></div>'
                    +'</div>',unsafe_allow_html=True)

                if tj_runs>=5:
                    a2e_col="green" if tj_a2e>=1.1 else "red" if tj_a2e<0.8 else ""
                    st.markdown(
                        f'<div class="card-sm" style="margin-bottom:14px">'
                        f'<div class="dl-label" style="margin-bottom:7px">J+T Combination — {int(tj_runs)} runs</div>'
                        f'<div style="display:flex;gap:20px;font-family:\'JetBrains Mono\',monospace;font-size:.84rem">'
                        f'<div>SR <span style="font-weight:700">{tj_sr:.1f}%</span></div>'
                        f'<div>A2E <span class="dl-value {a2e_col}" style="font-size:.9rem">{tj_a2e:.2f}</span></div>'
                        f'</div></div>',unsafe_allow_html=True)

                pf_px=safe_float(pfr.get("pfAiPrice") or pfr.get("modelPrice") or 0)
                pf_rank=pfr.get("pfAiRank") or pfr.get("rank")
                if pf_px>1 or pf_rank:
                    pf_val=price>0 and pf_px>price
                    st.markdown(
                        f'<div class="card-blue" style="margin-bottom:14px">'
                        f'<div class="dl-label" style="margin-bottom:8px;color:var(--blue-dark)">PF AI Model</div>'
                        f'<div style="display:flex;gap:20px;flex-wrap:wrap">'
                        +(f'<div><div class="dl-label">AI Price</div><div class="dl-value blue" style="font-size:1.15rem">${pf_px:.2f}</div></div>' if pf_px>1 else "")
                        +(f'<div><div class="dl-label">AI Rank</div><div class="dl-value blue">#{pf_rank}</div></div>' if pf_rank else "")
                        +f'</div>'
                        +(f'<div style="font-size:.72rem;color:var(--green);margin-top:6px;font-weight:600">AI price > SP — value signal</div>' if pf_val else "")
                        +f'</div>',unsafe_allow_html=True)

                sec_rtg=safe_float(sec_d.get("sectionalRating") or sec_d.get("closing600Rating") or 0)
                sec_600=safe_float(sec_d.get("averageClosing600") or sec_d.get("avg600") or 0)
                if sec_rtg>0 or sec_600>0:
                    st.markdown(
                        f'<div class="card-sm" style="margin-bottom:14px">'
                        f'<div class="dl-label" style="margin-bottom:7px">Sectionals</div>'
                        f'<div style="display:flex;gap:20px;font-family:\'JetBrains Mono\',monospace;font-size:.84rem">'
                        +(f'<div>Rating <span style="color:var(--blue);font-weight:700">{sec_rtg:.1f}</span></div>' if sec_rtg>0 else "")
                        +(f'<div>Avg 600m <span style="color:var(--blue);font-weight:700">{sec_600:.2f}s</span></div>' if sec_600>0 else "")
                        +f'</div></div>',unsafe_allow_html=True)

                if rating:
                    r_pct=rating["pct"]
                    r_col="var(--green)" if r_pct>=65 else "var(--amber)" if r_pct>=45 else "var(--red)"
                    st.markdown(
                        f'<div class="dl-label" style="margin-bottom:6px">Composite Rating</div>'
                        f'<div style="display:flex;align-items:baseline;gap:10px;margin-bottom:8px">'
                        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:1.9rem;font-weight:700;color:{r_col}">{rating["composite"]}</span>'
                        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:.72rem;color:var(--text4)">/ {MAX_SCORE}  ({r_pct}%)</span>'
                        f'</div>'
                        f'<div class="prob-bar" style="margin-bottom:16px"><div class="prob-fill" style="width:{r_pct}%;background:{r_col}"></div></div>',
                        unsafe_allow_html=True)
                    for fkey,fmax in FACTOR_WEIGHTS.items():
                        val=rating.get(fkey,0); pct=int(val/fmax*100) if fmax else 0
                        bc="#16a34a" if pct>=65 else "#3b82f6" if pct>=35 else "#dc2626"
                        st.markdown(
                            f'<div class="comp-row">'
                            f'<span class="comp-name">{FACTOR_LBLS[fkey]}</span>'
                            f'<div class="comp-bar"><div class="comp-fill" style="width:{pct}%;background:{bc}"></div></div>'
                            f'<span class="comp-score">{val:.1f}/{fmax}</span></div>',
                            unsafe_allow_html=True)

                if past:
                    st.markdown('<div class="dl-label" style="margin-top:16px;margin-bottom:8px">Recent Form</div>',unsafe_allow_html=True)
                    form_html='<div style="display:flex;gap:6px;flex-wrap:wrap">'
                    for run in past[:6]:
                        pos=safe_int(run.get("finishingPosition",0))
                        trk=(run.get("meetingName") or "")[:3].upper()
                        dst=safe_int(run.get("raceDistance") or 0)
                        box_c="#16a34a" if pos==1 else "#3b82f6" if pos<=3 else "#6b7280" if pos<=5 else "#dc2626"
                        form_html+=(f'<div style="text-align:center;background:var(--surface2);border:1px solid var(--border);'
                                    f'border-radius:var(--r);padding:6px 10px;min-width:42px">'
                                    f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:1.1rem;font-weight:700;color:{box_c}">{pos}</div>'
                                    f'<div style="font-size:.58rem;color:var(--text4)">{trk}</div>'
                                    f'<div style="font-size:.58rem;color:var(--text4)">{dst}m</div></div>')
                    form_html+='</div>'
                    st.markdown(form_html,unsafe_allow_html=True)

                nk=f"{hid}_{rid}"
                note=st.text_area("Notes",value=st.session_state.notes.get(nk,""),
                    key=f"note_{hid}_{rank}",height=56,placeholder="Add notes, intel...")
                st.session_state.notes[nk]=note

            with col_right:
                if not rating and not mf:
                    st.markdown('<div class="alert alert-blue">Click "Run Full Analysis" to compute ratings.</div>',unsafe_allow_html=True)
                elif price<=1:
                    st.markdown('<div class="alert alert-amber">No SP price yet.</div>',unsafe_allow_html=True)
                else:
                    if mf and mp:
                        tp=mf["true_pct"]; rp=mf["raw_pct"]; fair=mf["fair_odds"]; mp_p=round(mp*100,1)
                        diff=round(mp_p-tp,1); dc="var(--green)" if diff>0 else "var(--red)"
                        st.markdown(
                            f'<div class="card" style="margin-bottom:14px">'
                            f'<div class="dl-label" style="margin-bottom:14px;font-weight:700">Probability Breakdown</div>'
                            f'<div class="prob-grid">'
                            f'<div class="prob-cell-blue"><div class="dl-label">SP Odds</div><div class="dl-value blue" style="font-size:1.2rem">${price:.2f}</div></div>'
                            f'<div class="prob-cell-blue"><div class="dl-label">Fair Odds</div><div class="dl-value" style="font-size:1.2rem">${fair:.2f}</div></div>'
                            f'<div class="prob-cell"><div class="dl-label">Raw Mkt%</div><div class="dl-value" style="font-size:.95rem;color:var(--text3)">{rp}%</div></div>'
                            f'<div class="prob-cell"><div class="dl-label">True Mkt%</div><div class="dl-value" style="font-size:.95rem">{tp}%</div></div>'
                            f'<div class="prob-cell-blue"><div class="dl-label">Model%</div><div class="dl-value blue" style="font-size:.95rem;font-weight:700">{mp_p}%</div></div>'
                            f'<div class="prob-cell-blue"><div class="dl-label">Edge</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:.95rem;font-weight:700;color:{dc}">{"+" if diff>=0 else ""}{diff}%</div></div>'
                            f'</div>'
                            f'<div style="margin-top:10px;font-size:.68rem;color:var(--text4)">Book: {mf["overround"]}%  ·  EV/unit: {verdict["ev_pct"] if verdict else "—"}%</div>'
                            f'</div>',unsafe_allow_html=True)

                    if verdict:
                        g=verdict["gates"]
                        def gp(ok): return ("pill-green","Pass") if ok else ("pill-red","Fail")
                        g1c,g1t=gp(g["edge"]); g2c,g2t=gp(g["rating"]); g3c,g3t=gp(g["tj"]); g4c,g4t=gp(g["odds"])
                        gate_detail={"edge":f"Edge {'+' if verdict['edge_pct']>=0 else ''}{verdict['edge_pct']}% vs min {st.session_state.min_edge}%",
                            "rating":f"Rating {rating['pct'] if rating else '?'}% vs min {st.session_state.min_rating}%",
                            "tj":f"A2E {tj_a2e:.2f} vs min {st.session_state.min_tj_a2e}",
                            "odds":f"SP ${price:.2f}  range ${st.session_state.min_odds}–${st.session_state.max_odds}"}
                        st.markdown(
                            f'<div class="card" style="margin-bottom:14px">'
                            f'<div class="dl-label" style="margin-bottom:12px;font-weight:700">Value Gates</div>'
                            +"".join([f'<div class="gate-row"><span class="pill {pc}" style="width:42px;justify-content:center;flex-shrink:0">{pt}</span>'
                                      f'<span class="gate-lbl">{lbl}</span><span class="gate-detail">{gate_detail[gk]}</span></div>'
                                      for gk,(pc,pt),lbl in [("edge",(g1c,g1t),"Edge"),("rating",(g2c,g2t),"Min rating"),
                                                             ("tj",(g3c,g3t),"J+T A2E"),("odds",(g4c,g4t),"SP range")]])
                            +f'</div>',unsafe_allow_html=True)

                        if verdict["bet"]:
                            rec=compute_stake(st.session_state.bank,mp,price,st.session_state.staking_method,
                                st.session_state.kelly_fraction,st.session_state.flat_pct,
                                st.session_state.level_stake,st.session_state.max_stake_pct)
                            ev_c="#4ade80" if rec["ev"]>=0 else "#f87171"
                            st.markdown(
                                f'<div class="stake-card">'
                                f'<div class="stake-label">{st.session_state.staking_method}</div>'
                                f'<div class="stake-amount">${rec["stake"]:.2f}</div>'
                                f'<div class="stake-detail" style="color:{ev_c}">EV ${rec["ev"]:+.2f}  ·  {rec["ev_pct"]:+.1f}%  ·  {rec["pct_bank"]}% of bank</div>'
                                f'<div class="stake-detail">Break-even: {rec["roi_required"]:.1f}% ROI needed</div>'
                                f'</div>',unsafe_allow_html=True)
                            st.markdown(
                                '<div class="bet-banner"><div class="bet-banner-title">✓ BET — All four gates pass</div>'
                                '<div class="bet-banner-sub">Positive edge vs de-vigged market probability</div></div>',
                                unsafe_allow_html=True)
                            if st.button(f"📋  Log bet — {name}",key=f"log_{hid}_{rank}"):
                                add_bet(name,f"{rtrk} R{rnum}",rec["stake"],price,verdict["edge_pct"],verdict["model_pct"])
                                st.success(f"✓ Logged: {name} ${rec['stake']:.2f} @ ${price}")
                        else:
                            st.markdown(f'<div class="alert alert-red">No bet — {"  ·  ".join(verdict["reasons"])}</div>',unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# TAB 3: STAKING & BETS
# ════════════════════════════════════════════════════════════════
with TAB_STAKING:
    st.markdown("""<div class="page-hdr"><div>
      <div class="page-title">Staking & Bet Log</div>
      <div class="page-sub">Methods, discipline rules, bet management</div>
    </div></div>""",unsafe_allow_html=True)

    st.markdown('<div class="section-hdr">Staking Methods</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    for col,title,pill_c,body in [
        (c1,"Kelly Criterion","pill-blue","Mathematically optimal. Stake proportional to edge.<br><br><code>f* = (bp − q) / b</code><br><br><strong>Quarter Kelly (recommended)</strong> retains ~75% of growth rate while dramatically reducing variance."),
        (c2,"Flat Percentage","pill-muted","Fixed % of current bank per bet. Naturally scales down in losing runs, up in winning runs.<br><br>Simpler than Kelly. Ignores edge size."),
        (c3,"Level Stakes","pill-muted","Fixed dollar amount per bet. Easiest for tracking ROI.<br><br>Does not protect bank during drawdowns. Best for evaluating model performance."),
    ]:
        col.markdown(f'<div class="card"><div style="margin-bottom:10px"><span class="pill {pill_c}">{title}</span></div><div style="font-size:.8rem;color:var(--text2);line-height:1.9">{body}</div></div>',unsafe_allow_html=True)

    bpct=st.session_state.bank/st.session_state.starting_bank*100 if st.session_state.starting_bank else 100
    if bpct<70:
        st.markdown(f'<div class="alert alert-red">⚠ Stop-loss — bank at {bpct:.1f}% of start. Halve all stakes until bank recovers above 85%.</div>',unsafe_allow_html=True)
    elif bpct<85:
        st.markdown(f'<div class="alert alert-amber">Bank at {bpct:.1f}% — consider reducing stakes.</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-hdr">Bet Log</div>',unsafe_allow_html=True)
    log=st.session_state.bet_log
    if not log:
        st.markdown('<div class="alert alert-blue">No bets logged yet. Qualifying bets appear here after clicking "Log bet" in the Analysis tab.</div>',unsafe_allow_html=True)
    else:
        settled=[b for b in log if b["result"]!="Pending"]; pending=[b for b in log if b["result"]=="Pending"]
        if settled:
            s_pl=sum(b["pl"] for b in settled); s_stk=sum(b["stake"] for b in settled)
            s_roi=round(s_pl/s_stk*100,1) if s_stk else 0; s_wins=sum(1 for b in settled if b["result"]=="Won")
            pl_c="var(--green)" if s_pl>=0 else "var(--red)"
            st.markdown(f'<div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap">'
                        f'<span style="padding:4px 10px;border-radius:99px;background:var(--surface2);border:1px solid var(--border);font-size:.72rem">{len(settled)} settled</span>'
                        f'<span style="padding:4px 10px;border-radius:99px;background:var(--surface2);border:1px solid var(--border);font-size:.72rem">{len(pending)} pending</span>'
                        f'<span style="padding:4px 10px;border-radius:99px;background:var(--surface2);border:1px solid var(--border);font-size:.72rem;color:{pl_c}">P/L ${s_pl:+.2f}</span>'
                        f'<span style="padding:4px 10px;border-radius:99px;background:var(--surface2);border:1px solid var(--border);font-size:.72rem">ROI {s_roi:+.1f}%</span>'
                        f'<span style="padding:4px 10px;border-radius:99px;background:var(--surface2);border:1px solid var(--border);font-size:.72rem">{s_wins}/{len(settled)} wins</span>'
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
                    st.markdown(f'<div style="padding:9px 0;font-family:\'JetBrains Mono\',monospace;font-size:.8rem">'
                                f'<span style="color:var(--blue);font-weight:700">{bet["horse"]}</span>&nbsp;&nbsp;'
                                f'<span style="color:var(--text3)">${bet["stake"]:.2f} @ {bet["odds"]}</span></div>',unsafe_allow_html=True)
                with c2:
                    if st.button("Won",key=f"won_{idx}"): settle(idx,"Won"); st.rerun()
                with c3:
                    if st.button("Lost",key=f"lst_{idx}"): settle(idx,"Lost"); st.rerun()
                with c4:
                    if st.button("Void",key=f"vd_{idx}"): settle(idx,"Void"); st.rerun()

        if st.button("Clear All Bets",type="secondary"):
            st.session_state.bet_log=[]; st.rerun()


# ════════════════════════════════════════════════════════════════
# TAB 4: BANKROLL
# ════════════════════════════════════════════════════════════════
with TAB_BANKROLL:
    st.markdown("""<div class="page-hdr"><div>
      <div class="page-title">Bankroll Performance</div>
      <div class="page-sub">P/L tracking, ROI, drawdown monitoring</div>
    </div></div>""",unsafe_allow_html=True)

    stats=bankroll_stats()
    if not stats:
        st.markdown("""<div class="empty-state"><div class="empty-icon">📈</div>
          <div class="empty-title">No settled bets yet</div>
          <div class="empty-sub">Results appear here after settling bets in the Staking tab.</div>
        </div>""",unsafe_allow_html=True)
    else:
        pl_c="green" if stats["pl"]>=0 else "red"; roi_c="green" if stats["roi"]>=0 else "red"
        st.markdown(
            f'<div class="metric-grid">'
            f'<div class="metric-card blue"><div class="metric-label">Bank</div><div class="metric-value blue">${stats["bank"]:.0f}</div><div class="metric-sub">Start: ${st.session_state.starting_bank:.0f}</div></div>'
            f'<div class="metric-card {"green" if stats["pl"]>=0 else "red"}"><div class="metric-label">Total P/L</div><div class="metric-value {pl_c}">{("+" if stats["pl"]>=0 else "")}${stats["pl"]:.2f}</div></div>'
            f'<div class="metric-card {"green" if stats["roi"]>=0 else "red"}"><div class="metric-label">ROI</div><div class="metric-value {roi_c}">{("+" if stats["roi"]>=0 else "")}{stats["roi"]:.1f}%</div><div class="metric-sub">On ${stats["staked"]:.0f} staked</div></div>'
            f'<div class="metric-card"><div class="metric-label">Strike Rate</div><div class="metric-value">{stats["sr"]:.1f}%</div><div class="metric-sub">{stats["winners"]}/{stats["n"]} wins</div></div>'
            f'<div class="metric-card"><div class="metric-label">Avg Odds</div><div class="metric-value">{stats["avg_odds"]:.2f}</div></div>'
            f'<div class="metric-card red"><div class="metric-label">Max Drawdown</div><div class="metric-value red">-${abs(stats["max_dd"]):.2f}</div></div>'
            f'</div>',unsafe_allow_html=True)

        settled=[b for b in st.session_state.bet_log if b["result"]!="Pending"]
        if settled:
            st.markdown('<div class="section-hdr">Cumulative P/L</div>',unsafe_allow_html=True)
            pl_vals=[0]+list(pd.Series([b["pl"] for b in settled]).cumsum())
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=list(range(len(pl_vals))),y=pl_vals,mode="lines+markers",
                line=dict(color="#1d4ed8",width=2.5),
                marker=dict(size=5,color=["#16a34a" if v>=0 else "#dc2626" for v in pl_vals]),
                fill="tozeroy",fillcolor="rgba(29,78,216,0.08)"))
            fig.add_hline(y=0,line_dash="dash",line_color="#cbd5e1",line_width=1.5)
            fig.update_layout(paper_bgcolor="white",plot_bgcolor="white",margin=dict(t=10,b=10,l=10,r=10),
                xaxis=dict(title="Bet #",gridcolor="#f1f5f9",color="#64748b"),
                yaxis=dict(title="P/L ($)",gridcolor="#f1f5f9",color="#64748b"),
                height=320,showlegend=False,font=dict(family="Inter, sans-serif"))
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
# TAB 5: DEBUG
# ════════════════════════════════════════════════════════════════
with TAB_DEBUG:
    st.markdown("""<div class="page-hdr"><div>
      <div class="page-title">API Debug</div>
      <div class="page-sub">All API calls this session with status codes and response shape</div>
    </div></div>""",unsafe_allow_html=True)

    st.markdown(f'**Date format being used:** `{pf_date(race_date)}`', unsafe_allow_html=False)

    api_log=st.session_state.get("_api_log",[])
    if not api_log:
        st.markdown('<div class="alert alert-blue">No API calls yet. Fetch meetings to start logging.</div>',unsafe_allow_html=True)
    else:
        for entry in reversed(api_log[-20:]):
            status=entry["status"]
            color="#16a34a" if status==200 else "#dc2626" if status>=400 else "#d97706"
            st.markdown(
                f'<div style="background:#1e293b;border:1px solid #334155;border-radius:6px;padding:10px 14px;margin-bottom:6px;font-family:\'JetBrains Mono\',monospace;font-size:.72rem;color:#94a3b8">'
                f'<span style="color:{color};font-weight:700">[{status}]</span>'
                f'&nbsp;<span style="color:#e2e8f0">{entry["ts"]}</span>'
                f'&nbsp;&nbsp;<span style="color:#60a5fa">{entry["url"].replace(BASE_URL,"")}</span>'
                f'<br>params: {json.dumps(entry["params"])}'
                +( f'<br><span style="color:#f87171">{entry["note"]}</span>' if entry.get("note") else "")
                +f'</div>',unsafe_allow_html=True)

    # Show last runner-fetch debug if available
    dbg=st.session_state.get("_last_field_debug")
    if dbg:
        st.markdown('<div class="section-hdr">Last Runner Fetch Attempts</div>',unsafe_allow_html=True)
        for a in dbg.get("attempts",[]):
            ok=a.get("runners_found",0)>0
            color="#16a34a" if ok else "#dc2626"
            st.markdown(
                f'<div style="background:#1e293b;border:1px solid #334155;border-radius:6px;padding:10px 14px;margin-bottom:6px;font-family:\'JetBrains Mono\',monospace;font-size:.72rem;color:#94a3b8">'
                f'<span style="color:{color};font-weight:700">{"✓" if ok else "✗"}</span>'
                f'&nbsp;<span style="color:#e2e8f0">{a["label"]}</span>'
                f'&nbsp;runners_found=<span style="color:{"#4ade80" if ok else "#f87171"}">{a.get("runners_found",0)}</span>'
                f'&nbsp;top_keys={a.get("top_keys",[])}'
                f'</div>',unsafe_allow_html=True)

        for s in dbg.get("raw_samples",[]):
            st.markdown(f'**Raw sample — {s["label"]}:**',unsafe_allow_html=False)
            st.markdown(f'<div class="debug-box">{s["sample"]}</div>',unsafe_allow_html=True)

    if st.button("Clear debug log"):
        st.session_state["_api_log"]=[]; st.session_state["_last_field_debug"]=None; st.rerun()

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""<div style="text-align:center;padding:48px 0 24px;font-family:'JetBrains Mono',monospace;
font-size:.6rem;color:#cbd5e1;letter-spacing:.14em;text-transform:uppercase">
Racing Edge  ·  Research & Analysis Purposes Only  ·  Gamble Responsibly  ·  1800 858 858  ·  18+
</div>""",unsafe_allow_html=True)
