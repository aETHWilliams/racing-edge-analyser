"""
Racing Edge Analyser
Powered by PuntingForm API

Install:  pip install streamlit requests pandas numpy plotly
Run:      streamlit run racing_analyser.py
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Optional

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Racing Ebo",
    page_icon="None",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS – DARK RACING THEME
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

:root {
    --bg:           #0d0f14;
    --bg2:          #12151c;
    --bg3:          #181c25;
    --surface:      #1e2330;
    --surface2:     #252b3b;
    --border:       #2a3147;
    --border2:      #323b55;
    --text:         #e8ecf4;
    --text2:        #9aa3b8;
    --text3:        #5c6580;
    --gold:         #f0b429;
    --gold2:        #ffd166;
    --gold-dim:     rgba(240,180,41,0.12);
    --gold-glow:    rgba(240,180,41,0.25);
    --green:        #06d6a0;
    --green-dim:    rgba(6,214,160,0.10);
    --red:          #ef4444;
    --red-dim:      rgba(239,68,68,0.10);
    --blue:         #4da6ff;
    --blue-dim:     rgba(77,166,255,0.10);
    --amber:        #fb923c;
    --amber-dim:    rgba(251,146,60,0.10);
    --r:            8px;
    --r2:           12px;
    --r3:           16px;
    --shadow:       0 4px 24px rgba(0,0,0,0.4);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
    z-index: 999;
}
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input,
[data-testid="stSidebar"] .stSelectbox select {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: var(--r) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
}
[data-testid="stSidebar"] .stDateInput input {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: var(--r) !important;
    font-family: 'DM Mono', monospace !important;
}
.stTextArea textarea { font-size: 0.78rem !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text3) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 14px 22px !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
}
.stTabs [data-testid="stTabPanel"] {
    background: var(--bg) !important;
    padding-top: 28px !important;
}

/* Buttons */
.stButton > button {
    background: var(--gold) !important;
    color: #0d0f14 !important;
    border: none !important;
    border-radius: var(--r) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: var(--gold2) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px var(--gold-glow) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--surface) !important;
    color: var(--text2) !important;
    border: 1px solid var(--border2) !important;
}

/* Progress bar */
.stProgress > div > div { background: var(--gold) !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: var(--r2) !important; overflow: hidden; }
[data-testid="stDataFrame"] table { background: var(--bg2) !important; }
[data-testid="stDataFrame"] th { background: var(--surface) !important; color: var(--text2) !important; font-family: 'Syne', monospace !important; font-size: 0.65rem !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; border-bottom: 1px solid var(--border) !important; }
[data-testid="stDataFrame"] td { color: var(--text) !important; border-bottom: 1px solid var(--border) !important; font-family: 'DM Mono', monospace !important; font-size: 0.75rem !important; }
[data-testid="stDataFrame"] tr:hover td { background: var(--surface) !important; }

/* Line chart */
[data-testid="stArrowVegaLiteChart"] { background: var(--bg2) !important; border: 1px solid var(--border) !important; border-radius: var(--r2) !important; }

/* Expanders */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
}
.streamlit-expanderContent {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--r) var(--r) !important;
}

/* Alerts / info */
[data-testid="stAlert"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text2) !important;
    border-radius: var(--r) !important;
}

/* Slider */
[data-testid="stSlider"] > div > div { background: var(--gold) !important; }

/* Custom components */
.page-header {
    display: flex; align-items: baseline; gap: 16px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 16px; margin-bottom: 28px;
}
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem; font-weight: 800;
    color: var(--text); letter-spacing: -0.02em;
}
.page-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem; color: var(--text3);
    letter-spacing: 0.05em;
}

.metric-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px,1fr)); gap: 10px; margin-bottom: 24px; }
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r2);
    padding: 16px 18px;
}
.metric-label { font-family: 'Syne', monospace; font-size: 0.6rem; color: var(--text3); letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 6px; }
.metric-value { font-family: 'DM Mono', monospace; font-size: 1.6rem; font-weight: 500; color: var(--text); }
.metric-value.gold { color: var(--gold); }
.metric-value.green { color: var(--green); }
.metric-value.red { color: var(--red); }

.pill {
    display: inline-block; padding: 2px 9px; border-radius: 99px;
    font-family: 'Syne', monospace; font-size: 0.6rem; font-weight: 700;
    letter-spacing: 0.08em; text-transform: uppercase;
}
.pill-gold   { background: var(--gold-dim);  color: var(--gold);  border: 1px solid var(--gold-glow); }
.pill-green  { background: var(--green-dim); color: var(--green); border: 1px solid rgba(6,214,160,0.2); }
.pill-red    { background: var(--red-dim);   color: var(--red);   border: 1px solid rgba(239,68,68,0.2); }
.pill-amber  { background: var(--amber-dim); color: var(--amber); border: 1px solid rgba(251,146,60,0.2); }
.pill-blue   { background: var(--blue-dim);  color: var(--blue);  border: 1px solid rgba(77,166,255,0.2); }
.pill-muted  { background: var(--bg3);       color: var(--text3); border: 1px solid var(--border); }

.alert {
    border-radius: var(--r); padding: 12px 16px;
    font-size: 0.8rem; margin: 8px 0;
    font-family: 'DM Sans', sans-serif; line-height: 1.5;
}
.alert-green { background: var(--green-dim); border-left: 3px solid var(--green); color: var(--green); }
.alert-red   { background: var(--red-dim);   border-left: 3px solid var(--red);   color: var(--red); }
.alert-amber { background: var(--amber-dim); border-left: 3px solid var(--amber); color: var(--amber); }
.alert-blue  { background: var(--blue-dim);  border-left: 3px solid var(--blue);  color: var(--blue); }

.info-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r2);
    padding: 18px 20px;
    margin-bottom: 12px;
}
.info-card-sm {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 10px 14px;
    margin-bottom: 6px;
}
.mono { font-family: 'DM Mono', monospace; }
.syne { font-family: 'Syne', sans-serif; }

/* Bar */
.bar-wrap { background: var(--bg3); border-radius: 2px; height: 3px; width: 100%; }
.bar-fill { background: var(--gold); border-radius: 2px; height: 3px; }

/* Speedmap rows */
.sm-row {
    display: flex; align-items: center; gap: 16px;
    padding: 10px 14px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r); margin-bottom: 6px;
}
.sm-pos { font-family: 'Syne', monospace; font-size: 0.65rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text3); width: 70px; flex-shrink: 0; }
.sm-horses { font-family: 'DM Mono', monospace; font-size: 0.78rem; color: var(--text); }

/* Component rating row */
.comp-row {
    display: flex; align-items: center; gap: 8px;
    padding: 5px 0; border-bottom: 1px solid var(--border);
}
.comp-name { font-family: 'DM Mono', monospace; font-size: 0.68rem; color: var(--text3); width: 80px; flex-shrink: 0; }
.comp-score { font-family: 'DM Mono', monospace; font-size: 0.68rem; color: var(--text2); width: 40px; text-align: right; }

/* Market table override */
.mkt-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
.mkt-table th {
    background: var(--surface); color: var(--text3);
    font-family: 'Syne', monospace; font-size: 0.6rem;
    letter-spacing: 0.12em; text-transform: uppercase;
    padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border);
}
.mkt-table td {
    padding: 9px 14px; border-bottom: 1px solid var(--border);
    font-family: 'DM Mono', monospace; font-size: 0.76rem;
    color: var(--text);
}
.mkt-table tr:hover td { background: var(--surface); }
.mkt-table .edge-pos { color: var(--green); }
.mkt-table .edge-neg { color: var(--red); }
.mkt-table .horse-name { font-family: 'Syne', sans-serif; font-weight: 600; font-size: 0.8rem; color: var(--text); }
.mkt-table .fav-row td { background: rgba(240,180,41,0.04); }

/* Value badge */
.value-badge {
    background: linear-gradient(135deg, var(--gold-dim), rgba(240,180,41,0.05));
    border: 1px solid var(--gold-glow);
    border-radius: var(--r2);
    padding: 16px;
    margin-bottom: 14px;
}
.no-value-badge {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 10px 14px;
    margin-bottom: 12px;
    text-align: center;
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--text3);
}
.gate-row { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.gate-label { font-family: 'DM Mono', monospace; font-size: 0.72rem; color: var(--text2); }

.stake-card {
    background: linear-gradient(135deg, rgba(240,180,41,0.08), rgba(240,180,41,0.02));
    border: 1px solid var(--gold-glow);
    border-radius: var(--r2);
    padding: 16px;
    margin-bottom: 12px;
}
.stake-amount { font-family: 'DM Mono', monospace; font-size: 1.9rem; font-weight: 500; color: var(--gold); }

/* Section headings */
h2 { font-family: 'Syne', sans-serif !important; font-size: 0.8rem !important; font-weight: 700 !important; letter-spacing: 0.15em !important; text-transform: uppercase !important; color: var(--text3) !important; border-bottom: 1px solid var(--border) !important; padding-bottom: 8px !important; margin-bottom: 16px !important; }

/* Sidebar logo area */
.sidebar-logo { font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 800; color: var(--gold); letter-spacing: -0.02em; }
.sidebar-tagline { font-family: 'DM Mono', monospace; font-size: 0.6rem; color: var(--text3); letter-spacing: 0.08em; margin-top: 2px; margin-bottom: 20px; }
.sb-section { font-family: 'Syne', monospace; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; color: var(--text3); margin: 16px 0 8px; }

hr { border: none; border-top: 1px solid var(--border); margin: 20px 0; }

/* Race row */
.race-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); }
.race-info { font-family: 'DM Mono', monospace; font-size: 0.78rem; color: var(--text); }

/* Market probability bar */
.prob-bar-container { display: flex; align-items: center; gap: 8px; }
.prob-bar-bg { flex: 1; height: 4px; background: var(--bg3); border-radius: 2px; }
.prob-bar-fill { height: 4px; border-radius: 2px; }

/* Odds movement indicator */
.odds-move { font-family: 'DM Mono', monospace; font-size: 0.68rem; }
.odds-move.drift { color: var(--red); }
.odds-move.firm { color: var(--green); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
defaults = {
    "api_key": "", "races": [], "selected_race": None,
    "runners": [], "ratings": {}, "bet_log": [],
    "bank": 1000.0, "starting_bank": 1000.0,
    "staking_method": "Kelly", "kelly_fraction": 0.25,
    "flat_stake_pct": 2.0, "level_stake": 20.0,
    "max_stake_pct": 5.0, "min_odds": 1.80,
    "max_odds": 20.0, "min_rating": 60, "notes": {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
# API HELPERS
# ─────────────────────────────────────────────────────────────
BASE = "https://api.puntingform.com.au/v2"

def pf_get(endpoint: str, params: dict = {}) -> Optional[dict]:
    if not st.session_state.api_key:
        return None
    params = dict(params)
    params["apiKey"] = st.session_state.api_key
    try:
        r = requests.get(f"{BASE}/{endpoint}", params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"API {e.response.status_code}: {e.response.text[:200]}")
    except Exception as e:
        st.error(f"Connection error: {e}")
    return None

def fetch_meetings(target_date: date) -> list:
    ds = target_date.strftime("%Y-%m-%d")
    data = pf_get("form/meetingslist", {"meetingDate": ds})
    if not data:
        return []
    
    # Extract meeting list from payLoad
    meetings_raw = data.get("payLoad", []) if isinstance(data, dict) else data
    if not isinstance(meetings_raw, list):
        return []

    processed_meetings = []
    for meeting in meetings_raw:
        # Use the NEW extract_meeting_id from Step 1
        mid = extract_meeting_id(meeting)
        if not mid:
            continue
            
        # Now fetch the actual races for THIS meeting ID
        rdata = pf_get("form/meeting", {"meetingId": mid})
        if rdata:
            r_payload = rdata.get("payLoad", {})
            if isinstance(r_payload, dict):
                # Put the races into the meeting object
                meeting["races"] = r_payload.get("races", [])
            elif isinstance(r_payload, list):
                meeting["races"] = r_payload
            else:
                meeting["races"] = []
        else:
            meeting["races"] = []
            
        processed_meetings.append(meeting)
        
    return processed_meetings

def fetch_race_runners(race_id: str) -> list:
    """Fetch runners for a race using the raceId."""
    if not race_id or str(race_id) == "0":
        return []
    
    data = pf_get("form/fields", {"raceId": str(race_id)})
    if not data:
        return []
    
    # Extract the list of runners from the payLoad
    payload = data.get("payLoad", [])
    if isinstance(payload, dict):
        return payload.get("runners", [])
    return payload if isinstance(payload, list) else []

def fetch_runner_form(horse_id: str) -> list:
    if not horse_id or str(horse_id).strip() in ("", "0"):
        return []
    data = pf_get("form/form", {"horseId": str(horse_id)})
    if not data:
        return []
    payload = data.get("payLoad", data) if isinstance(data, dict) else data
    return payload if isinstance(payload, list) else []

def extract_meeting_id(meeting: dict) -> str:
    """Robustly extract meeting ID from various casing variations."""
    for field in ["meetingID", "meetingId", "id", "MeetingID"]:
        val = meeting.get(field)
        if val and str(val) != "0":
            return str(val)
    return ""

def extract_race_id(race: dict) -> str:
    """Robustly extract race ID from various casing variations."""
    for field in ["raceID", "raceId", "id", "RaceID"]:
        val = race.get(field)
        if val and str(val) != "0":
            return str(val)
    return ""

def extract_horse_id(runner: dict) -> str:
    """Robustly extract horse/runner ID."""
    for field in ["horseID", "horseId", "runnerId", "id", "runner_id"]:
        val = runner.get(field)
        if val and str(val) != "0":
            return str(val)
    return ""


# ─────────────────────────────────────────────────────────────
# ENHANCED RATING ENGINE
# ─────────────────────────────────────────────────────────────
WEIGHTS = {
    "sectional_3f": 20,
    "speed_rating": 20,
    "unlucky_factor": 15,
    "pace_adj_perf": 12,
    "class_rating": 10,
    "weight_rating": 8,
    "barrier_rating": 5,
    "jockey_trainer": 5,
    "track_rating": 3,
    "distance_rating": 2,
}
MAX_SCORE = sum(WEIGHTS.values())
LABELS = {
    "sectional_3f": "Final 3F", "speed_rating": "Speed", "unlucky_factor": "Unlucky",
    "pace_adj_perf": "Pace Adj", "class_rating": "Class", "weight_rating": "Weight",
    "barrier_rating": "Barrier", "jockey_trainer": "J+T", "track_rating": "Track",
    "distance_rating": "Distance",
}

def safe_float(val, default=0.0):
    try: return float(val)
    except: return default

def calc_sectional_rating(past_runs):
    if not past_runs: return 10.0
    scores = []
    for run in past_runs[:5]:
        final_3f = safe_float(run.get("final3F") or run.get("closingSectional"))
        if final_3f > 0:
            scores.append(final_3f)
        else:
            pos = safe_float(run.get("finishingPosition", 10))
            field = max(safe_float(run.get("numberOfRunners", 10)), 1)
            margin = safe_float(run.get("marginBeaten", 20))
            score = max(0, 20 - (pos-1)*2 - margin*0.5)
            scores.append(score)
    return min(max(sum(scores)/len(scores), 0), 20) if scores else 10.0

def calc_contextual_speed(runner, past_runs):
    raw = safe_float(runner.get("speedRating") or runner.get("bestSpeed") or 0)
    if raw <= 0: return 10.0
    cls = safe_float(runner.get("raceClass") or 0)
    adj = 5 if cls >= 90 else (3 if cls >= 80 else (1 if cls >= 70 else (-2 if cls <= 50 else 0)))
    going = (runner.get("going") or runner.get("trackCondition") or "").lower()
    if "soft" in going or "heavy" in going:
        adj -= 3
    speed_score = (raw + adj - 70) / 60 * 20
    return min(max(speed_score, 0), 20)

def calc_unlucky_factor(past_runs):
    if not past_runs: return 10.0
    unlucky = 10.0
    trouble_map = [("blocked",3),("traffic",3),("checked",2),("steadied",2),
                   ("wide",1.5),("bumped",2),("interfered",2),("slow start",2),
                   ("held up",3),("no clear run",3)]
    for run in past_runs[:3]:
        comments = (run.get("comments") or run.get("raceComment") or "").lower()
        for kw, val in trouble_map:
            if kw in comments:
                unlucky += val
        pos_turn = safe_float(run.get("positionAfterTurn") or run.get("turnPosition", 8))
        pos_fin = safe_float(run.get("finishingPosition", 10))
        if pos_turn >= 6 and pos_fin <= 4:
            unlucky += 2
    return min(max(unlucky, 0), 15)

def calc_pace_adjusted_performance(past_runs):
    if not past_runs: return 6.0
    score = 6.0
    for run in past_runs[:3]:
        pace = (run.get("racePace") or run.get("paceProfile") or {}).get("paceRating", "MODERATE")
        pos_early = safe_float(run.get("positionEarly") or run.get("firstPosition", 5))
        pos_fin = safe_float(run.get("finishingPosition", 10))
        if pace == "HOT" and pos_fin < pos_early:
            score += 2
        elif pace == "SOFT" and pos_early == 1 and pos_fin <= 3:
            score -= 1
        elif pos_fin < pos_early - 3:
            score += 1
    return min(max(score, 0), 12)

def calc_class_rating(runner, past):
    cur = safe_float(runner.get("raceClass") or 0)
    if not past or cur == 0: return 10.0
    prev = [safe_float(s.get("raceClass",0)) for s in past[:3] if s.get("raceClass")]
    if not prev: return 10.0
    avg_prev = sum(prev)/len(prev)
    return round(min(max(10 + (avg_prev - cur)*1.5, 2), 15), 1)

def calc_weight_rating(runner):
    w = safe_float(runner.get("weightTotal") or runner.get("weightCarried") or 57)
    dist = safe_float(runner.get("distance") or runner.get("raceDistance", 1200))
    base = max(0, 10 - (w-54)*0.5)
    if dist > 1600: base *= 1.2
    elif dist < 1200: base *= 0.8
    return min(max(base, 0), 8)

def calc_barrier_rating(runner):
    b = safe_float(runner.get("barrierNumber") or runner.get("barrier", 8))
    if b <= 0: return 2.5
    base = max(0, 10 - (b-4)*0.6)
    track = (runner.get("meetingName") or "").lower()
    if "caulfield" in track and safe_float(runner.get("distance",0)) <= 1200:
        base = base*1.3 if b<=4 else base*0.7
    return min(max(base, 0), 5)

def calc_jockey_trainer(runner):
    combo = runner.get("trainerJockeyA2E_Career") or {}
    runs = safe_float(combo.get("runners",0))
    if runs < 5: return 2.5
    sr = safe_float(combo.get("strikeRate",0))
    a2e = safe_float(combo.get("a2E",0))
    score = (sr/100 * 0.6 + a2e/2 * 0.4) * 5
    return min(max(score, 0), 5)

def calc_track_rating(runner, past):
    track = (runner.get("meetingName") or "").lower()
    runs = [s for s in past if (s.get("meetingName") or "").lower() == track]
    wins = [s for s in runs if safe_float(s.get("finishingPosition",99)) == 1]
    return round(len(wins)/len(runs)*5, 1) if runs else 3.0

def calc_distance_rating(runner, past):
    dist = safe_float(runner.get("distance") or 1200)
    runs = [s for s in past if abs(safe_float(s.get("raceDistance") or 0)-dist) <= 100]
    wins = [s for s in runs if safe_float(s.get("finishingPosition",99)) == 1]
    return round(len(wins)/len(runs)*5, 1) if runs else 2.0

def rate_runner(runner, past=[]):
    br = {
        "sectional_3f":    calc_sectional_rating(past),
        "speed_rating":    calc_contextual_speed(runner, past),
        "unlucky_factor":  calc_unlucky_factor(past),
        "pace_adj_perf":   calc_pace_adjusted_performance(past),
        "class_rating":    calc_class_rating(runner, past),
        "weight_rating":   calc_weight_rating(runner),
        "barrier_rating":  calc_barrier_rating(runner),
        "jockey_trainer":  calc_jockey_trainer(runner),
        "track_rating":    calc_track_rating(runner, past),
        "distance_rating": calc_distance_rating(runner, past),
    }
    br["composite"] = round(sum(br.values()), 1)
    br["pct"] = round(br["composite"] / MAX_SCORE * 100, 1)
    return br


# ─────────────────────────────────────────────────────────────
# MARKET FRAMING — Realistic bookmaker overround (120–125%)
# ─────────────────────────────────────────────────────────────
# Real Australian bookmakers run at ~120-125% on metro races
OVERROUND_TARGET = 1.22   # 122% — typical Australian bookie

def record_win_rate(rec):
    if not rec: return None
    s = safe_float(rec.get("starts", 0))
    f = safe_float(rec.get("firsts", 0))
    return f / s if s >= 3 else None

def frame_market(runners):
    """
    Frame the market at realistic bookmaker overround (122%).
    Returns per-runner market data including:
    - raw_implied: SP implied probability (includes full overround)
    - true_implied: de-viggged probability (actual win chance the market implies)
    - bookie_implied: what the bookie prices it at (raw / sum_raw)
    - overround: total book overround %
    """
    priced = [(r, safe_float(r.get("priceSP", 0))) for r in runners if safe_float(r.get("priceSP", 0)) > 1.0]
    if not priced:
        return {}

    # Calculate raw overround (sum of 1/odds)
    raw_sum = sum(1 / p for _, p in priced)
    overround_pct = round(raw_sum * 100, 1)

    result = {}
    for r, sp in priced:
        rid = extract_horse_id(r)
        raw_implied = 1 / sp

        # De-vigged "true" probability — proportional removal
        true_implied = raw_implied / raw_sum

        # Re-frame at target overround to simulate a 122% market
        framed = true_implied * OVERROUND_TARGET

        # Fair odds (true probability inverted — no overround)
        fair_odds = 1 / true_implied if true_implied > 0 else 0

        result[rid] = {
            "sp":              sp,
            "raw_implied_pct": round(raw_implied * 100, 1),
            "true_implied_pct": round(true_implied * 100, 1),
            "framed_pct":      round(framed * 100, 1),
            "fair_odds":       round(fair_odds, 2),
            "overround_total": overround_pct,
        }
    return result

def model_probability(runner, rating):
    career_win_pct = safe_float(runner.get("winPct", 0)) / 100.0
    track_wr  = record_win_rate(runner.get("trackRecord"))
    dist_wr   = record_win_rate(runner.get("distanceRecord"))
    tjA2E     = runner.get("trainerJockeyA2E_Career") or {}
    tj_sr     = safe_float(tjA2E.get("strikeRate", 0)) / 100.0
    tj_valid  = safe_float(tjA2E.get("runners", 0)) >= 5
    rat_sig   = (rating.get("pct", 50) / 100.0) if rating else 0.5

    score = career_win_pct * 3.0
    tw    = 3.0
    if track_wr is not None:
        score += track_wr * 1.5; tw += 1.5
    if dist_wr is not None:
        score += dist_wr * 1.5; tw += 1.5
    if tj_valid:
        score += tj_sr * 2.0; tw += 2.0
    score += rat_sig * 0.08; tw += 0.08

    return min(max(score / tw if tw else career_win_pct, 0.01), 0.98)

def normalise_field_probs(runners, ratings):
    probs = {}
    for r in runners:
        rid = extract_horse_id(r)
        probs[rid] = model_probability(r, ratings.get(rid, {}))
    total = sum(probs.values())
    if total > 0:
        probs = {k: round(v / total, 4) for k, v in probs.items()}
    return probs

def value_assessment(model_prob, true_implied_pct, sp, tj_a2e, rating_pct, min_rating):
    market_prob = true_implied_pct / 100.0
    edge        = model_prob - market_prob
    has_edge    = edge > 0
    rating_ok   = rating_pct >= min_rating
    tj_ok       = tj_a2e >= 1.0
    odds_ok     = sp >= 1.80
    bet         = has_edge and rating_ok and tj_ok and odds_ok
    reasons = []
    if not has_edge:  reasons.append(f"model {round(model_prob*100,1)}% vs market {round(market_prob*100,1)}% — no edge")
    if not rating_ok: reasons.append(f"rating {rating_pct}% below min {min_rating}%")
    if not tj_ok:     reasons.append(f"T+J A2E {round(tj_a2e,2)} below 1.0")
    if not odds_ok:   reasons.append("odds below minimum")
    return {
        "bet": bet, "edge_pct": round(edge*100,1), "has_edge": has_edge,
        "rating_ok": rating_ok, "tj_ok": tj_ok,
        "model_prob_pct": round(model_prob*100,1),
        "market_prob_pct": round(market_prob*100,1),
        "reasons": reasons,
    }


# ─────────────────────────────────────────────────────────────
# SPEEDMAP
# ─────────────────────────────────────────────────────────────
PACE_LABELS = {1:"Leader",2:"On Pace",3:"Midfield",4:"Back",5:"Last"}

def assign_pace(runners):
    for r in runners:
        if not r.get("pacePosition"):
            b = safe_float(r.get("barrier") or r.get("barrierNumber",8))
            r["pacePosition"] = 1 if b<=3 else 2 if b<=6 else 3 if b<=10 else 4
    return runners

def classify_tempo(runners):
    leaders = [r for r in runners if r.get("pacePosition")==1]
    on_pace = [r for r in runners if r.get("pacePosition")==2]
    n = len(leaders)
    if n>=3:    tempo,desc = "HOT",      "Multiple speed horses — fast early pace expected. Favours closers and midfielders."
    elif n==2:  tempo,desc = "GENUINE",  "Two leaders contesting — honest pace. All running styles viable."
    elif n==1 and len(on_pace)<=1: tempo,desc = "SOFT","Single uncontested leader — significant front-runner advantage."
    else:       tempo,desc = "MODERATE", "Balanced speed — no dominant pace advantage. Form runners get their chance."
    return {"tempo":tempo,"description":desc}


# ─────────────────────────────────────────────────────────────
# STAKING ENGINE
# ─────────────────────────────────────────────────────────────
def kelly_stake(bank, prob, odds, fraction):
    b = odds-1
    if b<=0 or prob<=0 or prob>=1: return 0.0
    k = (b*prob-(1-prob))/b
    return bank*fraction*max(k,0)

def recommended_stake(bank, model_prob, odds, method, kelly_frac, flat_pct, fixed, max_pct):
    edge = model_prob - (1/odds if odds > 1 else 0)
    if method == "Kelly":   stake = kelly_stake(bank, model_prob, odds, kelly_frac)
    elif method == "Flat %": stake = bank * flat_pct / 100 if edge > 0 else 0
    else:                    stake = fixed if edge > 0 else 0
    stake = min(round(stake, 2), bank * max_pct / 100)
    ev    = round((model_prob * (odds - 1) - (1 - model_prob)) * stake, 2)
    return {"stake": stake, "ev": ev}


# ─────────────────────────────────────────────────────────────
# BET LOG
# ─────────────────────────────────────────────────────────────
def log_bet(horse, race, stake, odds, edge):
    st.session_state.bet_log.append({
        "datetime": datetime.now().strftime("%d/%m %H:%M"),
        "horse":horse,"race":race,"stake":stake,"odds":odds,
        "edge":edge,"result":"Pending","pl":0.0,
    })

def settle_bet(idx, result):
    bet = st.session_state.bet_log[idx]
    pl  = bet["stake"]*(bet["odds"]-1) if result=="Won" else -bet["stake"]
    st.session_state.bet_log[idx].update({"result":result,"pl":pl})
    st.session_state.bank += pl

def bankroll_stats():
    log = [b for b in st.session_state.bet_log if b["result"]!="Pending"]
    if not log: return {}
    staked=sum(b["stake"] for b in log); pl=sum(b["pl"] for b in log)
    winners=[b for b in log if b["result"]=="Won"]
    running=peak=0; dds=[]
    for b in log:
        running+=b["pl"]; peak=max(peak,running); dds.append(running-peak)
    return {
        "bets":len(log),"winners":len(winners),
        "strike_rate":round(len(winners)/len(log)*100,1),
        "staked":round(staked,2),"pl":round(pl,2),
        "roi":round(pl/staked*100,1) if staked else 0,
        "avg_odds":round(sum(b["odds"] for b in log)/len(log),2),
        "max_dd":round(min(dds),2),"bank":round(st.session_state.bank,2),
    }


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🐎 Racing Edge</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">POWERED BY PUNTINGFORM</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-section">API Connection</div>', unsafe_allow_html=True)
    try:
        secret_key = st.secrets.get("PUNTINGFORM_API_KEY","")
    except:
        secret_key = ""
    api_key = st.text_input("API Key", type="password",
        value=st.session_state.api_key or secret_key,
        placeholder="Enter PuntingForm API key")
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key

    st.markdown('<div class="sb-section">Race Selection</div>', unsafe_allow_html=True)
    target_date  = st.date_input("Race Date", value=date.today()+timedelta(days=1))
    state_filter = st.multiselect("States", ["QLD","NSW","VIC","SA","WA","TAS","NT","ACT"])

    if st.button("Fetch Meetings"):
        with st.spinner("Fetching meetings..."):
            st.session_state.races = fetch_meetings(target_date)
        if st.session_state.races:
            st.success(f"{len(st.session_state.races)} meetings loaded")
        else:
            st.warning("No meetings found")

    st.markdown('<div class="sb-section">Staking</div>', unsafe_allow_html=True)
    st.session_state.bank = st.number_input("Bank ($)", value=st.session_state.bank, step=10.0)
    st.session_state.staking_method = st.selectbox("Method",["Kelly","Flat %","Level"],
        index=["Kelly","Flat %","Level"].index(st.session_state.staking_method))
    if st.session_state.staking_method=="Kelly":
        st.session_state.kelly_fraction = st.slider("Kelly Fraction",0.1,1.0,st.session_state.kelly_fraction,0.05)
    elif st.session_state.staking_method=="Flat %":
        st.session_state.flat_stake_pct = st.slider("% of Bank",0.5,10.0,st.session_state.flat_stake_pct,0.5)
    else:
        st.session_state.level_stake = st.number_input("Fixed Stake ($)",value=st.session_state.level_stake,step=5.0)
    st.session_state.max_stake_pct = st.slider("Max Stake %",1.0,15.0,st.session_state.max_stake_pct,0.5)

    st.markdown('<div class="sb-section">Filters</div>', unsafe_allow_html=True)
    st.session_state.min_odds   = st.number_input("Min Odds",  value=st.session_state.min_odds,  step=0.1)
    st.session_state.max_odds   = st.number_input("Max Odds",  value=st.session_state.max_odds,  step=0.5)
    st.session_state.min_rating = st.slider("Min Rating (%)",0,100,st.session_state.min_rating)


# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
t_races, t_analysis, t_staking, t_bankroll, t_guide = st.tabs([
    "🏁  Races", "📊  Analysis", "💰  Staking", "📈  Bankroll", "📖  Guide"
])

# ══════════════════════════════════════════════════════════════
# RACES
# ══════════════════════════════════════════════════════════════
with t_races:
    st.markdown('<div class="page-header"><span class="page-title">Race Meetings</span><span class="page-sub">SELECT A RACE TO ANALYSE</span></div>', unsafe_allow_html=True)

    if not st.session_state.api_key:
        st.markdown('<div class="alert alert-amber">⚠️  Enter your PuntingForm API key in the sidebar to begin.</div>', unsafe_allow_html=True)

    if not st.session_state.races:
        st.markdown('<div class="alert alert-blue">ℹ️  Use the sidebar to fetch meetings for your selected date.</div>', unsafe_allow_html=True)
    else:
        for meeting in st.session_state.races:
            track = meeting.get("track") or {}
            name  = track.get("name") or meeting.get("meetingName") or meeting.get("venueName","Unknown")
            state = track.get("state") or meeting.get("state","")
            races = meeting.get("races") or []

            if state_filter:
                if not any(f in state.upper() for f in state_filter):
                    continue

            with st.expander(f"  {name}  ·  {state}  ·  {len(races)} races"):
                for race in races:
                    race["_meetingName"] = name
                    race["_meetingState"] = state
                    r_num  = race.get("number") or race.get("raceNumber","?")
                    r_name = race.get("name") or race.get("raceName",f"Race {r_num}")
                    r_dist = race.get("distance") or race.get("raceDistance","?")
                    r_time = race.get("startTime") or race.get("raceTime","")
                    r_cls  = race.get("raceClass","")
                    r_id   = extract_race_id(race)

                    c1, c2 = st.columns([6,1])
                    with c1:
                        st.markdown(
                            f'<div class="race-row">'
                            f'<div class="race-info">'
                            f'<span style="color:var(--gold);font-family:\'Syne\',monospace;font-weight:700">R{r_num}</span>'
                            f'&nbsp;&nbsp;<span style="color:var(--text)">{r_name}</span>'
                            f'&nbsp;&nbsp;<span class="pill pill-muted">{r_dist}m</span>'
                            f'&nbsp;<span class="pill pill-muted">{r_cls}</span>'
                            f'&nbsp;&nbsp;<span style="color:var(--text3);font-size:0.72rem">{r_time}</span>'
                            f'{"" if r_id else "<span class=\"pill pill-red\">NO ID</span>"}'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )
                    with c2:
                        if not r_id:
                            st.markdown('<span class="pill pill-red" style="font-size:0.65rem">No ID</span>', unsafe_allow_html=True)
                        elif st.button("Analyse", key=f"sel_{r_id}_{r_num}"):
                            st.session_state.selected_race = race
                            st.session_state.runners = []
                            st.session_state.ratings = {}
                            with st.spinner(f"Loading runners for Race {r_num}..."):
                                runners = race.get("runners", [])
                                if not runners:
                                    runners = fetch_race_runners(r_id)
                                st.session_state.runners = assign_pace(runners)
                            if st.session_state.runners:
                                st.success(f"{len(st.session_state.runners)} runners — go to Analysis tab")
                            else:
                                st.error(f"No runners found for race ID {r_id}")


# ══════════════════════════════════════════════════════════════
# ANALYSIS
# ══════════════════════════════════════════════════════════════
with t_analysis:
    race    = st.session_state.selected_race
    runners = st.session_state.runners

    if not race:
        st.markdown('<div class="alert alert-blue">ℹ️  Select a race from the Races tab.</div>', unsafe_allow_html=True)
    elif not runners:
        st.markdown('<div class="alert alert-amber">⚠️  No runners loaded for this race.</div>', unsafe_allow_html=True)
    else:
        r_name = race.get("raceName") or race.get("name","Race")
        r_dist = race.get("raceDistance") or race.get("distance","?")
        r_trk  = race.get("_meetingName") or race.get("meetingName","")
        r_cond = race.get("trackCondition","")
        r_cls  = race.get("raceClass","")
        r_num  = race.get("raceNumber") or race.get("number","?")

        st.markdown(
            f'<div class="page-header">'
            f'<span class="page-title">Race {r_num} — {r_name}</span>'
            f'<span class="page-sub">{r_trk.upper()} &nbsp;·&nbsp; {r_dist}m &nbsp;·&nbsp; {r_cls} &nbsp;·&nbsp; {r_cond or "CONDITION TBC"}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        # ── Speedmap ──────────────────────────────────────────
        st.markdown("## Speedmap & Tempo")
        tempo = classify_tempo(runners)
        tempo_pill = {"HOT":"pill-red","GENUINE":"pill-amber","SOFT":"pill-green","MODERATE":"pill-blue"}.get(tempo["tempo"],"pill-muted")
        st.markdown(
            f'<div class="info-card" style="margin-bottom:14px;display:flex;align-items:center;gap:14px">'
            f'<span class="pill {tempo_pill}" style="font-size:0.68rem;padding:4px 14px">{tempo["tempo"]}</span>'
            f'<span style="font-size:0.82rem;color:var(--text2)">{tempo["description"]}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        positions = {1:[],2:[],3:[],4:[],5:[]}
        for r in runners:
            positions[int(r.get("pacePosition",3))].append(r.get("runnerName") or r.get("horseName") or r.get("name","?"))
        pace_colors = {1:"var(--red)",2:"var(--amber)",3:"var(--blue)",4:"var(--text3)",5:"var(--text3)"}
        for pos, lbl in {1:"Leader",2:"On Pace",3:"Midfield",4:"Back",5:"Last"}.items():
            horses = positions.get(pos,[])
            if horses:
                st.markdown(
                    f'<div class="sm-row">'
                    f'<span class="sm-pos" style="color:{pace_colors[pos]}">{lbl}</span>'
                    f'<span class="sm-horses">{" &nbsp;·&nbsp; ".join(horses)}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown('<hr>', unsafe_allow_html=True)

        # ── Rate runners ──────────────────────────────────────
        st.markdown("## Runner Analysis")
        col_btn, col_info = st.columns([2,5])
        with col_btn:
            rate_btn = st.button("⚡  Rate All Runners")
        with col_info:
            st.markdown(
                '<div style="padding-top:8px;font-family:\'DM Mono\',monospace;font-size:0.72rem;color:var(--text3)">'
                'Fetches past form for each runner and applies all 10 rating factors</div>',
                unsafe_allow_html=True
            )

        if rate_btn:
            ratings = {}; prog = st.progress(0)
            errors = []
            for i, runner in enumerate(runners):
                hid = extract_horse_id(runner)
                if hid:
                    past_runs = fetch_runner_form(hid)
                else:
                    past_runs = []
                    errors.append(runner.get("name","?"))
                ratings[hid or f"_idx_{i}"] = rate_runner(runner, past_runs)
                prog.progress((i+1)/len(runners))
            st.session_state.ratings = ratings
            prog.empty()
            if errors:
                st.warning(f"Could not fetch form for: {', '.join(errors)} (no horse ID)")
            else:
                st.success("All runners rated")

        ratings     = st.session_state.ratings
        mkt_frame   = frame_market(runners)
        field_probs = normalise_field_probs(runners, ratings) if ratings else {}

        # ── Market Frame Table ────────────────────────────────
        if mkt_frame:
            # Get overround from first entry
            sample_mf = next(iter(mkt_frame.values()), {})
            overround = sample_mf.get("overround_total", 0)

            st.markdown(
                f'<div style="display:flex;align-items:baseline;gap:16px;margin-bottom:12px">'
                f'<span style="font-family:\'Syne\',sans-serif;font-size:0.8rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:var(--text3)">Market Frame</span>'
                f'<span class="pill pill-muted">Book: {overround}%</span>'
                f'<span class="pill pill-muted">De-vigged → True %</span>'
                f'<span class="pill pill-gold">Model Overlay</span>'
                f'</div>',
                unsafe_allow_html=True
            )

            # Build rich HTML market table
            sorted_mkt = sorted(runners, key=lambda x: safe_float(x.get("priceSP",99)))
            rows_html = ""
            for rank, r in enumerate(sorted_mkt):
                rid  = extract_horse_id(r)
                mf   = mkt_frame.get(rid)
                if not mf:
                    continue
                name = r.get("name") or r.get("runnerName") or r.get("horseName","?")
                mp   = field_probs.get(rid, 0)
                sp   = mf["sp"]
                true_pct = mf["true_implied_pct"]
                raw_pct  = mf["raw_implied_pct"]
                fair_o   = mf["fair_odds"]
                diff = round(mp*100 - true_pct, 1) if mp else None

                edge_html = ""
                if diff is not None:
                    cls_  = "edge-pos" if diff > 0 else "edge-neg"
                    sign_ = "+" if diff >= 0 else ""
                    edge_html = f'<span class="{cls_}">{sign_}{diff}%</span>'

                # Odds bar (visual)
                bar_w = min(int(true_pct * 2.5), 100)
                bar_color = "var(--gold)" if (diff or 0) > 0 else "var(--text3)"

                fav_cls = " fav-row" if rank == 0 else ""
                fav_badge = ' <span class="pill pill-gold" style="font-size:0.55rem;padding:1px 6px">FAV</span>' if rank == 0 else ""

                rows_html += f"""
                <tr class="{fav_cls}">
                  <td style="font-family:'DM Mono',monospace;color:var(--text3);width:28px">{rank+1}</td>
                  <td><span class="horse-name">{name}</span>{fav_badge}</td>
                  <td style="font-family:'DM Mono',monospace;color:var(--gold);font-weight:500">${sp:.2f}</td>
                  <td style="color:var(--text3)">{raw_pct}%</td>
                  <td style="color:var(--text)">{true_pct}%
                    <div class="prob-bar-bg" style="margin-top:3px"><div class="prob-bar-fill" style="width:{bar_w}%;background:var(--text3)"></div></div>
                  </td>
                  <td style="color:var(--blue)">${fair_o:.2f}</td>
                  <td style="font-family:'DM Mono',monospace;color:var(--blue)">{f"{mp*100:.1f}%" if mp else "—"}</td>
                  <td>{edge_html if edge_html else "—"}</td>
                </tr>"""

            st.markdown(f"""
            <div class="info-card" style="padding:0;overflow:hidden">
              <table class="mkt-table" style="width:100%;border-collapse:collapse">
                <thead>
                  <tr>
                    <th>#</th><th>Horse</th><th>SP Odds</th>
                    <th>Raw%<br><span style="font-weight:400;color:var(--text3);font-size:0.55rem">incl. vig</span></th>
                    <th>True%<br><span style="font-weight:400;color:var(--text3);font-size:0.55rem">de-vigged</span></th>
                    <th>Fair Odds<br><span style="font-weight:400;color:var(--text3);font-size:0.55rem">no overround</span></th>
                    <th>Model%<br><span style="font-weight:400;color:var(--text3);font-size:0.55rem">our estimate</span></th>
                    <th>Edge<br><span style="font-weight:400;color:var(--text3);font-size:0.55rem">model vs market</span></th>
                  </tr>
                </thead>
                <tbody>{rows_html}</tbody>
              </table>
            </div>
            <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:var(--text3);margin-top:8px;margin-bottom:20px">
              Raw% = 1/SP (includes bookmaker vig) &nbsp;·&nbsp;
              True% = de-vigged market probability &nbsp;·&nbsp;
              Fair Odds = 1/True% (no overround) &nbsp;·&nbsp;
              Book total: {overround}%
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr>', unsafe_allow_html=True)

        # ── Per Runner Cards ──────────────────────────────────
        def sort_key(r):
            rid = extract_horse_id(r)
            return field_probs.get(rid, 0) if field_probs else -safe_float(r.get("priceSP",99))
        sorted_runners = sorted(runners, key=sort_key, reverse=True)

        for rank, runner in enumerate(sorted_runners, 1):
            hid      = extract_horse_id(runner)
            name     = runner.get("name") or runner.get("runnerName") or runner.get("horseName","Unknown")
            barrier  = runner.get("barrier") or runner.get("barrierNumber","?")
            jockey   = (runner.get("jockey") or {}).get("fullName","—") or runner.get("jockeyName","—")
            trainer  = (runner.get("trainer") or {}).get("fullName","—") or runner.get("trainerName","—")
            weight   = runner.get("weightTotal") or runner.get("weightCarried") or runner.get("handicapWeight","—")
            price    = safe_float(runner.get("priceSP") or runner.get("fixedOddsWin") or runner.get("price",0))
            pace_lbl = PACE_LABELS.get(int(runner.get("pacePosition",3)),"—")
            rating   = ratings.get(hid) if hid else None
            mf       = mkt_frame.get(hid, {})
            mp       = field_probs.get(hid, 0)
            tjA2E    = runner.get("trainerJockeyA2E_Career") or {}
            tj_a2e   = safe_float(tjA2E.get("a2E", 0))
            tj_sr    = safe_float(tjA2E.get("strikeRate", 0))
            tj_runs  = safe_float(tjA2E.get("runners", 0))

            verdict = None
            if rating and mf and mp:
                verdict = value_assessment(
                    model_prob=mp,
                    true_implied_pct=mf["true_implied_pct"],
                    sp=price,
                    tj_a2e=tj_a2e,
                    rating_pct=rating["pct"],
                    min_rating=st.session_state.min_rating,
                )

            # Label
            bet_indicator = "  ✦ BET" if (verdict and verdict["bet"]) else ""
            price_str = f"${price:.2f}" if price else "N/A"
            model_str = f"  Model {round(mp*100,1)}%" if mp else ""
            mkt_str   = f"  Mkt {mf.get('true_implied_pct','?')}%" if mf else ""
            edge_str  = ""
            if verdict:
                sign = "+" if verdict["edge_pct"] >= 0 else ""
                edge_str = f"  Edge {sign}{verdict['edge_pct']}%"

            label = f"#{rank}  {name}   B{barrier}   {price_str}{model_str}{mkt_str}{edge_str}{bet_indicator}"

            with st.expander(label, expanded=(rank<=2 or bool(verdict and verdict["bet"]))):
                left, right = st.columns([3,2])

                with left:
                    # Tags row
                    pace_colors_map = {"Leader":"pill-red","On Pace":"pill-amber","Midfield":"pill-blue","Back":"pill-muted","Last":"pill-muted"}
                    st.markdown(
                        f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px">'
                        f'<span class="pill pill-muted">B{barrier}</span>'
                        f'<span class="pill {pace_colors_map.get(pace_lbl,"pill-muted")}">{pace_lbl}</span>'
                        f'<span class="pill pill-muted">{weight}kg</span>'
                        f'{"<span class=\'pill pill-gold\'>FAV</span>" if rank==1 and not field_probs else ""}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f'<div style="font-size:0.78rem;color:var(--text2);line-height:2.0;margin-bottom:12px">'
                        f'<span style="color:var(--text3);font-size:0.68rem">JOCKEY</span>&nbsp;&nbsp;<span style="color:var(--text)">{jockey}</span><br>'
                        f'<span style="color:var(--text3);font-size:0.68rem">TRAINER</span>&nbsp;&nbsp;<span style="color:var(--text)">{trainer}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    # Career stats
                    career_win = safe_float(runner.get("winPct",0))
                    career_plc = safe_float(runner.get("placePct",0))
                    track_rec  = runner.get("trackRecord") or {}
                    dist_rec   = runner.get("distanceRecord") or {}
                    t_s = safe_float(track_rec.get("starts",0)); t_w = safe_float(track_rec.get("firsts",0))
                    d_s = safe_float(dist_rec.get("starts",0));  d_w = safe_float(dist_rec.get("firsts",0))
                    t_sr = round(t_w/t_s*100,1) if t_s > 0 else 0
                    d_sr = round(d_w/d_s*100,1) if d_s > 0 else 0

                    st.markdown(
                        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:14px">'
                        f'<div class="info-card-sm"><div class="metric-label">Career Win%</div><div style="font-family:\'DM Mono\',monospace;font-size:1rem;color:var(--text)">{career_win:.1f}%</div></div>'
                        f'<div class="info-card-sm"><div class="metric-label">Career Place%</div><div style="font-family:\'DM Mono\',monospace;font-size:1rem;color:var(--text)">{career_plc:.1f}%</div></div>'
                        f'<div class="info-card-sm"><div class="metric-label">Track {int(t_w)}/{int(t_s)}</div>'
                        f'<div style="font-family:\'DM Mono\',monospace;font-size:1rem;color:{"var(--green)" if t_sr > 20 else "var(--text)"}">{t_sr}%</div></div>'
                        f'<div class="info-card-sm"><div class="metric-label">Distance {int(d_w)}/{int(d_s)}</div>'
                        f'<div style="font-family:\'DM Mono\',monospace;font-size:1rem;color:{"var(--green)" if d_sr > 20 else "var(--text)"}">{d_sr}%</div></div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    # Jockey/trainer combo
                    if tj_runs >= 5:
                        tj_a2e_color = "var(--green)" if tj_a2e >= 1.0 else "var(--red)"
                        st.markdown(
                            f'<div class="info-card-sm" style="margin-bottom:14px">'
                            f'<div class="metric-label" style="margin-bottom:6px">J+T Combination ({int(tj_runs)} runs)</div>'
                            f'<div style="display:flex;gap:20px;font-family:\'DM Mono\',monospace;font-size:0.8rem">'
                            f'<span>SR <span style="color:var(--text)">{tj_sr:.1f}%</span></span>'
                            f'<span>A2E <span style="color:{tj_a2e_color};font-weight:500">{tj_a2e:.2f}</span></span>'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )

                    # Rating composite
                    if rating:
                        rating_color = "var(--green)" if rating["pct"] >= 70 else ("var(--amber)" if rating["pct"] >= 50 else "var(--red)")
                        st.markdown(
                            f'<div style="margin-bottom:10px">'
                            f'<div class="metric-label" style="margin-bottom:4px">Form Rating</div>'
                            f'<div style="display:flex;align-items:baseline;gap:8px;margin-bottom:6px">'
                            f'<span style="font-family:\'DM Mono\',monospace;font-size:1.7rem;color:{rating_color}">{rating["composite"]}</span>'
                            f'<span style="font-family:\'DM Mono\',monospace;font-size:0.72rem;color:var(--text3)">/ {MAX_SCORE} &nbsp; ({rating["pct"]}%)</span>'
                            f'</div>'
                            f'<div class="bar-wrap"><div class="bar-fill" style="width:{int(rating["pct"])}%;background:{rating_color}"></div></div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
                        for key, max_val in WEIGHTS.items():
                            val = rating.get(key,0)
                            pct = int(val/max_val*100) if max_val > 0 else 0
                            bar_col = "var(--gold)" if pct >= 70 else ("var(--blue)" if pct >= 40 else "var(--red)")
                            st.markdown(
                                f'<div class="comp-row">'
                                f'<span class="comp-name">{LABELS[key]}</span>'
                                f'<div style="flex:1;background:var(--bg3);border-radius:2px;height:2px">'
                                f'<div style="width:{pct}%;height:2px;background:{bar_col};border-radius:2px"></div></div>'
                                f'<span class="comp-score">{val:.1f}/{max_val}</span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                with right:
                    if not rating and not mf:
                        st.markdown('<div class="alert alert-blue">Click Rate All Runners to analyse</div>', unsafe_allow_html=True)
                    elif price <= 1:
                        st.markdown('<div class="alert alert-amber">No SP price available</div>', unsafe_allow_html=True)
                    else:
                        # ── Probability breakdown ──────────────────────
                        if mf and mp:
                            true_pct  = mf["true_implied_pct"]
                            raw_pct   = mf["raw_implied_pct"]
                            fair_o    = mf["fair_odds"]
                            model_pct = round(mp*100,1)
                            diff_pct  = round(model_pct - true_pct, 1)
                            diff_sign = "+" if diff_pct >= 0 else ""
                            diff_color = "var(--green)" if diff_pct > 0 else "var(--red)"

                            st.markdown(
                                f'<div class="info-card" style="margin-bottom:10px">'
                                f'<div class="metric-label" style="margin-bottom:10px">Probability Breakdown</div>'
                                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px">'
                                f'<div><div style="font-family:\'DM Mono\',monospace;font-size:0.6rem;color:var(--text3)">SP</div>'
                                f'<div style="font-family:\'DM Mono\',monospace;font-size:1.1rem;color:var(--gold)">${price:.2f}</div></div>'
                                f'<div><div style="font-family:\'DM Mono\',monospace;font-size:0.6rem;color:var(--text3)">Fair Odds</div>'
                                f'<div style="font-family:\'DM Mono\',monospace;font-size:1.1rem;color:var(--blue)">${fair_o:.2f}</div></div>'
                                f'<div><div style="font-family:\'DM Mono\',monospace;font-size:0.6rem;color:var(--text3)">Raw Mkt%</div>'
                                f'<div style="font-family:\'DM Mono\',monospace;font-size:1.1rem;color:var(--text2)">{raw_pct}%</div></div>'
                                f'<div><div style="font-family:\'DM Mono\',monospace;font-size:0.6rem;color:var(--text3)">True Mkt%</div>'
                                f'<div style="font-family:\'DM Mono\',monospace;font-size:1.1rem;color:var(--text)">{true_pct}%</div></div>'
                                f'<div><div style="font-family:\'DM Mono\',monospace;font-size:0.6rem;color:var(--text3)">Model%</div>'
                                f'<div style="font-family:\'DM Mono\',monospace;font-size:1.1rem;color:var(--blue)">{model_pct}%</div></div>'
                                f'<div><div style="font-family:\'DM Mono\',monospace;font-size:0.6rem;color:var(--text3)">Edge</div>'
                                f'<div style="font-family:\'DM Mono\',monospace;font-size:1.1rem;color:{diff_color}">{diff_sign}{diff_pct}%</div></div>'
                                f'</div>'
                                f'<div style="background:var(--bg3);border-radius:var(--r);padding:8px 10px;font-family:\'DM Mono\',monospace;font-size:0.68rem;color:var(--text3)">'
                                f'Bookie runs at {mf.get("overround_total","?")}% — you need True% not Raw% to find real value.'
                                f'</div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                        # ── Bet gates ─────────────────────────────────
                        if verdict:
                            g1 = "pill-green" if verdict["has_edge"]  else "pill-red"
                            g2 = "pill-green" if verdict["rating_ok"] else "pill-red"
                            g3 = "pill-green" if verdict["tj_ok"]     else "pill-red"
                            g1t = "PASS" if verdict["has_edge"]  else "FAIL"
                            g2t = "PASS" if verdict["rating_ok"] else "FAIL"
                            g3t = "PASS" if verdict["tj_ok"]     else "FAIL"

                            st.markdown(
                                f'<div class="info-card" style="margin-bottom:10px">'
                                f'<div class="metric-label" style="margin-bottom:10px">Bet Gates</div>'
                                f'<div class="gate-row"><span class="pill {g1}" style="width:42px;text-align:center">{g1t}</span><span class="gate-label">Positive edge (model &gt; market)</span></div>'
                                f'<div class="gate-row"><span class="pill {g2}" style="width:42px;text-align:center">{g2t}</span><span class="gate-label">Rating {rating["pct"] if rating else "?"}% ≥ min {st.session_state.min_rating}%</span></div>'
                                f'<div class="gate-row"><span class="pill {g3}" style="width:42px;text-align:center">{g3t}</span><span class="gate-label">T+J A2E {tj_a2e:.2f} ≥ 1.0 &nbsp; (SR {tj_sr:.1f}%)</span></div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                            if verdict["bet"]:
                                rec = recommended_stake(
                                    bank=st.session_state.bank, model_prob=mp, odds=price,
                                    method=st.session_state.staking_method,
                                    kelly_frac=st.session_state.kelly_fraction,
                                    flat_pct=st.session_state.flat_stake_pct,
                                    fixed=st.session_state.level_stake,
                                    max_pct=st.session_state.max_stake_pct,
                                )
                                ev_color = "var(--green)" if rec["ev"] >= 0 else "var(--red)"
                                st.markdown(
                                    f'<div class="stake-card">'
                                    f'<div class="metric-label" style="margin-bottom:6px">Recommended Stake — {st.session_state.staking_method}</div>'
                                    f'<div class="stake-amount">${rec["stake"]:.2f}</div>'
                                    f'<div style="font-family:\'DM Mono\',monospace;font-size:0.7rem;color:{ev_color};margin-top:4px">'
                                    f'EV ${rec["ev"]:+.2f} &nbsp;·&nbsp; {round(rec["stake"]/st.session_state.bank*100,1)}% of bank'
                                    f'</div></div>',
                                    unsafe_allow_html=True
                                )
                                st.markdown('<div class="alert alert-green">✦ BET — all three gates pass</div>', unsafe_allow_html=True)
                                if st.button(f"Log this bet — {name}", key=f"log_{hid}"):
                                    log_bet(name, f"{r_trk} R{r_num}", rec["stake"], price, verdict["edge_pct"])
                                    st.success("Bet logged ✓")
                            else:
                                reason_txt = " &nbsp;·&nbsp; ".join(verdict["reasons"])
                                st.markdown(f'<div class="alert alert-red">No bet — {reason_txt}</div>', unsafe_allow_html=True)

                # Notes
                nk   = f"{hid}_{extract_race_id(race)}"
                note = st.text_area("Notes", value=st.session_state.notes.get(nk,""), key=f"note_{hid}", height=52, placeholder="Add analysis notes...")
                st.session_state.notes[nk] = note


# ══════════════════════════════════════════════════════════════
# STAKING
# ══════════════════════════════════════════════════════════════
with t_staking:
    st.markdown('<div class="page-header"><span class="page-title">Staking Engine</span><span class="page-sub">METHODS · DISCIPLINE · BET LOG</span></div>', unsafe_allow_html=True)

    st.markdown("## Methods")
    c1,c2,c3 = st.columns(3)
    for col, title, pill_cls, body in [
        (c1,"Kelly Criterion","pill-gold","Mathematically optimal. Stakes proportional to your edge — bigger bets when edge is larger.<br><br><span style=\"font-family:'DM Mono',monospace;font-size:0.72rem;color:var(--text2)\">f = (bp − q) / b</span><br><br>Use Quarter Kelly (0.25) to reduce variance without sacrificing long-run growth. Full Kelly is theoretically correct but psychologically brutal during drawdowns."),
        (c2,"Flat Percentage","pill-blue","Fixed % of current bank on every qualifying bet. Automatically scales down during losing runs and up during winning streaks.<br><br>Simple, effective, easy to track ROI. Does not account for edge size — treats a 5% edge bet the same as a 25% edge bet."),
        (c3,"Level Stakes","pill-muted","Fixed dollar amount per bet regardless of bank size or edge magnitude.<br><br>Easiest for tracking ROI. Does not protect bank during drawdowns — a losing streak hits the same in dollar terms whether you're up or down."),
    ]:
        col.markdown(f'<div class="info-card"><div style="display:flex;align-items:center;gap:10px;margin-bottom:12px"><span class="pill {pill_cls}">{title}</span></div><div style="font-size:0.8rem;color:var(--text2);line-height:1.8">{body}</div></div>', unsafe_allow_html=True)

    bank_pct = st.session_state.bank / st.session_state.starting_bank * 100 if st.session_state.starting_bank else 100
    if bank_pct < 70:
        st.markdown(f'<div class="alert alert-red">⚠️  Stop-loss alert — bank at {bank_pct:.1f}% of starting bank. Halve all stakes until bank recovers above 85%.</div>', unsafe_allow_html=True)

    st.markdown("## Discipline Rules")
    rules = [
        (f"Never exceed {st.session_state.max_stake_pct:.1f}% of bank per bet", "Absolute size limit regardless of confidence or edge"),
        ("Only bet on positive model edge", "Model probability must exceed true market probability — not raw SP probability"),
        ("Stop-loss at 70% of starting bank", "Cut all stakes by 50% until bank recovers above 85%"),
        ("Log every single bet", "Discipline only works with honest, complete records — including losers"),
        ("No gut-feel overrides", "Emotional bets erode edge over time. The model is mechanical — keep it that way"),
        ("Minimum 200 bets before judging ROI", "50 bets is noise. Statistical significance requires volume"),
        ("Pre-race only", "This tool rates on pre-race data. It does not incorporate in-running information"),
        ("No chasing losses", "Staking method is applied mechanically. Never increase stakes to recover losses"),
    ]
    for rule, detail in rules:
        st.markdown(
            f'<div class="info-card-sm" style="display:flex;gap:14px;margin-bottom:6px">'
            f'<span style="color:var(--gold);font-family:\'DM Mono\',monospace;flex-shrink:0">—</span>'
            f'<div><div style="font-size:0.82rem;color:var(--text)">{rule}</div>'
            f'<div style="font-size:0.72rem;color:var(--text3);margin-top:2px">{detail}</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("## Bet Log")
    log = st.session_state.bet_log
    if not log:
        st.markdown('<div class="alert alert-blue">ℹ️  No bets logged yet. Qualifying bets can be logged from the Analysis tab.</div>', unsafe_allow_html=True)
    else:
        df_log = pd.DataFrame(log)
        st.dataframe(
            df_log[["datetime","horse","race","stake","odds","edge","result","pl"]].rename(columns={
                "datetime":"Time","horse":"Horse","race":"Race",
                "stake":"Stake $","odds":"Odds","edge":"Edge %","result":"Result","pl":"P/L $"
            }),
            use_container_width=True, hide_index=True
        )
        pending = [(i,b) for i,b in enumerate(log) if b["result"]=="Pending"]
        if pending:
            st.markdown("## Settle Bets")
            for idx, bet in pending:
                c1,c2,c3 = st.columns([5,1,1])
                with c1:
                    st.markdown(
                        f'<div style="font-family:\'DM Mono\',monospace;font-size:0.8rem;padding:8px 0">'
                        f'<span style="color:var(--gold)">{bet["horse"]}</span>'
                        f'&nbsp;&nbsp;<span style="color:var(--text3)">${bet["stake"]:.2f} @ {bet["odds"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with c2:
                    if st.button("✓ Won", key=f"won_{idx}"): settle_bet(idx,"Won"); st.rerun()
                with c3:
                    if st.button("✗ Lost", key=f"lost_{idx}"): settle_bet(idx,"Lost"); st.rerun()


# ══════════════════════════════════════════════════════════════
# BANKROLL
# ══════════════════════════════════════════════════════════════
with t_bankroll:
    st.markdown('<div class="page-header"><span class="page-title">Bankroll</span><span class="page-sub">PERFORMANCE ANALYTICS</span></div>', unsafe_allow_html=True)
    stats = bankroll_stats()
    if not stats:
        st.markdown('<div class="alert alert-blue">ℹ️  No settled bets yet.</div>', unsafe_allow_html=True)
    else:
        pl_color  = "green" if stats["pl"]  >= 0 else "red"
        roi_color = "green" if stats["roi"] >= 0 else "red"
        pl_sign   = "+" if stats["pl"]  >= 0 else ""
        roi_sign  = "+" if stats["roi"] >= 0 else ""
        st.markdown(f"""
        <div class="metric-grid">
          <div class="metric-card"><div class="metric-label">Current Bank</div><div class="metric-value gold">${stats['bank']:.0f}</div></div>
          <div class="metric-card"><div class="metric-label">Total P/L</div><div class="metric-value {pl_color}">{pl_sign}${stats['pl']:.2f}</div></div>
          <div class="metric-card"><div class="metric-label">ROI</div><div class="metric-value {roi_color}">{roi_sign}{stats['roi']:.1f}%</div></div>
          <div class="metric-card"><div class="metric-label">Strike Rate</div><div class="metric-value">{stats['strike_rate']:.1f}%</div></div>
          <div class="metric-card"><div class="metric-label">Total Bets</div><div class="metric-value">{stats['bets']}</div></div>
          <div class="metric-card"><div class="metric-label">Winners</div><div class="metric-value">{stats['winners']}</div></div>
          <div class="metric-card"><div class="metric-label">Avg Odds</div><div class="metric-value">{stats['avg_odds']}</div></div>
          <div class="metric-card"><div class="metric-label">Max Drawdown</div><div class="metric-value red">-${abs(stats['max_dd']):.2f}</div></div>
        </div>""", unsafe_allow_html=True)

        settled = [b for b in st.session_state.bet_log if b["result"]!="Pending"]

        st.markdown("## Cumulative P/L")
        pl_series = [0]+list(pd.Series([b["pl"] for b in settled]).cumsum())
        chart_df = pd.DataFrame({"Bet":range(len(pl_series)),"P/L ($)":pl_series}).set_index("Bet")
        st.line_chart(chart_df)

        st.markdown("## Performance by Odds Range")
        def odds_bucket(o):
            if o<2: return "< 2.0"
            elif o<4: return "2.0–4.0"
            elif o<7: return "4.0–7.0"
            elif o<12: return "7.0–12.0"
            else: return "12.0+"
        df_s = pd.DataFrame(settled); df_s["Range"] = df_s["odds"].apply(odds_bucket)
        grp = df_s.groupby("Range").agg(Bets=("pl","count"),PL=("pl","sum"),Staked=("stake","sum")).reset_index()
        grp["ROI %"] = (grp["PL"]/grp["Staked"]*100).round(1)
        grp["Win $"] = grp["PL"].round(2)
        st.dataframe(grp, use_container_width=True, hide_index=True)

        if st.button("Reset Bank and Log", type="secondary"):
            st.session_state.bet_log=[]; st.session_state.bank=st.session_state.starting_bank; st.rerun()


# ══════════════════════════════════════════════════════════════
# GUIDE
# ══════════════════════════════════════════════════════════════
with t_guide:
    st.markdown('<div class="page-header"><span class="page-title">Guide</span><span class="page-sub">HOW THE SYSTEM WORKS</span></div>', unsafe_allow_html=True)

    st.markdown("## Rating Factors")
    guide_df = pd.DataFrame({
        "Factor":      list(LABELS.values()),
        "Weight":      list(WEIGHTS.values()),
        "Description": [
            "Final 3F sectional / closing speed — identifies strong finishers and late sprinters",
            "Contextual speed rating adjusted for class, going condition, and race pace",
            "Trouble in running detected from comments (blocked, wide, bumped, interfered)",
            "Performance relative to race tempo — upgrades closers in hot-pace races",
            "Rewards class drops, penalises sharp class rises",
            "Carried weight with distance multiplier (matters more at 1600m+)",
            "Draw position with track-specific bias (Caulfield inside rail advantage)",
            "Jockey–trainer combination strike rate and A2E (above/below expectation)",
            "Win record at this specific track",
            "Win record at this specific distance (±100m tolerance)",
        ]
    })
    st.dataframe(guide_df, use_container_width=True, hide_index=True)

    st.markdown("## Market Framing Explained")
    st.markdown(f"""
    <div class="info-card" style="font-size:0.82rem;color:var(--text2);line-height:1.9">
    <div style="margin-bottom:12px">
    <span style="color:var(--text);font-family:'Syne',sans-serif;font-weight:600">Why not just use SP odds directly?</span><br>
    A bookmaker's starting price odds include an overround — they sum to more than 100% so the book always profits regardless of the outcome.
    On a typical Australian metro race, the total book is <span style="color:var(--gold)">~118–125%</span>. This means if you bet every horse at SP,
    you'd lose ~18–25% of your turnover over time.
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;font-family:'DM Mono',monospace;font-size:0.78rem">
      <div class="info-card-sm"><span style="color:var(--text3)">Raw Implied%</span><br><span style="color:var(--text)">= 1 / SP</span><br><span style="color:var(--text3);font-size:0.68rem">Includes full overround</span></div>
      <div class="info-card-sm"><span style="color:var(--text3)">True Implied%</span><br><span style="color:var(--text)">= Raw% / Sum(all Raw%)</span><br><span style="color:var(--text3);font-size:0.68rem">De-vigged — actual market view</span></div>
      <div class="info-card-sm"><span style="color:var(--text3)">Fair Odds</span><br><span style="color:var(--text)">= 1 / True%</span><br><span style="color:var(--text3);font-size:0.68rem">What the odds would be at 100%</span></div>
      <div class="info-card-sm"><span style="color:var(--text3)">Edge</span><br><span style="color:var(--text)">= Model% − True%</span><br><span style="color:var(--text3);font-size:0.68rem">Positive = value opportunity</span></div>
    </div>
    <div>
    A horse at $4.00 in a 10-runner race has a <span style="color:var(--amber)">raw implied probability of 25%</span>. But if the total book is 122%,
    its <span style="color:var(--green)">true market probability is only 20.5%</span>. Our model must beat 20.5%, not 25%, to find genuine value.
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## Speedmap")
    st.markdown("""
    <div class="info-card">
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px">
      <div><div class="pill pill-red" style="margin-bottom:8px">HOT</div><div style="font-size:0.78rem;color:var(--text2)">3+ leaders — burn-up expected. Back closers and midfielders.</div></div>
      <div><div class="pill pill-amber" style="margin-bottom:8px">GENUINE</div><div style="font-size:0.78rem;color:var(--text2)">Two leaders fighting — honest pace. All styles viable.</div></div>
      <div><div class="pill pill-green" style="margin-bottom:8px">SOFT</div><div style="font-size:0.78rem;color:var(--text2)">Single uncontested leader. Front-runner advantage.</div></div>
      <div><div class="pill pill-blue" style="margin-bottom:8px">MODERATE</div><div style="font-size:0.78rem;color:var(--text2)">Unclear dynamics. Look for versatile runners.</div></div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## Tips")
    tips = [
        ("Rate every runner", "Never skip a horse because it looks unwinnable — you need the full field to frame probabilities correctly"),
        ("Log every qualifying bet", "Discipline only works with honest, complete records including all losers"),
        ("Don't override the model", "Emotional bets erode edge. The model is mechanical — keep it that way"),
        ("Specialise", "Restricting to metro Thoroughbreds improves data consistency and model accuracy"),
        ("Volume before judgment", "50 bets is statistical noise. Assess profitability after 200+ settled bets"),
        ("Track closing line value", "Consistently beating the closing price is the strongest leading indicator that your model works"),
        ("Revisit weights if losing", "Negative ROI after 200+ bets? Revisit factor weights before abandoning the approach entirely"),
    ]
    for title, detail in tips:
        st.markdown(
            f'<div class="info-card-sm" style="display:flex;gap:14px;margin-bottom:6px">'
            f'<span style="color:var(--gold);font-family:\'DM Mono\',monospace;flex-shrink:0">—</span>'
            f'<div><div style="font-size:0.82rem;color:var(--text)">{title}</div>'
            f'<div style="font-size:0.72rem;color:var(--text3);margin-top:2px">{detail}</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown(
    '<div style="text-align:center;padding:40px 0 20px;font-family:\'DM Mono\',monospace;'
    'font-size:0.58rem;color:var(--text3);letter-spacing:0.12em">'
    'RACING EDGE &nbsp;·&nbsp; RESEARCH PURPOSES ONLY &nbsp;·&nbsp; GAMBLE RESPONSIBLY &nbsp;·&nbsp; 1800 858 858'
    '</div>',
    unsafe_allow_html=True
)
