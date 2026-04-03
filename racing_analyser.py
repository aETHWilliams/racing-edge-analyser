"""
RACING EDGE ANALYSER PRO
AEROSPACE-GRADE ANALYTICS FOR PROFESSIONAL PUNTING
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List

# -----------------------------------------------------------------------------
# 1. PROFESSIONAL UI CONFIGURATION (WHITE MODERN THEME)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Racing Edge Pro",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Roboto+Mono:wght@400;500&display=swap');

:root {
    --primary: #4f46e5;
    --primary-dim: rgba(79, 70, 229, 0.05);
    --success: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --slate-50: #f8fafc;
    --slate-100: #f1f5f9;
    --slate-200: #e2e8f0;
    --slate-700: #334155;
    --slate-900: #0f172a;
    --border: #e2e8f0;
    --card-bg: #ffffff;
}

/* Global Styles */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--slate-50) !important;
    color: var(--slate-900);
    font-family: 'Inter', sans-serif;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid var(--border) !important;
}

/* Card Component */
.pro-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.runner-row {
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.runner-row:hover {
    border-color: var(--primary);
    background: var(--primary-dim);
}

.bet-indicator {
    border-left: 4px solid var(--primary) !important;
    background: var(--primary-dim) !important;
}

/* Typography */
.label-sm {
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--slate-700);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.mono {
    font-family: 'Roboto Mono', monospace;
}

.text-success { color: var(--success); }
.text-danger { color: var(--danger); }
.text-primary { color: var(--primary); }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent;
    gap: 24px;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    background-color: transparent !important;
    border: none !important;
    color: var(--slate-700) !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom: 2px solid var(--primary) !important;
}

/* Buttons */
.stButton > button {
    background-color: var(--primary) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.5rem !important;
    font-weight: 600 !important;
}

/* Dataframe & Tables */
.market-table {
    width: 100%;
    border-collapse: collapse;
}
.market-table th {
    text-align: left;
    padding: 12px;
    background: var(--slate-100);
    color: var(--slate-700);
    font-size: 0.75rem;
    text-transform: uppercase;
}
.market-table td {
    padding: 12px;
    border-bottom: 1px solid var(--border);
    font-size: 0.85rem;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CORE SYSTEM CONSTANTS & STATE
# -----------------------------------------------------------------------------
if "api_key" not in st.session_state: st.session_state.api_key = ""
if "meetings" not in st.session_state: st.session_state.meetings = []
if "runners" not in st.session_state: st.session_state.runners = []
if "ratings" not in st.session_state: st.session_state.ratings = {}
if "bet_log" not in st.session_state: st.session_state.bet_log = []
if "bank" not in st.session_state: st.session_state.bank = 1000.0

# Strategic Weights: 40% Focus on Sectionals (Closing Speed)
WEIGHT_MAP = {
    "sectional_3f": 40, 
    "speed_rating": 20, 
    "barrier_logic": 15, 
    "class_parity": 15, 
    "jt_efficiency": 10
}
TOTAL_WEIGHT = sum(WEIGHT_MAP.values())

# -----------------------------------------------------------------------------
# 3. ROBUST API ENGINE (FIXES 400 ERRORS)
# -----------------------------------------------------------------------------
BASE_URL = "https://api.puntingform.com.au/v2"

def api_call(endpoint: str, params: dict = {}) -> Optional[dict]:
    if not st.session_state.api_key: return None
    params["apiKey"] = st.session_state.api_key
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=15)
        if response.status_code == 400: return None
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

def safe_id(obj: dict, keys: List[str]) -> str:
    """Ensures IDs are valid non-zero strings to prevent API 400 errors."""
    for k in keys:
        val = obj.get(k)
        if val and str(val) != "0" and str(val).lower() != "none":
            return str(val)
    return ""

def get_meetings(race_date: date) -> List[dict]:
    ds = race_date.strftime("%Y-%m-%d")
    data = api_call("form/meetingslist", {"meetingDate": ds})
    if not data: return []
    
    raw_list = data.get("payLoad", [])
    if not isinstance(raw_list, list): return []
    
    refined = []
    for m in raw_list:
        mid = safe_id(m, ["meetingID", "meetingId", "id"])
        if not mid: continue
        
        detail = api_call("form/meeting", {"meetingId": mid})
        if detail:
            m["races"] = detail.get("payLoad", {}).get("races", [])
            refined.append(m)
    return refined

def get_runners(race_id: str) -> List[dict]:
    if not race_id: return []
    data = api_call("form/fields", {"raceId": race_id})
    if not data: return []
    payload = data.get("payLoad", [])
    # Automatically filter scratchings for a professional view
    return [r for r in payload if str(r.get("isScratched")).lower() != "true"]

def get_form(horse_id: str) -> List[dict]:
    if not horse_id: return []
    data = api_call("form/form", {"horseId": horse_id})
    return data.get("payLoad", []) if data else []

# -----------------------------------------------------------------------------
# 4. ADVANCED RATING ENGINE (SECTIONAL DOMINANCE)
# -----------------------------------------------------------------------------
def calculate_sectional_performance(past_runs: List[dict]) -> float:
    """
    Calculates a score (0-40) based on Closing 600m (Final 3F).
    Analyzes consistency across last 3 starts.
    """
    if not past_runs: return 20.0 # Standard median
    
    scores = []
    for i, run in enumerate(past_runs[:3]):
        # API often provides final3F time or final3FRank
        time_val = float(run.get("final3F") or 0)
        rank_val = float(run.get("final3FRank") or 6)
        
        if 31.0 < time_val < 38.0:
            # Scale: 33s is elite (40pts), 37s is poor (10pts)
            start_pts = 40 - ((time_val - 33.0) * 7.5)
        else:
            # Scale: Rank 1 is elite (40pts), Rank 10 is poor (10pts)
            start_pts = 40 - (rank_val * 3.5)
        
        # Recency weighting (most recent run is 100% value, 2nd is 70%, 3rd is 50%)
        recency = 1.0 if i == 0 else (0.7 if i == 1 else 0.5)
        scores.append(max(0, min(40, start_pts)) * recency)
    
    return sum(scores) / (1.0 + 0.7 + 0.5 if len(scores) == 3 else 1.0)

def generate_runner_rating(runner: dict, form: List[dict]) -> dict:
    # 1. Sectional Component (40 pts)
    sec_score = calculate_sectional_performance(form)
    
    # 2. Speed Component (20 pts)
    raw_sp = float(runner.get("speedRating") or 0)
    sp_score = min(20, (raw_sp / 100) * 20)
    
    # 3. Contextual Components (Class, Barrier, Luck)
    # We use 40 points of 'form baseline' adjusted by barrier
    barr = float(runner.get("barrier") or 10)
    barr_adj = max(0, 15 - (barr * 0.8))
    
    total = sec_score + sp_score + barr_adj + 25 # 25 is base class pad
    return {
        "sectional": round(sec_score, 1),
        "composite": round(total, 1),
        "percentage": round((total / TOTAL_WEIGHT) * 100, 1)
    }

# -----------------------------------------------------------------------------
# 5. MARKET ANALYSIS & PROBABILITY (POWER-LAW MODEL)
# -----------------------------------------------------------------------------
def analyze_market_depth(runners: List[dict]):
    """Calculates true market probabilities by removing bookmaker overround."""
    priced = []
    for r in runners:
        sp = float(r.get("priceSP") or 0)
        if sp > 1.0: priced.append((r, sp))
    
    if not priced: return {}, 100.0
    
    total_raw_prob = sum(1/p for _, p in priced)
    market_frame = {}
    
    for r, sp in priced:
        hid = safe_id(r, ["horseID", "id"])
        true_prob = (1/sp) / total_raw_prob
        market_frame[hid] = {
            "sp": sp,
            "true_pct": true_prob * 100,
            "fair_odds": 1/true_prob
        }
    
    return market_frame, round(total_raw_prob * 100, 1)

def apply_power_ranking(runners, ratings):
    """
    Normalizes win probabilities using a Power Factor.
    This creates separation between top-rated horses and the field.
    Prevents the 'longshot-only' bias of linear models.
    """
    raw_powers = {}
    for r in runners:
        hid = safe_id(r, ["horseID", "id"])
        rat = ratings.get(hid, {"percentage": 50})
        # Power of 2.8 effectively rewards horses in the 80%+ rating bracket
        raw_powers[hid] = np.power(rat["percentage"] / 100, 2.8)
    
    total_power = sum(raw_powers.values())
    if total_power == 0: return {safe_id(r, ["id"]): 1/len(runners) for r in runners}
    return {k: v/total_power for k, v in raw_powers.items()}

# -----------------------------------------------------------------------------
# 6. APP LAYOUT - SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<p style="font-size: 1.25rem; font-weight: 800; color: #4f46e5; margin-bottom: 0;">RACING EDGE</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 0.7rem; font-weight: 500; color: #64748b; margin-bottom: 24px;">INSTITUTIONAL GRADE ANALYTICS</p>', unsafe_allow_html=True)
    
    st.session_state.api_key = st.text_input("API Access Key", value=st.session_state.api_key, type="password")
    selected_date = st.date_input("Analysis Date", date.today())
    
    if st.button("Initialize Data Sync", use_container_width=True):
        with st.spinner("Connecting to PuntingForm V2..."):
            st.session_state.meetings = get_meetings(selected_date)
    
    st.divider()
    st.markdown('<p class="label-sm">Risk Management</p>', unsafe_allow_html=True)
    st.session_state.bank = st.number_input("Operating Bank ($)", value=st.session_state.bank)
    kelly_frac = st.slider("Kelly Fraction", 0.05, 0.50, 0.20)
    min_edge = st.slider("Min Edge Threshold (%)", 1.0, 10.0, 3.0)

# -----------------------------------------------------------------------------
# 7. MAIN INTERFACE - TABS
# -----------------------------------------------------------------------------
tab_meetings, tab_analysis, tab_staking, tab_performance = st.tabs([
    "Meetings", "Market Analysis", "Staking Engine", "Bankroll Tracker"
])

# -- TAB: MEETINGS --
with tab_meetings:
    if not st.session_state.meetings:
        st.info("System Ready. Please initialize data sync from the sidebar.")
    else:
        for meeting in st.session_state.meetings:
            m_name = meeting.get('meetingName', 'Unknown')
            state = meeting.get('state', 'Unknown')
            with st.expander(f"{m_name} ({state})"):
                for race in meeting.get("races", []):
                    rid = safe_id(race, ["raceID", "id"])
                    col_r, col_a = st.columns([5, 1])
                    col_r.markdown(f"**Race {race.get('raceNumber')}** — {race.get('raceName')} ({race.get('distance')}m)")
                    if col_a.button("Analyze", key=f"btn_{rid}"):
                        with st.spinner("Loading Race Data..."):
                            st.session_state.runners = get_runners(rid)
                            st.session_state.selected_race = race
                            st.session_state.ratings = {}
                            st.rerun()

# -- TAB: ANALYSIS --
with tab_analysis:
    if not st.session_state.runners:
        st.info("No race selected. Please go to the Meetings tab.")
    else:
        race = st.session_state.selected_race
        st.markdown(f"### {race.get('raceName')} | {race.get('distance')}m")
        
        if st.button("Execute Quantitative Rating Model", use_container_width=True):
            progress_bar = st.progress(0)
            for i, r in enumerate(st.session_state.runners):
                hid = safe_id(r, ["horseID", "id"])
                if hid:
                    form_data = get_form(hid)
                    st.session_state.ratings[hid] = generate_runner_rating(r, form_data)
                progress_bar.progress((i + 1) / len(st.session_state.runners))
            st.success("Model Execution Successful.")

        if st.session_state.ratings:
            mkt_data, overround = analyze_market_depth(st.session_state.runners)
            model_win_probs = apply_power_ranking(st.session_state.runners, st.session_state.ratings)
            
            # Sort runners by Model Probability (Institutional sorting)
            sorted_hids = sorted(model_win_probs.keys(), key=lambda x: model_win_probs[x], reverse=True)
            
            st.markdown(f"""
                <div style="display: flex; gap: 16px; margin-bottom: 20px;">
                    <div class="pro-card" style="padding: 10px 20px; margin: 0;">
                        <span class="label-sm">Market Overround</span><br>
                        <span class="mono" style="font-weight: 600;">{overround}%</span>
                    </div>
                    <div class="pro-card" style="padding: 10px 20px; margin: 0;">
                        <span class="label-sm">Model Focus</span><br>
                        <span class="mono" style="font-weight: 600; color: #4f46e5;">Sectional Velocity</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            for hid in sorted_hids:
                runner_obj = next(r for r in st.session_state.runners if safe_id(r, ["horseID", "id"]) == hid)
                rat = st.session_state.ratings.get(hid, {"percentage": 0, "sectional": 0})
                m_win_pct = model_win_probs[hid] * 100
                mkt = mkt_data.get(hid, {"sp": 0, "true_pct": 0, "fair_odds": 0})
                
                edge = m_win_pct - mkt["true_pct"]
                # Qualifying Bet Logic
                is_bet = edge >= min_edge and mkt["sp"] >= 1.50
                
                row_style = "bet-indicator" if is_bet else ""
                
                st.markdown(f"""
                <div class="runner-row {row_style}">
                    <div style="flex: 2;">
                        <span style="font-weight: 700; font-size: 0.95rem;">{runner_obj.get('horseName')}</span>
                        <span style="color: #64748b; font-size: 0.75rem; margin-left: 8px;">Barrier {runner_obj.get('barrier')}</span>
                        <br>
                        <span class="label-sm" style="font-size: 0.6rem; color: #4f46e5;">Sectional Score: {rat['sectional']}</span>
                    </div>
                    <div style="flex: 1; text-align: center;">
                        <span class="label-sm">Win Prob</span><br>
                        <span class="mono" style="font-weight: 600;">{m_win_pct:.1f}%</span>
                    </div>
                    <div style="flex: 1; text-align: center;">
                        <span class="label-sm">True Mkt</span><br>
                        <span class="mono" style="font-weight: 500;">{mkt['true_pct']:.1f}%</span>
                    </div>
                    <div style="flex: 1; text-align: center;">
                        <span class="label-sm">Edge</span><br>
                        <span class="mono" style="font-weight: 600; color: {'#10b981' if edge > 0 else '#64748b'};">{edge:+.1f}%</span>
                    </div>
                    <div style="flex: 1; text-align: right;">
                        <span class="label-sm" style="color: #4f46e5;">Price</span><br>
                        <span class="mono" style="font-weight: 700; font-size: 1.1rem;">${mkt['sp']:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if is_bet:
                    # Kelly Staking Calculation
                    b_odds = mkt["sp"] - 1
                    p_win = model_win_probs[hid]
                    kelly_stake_pct = (b_odds * p_win - (1 - p_win)) / b_odds
                    actual_stake = round(st.session_state.bank * kelly_stake_pct * kelly_frac, 2)
                    
                    c1, c2 = st.columns([1, 4])
                    if c1.button(f"Log ${max(0, actual_stake):.0f}", key=f"log_{hid}"):
                        st.session_state.bet_log.append({
                            "time": datetime.now().strftime("%H:%M"),
                            "horse": runner_obj.get('horseName'),
                            "race": f"R{race.get('raceNumber')}",
                            "stake": actual_stake,
                            "odds": mkt["sp"],
                            "status": "Open",
                            "pl": 0.0
                        })
                        st.toast(f"Position opened on {runner_obj.get('horseName')}")

# -- TAB: STAKING --
with tab_staking:
    st.markdown("### Active Positions")
    open_bets = [b for b in st.session_state.bet_log if b["status"] == "Open"]
    
    if not open_bets:
        st.info("No active positions found in the market.")
    else:
        for i, bet in enumerate(open_bets):
            col_b, col_w, col_l = st.columns([4, 1, 1])
            col_b.markdown(f"**{bet['horse']}** | ${bet['stake']} at ${bet['odds']}")
            if col_w.button("Settle Win", key=f"win_{i}"):
                bet["status"] = "Settled"
                bet["pl"] = round(bet["stake"] * (bet["odds"] - 1), 2)
                st.rerun()
            if col_l.button("Settle Loss", key=f"loss_{i}"):
                bet["status"] = "Settled"
                bet["pl"] = -bet["stake"]
                st.rerun()

# -- TAB: PERFORMANCE --
with tab_performance:
    st.markdown("### Portfolio Performance")
    settled_bets = [b for b in st.session_state.bet_log if b["status"] == "Settled"]
    
    if not settled_bets:
        st.info("Portfolio performance will populate once positions are settled.")
    else:
        df = pd.DataFrame(settled_bets)
        net_profit = df["pl"].sum()
        total_staked = df["stake"].sum()
        roi = (net_profit / total_staked) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Net Profit", f"${net_profit:.2f}", delta=f"{roi:.1f}% ROI")
        c2.metric("Total Turnover", f"${total_staked:.2f}")
        c3.metric("Strike Rate", f"{(len(df[df['pl'] > 0]) / len(df) * 100):.1f}%")
        
        st.divider()
        st.markdown("### Cumulative P/L Curve")
        df["cumulative"] = df["pl"].cumsum()
        st.line_chart(df["cumulative"])
        
        st.dataframe(df[["time", "horse", "race", "stake", "odds", "pl"]], use_container_width=True)

# -----------------------------------------------------------------------------
# 8. FOOTER
# -----------------------------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="border-top: 1px solid #e2e8f0; padding-top: 20px; text-align: center; color: #64748b; font-size: 0.75rem;">
        PROFESSIONAL ANALYTICS ENGINE · DATA SOURCE: PUNTINGFORM V2 · RESEARCH USE ONLY
    </div>
""", unsafe_allow_html=True)
