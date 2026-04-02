"""
============================================================
  RACING EDGE ANALYSER  —  Full Professional System
  Powered by PuntingForm API + Staking Engine
============================================================
Dependencies:
    pip install streamlit requests pandas numpy plotly

Run:
    streamlit run racing_analyser.py
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import json
import math
from datetime import datetime, date, timedelta
from typing import Optional

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Racing Edge Analyser",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS  —  dark industrial theme
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

:root {
    --bg:       #0d0f14;
    --surface:  #161a22;
    --border:   #252b38;
    --accent:   #f0c040;
    --green:    #3ddc84;
    --red:      #ff5252;
    --blue:     #4fc3f7;
    --muted:    #6b7a99;
    --text:     #e8ecf4;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text);
    font-family: 'IBM Plex Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}

h1, h2, h3 { font-family: 'Bebas Neue', sans-serif; letter-spacing: 2px; color: var(--accent); }
h4, h5     { font-family: 'IBM Plex Mono', monospace; color: var(--text); }

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.metric-value { font-family: 'Bebas Neue', sans-serif; font-size: 2rem; color: var(--accent); }
.metric-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }

.horse-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.horse-card:hover { border-color: var(--accent); }

.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    margin-right: 4px;
}
.badge-green  { background: #1a3d2b; color: var(--green); border: 1px solid var(--green); }
.badge-red    { background: #3d1a1a; color: var(--red);   border: 1px solid var(--red); }
.badge-yellow { background: #3d3010; color: var(--accent); border: 1px solid var(--accent); }
.badge-blue   { background: #0d2233; color: var(--blue);  border: 1px solid var(--blue); }
.badge-grey   { background: #1c2231; color: var(--muted); border: 1px solid var(--border); }

.rating-bar-wrap { background: #1e2535; border-radius: 4px; height: 8px; width: 100%; margin-top: 4px; }
.rating-bar      { height: 8px; border-radius: 4px; background: var(--accent); }

.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
    margin-bottom: 12px;
}

.alert-box {
    padding: 10px 14px;
    border-radius: 6px;
    margin-bottom: 10px;
    font-size: 0.88rem;
}
.alert-info  { background: #0d2233; border-left: 3px solid var(--blue);  color: var(--blue); }
.alert-warn  { background: #2a2010; border-left: 3px solid var(--accent); color: var(--accent); }
.alert-good  { background: #0d2518; border-left: 3px solid var(--green); color: var(--green); }
.alert-bad   { background: #2a1010; border-left: 3px solid var(--red);   color: var(--red); }

code, .mono { font-family: 'IBM Plex Mono', monospace !important; }

/* Streamlit overrides */
div[data-testid="stMetric"] label { color: var(--muted) !important; }
div[data-testid="stMetric"] div   { color: var(--accent) !important; font-family: 'Bebas Neue'; font-size: 1.8rem; }
[data-testid="stSelectbox"] > div, [data-testid="stTextInput"] > div { background: var(--surface) !important; }
.stButton > button {
    background: var(--accent) !important;
    color: #0d0f14 !important;
    font-family: 'Bebas Neue', sans-serif !important;
    letter-spacing: 2px !important;
    border: none !important;
    font-size: 1rem !important;
    padding: 0.5rem 1.5rem !important;
}
.stButton > button:hover { background: #f5d060 !important; }
div[data-testid="stExpander"] { background: var(--surface) !important; border: 1px solid var(--border) !important; }

.stTabs [data-baseweb="tab-list"] { background: var(--surface); border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"]      { color: var(--muted); font-family: 'IBM Plex Mono'; font-size: 0.8rem; }
.stTabs [aria-selected="true"]    { color: var(--accent) !important; border-bottom: 2px solid var(--accent) !important; }

hr { border-color: var(--border) !important; }

.speedmap-lane {
    display: flex; align-items: center; gap: 8px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 4px; padding: 6px 10px; margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────
defaults = {
    "api_key": "",
    "races": [],
    "selected_race": None,
    "runners": [],
    "ratings": {},
    "bet_log": [],
    "bank": 1000.0,
    "starting_bank": 1000.0,
    "staking_method": "Kelly",
    "kelly_fraction": 0.25,
    "flat_stake_pct": 2.0,
    "level_stake": 20.0,
    "max_stake_pct": 5.0,
    "min_odds": 1.80,
    "max_odds": 20.0,
    "min_rating": 60,
    "notes": {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
# PUNTINGFORM API HELPERS
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
        st.error(f"API Error {e.response.status_code}: {e.response.text[:200]}")
    except Exception as e:
        st.error(f"Connection error: {e}")
    return None


def fetch_meetings(target_date: date) -> list:
    ds = target_date.strftime("%Y-%m-%d")
data = pf_get("form/meetingslist", {"meetingDate": ds})
  if not data:
        return []
    return data.get("payLoad", data) if isinstance(data, dict) else data


def fetch_race_runners(race_id: str) -> list:
    data = pf_get("form/runners", {"raceId": race_id})
    if not data:
        return []
    return data.get("payLoad", data) if isinstance(data, dict) else data


def fetch_speedmap(race_id: str) -> Optional[dict]:
    data = pf_get("form/speedmap", {"raceId": race_id})
    if not data:
        return None
    return data.get("payLoad", data) if isinstance(data, dict) else data


def fetch_runner_form(horse_id: str) -> list:
    data = pf_get("form/horseform", {"horseId": horse_id})
    if not data:
        return []
    return data.get("payLoad", data) if isinstance(data, dict) else data


def fetch_race_odds(race_id: str) -> list:
    data = pf_get("odds/flucs", {"raceId": race_id})
    if not data:
        return []
    return data.get("payLoad", data) if isinstance(data, dict) else data

# ─────────────────────────────────────────────────────────────
# RATING ENGINE
# ─────────────────────────────────────────────────────────────
WEIGHTS = {
    "form_rating":      20,
    "speed_rating":     20,
    "class_rating":     15,
    "barrier_rating":   10,
    "weight_rating":    10,
    "jockey_rating":    10,
    "trainer_rating":    5,
    "track_rating":      5,
    "distance_rating":   5,
}
MAX_SCORE = sum(WEIGHTS.values())   # 100


def safe_float(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def calc_form_rating(runner: dict, past_starts: list) -> float:
    """Score 0-20 based on recent finishes and margins."""
    if not past_starts:
        return 5.0
    score = 0.0
    weights_recent = [5, 4, 3, 2, 1]
    for i, s in enumerate(past_starts[:5]):
        pos  = safe_float(s.get("finishingPosition", 10))
        field = max(safe_float(s.get("numberOfRunners", 10)), 1)
        rel  = 1 - (pos - 1) / field
        score += rel * weights_recent[i]
    max_possible = sum(weights_recent[:min(5, len(past_starts))])
    return round((score / max_possible) * 20, 1) if max_possible else 10.0


def calc_speed_rating(runner: dict) -> float:
    """Use beyer/speed figure if present, else proxy from margin."""
    spd = safe_float(runner.get("speedRating") or runner.get("bestSpeed") or 0)
    if spd > 0:
        # normalise approx 90-130 range → 0-20
        return round(min(max((spd - 90) / 40 * 20, 0), 20), 1)
    return 10.0


def calc_class_rating(runner: dict, past_starts: list) -> float:
    """Reward horses dropping in class, penalise stepping up sharply."""
    current_class = safe_float(runner.get("raceClass") or 0)
    if not past_starts or current_class == 0:
        return 10.0
    prev_classes = [safe_float(s.get("raceClass", 0)) for s in past_starts[:3] if s.get("raceClass")]
    if not prev_classes:
        return 10.0
    avg_prev = sum(prev_classes) / len(prev_classes)
    diff = avg_prev - current_class   # positive = dropping in class
    score = 10 + min(max(diff * 1.5, -8), 8)
    return round(score, 1)


def calc_barrier_rating(runner: dict) -> float:
    """
    Barriers 1-6 ideal for most tracks; wide draws penalised.
    """
    barrier = safe_float(runner.get("barrierNumber") or runner.get("barrier", 8))
    field_size = safe_float(runner.get("numberOfRunners", 12))
    if barrier <= 0:
        return 8.0
    if barrier <= 4:
        return 10.0
    elif barrier <= 8:
        return 8.0
    elif barrier <= 12:
        return 6.0
    else:
        # Wide draw — severity scales with field size
        penalty = min((barrier - 12) * 0.5, 4)
        return max(10.0 - penalty, 2.0)


def calc_weight_rating(runner: dict) -> float:
    """Lower carried weight is slightly favoured."""
    wgt = safe_float(runner.get("weightCarried") or runner.get("handicapWeight", 57))
    # 54 = elite light, 60+ = heavy
    if wgt == 0:
        return 8.0
    score = max(10 - (wgt - 54) * 0.5, 2)
    return round(min(score, 10), 1)


def calc_jockey_rating(runner: dict) -> float:
    """Use strike-rate if provided."""
    sr = safe_float(runner.get("jockeyStrikeRate") or runner.get("jockeySR", 0))
    if sr > 0:
        return round(min(sr / 25 * 10, 10), 1)
    return 7.0


def calc_trainer_rating(runner: dict) -> float:
    sr = safe_float(runner.get("trainerStrikeRate") or runner.get("trainerSR", 0))
    if sr > 0:
        return round(min(sr / 25 * 5, 5), 1)
    return 3.5


def calc_track_rating(runner: dict, past_starts: list) -> float:
    """Check runs at same track."""
    track = (runner.get("meetingName") or "").lower()
    wins_at_track = sum(
        1 for s in past_starts
        if (s.get("meetingName") or "").lower() == track
        and safe_float(s.get("finishingPosition", 99)) == 1
    )
    runs_at_track = sum(
        1 for s in past_starts
        if (s.get("meetingName") or "").lower() == track
    )
    if runs_at_track == 0:
        return 3.0   # unknown track record
    sr = wins_at_track / runs_at_track
    return round(sr * 5, 1)


def calc_distance_rating(runner: dict, past_starts: list) -> float:
    distance = safe_float(runner.get("raceDistance") or runner.get("distance", 1200))
    wins_at_dist = 0
    runs_at_dist = 0
    for s in past_starts:
        d = safe_float(s.get("raceDistance") or s.get("distance", 0))
        if abs(d - distance) <= 100:
            runs_at_dist += 1
            if safe_float(s.get("finishingPosition", 99)) == 1:
                wins_at_dist += 1
    if runs_at_dist == 0:
        return 2.0
    return round((wins_at_dist / runs_at_dist) * 5, 1)


def rate_runner(runner: dict, past_starts: list = []) -> dict:
    """Return full breakdown of component scores and composite."""
    br = {
        "form_rating":      calc_form_rating(runner, past_starts),
        "speed_rating":     calc_speed_rating(runner),
        "class_rating":     calc_class_rating(runner, past_starts),
        "barrier_rating":   calc_barrier_rating(runner),
        "weight_rating":    calc_weight_rating(runner),
        "jockey_rating":    calc_jockey_rating(runner),
        "trainer_rating":   calc_trainer_rating(runner),
        "track_rating":     calc_track_rating(runner, past_starts),
        "distance_rating":  calc_distance_rating(runner, past_starts),
    }
    br["composite"] = round(sum(br.values()), 1)
    br["pct"] = round(br["composite"] / MAX_SCORE * 100, 1)
    return br

# ─────────────────────────────────────────────────────────────
# SPEEDMAP ENGINE
# ─────────────────────────────────────────────────────────────
POSITION_LABELS = {
    1: "Leader",
    2: "On-pace",
    3: "Midfield",
    4: "Back",
    5: "Last",
}

def classify_tempo(runners: list) -> dict:
    """
    Classify race tempo based on number of runners likely to lead.
    Returns pace assessment dict.
    """
    leaders     = [r for r in runners if r.get("pacePosition", 3) == 1]
    on_pace     = [r for r in runners if r.get("pacePosition", 3) == 2]
    contested   = len(leaders) + len(on_pace)

    if len(leaders) >= 3:
        tempo = "HOT"
        tempo_desc = "Multiple speed horses — expect a fast early pace, favours closers."
    elif len(leaders) == 2:
        tempo = "GENUINE"
        tempo_desc = "Two leaders will fight early — moderate-to-fast pace, suits midfielders."
    elif len(leaders) == 1 and len(on_pace) <= 1:
        tempo = "SOFT"
        tempo_desc = "Single leader likely to control — soft pace, favours on-pace runners."
    else:
        tempo = "MODERATE"
        tempo_desc = "Balanced speed — no dominant pace advantage."

    return {
        "tempo": tempo,
        "description": tempo_desc,
        "leaders": [r.get("runnerName", "?") for r in leaders],
        "on_pace": [r.get("runnerName", "?") for r in on_pace],
    }


# ─────────────────────────────────────────────────────────────
# STAKING ENGINE
# ─────────────────────────────────────────────────────────────
def kelly_stake(bank: float, prob: float, odds: float, fraction: float = 0.25) -> float:
    """Fractional Kelly criterion."""
    b = odds - 1
    if b <= 0 or prob <= 0 or prob >= 1:
        return 0.0
    q = 1 - prob
    k = (b * prob - q) / b
    stake = bank * fraction * max(k, 0)
    return stake


def flat_pct_stake(bank: float, pct: float) -> float:
    return bank * pct / 100


def level_stake(fixed: float) -> float:
    return fixed


def recommended_stake(
    bank: float,
    composite_pct: float,
    market_odds: float,
    method: str = "Kelly",
    kelly_fraction: float = 0.25,
    flat_pct: float = 2.0,
    fixed: float = 20.0,
    max_pct: float = 5.0,
) -> dict:
    """
    Return stake recommendation + edge calculation.
    composite_pct: 0-100 model rating
    """
    # Estimate win probability from model rating
    raw_prob = composite_pct / 100
    # Implied probability from market odds
    market_prob = 1 / market_odds if market_odds > 1 else 0
    edge = raw_prob - market_prob

    if method == "Kelly":
        stake = kelly_stake(bank, raw_prob, market_odds, kelly_fraction)
    elif method == "Flat %":
        stake = flat_pct_stake(bank, flat_pct) if edge > 0 else 0
    else:  # Level
        stake = level_stake(fixed) if edge > 0 else 0

    # Cap at max_pct of bank
    max_stake = bank * max_pct / 100
    stake = min(stake, max_stake)
    stake = round(stake, 2)

    return {
        "stake":        stake,
        "model_prob":   round(raw_prob * 100, 1),
        "market_prob":  round(market_prob * 100, 1),
        "edge_pct":     round(edge * 100, 1),
        "value":        edge > 0,
        "ev":           round((raw_prob * (market_odds - 1) - (1 - raw_prob)) * stake, 2),
    }


# ─────────────────────────────────────────────────────────────
# BET LOG HELPERS
# ─────────────────────────────────────────────────────────────
def log_bet(horse: str, race: str, stake: float, odds: float, edge: float):
    st.session_state.bet_log.append({
        "datetime": datetime.now().strftime("%d/%m %H:%M"),
        "horse":    horse,
        "race":     race,
        "stake":    stake,
        "odds":     odds,
        "edge":     edge,
        "result":   "Pending",
        "pl":       0.0,
    })


def settle_bet(idx: int, result: str):
    bet = st.session_state.bet_log[idx]
    if result == "Won":
        pl = bet["stake"] * (bet["odds"] - 1)
    else:
        pl = -bet["stake"]
    st.session_state.bet_log[idx]["result"] = result
    st.session_state.bet_log[idx]["pl"] = pl
    st.session_state.bank += pl


# ─────────────────────────────────────────────────────────────
# BANKROLL ANALYTICS
# ─────────────────────────────────────────────────────────────
def bankroll_stats() -> dict:
    log = [b for b in st.session_state.bet_log if b["result"] != "Pending"]
    if not log:
        return {}
    total_staked = sum(b["stake"] for b in log)
    total_pl     = sum(b["pl"] for b in log)
    winners      = [b for b in log if b["result"] == "Won"]
    roi          = total_pl / total_staked * 100 if total_staked else 0
    strike_rate  = len(winners) / len(log) * 100 if log else 0
    avg_odds     = sum(b["odds"] for b in log) / len(log)
    drawdowns    = []
    running = 0
    peak = 0
    for b in log:
        running += b["pl"]
        if running > peak:
            peak = running
        drawdowns.append(running - peak)
    max_dd = min(drawdowns)
    return {
        "bets":         len(log),
        "winners":      len(winners),
        "strike_rate":  round(strike_rate, 1),
        "total_staked": round(total_staked, 2),
        "total_pl":     round(total_pl, 2),
        "roi":          round(roi, 1),
        "avg_odds":     round(avg_odds, 2),
        "max_drawdown": round(max_dd, 2),
        "current_bank": round(st.session_state.bank, 2),
    }


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🏇 RACING EDGE")
    st.markdown('<div class="section-header">API CONNECTION</div>', unsafe_allow_html=True)
    api_key = st.text_input("PuntingForm API Key", type="password",
                            value=st.session_state.api_key,
                            placeholder="Enter key…")
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key

    st.markdown("---")
    st.markdown('<div class="section-header">RACE SELECTION</div>', unsafe_allow_html=True)
    tomorrow = date.today() + timedelta(days=1)
    target_date = st.date_input("Race Date", value=tomorrow)
    state_filter = st.multiselect("State filter", ["QLD","NSW","VIC","SA","WA","TAS","NT","ACT"], default=[])
    track_type   = st.selectbox("Track type", ["All", "Thoroughbred", "Harness", "Greyhound"])

    if st.button("⟳  FETCH MEETINGS"):
        with st.spinner("Fetching meetings…"):
            meetings = fetch_meetings(target_date)
            st.session_state.races = meetings
        if meetings:
            st.success(f"Found {len(meetings)} meetings")
        else:
            st.warning("No meetings found (check API key & date)")

    st.markdown("---")
    st.markdown('<div class="section-header">STAKING SETTINGS</div>', unsafe_allow_html=True)
    st.session_state.bank = st.number_input("Current Bank ($)", value=st.session_state.bank, step=10.0)
    if st.session_state.starting_bank == 1000.0 and st.session_state.bank != 1000.0:
        st.session_state.starting_bank = st.session_state.bank

    st.session_state.staking_method = st.selectbox(
        "Staking Method",
        ["Kelly", "Flat %", "Level"],
        index=["Kelly", "Flat %", "Level"].index(st.session_state.staking_method)
    )
    if st.session_state.staking_method == "Kelly":
        st.session_state.kelly_fraction = st.slider("Kelly Fraction", 0.1, 1.0, st.session_state.kelly_fraction, 0.05,
                                                      help="0.25 = Quarter Kelly (recommended for safety)")
    elif st.session_state.staking_method == "Flat %":
        st.session_state.flat_stake_pct = st.slider("% of Bank per Bet", 0.5, 10.0, st.session_state.flat_stake_pct, 0.5)
    else:
        st.session_state.level_stake = st.number_input("Fixed Stake ($)", value=st.session_state.level_stake, step=5.0)

    st.session_state.max_stake_pct = st.slider("Max Stake % of Bank", 1.0, 15.0, st.session_state.max_stake_pct, 0.5)

    st.markdown("---")
    st.markdown('<div class="section-header">FILTERS</div>', unsafe_allow_html=True)
    st.session_state.min_odds    = st.number_input("Min Odds", value=st.session_state.min_odds, step=0.1)
    st.session_state.max_odds    = st.number_input("Max Odds", value=st.session_state.max_odds, step=0.5)
    st.session_state.min_rating  = st.slider("Min Model Rating", 0, 100, st.session_state.min_rating)

# ─────────────────────────────────────────────────────────────
# MAIN TABS
# ─────────────────────────────────────────────────────────────
tab_races, tab_analysis, tab_staking, tab_bankroll, tab_guide = st.tabs([
    "🏁  RACES", "🔬  ANALYSIS", "💰  STAKING", "📊  BANKROLL", "📖  GUIDE"
])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — RACES
# ═══════════════════════════════════════════════════════════════
with tab_races:
    st.markdown("## RACE MEETINGS")
    if not st.session_state.api_key:
        st.markdown('<div class="alert-box alert-warn">⚠ Enter your PuntingForm API key in the sidebar to begin.</div>', unsafe_allow_html=True)

    meetings = st.session_state.races
    if not meetings:
        st.info("Fetch meetings using the sidebar button.")
    else:
        for meeting in meetings:
            name  = meeting.get("meetingName") or meeting.get("venueName", "Unknown")
            state = meeting.get("state","")
            races = meeting.get("races", [])

            # State filter
            if state_filter and state not in state_filter:
                continue

            with st.expander(f"🏟  {name}  ({state})  —  {len(races)} races"):
                for race in races:
                    r_num  = race.get("raceNumber", "?")
                    r_name = race.get("raceName", f"Race {r_num}")
                    r_dist = race.get("raceDistance", "?")
                    r_time = race.get("raceTime","")
                    r_id   = race.get("raceId") or race.get("id","")
                    r_cls  = race.get("raceClass","")

                    c1, c2, c3 = st.columns([3,1,1])
                    with c1:
                        st.markdown(f"**R{r_num} {r_name}** &nbsp; `{r_dist}m` &nbsp; `{r_cls}`")
                    with c2:
                        st.markdown(f"<span style='color:#6b7a99;font-size:0.85rem'>{r_time}</span>", unsafe_allow_html=True)
                    with c3:
                        if st.button("Analyse →", key=f"sel_{r_id}"):
                            st.session_state.selected_race = race
                            st.session_state.runners = []
                            st.session_state.ratings = {}
                            with st.spinner("Loading runners…"):
                                runners = fetch_race_runners(str(r_id))
                                st.session_state.runners = runners
                            st.success(f"Loaded {len(runners)} runners")

# ═══════════════════════════════════════════════════════════════
# TAB 2 — ANALYSIS
# ═══════════════════════════════════════════════════════════════
with tab_analysis:
    st.markdown("## RACE ANALYSIS")

    race = st.session_state.selected_race
    runners = st.session_state.runners

    if not race:
        st.info("Select a race from the RACES tab.")
    elif not runners:
        st.warning("No runners loaded for this race.")
    else:
        # ── Race header ────────────────────────────────────────
        r_name = race.get("raceName","Race")
        r_dist = race.get("raceDistance","?")
        r_cls  = race.get("raceClass","")
        r_trk  = race.get("meetingName","")
        r_cond = race.get("trackCondition","")

        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        with col_h1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Race</div><div class="metric-value" style="font-size:1.3rem">{r_name}</div></div>', unsafe_allow_html=True)
        with col_h2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Distance</div><div class="metric-value">{r_dist}m</div></div>', unsafe_allow_html=True)
        with col_h3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Track</div><div class="metric-value" style="font-size:1.2rem">{r_trk}</div></div>', unsafe_allow_html=True)
        with col_h4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Condition</div><div class="metric-value">{r_cond or "TBC"}</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # ── Speedmap ──────────────────────────────────────────
        st.markdown("### SPEEDMAP")

        # Assign pace positions from API or barrier heuristic
        for r in runners:
            if not r.get("pacePosition"):
                barrier = safe_float(r.get("barrierNumber") or r.get("barrier", 8))
                # Simple heuristic: low barrier → more likely to lead
                if barrier <= 3:
                    r["pacePosition"] = 1
                elif barrier <= 6:
                    r["pacePosition"] = 2
                elif barrier <= 10:
                    r["pacePosition"] = 3
                else:
                    r["pacePosition"] = 4

        tempo_info = classify_tempo(runners)
        tempo_colors = {"HOT":"#ff5252","GENUINE":"#f0c040","SOFT":"#3ddc84","MODERATE":"#4fc3f7"}
        tc = tempo_colors.get(tempo_info["tempo"],"#6b7a99")

        st.markdown(
            f'<div class="alert-box" style="border-left-color:{tc};color:{tc};background:#161a22">'
            f'<strong>PACE ASSESSMENT: {tempo_info["tempo"]}</strong><br>{tempo_info["description"]}'
            f'</div>',
            unsafe_allow_html=True
        )

        # Visual lane display
        positions = {1:[], 2:[], 3:[], 4:[], 5:[]}
        for r in runners:
            pp = int(r.get("pacePosition",3))
            positions[pp].append(r.get("runnerName") or r.get("horseName","?"))

        pos_labels = {1:"🔴 LEADER", 2:"🟡 ON PACE", 3:"🟢 MIDFIELD", 4:"🔵 BACK", 5:"⚫ LAST"}
        for pos, label in pos_labels.items():
            horses = positions.get(pos,[])
            if horses:
                names = "  ·  ".join(horses)
                st.markdown(
                    f'<div class="speedmap-lane">'
                    f'<span style="font-family:\'IBM Plex Mono\';font-size:0.75rem;min-width:110px;color:#6b7a99">{label}</span>'
                    f'<span style="font-size:0.88rem">{names}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown("---")

        # ── Runner Ratings ────────────────────────────────────
        st.markdown("### RUNNER RATINGS")

        if st.button("⚡  RATE ALL RUNNERS"):
            ratings = {}
            prog = st.progress(0)
            for i, runner in enumerate(runners):
                horse_id = str(runner.get("horseId") or runner.get("id",""))
                past = fetch_runner_form(horse_id) if horse_id else []
                ratings[horse_id] = rate_runner(runner, past)
                prog.progress((i+1)/len(runners))
            st.session_state.ratings = ratings
            prog.empty()
            st.success("Ratings complete!")

        ratings = st.session_state.ratings

        # Sort runners by composite score
        def runner_score(r):
            hid = str(r.get("horseId") or r.get("id",""))
            return ratings.get(hid, {}).get("composite", 0)

        sorted_runners = sorted(runners, key=runner_score, reverse=True)

        for rank, runner in enumerate(sorted_runners, 1):
            horse_id   = str(runner.get("horseId") or runner.get("id",""))
            horse_name = runner.get("runnerName") or runner.get("horseName","Unknown")
            barrier    = runner.get("barrierNumber") or runner.get("barrier","?")
            jockey     = runner.get("jockeyName","?")
            trainer    = runner.get("trainerName","?")
            weight     = runner.get("weightCarried") or runner.get("handicapWeight","?")
            price      = safe_float(runner.get("fixedOddsWin") or runner.get("price",0))
            pace_pos   = int(runner.get("pacePosition",3))
            pace_label = POSITION_LABELS.get(pace_pos, "Unknown")

            rating = ratings.get(horse_id)

            with st.expander(
                f"#{rank}  {horse_name}   "
                f"Barrier {barrier}   "
                f"{('$'+str(price)) if price else 'N/A'}",
                expanded=(rank <= 3)
            ):
                c_left, c_right = st.columns([3, 2])

                with c_left:
                    st.markdown(
                        f'<span class="badge badge-grey">B{barrier}</span>'
                        f'<span class="badge badge-blue">{pace_label}</span>'
                        f'<span class="badge badge-grey">{weight}kg</span>',
                        unsafe_allow_html=True
                    )
                    st.markdown(f"**Jockey:** {jockey} &nbsp;|&nbsp; **Trainer:** {trainer}")

                    if rating:
                        st.markdown(
                            f"<br><strong style='color:#f0c040'>COMPOSITE RATING: {rating['composite']} / {MAX_SCORE} "
                            f"({rating['pct']}%)</strong>",
                            unsafe_allow_html=True
                        )
                        bar_w = int(rating["pct"])
                        st.markdown(
                            f'<div class="rating-bar-wrap"><div class="rating-bar" style="width:{bar_w}%"></div></div>',
                            unsafe_allow_html=True
                        )
                        # Component breakdown table
                        comp_data = {
                            "Component":  [k.replace("_rating","").replace("_"," ").title() for k in WEIGHTS.keys()],
                            "Score":      [rating.get(k,0) for k in WEIGHTS.keys()],
                            "Max":        list(WEIGHTS.values()),
                        }
                        df_comp = pd.DataFrame(comp_data)
                        df_comp["%"] = (df_comp["Score"] / df_comp["Max"] * 100).round(0).astype(int)
                        st.dataframe(df_comp, use_container_width=True, hide_index=True)

                with c_right:
                    if rating and price > 1:
                        rec = recommended_stake(
                            bank=st.session_state.bank,
                            composite_pct=rating["pct"],
                            market_odds=price,
                            method=st.session_state.staking_method,
                            kelly_fraction=st.session_state.kelly_fraction,
                            flat_pct=st.session_state.flat_stake_pct,
                            fixed=st.session_state.level_stake,
                            max_pct=st.session_state.max_stake_pct,
                        )
                        edge_col = "badge-green" if rec["value"] else "badge-red"
                        edge_txt = f"+{rec['edge_pct']}%" if rec['edge_pct'] >= 0 else f"{rec['edge_pct']}%"

                        st.markdown(
                            f'<div class="metric-card">'
                            f'<div class="metric-label">RECOMMENDED STAKE</div>'
                            f'<div class="metric-value">${rec["stake"]:.2f}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f'<span class="badge {edge_col}">EDGE {edge_txt}</span><br>'
                            f'<span style="font-size:0.8rem;color:#6b7a99">Model prob: {rec["model_prob"]}% &nbsp;|&nbsp; '
                            f'Market prob: {rec["market_prob"]}%</span><br>'
                            f'<span style="font-size:0.8rem;color:#6b7a99">Expected Value: ${rec["ev"]:.2f}</span>',
                            unsafe_allow_html=True
                        )

                        # Filters check
                        passes = (
                            rec["value"]
                            and st.session_state.min_odds <= price <= st.session_state.max_odds
                            and rating["pct"] >= st.session_state.min_rating
                            and rec["stake"] > 0
                        )
                        if passes:
                            st.markdown('<div class="alert-box alert-good">✅ QUALIFIES FOR BET</div>', unsafe_allow_html=True)
                            if st.button(f"Log bet — {horse_name}", key=f"log_{horse_id}"):
                                log_bet(
                                    horse=horse_name,
                                    race=f"{r_trk} {r_name}",
                                    stake=rec["stake"],
                                    odds=price,
                                    edge=rec["edge_pct"]
                                )
                                st.success("Bet logged!")
                        else:
                            reasons = []
                            if not rec["value"]:    reasons.append("no value edge")
                            if price < st.session_state.min_odds: reasons.append("odds too short")
                            if price > st.session_state.max_odds: reasons.append("odds too long")
                            if rating["pct"] < st.session_state.min_rating: reasons.append("rating below threshold")
                            st.markdown(f'<div class="alert-box alert-bad">❌ No bet — {", ".join(reasons)}</div>', unsafe_allow_html=True)

                # Notes
                note_key = f"{horse_id}_{race.get('raceId','')}"
                existing_note = st.session_state.notes.get(note_key, "")
                note = st.text_area("📝 Notes", value=existing_note, key=f"note_{horse_id}", height=60)
                if note != existing_note:
                    st.session_state.notes[note_key] = note

# ═══════════════════════════════════════════════════════════════
# TAB 3 — STAKING
# ═══════════════════════════════════════════════════════════════
with tab_staking:
    st.markdown("## STAKING ENGINE & BET LOG")

    # Staking explainer
    st.markdown("### STAKING METHODS EXPLAINED")
    col_k, col_f, col_l = st.columns(3)
    with col_k:
        st.markdown("""
<div class="horse-card">
<h4>Kelly Criterion</h4>
<p style="font-size:0.85rem;color:#6b7a99">
Mathematically optimal staking. Bets a fraction of bank proportional to your edge.<br><br>
<strong>Formula:</strong> <code>f = (bp - q) / b</code><br>
b = decimal odds − 1<br>p = model win prob<br>q = 1 − p<br><br>
We apply a <strong>fractional Kelly</strong> (default 25%) to reduce variance and protect bankroll during downswings.
</p>
</div>
""", unsafe_allow_html=True)
    with col_f:
        st.markdown("""
<div class="horse-card">
<h4>Flat % of Bank</h4>
<p style="font-size:0.85rem;color:#6b7a99">
Bet a fixed % of current bank on every qualifying selection.<br><br>
<strong>Pros:</strong> Simple, automatically reduces stakes during losing runs.<br><br>
<strong>Cons:</strong> Ignores edge size — same stake for a small edge vs huge edge.
</p>
</div>
""", unsafe_allow_html=True)
    with col_l:
        st.markdown("""
<div class="horse-card">
<h4>Level Stakes</h4>
<p style="font-size:0.85rem;color:#6b7a99">
Fixed dollar amount per bet regardless of bank size or edge.<br><br>
<strong>Pros:</strong> Easiest to track ROI.<br><br>
<strong>Cons:</strong> Does not account for bankroll growth or drawdowns. Riskier during downswings.
</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### DISCIPLINE RULES")
    st.markdown("""
<div class="horse-card">
<ul style="font-size:0.88rem;line-height:2">
<li>🔒 <strong>Never exceed max stake % of bank</strong> — currently <code>{:.1f}%</code></li>
<li>📉 <strong>Stop-loss rule:</strong> If bank drops below 70% of starting bank, reduce stakes by 50% until recovered</li>
<li>🎯 <strong>Only bet when there is a positive value edge</strong> — model probability must exceed market implied probability</li>
<li>📅 <strong>Pre-race only</strong> — no in-running bets; this tool rates on pre-race information only</li>
<li>🚫 <strong>No chasing losses</strong> — staking method is applied mechanically, not emotionally</li>
<li>📊 <strong>Track everything</strong> — log every bet, win or lose, to allow accurate ROI calculation</li>
<li>🔁 <strong>Review monthly</strong> — reassess rating weights if ROI is negative over 100+ bets</li>
</ul>
</div>
""".format(st.session_state.max_stake_pct), unsafe_allow_html=True)

    # Stop-loss warning
    bank_pct = st.session_state.bank / st.session_state.starting_bank * 100 if st.session_state.starting_bank else 100
    if bank_pct < 70:
        st.markdown(
            f'<div class="alert-box alert-bad">⚠️ STOP-LOSS ALERT — Bank at {bank_pct:.1f}% of starting bank. '
            f'Reduce stake size by 50% until bank recovers above 85%.</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("### BET LOG")

    log = st.session_state.bet_log
    if not log:
        st.info("No bets logged yet. Rate runners in the Analysis tab and log qualifying bets.")
    else:
        df_log = pd.DataFrame(log)
        # Colour coding for results
        st.dataframe(
            df_log[["datetime","horse","race","stake","odds","edge","result","pl"]].rename(columns={
                "datetime":"Date/Time","horse":"Horse","race":"Race",
                "stake":"Stake ($)","odds":"Odds","edge":"Edge %",
                "result":"Result","pl":"P/L ($)"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### Settle Bets")
        pending = [(i,b) for i,b in enumerate(log) if b["result"]=="Pending"]
        if pending:
            for idx, bet in pending:
                c1, c2, c3, c4 = st.columns([3,1,1,1])
                with c1:
                    st.markdown(f"**{bet['horse']}** — ${bet['stake']:.2f} @ {bet['odds']}")
                with c2:
                    st.markdown(f"Edge: `{bet['edge']}%`")
                with c3:
                    if st.button("✅ Won", key=f"won_{idx}"):
                        settle_bet(idx, "Won")
                        st.rerun()
                with c4:
                    if st.button("❌ Lost", key=f"lost_{idx}"):
                        settle_bet(idx, "Lost")
                        st.rerun()
        else:
            st.success("All bets settled.")

# ═══════════════════════════════════════════════════════════════
# TAB 4 — BANKROLL
# ═══════════════════════════════════════════════════════════════
with tab_bankroll:
    st.markdown("## BANKROLL DASHBOARD")

    stats = bankroll_stats()
    if not stats:
        st.info("No settled bets yet.")
    else:
        c1,c2,c3,c4 = st.columns(4)
        def stat_card(col, label, val, prefix="", suffix=""):
            col.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{prefix}{val}{suffix}</div></div>',
                unsafe_allow_html=True
            )
        stat_card(c1, "Current Bank",   f"{stats['current_bank']:.2f}", "$")
        stat_card(c2, "Total P/L",      f"{stats['total_pl']:+.2f}", "$")
        stat_card(c3, "ROI",            f"{stats['roi']:+.1f}", suffix="%")
        stat_card(c4, "Strike Rate",    f"{stats['strike_rate']:.1f}", suffix="%")

        c5,c6,c7,c8 = st.columns(4)
        stat_card(c5, "Total Bets",     stats["bets"])
        stat_card(c6, "Winners",        stats["winners"])
        stat_card(c7, "Avg Odds",       stats["avg_odds"])
        stat_card(c8, "Max Drawdown",   f"{stats['max_drawdown']:.2f}", "$")

        # P/L curve
        st.markdown("---")
        st.markdown("### CUMULATIVE P/L CURVE")
        settled = [b for b in st.session_state.bet_log if b["result"] != "Pending"]
        if settled:
            pl_series = [0] + list(pd.Series([b["pl"] for b in settled]).cumsum())
            df_pl = pd.DataFrame({"Bet #": list(range(len(pl_series))), "Cumulative P/L": pl_series})
            st.line_chart(df_pl.set_index("Bet #"))

        # By odds range
        st.markdown("### PERFORMANCE BY ODDS RANGE")
        if settled:
            def odds_bucket(o):
                if o < 2:   return "<2.0"
                elif o < 4: return "2–4"
                elif o < 7: return "4–7"
                elif o < 12: return "7–12"
                else:       return "12+"
            df_s = pd.DataFrame(settled)
            df_s["OddsRange"] = df_s["odds"].apply(odds_bucket)
            grp = df_s.groupby("OddsRange").agg(
                Bets=("pl","count"),
                PL=("pl","sum"),
                Staked=("stake","sum")
            ).reset_index()
            grp["ROI%"] = (grp["PL"] / grp["Staked"] * 100).round(1)
            st.dataframe(grp, use_container_width=True, hide_index=True)

        # Reset
        st.markdown("---")
        if st.button("🔄 Reset Bank & Log", type="secondary"):
            st.session_state.bet_log = []
            st.session_state.bank = st.session_state.starting_bank
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# TAB 5 — GUIDE
# ═══════════════════════════════════════════════════════════════
with tab_guide:
    st.markdown("## SYSTEM GUIDE")

    st.markdown("""
### HOW THE RATING SYSTEM WORKS

Each runner is scored across **9 factors** totalling 100 points:

| Factor | Max | What it measures |
|---|---|---|
| Form Rating | 20 | Recent finishing positions weighted to last 5 runs |
| Speed Rating | 20 | Normalised speed figure (90–130 scale) |
| Class Rating | 15 | Is the horse dropping/rising in class? |
| Barrier Rating | 10 | Draw position relative to field size |
| Weight Rating | 10 | Carried weight vs field average |
| Jockey Rating | 10 | Jockey strike rate at current track |
| Trainer Rating | 5  | Trainer strike rate |
| Track Rating | 5  | Win rate at this specific track |
| Distance Rating | 5  | Win rate at this specific distance |

---

### SPEEDMAP INTERPRETATION

The speedmap predicts the race tempo by identifying how many horses want to lead:

| Tempo | Meaning | Strategy |
|---|---|---|
| HOT | 3+ leaders — expect a burn-up | Back closers and midfielders |
| GENUINE | 2 leaders — honest pace | Neutral — all running styles viable |
| SOFT | 1 leader, no pressure | Front-runner has a huge advantage |
| MODERATE | Mixed speed — unclear | Look for adaptable runners |

---

### VALUE BETTING

A **value bet** exists when your model's estimated win probability exceeds the market's implied probability:

> Model probability > (1 / decimal odds)

If your model says a horse has a 30% chance of winning but it's priced at $4.00 (25% implied), you have a **+5% edge**. Over hundreds of bets, positive edges compound into profit.

The **expected value (EV)** of a bet:
> EV = (Win Prob × Net Win) − (Loss Prob × Stake)

Only bet when EV is positive.

---

### BANKROLL MANAGEMENT

**Why it matters:** Even a profitable system can go broke with poor staking.

- **Kelly Criterion** is mathematically proven to maximise long-run bankroll growth
- **Fractional Kelly (25%)** is recommended — full Kelly is extremely volatile
- **Never bet more than your max stake %** regardless of how confident you feel
- **Track ROI, not just winners** — a 30% strike rate can be very profitable at long odds

**Sample bankroll milestones:**

| Starting Bank | Conservative (1% flat) | Moderate (2.5% flat) |
|---|---|---|
| $500 | $5/bet | $12.50/bet |
| $1,000 | $10/bet | $25/bet |
| $2,500 | $25/bet | $62.50/bet |
| $5,000 | $50/bet | $125/bet |

---

### API — PUNTINGFORM

Get your API key at [puntingform.com.au](https://www.puntingform.com.au).

Key endpoints used by this app:
- `/v2/form/meetings` — fetches all meetings for a given date
- `/v2/form/runners` — returns runners and form data for a race
- `/v2/form/speedmap` — position predictions
- `/v2/form/horseform` — full past-start history per horse
- `/v2/odds/flucs` — live and early fixed odds

---

### TIPS FOR PROFITABLE USE

1. **Rate every runner** — never skip a horse because it looks unwinnable
2. **Log every qualifying bet** — discipline only works with full records
3. **Don't override the model** — emotional bets erode edge
4. **Review monthly** — if ROI is negative after 200+ bets, adjust weights
5. **Specialize** — consider filtering to 1 track type (e.g., metro Thoroughbred only)
6. **Beware of small samples** — 50 bets is not enough to judge profitability
    """)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#252b38;font-size:0.75rem;font-family:\'IBM Plex Mono\'">'
    'Racing Edge Analyser · For entertainment & research purposes only · '
    'Please gamble responsibly · 1800 858 858</p>',
    unsafe_allow_html=True
)
