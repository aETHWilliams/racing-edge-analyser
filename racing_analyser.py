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
    page_title="Racing Edge",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:         #08090b;
    --surface:    #111316;
    --surface2:   #181b1f;
    --border:     #1f2328;
    --border2:    #2a2f38;
    --accent:     #c8f135;
    --red:        #f1543f;
    --green:      #3cf0a0;
    --blue:       #5ab4ff;
    --amber:      #f5a623;
    --text:       #d4dae6;
    --muted:      #4a5568;
    --muted2:     #6b7a99;
    --radius:     6px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif !important; }

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

h1 {
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem; font-weight: 500;
    color: var(--accent);
    letter-spacing: 0.08em; text-transform: uppercase;
}
h2 {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem; font-weight: 400;
    color: var(--muted2);
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 16px;
}
h3 {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem; color: var(--muted2);
    letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 12px;
}

.card    { background: var(--surface);  border: 1px solid var(--border);  border-radius: var(--radius); padding: 20px;    margin-bottom: 12px; }
.card-sm { background: var(--surface2); border: 1px solid var(--border);  border-radius: var(--radius); padding: 14px 16px; margin-bottom: 8px; }

.stat-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 20px; }
.stat { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px 18px; }
.stat-label { font-family: 'DM Mono', monospace; font-size: 0.62rem; color: var(--muted); letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 6px; }
.stat-value { font-family: 'DM Mono', monospace; font-size: 1.55rem; font-weight: 500; color: var(--text); line-height: 1; }
.stat-value.accent { color: var(--accent); }
.stat-value.green  { color: var(--green); }
.stat-value.red    { color: var(--red); }
.stat-value.amber  { color: var(--amber); }

.pill { display: inline-block; font-family: 'DM Mono', monospace; font-size: 0.6rem; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; padding: 3px 8px; border-radius: 3px; margin-right: 4px; }
.pill-green  { background: rgba(60,240,160,0.08);  color: var(--green);  border: 1px solid rgba(60,240,160,0.2); }
.pill-red    { background: rgba(241,84,63,0.08);   color: var(--red);    border: 1px solid rgba(241,84,63,0.2); }
.pill-amber  { background: rgba(245,166,35,0.08);  color: var(--amber);  border: 1px solid rgba(245,166,35,0.2); }
.pill-blue   { background: rgba(90,180,255,0.08);  color: var(--blue);   border: 1px solid rgba(90,180,255,0.2); }
.pill-accent { background: rgba(200,241,53,0.08);  color: var(--accent); border: 1px solid rgba(200,241,53,0.2); }
.pill-muted  { background: rgba(74,85,104,0.15);   color: var(--muted2); border: 1px solid var(--border2); }

.alert { padding: 10px 14px; border-radius: var(--radius); font-size: 0.82rem; margin-bottom: 12px; font-family: 'DM Mono', monospace; }
.alert-green { background: rgba(60,240,160,0.06);  border-left: 2px solid var(--green);  color: var(--green); }
.alert-red   { background: rgba(241,84,63,0.06);   border-left: 2px solid var(--red);    color: var(--red); }
.alert-amber { background: rgba(245,166,35,0.06);  border-left: 2px solid var(--amber);  color: var(--amber); }
.alert-blue  { background: rgba(90,180,255,0.06);  border-left: 2px solid var(--blue);   color: var(--blue); }

.bar-wrap { background: var(--border2); border-radius: 2px; height: 3px; width: 100%; margin-top: 6px; }
.bar-fill { height: 3px; border-radius: 2px; background: var(--accent); }

.sm-row { display: flex; align-items: center; gap: 12px; padding: 8px 12px; border-radius: var(--radius); background: var(--surface2); border: 1px solid var(--border); margin-bottom: 5px; }
.sm-pos { font-family: 'DM Mono', monospace; font-size: 0.6rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; min-width: 80px; }
.sm-horses { font-size: 0.82rem; color: var(--text); }

.comp-row { display: flex; align-items: center; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid var(--border); font-size: 0.78rem; }
.comp-row:last-child { border-bottom: none; }
.comp-name  { color: var(--muted2); font-family: 'DM Mono', monospace; font-size: 0.68rem; letter-spacing: 0.06em; }
.comp-score { font-family: 'DM Mono', monospace; font-size: 0.75rem; color: var(--text); }

[data-testid="stSidebar"] label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.65rem !important; letter-spacing: 0.1em !important;
    text-transform: uppercase !important; color: var(--muted2) !important;
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {
    background: var(--surface2) !important; border: 1px solid var(--border2) !important;
    color: var(--text) !important; border-radius: var(--radius) !important;
    font-family: 'DM Mono', monospace !important; font-size: 0.8rem !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: var(--surface2) !important; border: 1px solid var(--border2) !important;
    color: var(--text) !important; border-radius: var(--radius) !important;
}

.stButton > button {
    background: var(--accent) !important; color: #08090b !important;
    border: none !important; border-radius: var(--radius) !important;
    font-family: 'DM Mono', monospace !important; font-size: 0.7rem !important;
    font-weight: 500 !important; letter-spacing: 0.1em !important;
    text-transform: uppercase !important; padding: 0.45rem 1.2rem !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
.stButton > button[kind="secondary"] {
    background: var(--surface2) !important; color: var(--muted2) !important;
    border: 1px solid var(--border2) !important;
}

.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid var(--border) !important; gap: 0 !important; }
.stTabs [data-baseweb="tab"] { font-family: 'DM Mono', monospace !important; font-size: 0.65rem !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; color: var(--muted) !important; padding: 10px 20px !important; background: transparent !important; border: none !important; }
.stTabs [aria-selected="true"] { color: var(--accent) !important; border-bottom: 1px solid var(--accent) !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 24px !important; }

[data-testid="stExpander"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; margin-bottom: 8px !important; }
[data-testid="stExpander"] summary { font-family: 'DM Mono', monospace !important; font-size: 0.78rem !important; color: var(--text) !important; padding: 12px 16px !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: var(--radius) !important; }
[data-testid="stSlider"] label { color: var(--muted2) !important; }

.sb-label { font-family: 'DM Mono', monospace; font-size: 0.58rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); padding: 12px 0 6px; border-bottom: 1px solid var(--border); margin-bottom: 12px; }

.title-bar { display: flex; align-items: baseline; gap: 16px; padding-bottom: 20px; border-bottom: 1px solid var(--border); margin-bottom: 24px; }
.title-main { font-family: 'DM Mono', monospace; font-size: 1rem; font-weight: 500; color: var(--accent); letter-spacing: 0.12em; text-transform: uppercase; }
.title-sub  { font-family: 'DM Mono', monospace; font-size: 0.65rem; color: var(--muted); letter-spacing: 0.08em; }

hr { border: none; border-top: 1px solid var(--border); margin: 20px 0; }
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

# FIX 1: fetch_meetings had broken indentation — `if not data` and `return []`
# were misplaced as stray lines outside their logical block.
def fetch_meetings(target_date: date) -> list:
    ds = target_date.strftime("%Y-%m-%d")
    data = pf_get("form/meetingslist", {"meetingDate": ds})
    if not data:
        return []
    payload = data.get("payLoad", data) if isinstance(data, dict) else data
    return payload if isinstance(payload, list) else []

def fetch_race_runners(race_id: str) -> list:
    data = pf_get("form/form", {"raceId": race_id})
    if not data:
        return []
    return data.get("payLoad", data) if isinstance(data, dict) else data

def fetch_runner_form(horse_id: str) -> list:
    data = pf_get("form/form", {"horseId": horse_id})
    if not data:
        return []
    payload = data.get("payLoad", data) if isinstance(data, dict) else data
    return payload if isinstance(payload, list) else []


# ─────────────────────────────────────────────────────────────
# RATING ENGINE
# ─────────────────────────────────────────────────────────────
WEIGHTS = {
    "form_rating": 20, "speed_rating": 20, "class_rating": 15,
    "barrier_rating": 10, "weight_rating": 10, "jockey_rating": 10,
    "trainer_rating": 5, "track_rating": 5, "distance_rating": 5,
}
MAX_SCORE = sum(WEIGHTS.values())
LABELS = {
    "form_rating": "Form", "speed_rating": "Speed", "class_rating": "Class",
    "barrier_rating": "Barrier", "weight_rating": "Weight", "jockey_rating": "Jockey",
    "trainer_rating": "Trainer", "track_rating": "Track", "distance_rating": "Distance",
}

def safe_float(val, default=0.0):
    try:   return float(val)
    except: return default

def calc_form_rating(past):
    if not past: return 5.0
    w = [5,4,3,2,1]; score = denom = 0.0
    for i, s in enumerate(past[:5]):
        pos = safe_float(s.get("finishingPosition",10))
        field = max(safe_float(s.get("numberOfRunners",10)),1)
        score += (1-(pos-1)/field)*w[i]; denom += w[i]
    return round(score/denom*20,1) if denom else 10.0

def calc_speed_rating(runner):
    spd = safe_float(runner.get("speedRating") or runner.get("bestSpeed") or 0)
    return round(min(max((spd-90)/40*20,0),20),1) if spd>0 else 10.0

def calc_class_rating(runner, past):
    cur = safe_float(runner.get("raceClass") or 0)
    if not past or cur==0: return 10.0
    prev = [safe_float(s.get("raceClass",0)) for s in past[:3] if s.get("raceClass")]
    return round(min(max(10+(sum(prev)/len(prev)-cur)*1.5,2),15),1) if prev else 10.0

def calc_barrier_rating(runner):
    b = safe_float(runner.get("barrierNumber") or runner.get("barrier",8))
    if b<=0: return 8.0
    if b<=4: return 10.0
    if b<=8: return 8.0
    if b<=12: return 6.0
    return round(max(10-(b-12)*0.5,2),1)

def calc_weight_rating(runner):
    w = safe_float(runner.get("weightCarried") or runner.get("handicapWeight",57))
    return round(min(max(10-(w-54)*0.5,2),10),1) if w else 8.0

def calc_jockey_rating(runner):
    sr = safe_float(runner.get("jockeyStrikeRate") or runner.get("jockeySR",0))
    return round(min(sr/25*10,10),1) if sr>0 else 7.0

def calc_trainer_rating(runner):
    sr = safe_float(runner.get("trainerStrikeRate") or runner.get("trainerSR",0))
    return round(min(sr/25*5,5),1) if sr>0 else 3.5

def calc_track_rating(runner, past):
    track = (runner.get("meetingName") or "").lower()
    runs  = [s for s in past if (s.get("meetingName") or "").lower()==track]
    wins  = [s for s in runs if safe_float(s.get("finishingPosition",99))==1]
    return round(len(wins)/len(runs)*5,1) if runs else 3.0

def calc_distance_rating(runner, past):
    dist = safe_float(runner.get("raceDistance") or runner.get("distance",1200))
    runs = [s for s in past if abs(safe_float(s.get("raceDistance") or s.get("distance",0))-dist)<=100]
    wins = [s for s in runs if safe_float(s.get("finishingPosition",99))==1]
    return round(len(wins)/len(runs)*5,1) if runs else 2.0

def rate_runner(runner, past=[]):
    br = {
        "form_rating":     calc_form_rating(past),
        "speed_rating":    calc_speed_rating(runner),
        "class_rating":    calc_class_rating(runner,past),
        "barrier_rating":  calc_barrier_rating(runner),
        "weight_rating":   calc_weight_rating(runner),
        "jockey_rating":   calc_jockey_rating(runner),
        "trainer_rating":  calc_trainer_rating(runner),
        "track_rating":    calc_track_rating(runner,past),
        "distance_rating": calc_distance_rating(runner,past),
    }
    br["composite"] = round(sum(br.values()),1)
    br["pct"]       = round(br["composite"]/MAX_SCORE*100,1)
    return br


# ─────────────────────────────────────────────────────────────
# SPEEDMAP
# ─────────────────────────────────────────────────────────────
PACE_LABELS = {1:"Leader",2:"On Pace",3:"Midfield",4:"Back",5:"Last"}

def assign_pace(runners):
    for r in runners:
        if not r.get("pacePosition"):
            b = safe_float(r.get("barrierNumber") or r.get("barrier",8))
            r["pacePosition"] = 1 if b<=3 else 2 if b<=6 else 3 if b<=10 else 4
    return runners

def classify_tempo(runners):
    leaders = [r for r in runners if r.get("pacePosition")==1]
    on_pace = [r for r in runners if r.get("pacePosition")==2]
    n = len(leaders)
    if n>=3:    tempo,desc = "HOT",      "Multiple speed horses — fast early pace, favours closers."
    elif n==2:  tempo,desc = "GENUINE",  "Two leaders contesting — honest pace, all styles viable."
    elif n==1 and len(on_pace)<=1: tempo,desc = "SOFT","Single uncontested leader — front-runner advantage."
    else:       tempo,desc = "MODERATE", "Balanced speed — no dominant pace advantage."
    return {"tempo":tempo,"description":desc}


# ─────────────────────────────────────────────────────────────
# STAKING ENGINE
# ─────────────────────────────────────────────────────────────
def kelly_stake(bank, prob, odds, fraction):
    b = odds-1
    if b<=0 or prob<=0 or prob>=1: return 0.0
    k = (b*prob-(1-prob))/b
    return bank*fraction*max(k,0)

def recommended_stake(bank, pct, odds, method, kelly_frac, flat_pct, fixed, max_pct):
    prob = pct/100; mkt = 1/odds if odds>1 else 0; edge = prob-mkt
    if method=="Kelly":      stake = kelly_stake(bank,prob,odds,kelly_frac)
    elif method=="Flat %":   stake = bank*flat_pct/100 if edge>0 else 0
    else:                    stake = fixed if edge>0 else 0
    stake = min(round(stake,2), bank*max_pct/100)
    return {
        "stake": stake, "model_prob": round(prob*100,1),
        "market_prob": round(mkt*100,1), "edge_pct": round(edge*100,1),
        "value": edge>0, "ev": round((prob*(odds-1)-(1-prob))*stake,2),
    }


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
    st.markdown('<div class="title-main">Racing Edge</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-label">API Connection</div>', unsafe_allow_html=True)
    try:
        secret_key = st.secrets.get("PUNTINGFORM_API_KEY","")
    except:
        secret_key = ""
    api_key = st.text_input("PuntingForm API Key", type="password",
        value=st.session_state.api_key or secret_key,
        placeholder="Auto-loaded from secrets")
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key

    st.markdown('<div class="sb-label">Race Selection</div>', unsafe_allow_html=True)
    target_date  = st.date_input("Race Date", value=date.today()+timedelta(days=1))
    state_filter = st.multiselect("States", ["QLD","NSW","VIC","SA","WA","TAS","NT","ACT"])

    if st.button("Fetch Meetings"):
        with st.spinner("Fetching..."):
            st.session_state.races = fetch_meetings(target_date)
        if st.session_state.races:
            st.success(f"{len(st.session_state.races)} meetings loaded")
        else:
            st.warning("No meetings found")

    st.markdown('<div class="sb-label">Staking</div>', unsafe_allow_html=True)
    st.session_state.bank = st.number_input("Bank ($)", value=st.session_state.bank, step=10.0)
    st.session_state.staking_method = st.selectbox("Method",["Kelly","Flat %","Level"],
        index=["Kelly","Flat %","Level"].index(st.session_state.staking_method))
    if st.session_state.staking_method=="Kelly":
        st.session_state.kelly_fraction = st.slider("Kelly Fraction",0.1,1.0,st.session_state.kelly_fraction,0.05)
    elif st.session_state.staking_method=="Flat %":
        st.session_state.flat_stake_pct = st.slider("% of Bank",0.5,10.0,st.session_state.flat_stake_pct,0.5)
    else:
        st.session_state.level_stake = st.number_input("Fixed Stake ($)",value=st.session_state.level_stake,step=5.0)
    st.session_state.max_stake_pct = st.slider("Max Stake % of Bank",1.0,15.0,st.session_state.max_stake_pct,0.5)

    st.markdown('<div class="sb-label">Filters</div>', unsafe_allow_html=True)
    st.session_state.min_odds   = st.number_input("Min Odds",  value=st.session_state.min_odds,  step=0.1)
    st.session_state.max_odds   = st.number_input("Max Odds",  value=st.session_state.max_odds,  step=0.5)
    st.session_state.min_rating = st.slider("Min Rating (%)",0,100,st.session_state.min_rating)


# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
t_races, t_analysis, t_staking, t_bankroll, t_guide = st.tabs([
    "Races","Analysis","Staking","Bankroll","Guide"
])


# ══════════════════════════════════════════════════════════════
# RACES
# ══════════════════════════════════════════════════════════════
with t_races:
    st.markdown('<div class="title-bar"><span class="title-main">Race Meetings</span><span class="title-sub">Select a race to analyse</span></div>', unsafe_allow_html=True)

    if not st.session_state.api_key:
        st.markdown('<div class="alert alert-amber">Enter your PuntingForm API key in the sidebar to begin.</div>', unsafe_allow_html=True)

    if not st.session_state.races:
        st.markdown('<div class="alert alert-blue">Fetch meetings using the sidebar button.</div>', unsafe_allow_html=True)
    else:
        for meeting in st.session_state.races:
            name  = meeting.get("meetingName") or meeting.get("venueName","Unknown")
            state = meeting.get("state","")
            races = meeting.get("races",[])

            # FIX 2: `continue` was outside the for loop due to wrong indentation.
            # It must be inside the `for meeting` loop to skip non-matching states.
            if state_filter:
                normalized_state = state.upper()
                if not any(f in normalized_state for f in state_filter):
                    continue

            with st.expander(f"{name}  —  {state}  —  {len(races)} races"):
                for race in races:
                    r_num  = race.get("raceNumber","?")
                    r_name = race.get("raceName",f"Race {r_num}")
                    r_dist = race.get("raceDistance","?")
                    r_time = race.get("raceTime","")
                    r_cls  = race.get("raceClass","")
                    r_id   = str(race.get("raceId") or race.get("id",""))

                    c1,c2,c3 = st.columns([4,1,1])
                    with c1:
                        st.markdown(
                            f'<span style="font-family:\'DM Mono\',monospace;font-size:0.8rem">R{r_num} &nbsp; {r_name}</span>'
                            f'&nbsp;<span class="pill pill-muted">{r_dist}m</span>'
                            f'&nbsp;<span class="pill pill-muted">{r_cls}</span>'
                            f'&nbsp;<span style="font-family:\'DM Mono\',monospace;font-size:0.7rem;color:#4a5568">{r_time}</span>',
                            unsafe_allow_html=True
                        )
                    with c3:
                        if st.button("Analyse", key=f"sel_{r_id}"):
                            st.session_state.selected_race = race
                            st.session_state.runners = []
                            st.session_state.ratings = {}
                            with st.spinner("Loading runners..."):
                                runners = fetch_race_runners(r_id)
                                st.session_state.runners = assign_pace(runners)
                            st.success(f"{len(runners)} runners loaded — go to Analysis tab")


# ══════════════════════════════════════════════════════════════
# ANALYSIS
# ══════════════════════════════════════════════════════════════
with t_analysis:
    race    = st.session_state.selected_race
    runners = st.session_state.runners

    if not race:
        st.markdown('<div class="alert alert-blue">Select a race from the Races tab.</div>', unsafe_allow_html=True)
    elif not runners:
        st.markdown('<div class="alert alert-amber">No runners loaded for this race.</div>', unsafe_allow_html=True)
    else:
        r_name = race.get("raceName","Race")
        r_dist = race.get("raceDistance","?")
        r_trk  = race.get("meetingName","")
        r_cond = race.get("trackCondition","")
        r_cls  = race.get("raceClass","")

        st.markdown(
            f'<div class="title-bar">'
            f'<span class="title-main">{r_name}</span>'
            f'<span class="title-sub">{r_trk} &nbsp;|&nbsp; {r_dist}m &nbsp;|&nbsp; {r_cls} &nbsp;|&nbsp; {r_cond or "Condition TBC"}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Speedmap
        st.markdown("## Speedmap")
        tempo = classify_tempo(runners)
        tempo_pill = {"HOT":"pill-red","GENUINE":"pill-amber","SOFT":"pill-green","MODERATE":"pill-blue"}.get(tempo["tempo"],"pill-muted")
        st.markdown(
            f'<div class="card-sm" style="margin-bottom:14px">'
            f'<span class="pill {tempo_pill}">{tempo["tempo"]} PACE</span>'
            f'&nbsp;<span style="font-size:0.8rem;color:#6b7a99">{tempo["description"]}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        positions = {1:[],2:[],3:[],4:[],5:[]}
        for r in runners:
            positions[int(r.get("pacePosition",3))].append(r.get("runnerName") or r.get("horseName","?"))
        for pos,lbl in {1:"Leader",2:"On Pace",3:"Midfield",4:"Back",5:"Last"}.items():
            horses = positions.get(pos,[])
            if horses:
                st.markdown(
                    f'<div class="sm-row"><span class="sm-pos">{lbl}</span>'
                    f'<span class="sm-horses">{" &nbsp;&middot;&nbsp; ".join(horses)}</span></div>',
                    unsafe_allow_html=True
                )

        st.markdown('<hr>', unsafe_allow_html=True)

        # Ratings
        st.markdown("## Runner Ratings")
        if st.button("Rate All Runners"):
            ratings = {}; prog = st.progress(0)
            for i, runner in enumerate(runners):
                hid  = str(runner.get("horseId") or runner.get("id",""))
                past = fetch_runner_form(hid) if hid else []
                ratings[hid] = rate_runner(runner, past)
                prog.progress((i+1)/len(runners))
            st.session_state.ratings = ratings; prog.empty()
            st.success("All runners rated")

        ratings = st.session_state.ratings
        sorted_runners = sorted(runners, key=lambda r: ratings.get(str(r.get("horseId") or r.get("id","")),{}).get("composite",0), reverse=True)

        for rank, runner in enumerate(sorted_runners, 1):
            hid      = str(runner.get("horseId") or runner.get("id",""))
            name     = runner.get("runnerName") or runner.get("horseName","Unknown")
            barrier  = runner.get("barrierNumber") or runner.get("barrier","?")
            jockey   = runner.get("jockeyName","—")
            trainer  = runner.get("trainerName","—")
            weight   = runner.get("weightCarried") or runner.get("handicapWeight","—")
            price    = safe_float(runner.get("fixedOddsWin") or runner.get("price",0))
            pace_lbl = PACE_LABELS.get(int(runner.get("pacePosition",3)),"—")
            rating   = ratings.get(hid)
            label    = f"#{rank}  {name}   Barrier {barrier}   {'$'+str(price) if price else 'N/A'}"
            if rating: label += f"   Rating {rating['pct']}%"

            with st.expander(label, expanded=(rank<=3)):
                left, right = st.columns([3,2])
                with left:
                    st.markdown(
                        f'<span class="pill pill-muted">B{barrier}</span>'
                        f'<span class="pill pill-blue">{pace_lbl}</span>'
                        f'<span class="pill pill-muted">{weight}kg</span>',
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f'<div style="margin-top:10px;font-size:0.78rem;color:#6b7a99">'
                        f'Jockey &nbsp;<span style="color:#d4dae6">{jockey}</span>'
                        f'&nbsp;&nbsp; Trainer &nbsp;<span style="color:#d4dae6">{trainer}</span></div>',
                        unsafe_allow_html=True
                    )
                    if rating:
                        st.markdown(
                            f'<div style="margin-top:14px">'
                            f'<div style="font-family:\'DM Mono\',monospace;font-size:0.62rem;color:#4a5568;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:4px">Composite Rating</div>'
                            f'<div style="font-family:\'DM Mono\',monospace;font-size:1.4rem;color:#c8f135">{rating["composite"]}'
                            f'<span style="font-size:0.75rem;color:#6b7a99"> / {MAX_SCORE} &nbsp; ({rating["pct"]}%)</span></div>'
                            f'<div class="bar-wrap"><div class="bar-fill" style="width:{int(rating["pct"])}%"></div></div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
                        for key, max_val in WEIGHTS.items():
                            val = rating.get(key,0); pct = int(val/max_val*100)
                            st.markdown(
                                f'<div class="comp-row">'
                                f'<span class="comp-name">{LABELS[key]}</span>'
                                f'<div style="flex:1;margin:0 12px;background:var(--border2);border-radius:2px;height:2px">'
                                f'<div style="width:{pct}%;height:2px;background:var(--accent);border-radius:2px"></div></div>'
                                f'<span class="comp-score">{val} / {max_val}</span></div>',
                                unsafe_allow_html=True
                            )

                with right:
                    if rating and price > 1:
                        rec = recommended_stake(
                            bank=st.session_state.bank, pct=rating["pct"], odds=price,
                            method=st.session_state.staking_method, kelly_frac=st.session_state.kelly_fraction,
                            flat_pct=st.session_state.flat_stake_pct, fixed=st.session_state.level_stake,
                            max_pct=st.session_state.max_stake_pct,
                        )
                        ec = "green" if rec["value"] else "red"
                        es = f"+{rec['edge_pct']}%" if rec["edge_pct"]>=0 else f"{rec['edge_pct']}%"
                        st.markdown(
                            f'<div class="card-sm">'
                            f'<div class="stat-label">Recommended Stake</div>'
                            f'<div style="font-family:\'DM Mono\',monospace;font-size:1.5rem;color:var(--accent);margin-bottom:10px">${rec["stake"]:.2f}</div>'
                            f'<div style="font-size:0.72rem;color:#6b7a99;font-family:\'DM Mono\',monospace;line-height:1.9">'
                            f'Edge &nbsp;<span style="color:var(--{ec})">{es}</span><br>'
                            f'Model prob &nbsp;<span style="color:#d4dae6">{rec["model_prob"]}%</span><br>'
                            f'Market prob &nbsp;<span style="color:#d4dae6">{rec["market_prob"]}%</span><br>'
                            f'Expected value &nbsp;<span style="color:var(--{ec})">${rec["ev"]:.2f}</span>'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )
                        passes = (
                            rec["value"]
                            and st.session_state.min_odds <= price <= st.session_state.max_odds
                            and rating["pct"] >= st.session_state.min_rating
                            and rec["stake"] > 0
                        )
                        if passes:
                            st.markdown('<div class="alert alert-green">Qualifies — positive edge and passes all filters</div>', unsafe_allow_html=True)
                            if st.button(f"Log Bet — {name}", key=f"log_{hid}"):
                                log_bet(name, f"{r_trk} {r_name}", rec["stake"], price, rec["edge_pct"])
                                st.success("Bet logged")
                        else:
                            reasons = []
                            if not rec["value"]:                                reasons.append("no value edge")
                            if price < st.session_state.min_odds:               reasons.append("odds too short")
                            if price > st.session_state.max_odds:               reasons.append("odds too long")
                            if rating["pct"] < st.session_state.min_rating:     reasons.append("rating below threshold")
                            st.markdown(f'<div class="alert alert-red">No bet — {", ".join(reasons)}</div>', unsafe_allow_html=True)

                nk   = f"{hid}_{race.get('raceId','')}"
                note = st.text_area("Notes", value=st.session_state.notes.get(nk,""), key=f"note_{hid}", height=55, placeholder="Add notes...")
                st.session_state.notes[nk] = note


# ══════════════════════════════════════════════════════════════
# STAKING
# ══════════════════════════════════════════════════════════════
with t_staking:
    st.markdown('<div class="title-bar"><span class="title-main">Staking Engine</span><span class="title-sub">Methods, discipline rules and bet log</span></div>', unsafe_allow_html=True)

    st.markdown("## Methods")
    c1,c2,c3 = st.columns(3)
    for col, title, body in [
        (c1,"Kelly Criterion","Mathematically optimal. Stakes proportional to your edge.<br><br><span style=\"font-family:'DM Mono',monospace;font-size:0.72rem;color:#d4dae6\">f = (bp - q) / b</span><br><br>Quarter Kelly (0.25) is strongly recommended — reduces variance without sacrificing long-run growth."),
        (c2,"Flat Percentage","Fixed % of current bank on every qualifying bet. Automatically scales down during losing runs.<br><br>Simple and effective but does not account for edge size."),
        (c3,"Level Stakes","Fixed dollar amount per bet regardless of bank or edge.<br><br>Easiest for tracking ROI. Does not protect bank during drawdowns."),
    ]:
        col.markdown(f'<div class="card"><div class="stat-label" style="margin-bottom:8px">{title}</div><div style="font-size:0.8rem;color:#6b7a99;line-height:1.7">{body}</div></div>', unsafe_allow_html=True)

    bank_pct = st.session_state.bank / st.session_state.starting_bank * 100 if st.session_state.starting_bank else 100
    if bank_pct < 70:
        st.markdown(f'<div class="alert alert-red">Stop-loss alert — bank at {bank_pct:.1f}% of starting bank. Halve all stakes until bank recovers above 85%.</div>', unsafe_allow_html=True)

    st.markdown("## Discipline Rules")
    for rule in [
        f"Never exceed {st.session_state.max_stake_pct:.1f}% of bank per bet regardless of confidence",
        "Only bet when model probability exceeds market implied probability (positive edge)",
        "Stop-loss: if bank drops below 70% of starting bank, reduce all stakes by 50%",
        "Log every single bet — discipline only works with honest, complete records",
        "Do not override the model with gut feel — emotional bets erode edge over time",
        "Review ROI every 100 bets — reassess rating weights if consistently negative after 200+",
        "Pre-race only — this tool rates on pre-race data, not in-running information",
        "No chasing losses — staking method is applied mechanically, not reactively",
    ]:
        st.markdown(f'<div class="card-sm" style="font-size:0.82rem"><span style="color:var(--accent);font-family:\'DM Mono\',monospace;margin-right:10px">—</span>{rule}</div>', unsafe_allow_html=True)

    st.markdown("## Bet Log")
    log = st.session_state.bet_log
    if not log:
        st.markdown('<div class="alert alert-blue">No bets logged yet.</div>', unsafe_allow_html=True)
    else:
        df_log = pd.DataFrame(log)
        st.dataframe(
            df_log[["datetime","horse","race","stake","odds","edge","result","pl"]].rename(columns={
                "datetime":"Date/Time","horse":"Horse","race":"Race",
                "stake":"Stake","odds":"Odds","edge":"Edge %","result":"Result","pl":"P/L"
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
                        f'<span style="font-family:\'DM Mono\',monospace;font-size:0.8rem">{bet["horse"]}</span>'
                        f'&nbsp;<span style="color:#6b7a99;font-size:0.75rem">${bet["stake"]:.2f} @ {bet["odds"]}</span>',
                        unsafe_allow_html=True
                    )
                with c2:
                    if st.button("Won", key=f"won_{idx}"): settle_bet(idx,"Won"); st.rerun()
                with c3:
                    if st.button("Lost", key=f"lost_{idx}"): settle_bet(idx,"Lost"); st.rerun()


# ══════════════════════════════════════════════════════════════
# BANKROLL
# ══════════════════════════════════════════════════════════════
with t_bankroll:
    st.markdown('<div class="title-bar"><span class="title-main">Bankroll</span><span class="title-sub">Performance analytics</span></div>', unsafe_allow_html=True)
    stats = bankroll_stats()
    if not stats:
        st.markdown('<div class="alert alert-blue">No settled bets yet.</div>', unsafe_allow_html=True)
    else:
        plc  = "green" if stats["pl"]>=0  else "red"
        roic = "green" if stats["roi"]>=0 else "red"
        st.markdown(f"""
<div class="stat-grid">
  <div class="stat"><div class="stat-label">Current Bank</div><div class="stat-value">${stats['bank']:.0f}</div></div>
  <div class="stat"><div class="stat-label">Total P/L</div><div class="stat-value {plc}">{'+' if stats['pl']>=0 else ''}${stats['pl']:.2f}</div></div>
  <div class="stat"><div class="stat-label">ROI</div><div class="stat-value {roic}">{'+' if stats['roi']>=0 else ''}{stats['roi']:.1f}%</div></div>
  <div class="stat"><div class="stat-label">Strike Rate</div><div class="stat-value">{stats['strike_rate']:.1f}%</div></div>
  <div class="stat"><div class="stat-label">Total Bets</div><div class="stat-value">{stats['bets']}</div></div>
  <div class="stat"><div class="stat-label">Winners</div><div class="stat-value">{stats['winners']}</div></div>
  <div class="stat"><div class="stat-label">Avg Odds</div><div class="stat-value">{stats['avg_odds']}</div></div>
  <div class="stat"><div class="stat-label">Max Drawdown</div><div class="stat-value red">${stats['max_dd']:.2f}</div></div>
</div>""", unsafe_allow_html=True)

        settled = [b for b in st.session_state.bet_log if b["result"]!="Pending"]
        st.markdown("## Cumulative P/L")
        pl_series = [0]+list(pd.Series([b["pl"] for b in settled]).cumsum())
        st.line_chart(pd.DataFrame({"Bet":range(len(pl_series)),"P/L":pl_series}).set_index("Bet"), color="#c8f135")

        st.markdown("## By Odds Range")
        def odds_bucket(o):
            if o<2: return "< 2.0"
            elif o<4: return "2.0 – 4.0"
            elif o<7: return "4.0 – 7.0"
            elif o<12: return "7.0 – 12.0"
            else: return "12.0+"
        df_s = pd.DataFrame(settled); df_s["Range"] = df_s["odds"].apply(odds_bucket)
        grp = df_s.groupby("Range").agg(Bets=("pl","count"),PL=("pl","sum"),Staked=("stake","sum")).reset_index()
        grp["ROI %"] = (grp["PL"]/grp["Staked"]*100).round(1)
        st.dataframe(grp, use_container_width=True, hide_index=True)

        if st.button("Reset Bank and Log", type="secondary"):
            st.session_state.bet_log=[]; st.session_state.bank=st.session_state.starting_bank; st.rerun()


# ══════════════════════════════════════════════════════════════
# GUIDE
# ══════════════════════════════════════════════════════════════
with t_guide:
    st.markdown('<div class="title-bar"><span class="title-main">Guide</span><span class="title-sub">How the system works</span></div>', unsafe_allow_html=True)

    st.markdown("## Rating Factors")
    st.dataframe(pd.DataFrame({
        "Factor":      list(LABELS.values()),
        "Max Score":   list(WEIGHTS.values()),
        "Description": [
            "Weighted finishing positions across last 5 runs",
            "Normalised speed figure (benchmarked 90-130 scale)",
            "Rewards horses dropping in class, penalises sharp rises",
            "Draw position relative to field size",
            "Carried weight versus field average",
            "Jockey win strike rate at current track",
            "Trainer win strike rate",
            "Win record at this specific venue",
            "Win record at this specific distance",
        ]
    }), use_container_width=True, hide_index=True)

    st.markdown("## Speedmap")
    st.markdown("""
<div class="card">
<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px">
  <div><div class="pill pill-red" style="margin-bottom:8px">HOT</div><div style="font-size:0.78rem;color:#6b7a99">3+ leaders — burn-up early. Back closers and midfielders.</div></div>
  <div><div class="pill pill-amber" style="margin-bottom:8px">GENUINE</div><div style="font-size:0.78rem;color:#6b7a99">2 leaders fighting — honest pace. All styles viable.</div></div>
  <div><div class="pill pill-green" style="margin-bottom:8px">SOFT</div><div style="font-size:0.78rem;color:#6b7a99">Single uncontested leader. Front-runner has a big advantage.</div></div>
  <div><div class="pill pill-blue" style="margin-bottom:8px">MODERATE</div><div style="font-size:0.78rem;color:#6b7a99">Unclear dynamics. Look for adaptable runners.</div></div>
</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("## Value Betting")
    st.markdown("""
<div class="card" style="font-size:0.82rem;color:#6b7a99;line-height:1.8">
A value bet exists when your model's estimated probability exceeds the market's implied probability.<br><br>
<span style="font-family:'DM Mono',monospace;font-size:0.8rem;color:#d4dae6">Value = Model Prob &gt; (1 / Decimal Odds)</span><br><br>
If the model says 30% and the market prices the horse at $4.00 (25% implied), you hold a +5% edge.
Over hundreds of bets, positive edges compound into profit regardless of individual results.<br><br>
<span style="font-family:'DM Mono',monospace;font-size:0.8rem;color:#d4dae6">EV = (Win% x Net Win) — (Loss% x Stake)</span><br>
Only bet when EV is positive.
</div>
""", unsafe_allow_html=True)

    st.markdown("## Tips")
    for tip in [
        "Rate every runner — never skip a horse because it looks unwinnable",
        "Log every qualifying bet, win or lose — discipline only works with honest records",
        "Do not override the model with gut feel — emotional bets erode edge",
        "Specialise — restricting to metro Thoroughbreds improves data consistency",
        "50 bets is not enough to judge profitability — assess after 200+",
        "If ROI is negative after 200 bets, revisit factor weights before abandoning",
        "Track your closing line value — consistently beating the close means your model works",
    ]:
        st.markdown(f'<div class="card-sm" style="font-size:0.82rem"><span style="color:var(--accent);font-family:\'DM Mono\',monospace;margin-right:10px">—</span>{tip}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown(
    '<div style="text-align:center;padding:32px 0 16px;font-family:\'DM Mono\',monospace;'
    'font-size:0.6rem;color:#1f2328;letter-spacing:0.1em">'
    'Racing Edge &nbsp;|&nbsp; Research purposes only &nbsp;|&nbsp; Gamble Responsibly &nbsp;|&nbsp; 1800 858 858'
    '</div>',
    unsafe_allow_html=True
)
