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
    page_icon="🐎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS – MODERN WHITE THEME
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-primary:      #ffffff;
    --bg-secondary:    #f8f9fc;
    --bg-tertiary:     #f1f3f8;
    --surface:         #ffffff;
    --surface2:        #f8f9fc;
    --border-light:    #e9ecef;
    --border-medium:   #dee2e6;
    --text-primary:    #1e293b;
    --text-secondary:  #475569;
    --text-tertiary:   #64748b;
    --accent:          #3b82f6;
    --accent-light:    #dbeafe;
    --accent-hover:    #2563eb;
    --green:           #10b981;
    --green-light:     #d1fae5;
    --red:             #ef4444;
    --red-light:       #fee2e2;
    --amber:           #f59e0b;
    --amber-light:     #fef3c7;
    --purple:          #8b5cf6;
    --radius-sm:       6px;
    --radius-md:       10px;
    --radius-lg:       16px;
    --shadow-sm:       0 1px 2px rgba(0,0,0,0.03), 0 1px 2px rgba(0,0,0,0.05);
    --shadow-md:       0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-primary) !important;
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-light) !important;
}

.card    { background: var(--surface);  border: 1px solid var(--border-light);  border-radius: var(--radius-md); padding: 20px; box-shadow: var(--shadow-sm); }
.card-sm { background: var(--surface2); border: 1px solid var(--border-light);  border-radius: var(--radius-sm); padding: 14px 16px; }

.stat { background: var(--bg-secondary); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 16px 18px; }
.stat-label { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--text-tertiary); letter-spacing: 0.05em; text-transform: uppercase; }
.stat-value { font-family: 'JetBrains Mono', monospace; font-size: 1.75rem; font-weight: 600; color: var(--text-primary); }
.stat-value.accent { color: var(--accent); }
.stat-value.green  { color: var(--green); }
.stat-value.red    { color: var(--red); }

.pill-green  { background: var(--green-light); color: var(--green); border: none; }
.pill-red    { background: var(--red-light);   color: var(--red);   border: none; }
.pill-amber  { background: var(--amber-light); color: var(--amber); border: none; }
.pill-blue   { background: var(--accent-light);color: var(--accent); border: none; }
.pill-muted  { background: var(--bg-tertiary); color: var(--text-tertiary); border: 1px solid var(--border-light); }

.alert-green { background: var(--green-light); border-left: 3px solid var(--green); color: var(--green); }
.alert-red   { background: var(--red-light);   border-left: 3px solid var(--red);   color: var(--red); }
.alert-amber { background: var(--amber-light); border-left: 3px solid var(--amber); color: var(--amber); }
.alert-blue  { background: var(--accent-light);border-left: 3px solid var(--accent); color: var(--accent); }

.bar-wrap { background: var(--border-medium); border-radius: 2px; }
.bar-fill { background: var(--accent); }

.sm-row { background: var(--bg-secondary); border: 1px solid var(--border-light); }
.comp-row { border-bottom: 1px solid var(--border-light); }

.stButton > button {
    background: var(--accent) !important; color: white !important;
    border: none !important; border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
}
.stButton > button:hover { background: var(--accent-hover) !important; }

.stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid var(--border-light) !important; }
.stTabs [aria-selected="true"] { color: var(--accent) !important; border-bottom: 2px solid var(--accent) !important; }

.title-main { font-family: 'JetBrains Mono', monospace; font-size: 1.25rem; font-weight: 600; color: var(--text-primary); }
.title-sub  { font-family: 'Inter', sans-serif; font-size: 0.75rem; color: var(--text-tertiary); }

hr { border-top: 1px solid var(--border-light); }
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

def fetch_meetings(target_date: date) -> list:
    ds = target_date.strftime("%Y-%m-%d")
    data = pf_get("form/meetingslist", {"meetingDate": ds})
    if not data:
        return []
    payload = data.get("payLoad", data) if isinstance(data, dict) else data
    meetings = payload if isinstance(payload, list) else []
    for meeting in meetings:
        mid = str(meeting.get("meetingId", ""))
        if not mid:
            continue
        rdata = pf_get("form/meeting", {"meetingId": mid})
        if rdata:
            rpayload = rdata.get("payLoad", rdata) if isinstance(rdata, dict) else rdata
            if isinstance(rpayload, dict):
                meeting["races"] = rpayload.get("races") or []
                meeting["_raw_meeting"] = rpayload
            elif isinstance(rpayload, list):
                meeting["races"] = rpayload
            else:
                meeting["races"] = []
        else:
            meeting["races"] = []
    return meetings

def fetch_race_runners(race_id: str) -> list:
    data = pf_get("form/fields", {"raceId": race_id})
    if not data:
        return []
    payload = data.get("payLoad", data) if isinstance(data, dict) else data
    return payload if isinstance(payload, list) else []

def fetch_runner_form(horse_id: str) -> list:
    data = pf_get("form/form", {"horseId": horse_id})
    if not data:
        return []
    payload = data.get("payLoad", data) if isinstance(data, dict) else data
    return payload if isinstance(payload, list) else []


# ─────────────────────────────────────────────────────────────
# ENHANCED RATING ENGINE (ADVANCED FACTORS)
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
# PREDICTED PRICE (FAIR ODDS) & VALUE DETECTION
# ─────────────────────────────────────────────────────────────
def calculate_true_probability(runner: dict, rating: dict) -> float:
    rating_pct = rating.get("pct", 50) / 100.0 if rating else 0.5
    career_win = safe_float(runner.get("winPct", 0)) / 100.0
    track_rec = runner.get("trackRecord") or {}
    track_win = (safe_float(track_rec.get("firsts",0)) / max(safe_float(track_rec.get("starts",0)),1)) if track_rec.get("starts",0) > 0 else career_win
    dist_rec = runner.get("distanceRecord") or {}
    dist_win = (safe_float(dist_rec.get("firsts",0)) / max(safe_float(dist_rec.get("starts",0)),1)) if dist_rec.get("starts",0) > 0 else career_win
    last_start = runner.get("lastStart") or {}
    last_pos = safe_float(last_start.get("finishingPosition", 10))
    last_factor = max(0, 1 - (last_pos-1)/20) if last_pos > 0 else 0.5
    tj_combo = runner.get("trainerJockeyA2E_Career") or {}
    tj_factor = safe_float(tj_combo.get("strikeRate", 0)) / 100.0
    true_prob = (rating_pct * 0.50 + career_win * 0.15 + track_win * 0.10 +
                 dist_win * 0.10 + last_factor * 0.05 + tj_factor * 0.10)
    return min(max(true_prob, 0.01), 0.95)

def detect_value_bet(runner: dict, rating: dict, actual_odds: float) -> dict:
    true_prob = calculate_true_probability(runner, rating)
    fair_odds = 1 / true_prob if true_prob > 0 else 0
    if actual_odds <= 0 or fair_odds <= 0:
        return {"is_value": False, "edge_pct": 0, "fair_odds": 0}
    edge_pct = (true_prob * actual_odds - 1) * 100
    is_value = edge_pct >= 10
    return {
        "is_value": is_value,
        "edge_pct": round(edge_pct, 1),
        "fair_odds": round(fair_odds, 2),
        "true_prob_pct": round(true_prob * 100, 1),
        "market_prob_pct": round((1 / actual_odds) * 100, 1) if actual_odds > 0 else 0,
    }


# ─────────────────────────────────────────────────────────────
# MARKET FRAMING & MODEL PROBABILITY (required for analysis)
# ─────────────────────────────────────────────────────────────
OVERROUND_TARGET = 1.10

def record_win_rate(rec):
    if not rec: return None
    s = safe_float(rec.get("starts", 0))
    f = safe_float(rec.get("firsts", 0))
    return f / s if s >= 3 else None

def frame_market(runners):
    priced = [(r, safe_float(r.get("priceSP", 0))) for r in runners if safe_float(r.get("priceSP", 0)) > 1.0]
    if not priced:
        return {}
    raw_sum = sum(1 / p for _, p in priced)
    result = {}
    for r, sp in priced:
        rid = str(r.get("runnerId") or r.get("id", ""))
        raw_implied  = 1 / sp
        true_implied = raw_implied / raw_sum
        framed       = true_implied * OVERROUND_TARGET
        result[rid] = {
            "sp":             sp,
            "implied_raw":    round(raw_implied * 100, 1),
            "true_implied":   round(true_implied * 100, 1),
            "framed_implied": round(framed * 100, 1),
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
        rid = str(r.get("runnerId") or r.get("id", ""))
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
            track = meeting.get("track") or {}
            name  = track.get("name") or meeting.get("meetingName") or meeting.get("venueName","Unknown")
            state = track.get("state") or meeting.get("state","")
            races = meeting.get("races") or []

            if state_filter:
                normalized_state = state.upper()
                if not any(f in normalized_state for f in state_filter):
                    continue

            with st.expander(f"{name}  —  {state}  —  {len(races)} races"):
                for race in races:
                    race["_meetingName"] = name
                    race["_meetingState"] = state
                    r_num  = race.get("number") or race.get("raceNumber","?")
                    r_name = race.get("name") or race.get("raceName",f"Race {r_num}")
                    r_dist = race.get("distance") or race.get("raceDistance","?")
                    r_time = race.get("startTime") or race.get("raceTime","")
                    r_cls  = race.get("raceClass","")
                    r_id   = str(race.get("raceId") or race.get("id",""))

                    c1,c2,c3 = st.columns([4,1,1])
                    with c1:
                        st.markdown(
                            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.8rem">R{r_num} &nbsp; {r_name}</span>'
                            f'&nbsp;<span class="pill pill-muted">{r_dist}m</span>'
                            f'&nbsp;<span class="pill pill-muted">{r_cls}</span>'
                            f'&nbsp;<span style="font-family:\'Inter\',monospace;font-size:0.7rem;color:#64748b">{r_time}</span>',
                            unsafe_allow_html=True
                        )
                    with c3:
                        if st.button("Analyse", key=f"sel_{r_id}"):
                            st.session_state.selected_race = race
                            st.session_state.runners = []
                            st.session_state.ratings = {}
                            with st.spinner("Loading runners..."):
                                runners = st.session_state.selected_race.get("runners", [])
                                if not runners:
                                    runners = fetch_race_runners(r_id)
                                st.session_state.runners = assign_pace(runners)
                            st.success(f"{len(st.session_state.runners)} runners loaded — go to Analysis tab")


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
        r_trk  = race.get("_meetingName") or race.get("meetingName","")
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
            f'&nbsp;<span style="font-size:0.8rem;color:#64748b">{tempo["description"]}</span>'
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

        # Rate runners + build market frame
        st.markdown("## Runner Analysis")
        if st.button("Rate All Runners"):
            ratings = {}; prog = st.progress(0)
            for i, runner in enumerate(runners):
                hid = str(runner.get("runnerId") or runner.get("horseId") or runner.get("id",""))
                past_runs = fetch_runner_form(hid)  # fetch past runs for advanced factors
                ratings[hid] = rate_runner(runner, past_runs)
                prog.progress((i+1)/len(runners))
            st.session_state.ratings = ratings; prog.empty()
            st.success("All runners rated")

        ratings     = st.session_state.ratings
        mkt_frame   = frame_market(runners)
        field_probs = normalise_field_probs(runners, ratings) if ratings else {}

        def sort_key(r):
            rid = str(r.get("runnerId") or r.get("id",""))
            return field_probs.get(rid, 0) if field_probs else -safe_float(r.get("priceSP",99))
        sorted_runners = sorted(runners, key=sort_key, reverse=True)

        # Market overview table
        if mkt_frame:
            st.markdown("## Market Frame (110%)")
            mkt_rows = []
            for r in sorted(runners, key=lambda x: safe_float(x.get("priceSP",99))):
                rid  = str(r.get("runnerId") or r.get("id",""))
                mf   = mkt_frame.get(rid)
                if not mf: continue
                mp   = field_probs.get(rid, 0)
                diff = round(mp*100 - mf["true_implied"], 1)
                mkt_rows.append({
                    "Horse":       r.get("name","?"),
                    "SP":          f"${mf['sp']}",
                    "Market %":    f"{mf['true_implied']}%",
                    "Model %":     f"{round(mp*100,1)}%" if mp else "-",
                    "Edge":        (f"+{diff}%" if diff > 0 else f"{diff}%") if mp else "-",
                })
            if mkt_rows:
                st.dataframe(pd.DataFrame(mkt_rows), use_container_width=True, hide_index=True)
            st.markdown('<hr>', unsafe_allow_html=True)

        for rank, runner in enumerate(sorted_runners, 1):
            hid      = str(runner.get("runnerId") or runner.get("horseId") or runner.get("id",""))
            name     = runner.get("name") or runner.get("runnerName") or runner.get("horseName","Unknown")
            barrier  = runner.get("barrier") or runner.get("barrierNumber","?")
            jockey   = (runner.get("jockey") or {}).get("fullName","—") or runner.get("jockeyName","—")
            trainer  = (runner.get("trainer") or {}).get("fullName","—") or runner.get("trainerName","—")
            weight   = runner.get("weightTotal") or runner.get("weightCarried") or runner.get("handicapWeight","—")
            price    = safe_float(runner.get("priceSP") or runner.get("fixedOddsWin") or runner.get("price",0))
            pace_lbl = PACE_LABELS.get(int(runner.get("pacePosition",3)),"—")
            rating   = ratings.get(hid)
            mf       = mkt_frame.get(hid, {})
            mp       = field_probs.get(hid, 0)
            tjA2E    = runner.get("trainerJockeyA2E_Career") or {}
            tj_a2e   = safe_float(tjA2E.get("a2E", 0))

            verdict = None
            if rating and mf and mp:
                verdict = value_assessment(
                    model_prob=mp,
                    true_implied_pct=mf["true_implied"],
                    sp=price,
                    tj_a2e=tj_a2e,
                    rating_pct=rating["pct"],
                    min_rating=st.session_state.min_rating,
                )

            bet_flag = "  ✦ BET" if (verdict and verdict["bet"]) else ""
            label = f"#{rank}  {name}   B{barrier}   {'$'+str(price) if price else 'N/A'}"
            if mp: label += f"   Model {round(mp*100,1)}%"
            if mf: label += f"   Mkt {mf.get('true_implied','?')}%"
            label += bet_flag

            with st.expander(label, expanded=(rank<=3 or bool(verdict and verdict["bet"]))):
                left, right = st.columns([3,2])
                with left:
                    st.markdown(
                        f'<span class="pill pill-muted">B{barrier}</span>'
                        f'<span class="pill pill-blue">{pace_lbl}</span>'
                        f'<span class="pill pill-muted">{weight}kg</span>',
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f'<div style="margin-top:10px;font-size:0.78rem;color:#64748b">'
                        f'Jockey &nbsp;<span style="color:#1e293b">{jockey}</span>'
                        f'&nbsp;&nbsp; Trainer &nbsp;<span style="color:#1e293b">{trainer}</span></div>',
                        unsafe_allow_html=True
                    )
                    career_win = safe_float(runner.get("winPct",0))
                    career_plc = safe_float(runner.get("placePct",0))
                    track_rec  = runner.get("trackRecord") or {}
                    dist_rec   = runner.get("distanceRecord") or {}
                    t_s = safe_float(track_rec.get("starts",0)); t_w = safe_float(track_rec.get("firsts",0))
                    d_s = safe_float(dist_rec.get("starts",0));  d_w = safe_float(dist_rec.get("firsts",0))
                    st.markdown(
                        f'<div style="margin-top:12px;display:grid;grid-template-columns:1fr 1fr;gap:6px">'
                        f'<div class="card-sm"><div class="stat-label">Career Win%</div>'
                        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:1rem;color:#1e293b">{career_win:.1f}%</div></div>'
                        f'<div class="card-sm"><div class="stat-label">Career Place%</div>'
                        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:1rem;color:#1e293b">{career_plc:.1f}%</div></div>'
                        f'<div class="card-sm"><div class="stat-label">Track Record</div>'
                        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:1rem;color:#1e293b">{int(t_w)}/{int(t_s)}</div></div>'
                        f'<div class="card-sm"><div class="stat-label">Dist Record</div>'
                        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:1rem;color:#1e293b">{int(d_w)}/{int(d_s)}</div></div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    if rating:
                        st.markdown(
                            f'<div style="margin-top:14px">'
                            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.62rem;color:#64748b;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:4px">Form Rating</div>'
                            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:1.4rem;color:#3b82f6">{rating["composite"]}'
                            f'<span style="font-size:0.75rem;color:#64748b"> / {MAX_SCORE} &nbsp; ({rating["pct"]}%)</span></div>'
                            f'<div class="bar-wrap"><div class="bar-fill" style="width:{int(rating["pct"])}%"></div></div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
                        for key, max_val in WEIGHTS.items():
                            val = rating.get(key,0); pct = int(val/max_val*100)
                            st.markdown(
                                f'<div class="comp-row"><span class="comp-name">{LABELS[key]}</span>'
                                f'<div style="flex:1;margin:0 12px;background:var(--border-medium);border-radius:2px;height:2px">'
                                f'<div style="width:{pct}%;height:2px;background:var(--accent);border-radius:2px"></div></div>'
                                f'<span class="comp-score">{val} / {max_val}</span></div>',
                                unsafe_allow_html=True
                            )

                with right:
                    if verdict and price > 1:
                        # ---- Value bet detection card ----
                        value_info = detect_value_bet(runner, rating, price)
                        if value_info["is_value"]:
                            st.markdown(f"""
                            <div style="background: var(--green-light); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 1rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                                    <div>
                                        <span class="pill pill-green">💰 VALUE BET</span>
                                        <span style="margin-left: 0.5rem; font-weight: 600;">+{value_info['edge_pct']}% edge</span>
                                    </div>
                                    <div style="font-family: 'JetBrains Mono', monospace;">
                                        Predicted: <strong>${value_info['fair_odds']}</strong> &nbsp;|&nbsp;
                                        Actual: <strong>${price:.2f}</strong>
                                    </div>
                                </div>
                                <div style="margin-top: 0.5rem; font-size: 0.8rem;">
                                    Model {value_info['true_prob_pct']}% vs Market {value_info['market_prob_pct']}%
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="background: var(--bg-tertiary); border-radius: var(--radius-md); padding: 0.75rem; margin-bottom: 1rem; text-align: center;">
                                <span style="color: var(--text-tertiary);">Predicted ${value_info['fair_odds']} &nbsp;→&nbsp; Actual ${price:.2f}</span>
                                <span style="margin-left: 0.5rem;" class="pill pill-muted">{value_info['edge_pct']:+.1f}% edge</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        g1 = "pill-green" if verdict["has_edge"]  else "pill-red"
                        g2 = "pill-green" if verdict["rating_ok"] else "pill-red"
                        g3 = "pill-green" if verdict["tj_ok"]     else "pill-red"
                        tj_sr = safe_float(tjA2E.get("strikeRate",0))
                        st.markdown(
                            f'<div class="card-sm" style="margin-bottom:10px">'
                            f'<div class="stat-label" style="margin-bottom:8px">Probability</div>'
                            f'<div style="font-size:0.72rem;font-family:\'JetBrains Mono\',monospace;line-height:2.0">'
                            f'SP &nbsp;<span style="color:#1e293b">${price}</span>'
                            f'&nbsp;&nbsp; Market &nbsp;<span style="color:#1e293b">{mf.get("true_implied","?")}%</span><br>'
                            f'Model &nbsp;<span style="color:#3b82f6;font-size:0.95rem">{verdict["model_prob_pct"]}%</span>'
                            f'&nbsp;&nbsp; Edge &nbsp;<span style="color:{"var(--green)" if verdict["has_edge"] else "var(--red)"}">{"+" if verdict["edge_pct"]>=0 else ""}{verdict["edge_pct"]}%</span>'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f'<div class="card-sm" style="margin-bottom:10px">'
                            f'<div class="stat-label" style="margin-bottom:8px">Bet Gates</div>'
                            f'<div style="font-size:0.72rem;font-family:\'JetBrains Mono\',monospace;line-height:2.1">'
                            f'<span class="pill {g1}">{"PASS" if verdict["has_edge"] else "FAIL"}</span> Positive edge<br>'
                            f'<span class="pill {g2}">{"PASS" if verdict["rating_ok"] else "FAIL"}</span> Rating {rating["pct"] if rating else "?"}% (min {st.session_state.min_rating}%)<br>'
                            f'<span class="pill {g3}">{"PASS" if verdict["tj_ok"] else "FAIL"}</span> T+J A2E {round(tj_a2e,2)} &nbsp; SR {tj_sr:.1f}%'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )
                        if verdict["bet"]:
                            rec = recommended_stake(
                                bank=st.session_state.bank, model_prob=mp, odds=price,
                                method=st.session_state.staking_method, kelly_frac=st.session_state.kelly_fraction,
                                flat_pct=st.session_state.flat_stake_pct, fixed=st.session_state.level_stake,
                                max_pct=st.session_state.max_stake_pct,
                            )
                            st.markdown(
                                f'<div class="card-sm" style="border-color:var(--green);margin-bottom:10px">'
                                f'<div class="stat-label">Stake</div>'
                                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:1.5rem;color:#3b82f6">${rec["stake"]:.2f}</div>'
                                f'<div style="font-size:0.7rem;color:#64748b;margin-top:4px">EV ${rec["ev"]:.2f}</div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                            st.markdown('<div class="alert alert-green">BET — all three gates pass</div>', unsafe_allow_html=True)
                            if st.button(f"Log Bet — {name}", key=f"log_{hid}"):
                                log_bet(name, f"{r_trk} {r_name}", rec["stake"], price, verdict["edge_pct"])
                                st.success("Bet logged")
                        else:
                            st.markdown(
                                f'<div class="alert alert-red">No bet — {" · ".join(verdict["reasons"])}</div>',
                                unsafe_allow_html=True
                            )
                    elif price <= 1:
                        st.markdown('<div class="alert alert-amber">No SP price available</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="alert alert-blue">Click Rate All Runners to analyse</div>', unsafe_allow_html=True)

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
        (c1,"Kelly Criterion","Mathematically optimal. Stakes proportional to your edge.<br><br><span style=\"font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#475569\">f = (bp - q) / b</span><br><br>Quarter Kelly (0.25) is strongly recommended — reduces variance without sacrificing long-run growth."),
        (c2,"Flat Percentage","Fixed % of current bank on every qualifying bet. Automatically scales down during losing runs.<br><br>Simple and effective but does not account for edge size."),
        (c3,"Level Stakes","Fixed dollar amount per bet regardless of bank or edge.<br><br>Easiest for tracking ROI. Does not protect bank during drawdowns."),
    ]:
        col.markdown(f'<div class="card"><div class="stat-label" style="margin-bottom:8px">{title}</div><div style="font-size:0.8rem;color:#64748b;line-height:1.7">{body}</div></div>', unsafe_allow_html=True)

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
        st.markdown(f'<div class="card-sm" style="font-size:0.82rem"><span style="color:var(--accent);font-family:\'JetBrains Mono\',monospace;margin-right:10px">—</span>{rule}</div>', unsafe_allow_html=True)

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
                        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.8rem">{bet["horse"]}</span>'
                        f'&nbsp;<span style="color:#64748b;font-size:0.75rem">${bet["stake"]:.2f} @ {bet["odds"]}</span>',
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
        st.line_chart(pd.DataFrame({"Bet":range(len(pl_series)),"P/L":pl_series}).set_index("Bet"), color="#3b82f6")

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
            "Final 3F sectional / closing speed – identifies strong finishers",
            "Contextual speed adjusted for class, going, and pace",
            "Trouble in running (blocked, wide, bumped, interfered) – penalty relief",
            "Performance relative to race tempo (upgrades closers in hot paces)",
            "Rewards horses dropping in class, penalises sharp rises",
            "Carried weight with distance multiplier (weight matters more at 1600m+)",
            "Draw position with track‑specific bias (Caulfield inside advantage)",
            "Jockey‑trainer combination strike rate and A2E",
            "Win record at this specific venue",
            "Win record at this specific distance (±100m)",
        ]
    }), use_container_width=True, hide_index=True)

    st.markdown("## Speedmap")
    st.markdown("""
<div class="card">
<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px">
  <div><div class="pill pill-red" style="margin-bottom:8px">HOT</div><div style="font-size:0.78rem;color:#64748b">3+ leaders — burn-up early. Back closers and midfielders.</div></div>
  <div><div class="pill pill-amber" style="margin-bottom:8px">GENUINE</div><div style="font-size:0.78rem;color:#64748b">2 leaders fighting — honest pace. All styles viable.</div></div>
  <div><div class="pill pill-green" style="margin-bottom:8px">SOFT</div><div style="font-size:0.78rem;color:#64748b">Single uncontested leader. Front-runner has a big advantage.</div></div>
  <div><div class="pill pill-blue" style="margin-bottom:8px">MODERATE</div><div style="font-size:0.78rem;color:#64748b">Unclear dynamics. Look for adaptable runners.</div></div>
</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("## Value Betting")
    st.markdown("""
<div class="card" style="font-size:0.82rem;color:#64748b;line-height:1.8">
A value bet exists when your model's estimated probability exceeds the market's implied probability.<br><br>
<span style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#1e293b">Value = Model Prob &gt; (1 / Decimal Odds)</span><br><br>
If the model says 30% and the market prices the horse at $4.00 (25% implied), you hold a +5% edge.
Over hundreds of bets, positive edges compound into profit regardless of individual results.<br><br>
<span style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#1e293b">EV = (Win% x Net Win) — (Loss% x Stake)</span><br>
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
        st.markdown(f'<div class="card-sm" style="font-size:0.82rem"><span style="color:var(--accent);font-family:\'JetBrains Mono\',monospace;margin-right:10px">—</span>{tip}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown(
    '<div style="text-align:center;padding:32px 0 16px;font-family:\'JetBrains Mono\',monospace;'
    'font-size:0.6rem;color:#cbd5e1;letter-spacing:0.1em">'
    'Racing Edge &nbsp;|&nbsp; Research purposes only &nbsp;|&nbsp; Gamble Responsibly &nbsp;|&nbsp; 1800 858 858'
    '</div>',
    unsafe_allow_html=True
)
