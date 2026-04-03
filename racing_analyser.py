"""
Racing Edge Analyser  —  Powered by PuntingForm API v2

Install:  pip install streamlit requests pandas numpy
Run:      streamlit run racing_analyser.py

KEY API FIXES:
  - form/meetings (plural) returns meetings with races nested when called with meetingDate.
  - form/form takes raceId (NOT horseId) — one call fetches all runners' history
  - form/fields takes raceId OR meetingDate+track+raceNumber
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Optional

st.set_page_config(page_title="Racing Edge", page_icon="RE", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');
:root {
  --bg:#f4f6fa; --surface:#fff; --surface2:#f0f3f8; --border:#dde2ec; --border2:#c5ccda;
  --blue:#1a56db; --blue2:#1e429f; --blue-l:#ebf0fe; --blue-m:#c3d1fa;
  --text:#0f172a; --text2:#374151; --text3:#6b7280; --text4:#9ca3af;
  --green:#059669; --green-l:#d1fae5; --red:#dc2626; --red-l:#fee2e2;
  --amber:#d97706; --amber-l:#fef3c7;
  --r:6px; --r2:10px; --sh:0 1px 3px rgba(0,0,0,.06),0 1px 2px rgba(0,0,0,.04);
}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text);font-family:'IBM Plex Sans',sans-serif;font-size:14px}
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important}
[data-testid="stSidebar"] *{color:var(--text)!important}
[data-testid="stSidebar"] input,[data-testid="stSidebar"] select{background:var(--surface2)!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:var(--r)!important}
[data-testid="stSidebar"] [data-baseweb="select"]>div{background:var(--surface2)!important;border:1px solid var(--border)!important}
.stTextInput input,.stNumberInput input,.stTextArea textarea{background:var(--surface)!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:var(--r)!important;font-family:'IBM Plex Mono',monospace!important;font-size:.82rem!important}
.stTabs [data-baseweb="tab-list"]{background:var(--surface)!important;border-bottom:2px solid var(--border)!important;gap:0!important}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--text3)!important;font-family:'IBM Plex Sans',sans-serif!important;font-size:.78rem!important;font-weight:500!important;padding:12px 20px!important;border:none!important;border-bottom:2px solid transparent!important;margin-bottom:-2px!important}
.stTabs [aria-selected="true"]{color:var(--blue)!important;border-bottom:2px solid var(--blue)!important;font-weight:600!important}
.stTabs [data-testid="stTabPanel"]{background:var(--bg)!important;padding-top:24px!important}
.stButton>button{background:var(--blue)!important;color:#fff!important;border:none!important;border-radius:var(--r)!important;font-family:'IBM Plex Sans',sans-serif!important;font-weight:500!important;font-size:.8rem!important;padding:.45rem 1.1rem!important;box-shadow:var(--sh)!important}
.stButton>button:hover{background:var(--blue2)!important}
.stButton>button[kind="secondary"]{background:var(--surface)!important;color:var(--text2)!important;border:1px solid var(--border)!important;box-shadow:none!important}
.stProgress>div>div{background:var(--blue)!important}
[data-testid="stDataFrame"]{border:1px solid var(--border)!important;border-radius:var(--r2)!important;overflow:hidden;box-shadow:var(--sh)}
[data-testid="stDataFrame"] table{background:var(--surface)!important}
[data-testid="stDataFrame"] th{background:var(--blue-l)!important;color:var(--blue2)!important;font-family:'IBM Plex Sans',sans-serif!important;font-size:.68rem!important;font-weight:600!important;letter-spacing:.05em!important;text-transform:uppercase!important;border-bottom:1px solid var(--blue-m)!important;padding:10px 12px!important}
[data-testid="stDataFrame"] td{color:var(--text)!important;border-bottom:1px solid var(--border)!important;font-family:'IBM Plex Mono',monospace!important;font-size:.78rem!important;padding:8px 12px!important}
[data-testid="stDataFrame"] tr:hover td{background:var(--blue-l)!important}
.streamlit-expanderHeader{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:var(--r)!important;color:var(--text)!important;font-family:'IBM Plex Mono',monospace!important;font-size:.8rem!important;box-shadow:var(--sh)!important}
.streamlit-expanderContent{background:var(--surface)!important;border:1px solid var(--border)!important;border-top:none!important;border-radius:0 0 var(--r) var(--r)!important}
[data-testid="stSlider"]>div>div{background:var(--blue)!important}
.ph{border-bottom:2px solid var(--border);padding-bottom:14px;margin-bottom:24px}
.pt{font-family:'IBM Plex Sans',sans-serif;font-size:1.35rem;font-weight:600;color:var(--text);letter-spacing:-.01em;display:block;margin-bottom:4px}
.ps{font-family:'IBM Plex Mono',monospace;font-size:.68rem;color:var(--text3);letter-spacing:.04em;text-transform:uppercase}
.mg{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin-bottom:20px}
.mc{background:var(--surface);border:1px solid var(--border);border-radius:var(--r2);padding:14px 16px;box-shadow:var(--sh)}
.ml{font-family:'IBM Plex Sans',sans-serif;font-size:.66rem;font-weight:500;color:var(--text3);letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px}
.mv{font-family:'IBM Plex Mono',monospace;font-size:1.45rem;font-weight:500;color:var(--text);line-height:1}
.mv.blue{color:var(--blue)}.mv.green{color:var(--green)}.mv.red{color:var(--red)}
.pill{display:inline-block;padding:2px 8px;border-radius:99px;font-family:'IBM Plex Sans',sans-serif;font-size:.65rem;font-weight:600;letter-spacing:.04em;text-transform:uppercase;line-height:1.6}
.pill-blue{background:var(--blue-l);color:var(--blue);border:1px solid var(--blue-m)}
.pill-green{background:var(--green-l);color:var(--green);border:1px solid #6ee7b7}
.pill-red{background:var(--red-l);color:var(--red);border:1px solid #fca5a5}
.pill-amber{background:var(--amber-l);color:var(--amber);border:1px solid #fcd34d}
.pill-muted{background:var(--surface2);color:var(--text3);border:1px solid var(--border)}
.alert{border-radius:var(--r);padding:10px 14px;font-size:.8rem;margin:6px 0;line-height:1.5;font-family:'IBM Plex Sans',sans-serif}
.alert-green{background:var(--green-l);border-left:3px solid var(--green);color:var(--green)}
.alert-red{background:var(--red-l);border-left:3px solid var(--red);color:var(--red)}
.alert-amber{background:var(--amber-l);border-left:3px solid var(--amber);color:var(--amber)}
.alert-blue{background:var(--blue-l);border-left:3px solid var(--blue);color:var(--blue2)}
.ic{background:var(--surface);border:1px solid var(--border);border-radius:var(--r2);padding:16px 18px;margin-bottom:10px;box-shadow:var(--sh)}
.ic-sm{background:var(--surface2);border:1px solid var(--border);border-radius:var(--r);padding:9px 12px;margin-bottom:5px}
.ic-blue{background:var(--blue-l);border:1px solid var(--blue-m);border-radius:var(--r2);padding:14px 16px;margin-bottom:10px}
.mkt-table{width:100%;border-collapse:collapse}
.mkt-table th{background:var(--blue-l);color:var(--blue2);font-family:'IBM Plex Sans',sans-serif;font-size:.65rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;padding:9px 12px;text-align:left;border-bottom:1px solid var(--blue-m)}
.mkt-table td{padding:8px 12px;border-bottom:1px solid var(--border);font-family:'IBM Plex Mono',monospace;font-size:.76rem;color:var(--text)}
.mkt-table tr:last-child td{border-bottom:none}
.mkt-table tr:hover td{background:var(--blue-l)}
.horse-col{font-family:'IBM Plex Sans',sans-serif;font-weight:500;color:var(--text);font-size:.82rem}
.edge-pos{color:var(--green);font-weight:500}.edge-neg{color:var(--red)}
.val-row td{background:rgba(5,150,105,.04)}
.fav-b{display:inline-block;padding:1px 5px;border-radius:3px;background:var(--blue-l);color:var(--blue);font-family:'IBM Plex Sans',sans-serif;font-size:.58rem;font-weight:600;margin-left:5px;text-transform:uppercase}
.prob-bar{height:3px;border-radius:2px;background:var(--border)}
.prob-fill{height:3px;border-radius:2px}
.comp-row{display:flex;align-items:center;gap:8px;padding:4px 0;border-bottom:1px solid var(--border)}
.comp-name{font-family:'IBM Plex Mono',monospace;font-size:.66rem;color:var(--text3);width:80px;flex-shrink:0}
.comp-score{font-family:'IBM Plex Mono',monospace;font-size:.66rem;color:var(--text2);width:44px;text-align:right}
.sm-row{display:flex;align-items:center;gap:14px;padding:8px 12px;background:var(--surface);border:1px solid var(--border);border-radius:var(--r);margin-bottom:4px;box-shadow:var(--sh)}
.sm-pos{font-family:'IBM Plex Sans',sans-serif;font-size:.68rem;font-weight:600;letter-spacing:.04em;text-transform:uppercase;width:68px;flex-shrink:0}
.sm-horses{font-family:'IBM Plex Mono',monospace;font-size:.78rem;color:var(--text2)}
.stake-card{background:var(--blue-l);border:1px solid var(--blue-m);border-radius:var(--r2);padding:14px 16px;margin-bottom:10px}
.stake-amt{font-family:'IBM Plex Mono',monospace;font-size:1.8rem;font-weight:600;color:var(--blue)}
.gate-row{display:flex;align-items:center;gap:10px;margin-bottom:7px}
.gate-lbl{font-family:'IBM Plex Sans',sans-serif;font-size:.76rem;color:var(--text2)}
.sb-logo{font-family:'IBM Plex Sans',sans-serif;font-size:1.1rem;font-weight:600;color:var(--blue);letter-spacing:-.01em}
.sb-sec{font-family:'IBM Plex Sans',sans-serif;font-size:.68rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--text3);margin:16px 0 8px;border-top:1px solid var(--border);padding-top:14px}
h2{font-family:'IBM Plex Sans',sans-serif!important;font-size:.72rem!important;font-weight:600!important;letter-spacing:.1em!important;text-transform:uppercase!important;color:var(--text3)!important;border-bottom:1px solid var(--border)!important;padding-bottom:8px!important;margin:20px 0 14px!important}
hr{border:none;border-top:1px solid var(--border);margin:18px 0}
.dbg{background:#fffbeb;border:1px solid #fcd34d;border-radius:var(--r);padding:12px 14px;font-family:'IBM Plex Mono',monospace;font-size:.72rem;color:#78350f;margin-bottom:12px}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
defaults = {
    "api_key":"","races":[],"selected_race":None,"runners":[],
    "ratings":{},"pf_ratings":{},"bet_log":[],"bank":1000.0,"starting_bank":1000.0,
    "staking_method":"Kelly","kelly_fraction":0.25,"flat_stake_pct":2.0,
    "level_stake":20.0,"max_stake_pct":5.0,"min_odds":2.0,"max_odds":30.0,
    "min_rating":55,"notes":{},"_debug_raw":None,
}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k]=v

# ── API core ──────────────────────────────────────────────────
BASE = "https://api.puntingform.com.au/v2"

def pf_get(endpoint:str, params:dict={}) -> Optional[dict]:
    if not st.session_state.api_key: return None
    p = dict(params); p["apiKey"] = st.session_state.api_key
    try:
        r = requests.get(f"{BASE}/{endpoint}", params=p, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"API {e.response.status_code}: {e.response.text[:300]}")
    except Exception as e:
        st.error(f"Connection error: {e}")
    return None

def safe_float(v, d=0.0):
    try: return float(v)
    except: return d

def extract_payload(data) -> list:
    if not data: return []
    if isinstance(data,list): return data
    if isinstance(data,dict):
        p = data.get("payLoad", data)
        if isinstance(p,list): return p
        if isinstance(p,dict):
            for v in p.values():
                if isinstance(v,list): return v
    return []

def get_race_id(race:dict) -> str:
    for f in ["raceId","RaceId","race_id","raceID"]:
        v = race.get(f)
        if v and str(v).strip() not in ("","0"): return str(v).strip()
    return ""

def get_horse_id(runner:dict) -> str:
    for f in ["horseId","HorseId","horse_id","runnerId","RunnerID"]:
        v = runner.get(f)
        if v and str(v).strip() not in ("","0"): return str(v).strip()
    return ""

# ── Meetings — ONE call, races already nested ─────────────────
def fetch_meetings(target_date:date) -> list:
    """
    FIX: Using form/meetings (plural) endpoint.
    This endpoint returns meetings with races populated in a single nested list.
    """
    ds = target_date.strftime("%Y-%m-%d")
    data = pf_get("form/meetings", {"meetingDate": ds})
    if not data: return []
    st.session_state["_debug_raw"] = data
    meetings = extract_payload(data)
    result = []
    for m in meetings:
        tr   = m.get("track") or {}
        name = tr.get("name") or m.get("meetingName") or m.get("venueName") or m.get("trackName") or "Unknown"
        state= tr.get("state") or m.get("state") or ""
        races= m.get("races") or m.get("Races") or m.get("raceList") or []
        m["races"] = races
        for race in races:
            race.setdefault("_meetingName", name)
            race.setdefault("_meetingState", state)
            race.setdefault("_meetingDate", ds)
        result.append(m)
    return result

# ── Race runners — form/fields by raceId ─────────────────────
def fetch_race_runners(race:dict) -> list:
    rid = get_race_id(race)
    if rid:
        data = pf_get("form/fields", {"raceId": rid})
        rows = extract_payload(data)
        if rows: return rows

    params = {}
    if race.get("_meetingDate"): params["meetingDate"] = race["_meetingDate"]
    if race.get("_meetingName"): params["track"]       = race["_meetingName"]
    rnum = race.get("raceNumber") or race.get("number") or race.get("raceNo")
    if rnum: params["raceNumber"] = str(rnum)
    if len(params) == 3:
        data = pf_get("form/fields", params)
        rows = extract_payload(data)
        if rows: return rows

    return race.get("runners") or race.get("fields") or race.get("horses") or []

# ── Past form — form/form by raceId (NOT horseId) ────────────
def fetch_past_form(race_id:str) -> list:
    if not race_id or str(race_id).strip() in ("","0"): return []
    data = pf_get("form/form", {"raceId": race_id})
    return extract_payload(data)

# ── PF AI Ratings — ratings/meetingratings by raceId ─────────
def fetch_pf_ratings(race_id:str) -> dict:
    if not race_id: return {}
    data = pf_get("ratings/meetingratings", {"raceId": race_id})
    rows = extract_payload(data)
    return {get_horse_id(r): r for r in rows if get_horse_id(r)}

# ── Sectionals — ratings/meetingsectionals by raceId ─────────
def fetch_sectionals(race_id:str) -> dict:
    if not race_id: return {}
    data = pf_get("ratings/meetingsectionals", {"raceId": race_id})
    rows = extract_payload(data)
    return {get_horse_id(r): r for r in rows if get_horse_id(r)}


# ── Rating engine ─────────────────────────────────────────────
WEIGHTS = {
    "sectional_speed":   22,
    "overall_speed":     18,
    "form_consistency":  12,
    "class_adj":         10,
    "unlucky_factor":     8,
    "pace_suitability":   7,
    "weight_carried":     5,
    "barrier_draw":       4,
    "jockey_trainer":     6,
    "track_affinity":     4,
    "distance_affinity":  4,
}
MAX_SCORE = sum(WEIGHTS.values())
LABELS = {
    "sectional_speed":  "Sectionals",
    "overall_speed":    "Speed Rtg",
    "form_consistency": "Consistency",
    "class_adj":        "Class Adj",
    "unlucky_factor":   "Unlucky",
    "pace_suitability": "Pace Fit",
    "weight_carried":   "Weight",
    "barrier_draw":     "Barrier",
    "jockey_trainer":   "J+T Combo",
    "track_affinity":   "Track",
    "distance_affinity":"Distance",
}

def _r_sectional(runner:dict, past:list, secs:dict) -> float:
    hid = get_horse_id(runner)
    sec = secs.get(hid, {})
    sr  = safe_float(sec.get("sectionalRating") or sec.get("closing600Rating") or 0)
    if sr > 0: return min(sr/100*22, 22)
    scores = []
    for run in past[:6]:
        cs = safe_float(run.get("closingSectional") or run.get("final3F") or run.get("last600") or 0)
        if 28 < cs < 40:
            scores.append(max(0, min(22, (36-cs)/3*22)))
        else:
            pos = safe_float(run.get("finishingPosition",10))
            field = max(safe_float(run.get("numberOfRunners",10)),1)
            margin= safe_float(run.get("marginBeaten",20))
            scores.append(max(0, (1-(pos-1)/field)*14 + max(0,1-margin/8)*8))
    return round(min(max(sum(scores)/len(scores),0),22),2) if scores else 11.0

def _r_speed(runner:dict, past:list) -> float:
    raw = safe_float(runner.get("speedRating") or runner.get("pfSpeedRating") or runner.get("bestSpeed") or 0)
    if raw <= 0:
        best = min((safe_float(r.get("finishingPosition",99)) for r in past[:5]), default=5)
        return round(min(max(18 - best*1.5, 2), 18), 2)
    cls = safe_float(runner.get("raceClass") or 0)
    ca  = 4 if cls>=90 else 2 if cls>=80 else 0 if cls>=65 else -3
    going = (runner.get("going") or runner.get("trackCondition") or "").lower()
    ga  = -3 if "heavy" in going else -2 if "soft" in going else -1 if "slow" in going else 0
    return round(min(max((raw+ca+ga-65)/55*18,0),18),2)

def _r_consistency(runner:dict, past:list) -> float:
    if not past: return 6.0
    score=0.0; ws=[3.0,2.5,2.0,1.5,1.0,0.8]
    for i,run in enumerate(past[:6]):
        w=ws[i] if i<len(ws) else 0.5
        pos=safe_float(run.get("finishingPosition",99))
        field=max(safe_float(run.get("numberOfRunners",10)),1)
        if pos==1: score+=w
        elif pos<=2: score+=w*.7
        elif pos<=3: score+=w*.5
        elif pos/field<=0.4: score+=w*.25
    lp=safe_float((past[0] or {}).get("finishingPosition",99))
    if lp==1: score+=1.5
    elif lp<=3: score+=0.8
    return round(min(max(score,0),12),2)

def _r_class(runner:dict, past:list) -> float:
    cur=safe_float(runner.get("raceClass") or 0)
    if not past or cur==0: return 5.0
    prev=[safe_float(r.get("raceClass",0)) for r in past[:4] if r.get("raceClass")]
    if not prev: return 5.0
    return round(min(max(5.0+(sum(prev)/len(prev)-cur)*1.8,0),10),2)

def _r_unlucky(past:list) -> float:
    if not past: return 4.0
    kws=[("blocked",3.5),("no clear run",3.5),("held up",3.0),("traffic",3.0),
         ("checked",2.5),("steadied",2.5),("interfered",2.5),("bumped",2.0),
         ("wide",1.5),("slow start",2.0),("hampered",2.5),("crowded",2.0)]
    score=4.0
    for run in past[:3]:
        c=(run.get("raceComment") or run.get("comments") or "").lower()
        for kw,val in kws:
            if kw in c: score+=val; break
        pt=safe_float(run.get("positionAfterTurn") or run.get("turnPosition") or 0)
        pf=safe_float(run.get("finishingPosition",99))
        if pt>=6 and pf<=3: score+=1.5
    return round(min(max(score,0),8),2)

def _r_pace(runner:dict, past:list) -> float:
    score=3.5; barrier=safe_float(runner.get("barrier") or runner.get("barrierNumber") or 8)
    for run in past[:4]:
        pe=safe_float(run.get("positionEarly") or run.get("firstPosition") or 5)
        pf=safe_float(run.get("finishingPosition",10))
        if pe>=5 and pf<=3: score+=0.8
        if pe<=3 and pf<=4: score+=0.5
    if barrier<=4 and int(runner.get("pacePosition") or 3)<=2: score+=0.5
    return round(min(max(score,0),7),2)

def _r_weight(runner:dict) -> float:
    w=safe_float(runner.get("weightTotal") or runner.get("weightCarried") or runner.get("handicapWeight") or 57)
    dist=safe_float(runner.get("distance") or runner.get("raceDistance") or 1200)
    base=max(0,5-(w-54)*0.55)
    mult=1.3 if dist>=2000 else 1.15 if dist>=1600 else 0.9 if dist<=1100 else 1.0
    return round(min(max(base*mult,0),5),2)

def _r_barrier(runner:dict) -> float:
    b=safe_float(runner.get("barrierNumber") or runner.get("barrier") or 8)
    dist=safe_float(runner.get("distance") or runner.get("raceDistance") or 1200)
    track=(runner.get("_meetingName") or runner.get("meetingName") or "").lower()
    if b<=0: return 2.0
    base=max(0,4-(b-1)*0.35)
    if any(t in track for t in ["flemington","randwick","caulfield"]) and dist<=1400:
        base=base*1.2 if b<=5 else base*0.8
    elif any(t in track for t in ["rosehill","sandown"]):
        base=base*1.1 if b<=6 else base*0.9
    return round(min(max(base,0),4),2)

def _r_jt(runner:dict) -> float:
    combo=runner.get("trainerJockeyA2E_Career") or {}
    runs=safe_float(combo.get("runners",0))
    if runs<5: return 3.0
    sr=safe_float(combo.get("strikeRate",0))
    a2e=safe_float(combo.get("a2E",0))
    p3=safe_float(combo.get("placeRate",0))
    return round(min(max((a2e*.5+sr/100*.35+p3/100*.15)*8,0),6),2)

def _r_track(runner:dict, past:list) -> float:
    track=(runner.get("_meetingName") or runner.get("meetingName") or "").lower()
    tr=runner.get("trackRecord") or {}
    s=safe_float(tr.get("starts",0)); w=safe_float(tr.get("firsts",0))
    p=safe_float(tr.get("seconds",0))+safe_float(tr.get("thirds",0))
    if s>0: return round(min((w/s*.7+p/s*.3)*4,4),2)
    if track and past:
        runs=[r for r in past if (r.get("meetingName") or "").lower()==track]
        if runs:
            wins=sum(1 for r in runs if safe_float(r.get("finishingPosition",99))==1)
            places=sum(1 for r in runs if safe_float(r.get("finishingPosition",99))<=3)
            return round(min((wins/len(runs)*.7+places/len(runs)*.3)*4,4),2)
    return 2.0

def _r_distance(runner:dict, past:list) -> float:
    dist=safe_float(runner.get("distance") or runner.get("raceDistance") or 1200)
    dr=runner.get("distanceRecord") or {}
    s=safe_float(dr.get("starts",0)); w=safe_float(dr.get("firsts",0))
    p=safe_float(dr.get("seconds",0))+safe_float(dr.get("thirds",0))
    if s>0: return round(min((w/s*.7+p/s*.3)*4,4),2)
    if past:
        runs=[r for r in past if abs(safe_float(r.get("raceDistance") or 0)-dist)<=100]
        if runs:
            wins=sum(1 for r in runs if safe_float(r.get("finishingPosition",99))==1)
            places=sum(1 for r in runs if safe_float(r.get("finishingPosition",99))<=3)
            return round(min((wins/len(runs)*.7+places/len(runs)*.3)*4,4),2)
    return 2.0

def rate_runner(runner:dict, past:list=[], secs:dict={}) -> dict:
    br = {
        "sectional_speed":   _r_sectional(runner, past, secs),
        "overall_speed":     _r_speed(runner, past),
        "form_consistency":  _r_consistency(runner, past),
        "class_adj":         _r_class(runner, past),
        "unlucky_factor":    _r_unlucky(past),
        "pace_suitability":  _r_pace(runner, past),
        "weight_carried":    _r_weight(runner),
        "barrier_draw":      _r_barrier(runner),
        "jockey_trainer":    _r_jt(runner),
        "track_affinity":    _r_track(runner, past),
        "distance_affinity": _r_distance(runner, past),
    }
    br["composite"] = round(sum(br.values()),2)
    br["pct"]       = round(br["composite"]/MAX_SCORE*100,1)
    return br


# ── Market framing — 122% realistic overround ─────────────────
def frame_market(runners:list) -> dict:
    priced=[(r, safe_float(r.get("priceSP") or r.get("fixedOddsWin") or 0)) for r in runners]
    priced=[(r,p) for r,p in priced if p>1.01]
    if not priced: return {}
    raw_sum=sum(1/p for _,p in priced)
    out={}
    for r,sp in priced:
        rid=get_horse_id(r); raw=1/sp; true=raw/raw_sum
        out[rid]={"sp":sp,"raw_pct":round(raw*100,2),"true_pct":round(true*100,2),
                  "fair_odds":round(1/true,2),"overround":round(raw_sum*100,1)}
    return out


# ── Model probability ─────────────────────────────────────────
def _wr(rec:dict, ks="starts", kw="firsts") -> Optional[float]:
    s=safe_float(rec.get(ks,0)); w=safe_float(rec.get(kw,0))
    return w/s if s>=3 else None

def model_prob(runner:dict, rating:dict, pf_r:dict={}) -> float:
    rp  = rating.get("pct",50)/100 if rating else 0.5
    cw  = safe_float(runner.get("winPct",0))/100
    tr  = _wr(runner.get("trackRecord") or {})
    dr  = _wr(runner.get("distanceRecord") or {})
    tj  = runner.get("trainerJockeyA2E_Career") or {}
    tsr = safe_float(tj.get("strikeRate",0))/100
    tv  = safe_float(tj.get("runners",0))>=5
    pf_px=safe_float(pf_r.get("pfAiPrice") or pf_r.get("modelPrice") or 0)
    pf_p =(1/pf_px) if pf_px>1 else 0
    lp  = safe_float((runner.get("lastStart") or {}).get("finishingPosition",99))
    s,w = 0.0, 0.0
    if pf_p>0:       s+=pf_p*4.0;  w+=4.0
    s+=rp*0.12;      w+=0.12
    s+=cw*2.5;       w+=2.5
    if tr is not None: s+=tr*1.5; w+=1.5
    if dr is not None: s+=dr*1.5; w+=1.5
    if tv:           s+=tsr*2.0;  w+=2.0
    if lp==1:        s+=0.04;     w+=0.10
    return min(max(s/w if w else cw, 0.005), 0.97)

def normalise_probs(runners:list, ratings:dict, pf_ratings:dict) -> dict:
    raw={get_horse_id(r): model_prob(r,ratings.get(get_horse_id(r),{}),pf_ratings.get(get_horse_id(r),{})) for r in runners}
    t=sum(raw.values())
    return {k:round(v/t,5) for k,v in raw.items()} if t>0 else raw

def value_check(mp:float,true_pct:float,sp:float,rpct:float,tj_a2e:float,min_r:int) -> dict:
    mkt=true_pct/100; edge=mp-mkt
    gates={"has_edge":edge>0,"rating_ok":rpct>=min_r,"tj_ok":tj_a2e>=1.0,
           "odds_ok":sp>=st.session_state.min_odds}
    bet=all(gates.values()); reasons=[]
    if not gates["has_edge"]:  reasons.append(f"model {round(mp*100,1)}% vs market {round(mkt*100,1)}%")
    if not gates["rating_ok"]: reasons.append(f"rating {rpct}% below min {min_r}%")
    if not gates["tj_ok"]:     reasons.append(f"T+J A2E {round(tj_a2e,2)} below 1.0")
    if not gates["odds_ok"]:   reasons.append(f"SP ${sp} below min ${st.session_state.min_odds}")
    return {"bet":bet,"edge_pct":round(edge*100,1),"model_pct":round(mp*100,1),
            "market_pct":round(mkt*100,1),"gates":gates,"reasons":reasons}


# ── Speedmap ──────────────────────────────────────────────────
PACE_LABELS={1:"Leader",2:"On Pace",3:"Midfield",4:"Back",5:"Last"}

def assign_pace(runners:list) -> list:
    for r in runners:
        if not r.get("pacePosition"):
            b=safe_float(r.get("barrier") or r.get("barrierNumber") or 8)
            r["pacePosition"]=1 if b<=3 else 2 if b<=6 else 3 if b<=10 else 4
    return runners

def classify_tempo(runners:list) -> dict:
    leaders=[r for r in runners if r.get("pacePosition")==1]
    onpace =[r for r in runners if r.get("pacePosition")==2]
    n=len(leaders)
    if n>=3:   return {"tempo":"HOT",      "cls":"pill-red",  "desc":"Multiple leaders — burn-up expected. Favours closers."}
    elif n==2: return {"tempo":"GENUINE",  "cls":"pill-amber","desc":"Two leaders — honest tempo. All styles viable."}
    elif n==1 and len(onpace)<=1: return {"tempo":"SOFT","cls":"pill-blue","desc":"Single uncontested leader — front-runner advantage."}
    else:      return {"tempo":"MODERATE", "cls":"pill-muted","desc":"Balanced dynamics — form runners get their run."}


# ── Staking ───────────────────────────────────────────────────
def kelly_stake(bank,prob,odds,frac):
    b=odds-1
    if b<=0 or prob<=0 or prob>=1: return 0.0
    return bank*frac*max((b*prob-(1-prob))/b, 0)

def calc_stake(bank,mp,sp,method,kf,fp,fx,mx) -> dict:
    edge=mp-(1/sp if sp>1 else 0)
    if method=="Kelly":   s=kelly_stake(bank,mp,sp,kf)
    elif method=="Flat %": s=bank*fp/100 if edge>0 else 0
    else:                  s=fx if edge>0 else 0
    s=min(round(s,2),bank*mx/100)
    ev=round((mp*(sp-1)-(1-mp))*s,2)
    return {"stake":s,"ev":ev,"pct":round(s/bank*100,1) if bank else 0}


# ── Bet log ───────────────────────────────────────────────────
def log_bet(horse,race,stake,odds,edge):
    st.session_state.bet_log.append({"datetime":datetime.now().strftime("%d/%m %H:%M"),
        "horse":horse,"race":race,"stake":stake,"odds":odds,"edge":edge,"result":"Pending","pl":0.0})

def settle_bet(idx,result):
    bet=st.session_state.bet_log[idx]
    pl=bet["stake"]*(bet["odds"]-1) if result=="Won" else -bet["stake"]
    st.session_state.bet_log[idx].update({"result":result,"pl":pl})
    st.session_state.bank+=pl

def bankroll_stats() -> dict:
    log=[b for b in st.session_state.bet_log if b["result"]!="Pending"]
    if not log: return {}
    staked=sum(b["stake"] for b in log); pl=sum(b["pl"] for b in log)
    winners=[b for b in log if b["result"]=="Won"]
    run=peak=0; dds=[]
    for b in log: run+=b["pl"]; peak=max(peak,run); dds.append(run-peak)
    return {"bets":len(log),"winners":len(winners),"sr":round(len(winners)/len(log)*100,1),
            "staked":round(staked,2),"pl":round(pl,2),"roi":round(pl/staked*100,1) if staked else 0,
            "avg_odds":round(sum(b["odds"] for b in log)/len(log),2),
            "max_dd":round(min(dds),2),"bank":round(st.session_state.bank,2)}


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-logo">Racing Edge</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:.62rem;color:#9ca3af;margin-bottom:4px">PUNTINGFORM API v2</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-sec">API</div>', unsafe_allow_html=True)
    try:    secret_key=st.secrets.get("PUNTINGFORM_API_KEY","")
    except: secret_key=""
    api_key=st.text_input("API Key",type="password",value=st.session_state.api_key or secret_key,placeholder="Enter key...")
    if api_key!=st.session_state.api_key: st.session_state.api_key=api_key
    st.markdown('<div class="sb-sec">Race Selection</div>', unsafe_allow_html=True)
    target_date =st.date_input("Date",value=date.today()+timedelta(days=1))
    state_filter=st.multiselect("States",["QLD","NSW","VIC","SA","WA","TAS","NT","ACT"])
    if st.button("Fetch Meetings"):
        with st.spinner("Fetching..."):
            st.session_state.races=fetch_meetings(target_date)
        st.success(f"{len(st.session_state.races)} meetings") if st.session_state.races else st.warning("No meetings found")
    st.markdown('<div class="sb-sec">Staking</div>', unsafe_allow_html=True)
    st.session_state.bank=st.number_input("Bank ($)",value=st.session_state.bank,step=10.0)
    st.session_state.staking_method=st.selectbox("Method",["Kelly","Flat %","Level"],
        index=["Kelly","Flat %","Level"].index(st.session_state.staking_method))
    if st.session_state.staking_method=="Kelly":
        st.session_state.kelly_fraction=st.slider("Kelly Fraction",0.1,1.0,st.session_state.kelly_fraction,0.05)
    elif st.session_state.staking_method=="Flat %":
        st.session_state.flat_stake_pct=st.slider("% of Bank",0.5,10.0,st.session_state.flat_stake_pct,0.5)
    else:
        st.session_state.level_stake=st.number_input("Fixed ($)",value=st.session_state.level_stake,step=5.0)
    st.session_state.max_stake_pct=st.slider("Max Stake %",1.0,15.0,st.session_state.max_stake_pct,0.5)
    st.markdown('<div class="sb-sec">Filters</div>', unsafe_allow_html=True)
    st.session_state.min_odds  =st.number_input("Min Odds",value=st.session_state.min_odds,step=0.5)
    st.session_state.max_odds  =st.number_input("Max Odds",value=st.session_state.max_odds,step=1.0)
    st.session_state.min_rating=st.slider("Min Rating %",0,100,st.session_state.min_rating)


# ── Tabs ──────────────────────────────────────────────────────
t_races,t_analysis,t_staking,t_bankroll,t_guide=st.tabs(["Races","Analysis","Staking","Bankroll","Guide"])


# ════════════════════════════════════════════════
# RACES TAB
# ════════════════════════════════════════════════
with t_races:
    st.markdown('<div class="ph"><span class="pt">Race Meetings</span><span class="ps">Select a race to load its field</span></div>', unsafe_allow_html=True)
    if not st.session_state.api_key:
        st.markdown('<div class="alert alert-amber">Enter your PuntingForm API key in the sidebar.</div>', unsafe_allow_html=True)

    raw=st.session_state.get("_debug_raw")
    if raw:
        with st.expander("API Debug — raw response"):
            st.markdown('<div class="dbg">This panel shows what the form/meetings API returned.</div>', unsafe_allow_html=True)
            meetings_raw=extract_payload(raw)
            if meetings_raw:
                first=meetings_raw[0]
                st.write("**First meeting keys:**", list(first.keys()))
                races_found=first.get("races") or first.get("Races") or first.get("raceList") or []
                st.write(f"**Races embedded:** {len(races_found)}")
                if races_found:
                    r0=races_found[0]
                    st.write("**First race keys:**", list(r0.keys()))
                    rid=get_race_id(r0)
                    st.write(f"**raceId extracted:** `{rid or 'NOT FOUND'}`")

    if not st.session_state.races:
        st.markdown('<div class="alert alert-blue">Fetch meetings using the sidebar button.</div>', unsafe_allow_html=True)
    else:
        for meeting in st.session_state.races:
            tr   =meeting.get("track") or {}
            name =tr.get("name") or meeting.get("meetingName") or meeting.get("venueName") or "Unknown"
            state=tr.get("state") or meeting.get("state") or ""
            races=meeting.get("races") or []
            if state_filter and not any(f in state.upper() for f in state_filter): continue
            with st.expander(f"{name}  —  {state}  —  {len(races)} races"):
                if not races:
                    st.markdown('<div class="alert alert-amber">No races in this meeting. Check API Debug panel.</div>', unsafe_allow_html=True)
                for race in races:
                    rnum =race.get("raceNumber") or race.get("number") or "?"
                    rname=race.get("raceName") or race.get("name") or f"Race {rnum}"
                    rdist=race.get("raceDistance") or race.get("distance") or "?"
                    rtime=race.get("startTime") or race.get("raceTime") or ""
                    rcls =race.get("raceClass") or ""
                    rid  =get_race_id(race)
                    c1,c2=st.columns([7,1])
                    with c1:
                        id_b='' if rid else ' <span class="pill pill-amber">No raceId</span>'
                        st.markdown(
                            f'<div style="padding:6px 0;border-bottom:1px solid var(--border)">'
                            f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:.78rem;color:var(--blue);font-weight:600">R{rnum}</span>'
                            f'&nbsp;&nbsp;<span style="font-family:\'IBM Plex Sans\',sans-serif;font-size:.82rem">{rname}</span>'
                            f'&nbsp;&nbsp;<span class="pill pill-muted">{rdist}m</span>'
                            f'&nbsp;<span class="pill pill-muted">{rcls}</span>'
                            f'&nbsp;&nbsp;<span style="font-family:\'IBM Plex Mono\',monospace;font-size:.7rem;color:var(--text3)">{rtime}</span>'
                            f'{id_b}</div>',
                            unsafe_allow_html=True
                        )
                    with c2:
                        if st.button("Load",key=f"sel_{name}_{rnum}"):
                            st.session_state.selected_race=race
                            st.session_state.runners=[]; st.session_state.ratings={}; st.session_state.pf_ratings={}
                            with st.spinner(f"Loading R{rnum}..."):
                                runners=fetch_race_runners(race)
                                st.session_state.runners=assign_pace(runners)
                            if st.session_state.runners:
                                st.success(f"{len(st.session_state.runners)} runners — go to Analysis tab")
                            else:
                                st.error("No runners found. Check API Debug panel.")


# ════════════════════════════════════════════════
# ANALYSIS TAB
# ════════════════════════════════════════════════
with t_analysis:
    race=st.session_state.selected_race
    runners=st.session_state.runners

    if not race:
        st.markdown('<div class="alert alert-blue">Select a race from the Races tab.</div>', unsafe_allow_html=True)
    elif not runners:
        st.markdown('<div class="alert alert-amber">No runners loaded. Click Load on a race.</div>', unsafe_allow_html=True)
    else:
        rname=race.get("raceName") or race.get("name") or "Race"
        rdist=race.get("raceDistance") or race.get("distance") or "?"
        rtrk =race.get("_meetingName") or race.get("meetingName") or ""
        rcond=race.get("trackCondition") or ""
        rcls =race.get("raceClass") or ""
        rnum =race.get("raceNumber") or race.get("number") or "?"
        rid  =get_race_id(race)

        st.markdown(
            f'<div class="ph"><span class="pt">Race {rnum} — {rname}</span>'
            f'<span class="ps">{rtrk}  ·  {rdist}m  ·  {rcls}  ·  {rcond or "Condition TBC"}'
            f'{"  ·  raceId " + rid if rid else "  ·  No raceId"}</span></div>',
            unsafe_allow_html=True
        )

        # Speedmap
        st.markdown("## Speedmap")
        tempo=classify_tempo(runners)
        st.markdown(
            f'<div class="ic" style="display:flex;align-items:center;gap:12px;margin-bottom:12px">'
            f'<span class="pill {tempo["cls"]}">{tempo["tempo"]} PACE</span>'
            f'<span style="font-size:.82rem;color:var(--text2)">{tempo["desc"]}</span></div>',
            unsafe_allow_html=True
        )
        positions={1:[],2:[],3:[],4:[],5:[]}
        for r in runners:
            positions[int(r.get("pacePosition",3))].append(r.get("name") or r.get("runnerName") or r.get("horseName") or "?")
        pc={1:"var(--red)",2:"var(--amber)",3:"var(--blue)",4:"var(--text3)",5:"var(--text3)"}
        for pos,lbl in PACE_LABELS.items():
            h=positions.get(pos,[])
            if h:
                st.markdown(f'<div class="sm-row"><span class="sm-pos" style="color:{pc[pos]}">{lbl}</span><span class="sm-horses">{" &nbsp;·&nbsp; ".join(h)}</span></div>',unsafe_allow_html=True)

        st.markdown('<hr>',unsafe_allow_html=True)

        # Rate all runners
        st.markdown("## Runner Ratings")
        cb,ci=st.columns([2,5])
        with cb: rate_btn=st.button("Rate All Runners")
        with ci:
            st.markdown('<div style="padding-top:8px;font-family:\'IBM Plex Mono\',monospace;font-size:.7rem;color:var(--text3)">Uses raceId to fetch form — avoids 400 error.</div>',unsafe_allow_html=True)

        if rate_btn:
            ratings_new={}; pf_new={}; secs_new={}; past_by_hid={}
            prog=st.progress(0); sb=st.empty()
            if rid:
                sb.markdown('<div class="alert alert-blue">Fetching past form (form/form)...</div>',unsafe_allow_html=True)
                past_rows=fetch_past_form(rid)
                for row in past_rows:
                    hid=get_horse_id(row)
                    if hid: past_by_hid.setdefault(hid,[]).append(row)
                sb.markdown('<div class="alert alert-blue">Fetching PF AI ratings...</div>',unsafe_allow_html=True)
                pf_new=fetch_pf_ratings(rid)
                sb.markdown('<div class="alert alert-blue">Fetching sectional data...</div>',unsafe_allow_html=True)
                secs_new=fetch_sectionals(rid)
            else:
                sb.markdown('<div class="alert alert-amber">No raceId — limited analysis.</div>',unsafe_allow_html=True)
            for i,runner in enumerate(runners):
                hid=get_horse_id(runner)
                ratings_new[hid or f"_i{i}"]=rate_runner(runner, past_by_hid.get(hid,[]), secs_new)
                prog.progress((i+1)/len(runners))
            st.session_state.ratings=ratings_new; st.session_state.pf_ratings=pf_new
            prog.empty(); sb.empty()
            st.success(f"Rated {len(runners)} runners")

        ratings   =st.session_state.ratings
        pf_ratings=st.session_state.pf_ratings
        mkt       =frame_market(runners)
        fp        =normalise_probs(runners,ratings,pf_ratings) if ratings else {}

        # Market frame table
        st.markdown("## Market Frame")
        if not mkt:
            st.markdown('<div class="alert alert-amber">No prices available.</div>',unsafe_allow_html=True)
        else:
            sample=next(iter(mkt.values()),{}); overround=sample.get("overround",0)
            sorted_mkt=sorted(runners,key=lambda x: safe_float(x.get("priceSP") or x.get("fixedOddsWin") or 99))
            rows_html=""
            for rank,r in enumerate(sorted_mkt):
                rid2=get_horse_id(r); mf=mkt.get(rid2)
                if not mf: continue
                name2=r.get("name") or r.get("runnerName") or r.get("horseName") or "?"
                sp=mf["sp"]; raw_p=mf["raw_pct"]; tru_p=mf["true_pct"]; fair=mf["fair_odds"]
                mp2=fp.get(rid2,0); pfr=pf_ratings.get(rid2,{})
                pf_px=safe_float(pfr.get("pfAiPrice") or pfr.get("modelPrice") or 0)
                diff=round(mp2*100-tru_p,1) if mp2 else None; is_val=diff is not None and diff>0
                edge_html=f'<span class="{"edge-pos" if (diff or 0)>0 else "edge-neg"}">{("+" if (diff or 0)>=0 else "")}{diff}%</span>' if diff is not None else "—"
                bar_w=min(int(tru_p*3),100); bar_c="#059669" if is_val else "#c3d1fa"
                rows_html+=f"""
                <tr class="{'val-row' if is_val else ''}">
                  <td>{rank+1}</td>
                  <td><span class="horse-col">{name2}</span></td>
                  <td style="color:var(--blue);font-weight:600">${sp:.2f}</td>
                  <td>{tru_p}%</td>
                  <td style="color:var(--text2)">${fair:.2f}</td>
                  <td style="color:var(--blue)">${pf_px:.2f}</td>
                  <td style="color:var(--blue)">{f"{mp2*100:.1f}%" if mp2 else "—"}</td>
                  <td>{edge_html}</td>
                </tr>"""
            st.markdown(f"""
            <div class="ic" style="padding:0;overflow:hidden">
              <table class="mkt-table">
                <thead><tr>
                  <th>#</th><th>Horse</th><th>SP</th><th>True%</th><th>Fair</th><th>PF AI</th><th>Model%</th><th>Edge</th>
                </tr></thead>
                <tbody>{rows_html}</tbody>
              </table>
            </div>""", unsafe_allow_html=True)

        st.markdown('<hr>',unsafe_allow_html=True)

        # Per-runner detail
        def sk(r): rid2=get_horse_id(r); return fp.get(rid2,0) if fp else -safe_float(r.get("priceSP") or 99)
        for rank,runner in enumerate(sorted(runners,key=sk,reverse=True),1):
            hid    =get_horse_id(runner)
            name   =runner.get("name") or runner.get("runnerName") or runner.get("horseName") or "Unknown"
            price  =safe_float(runner.get("priceSP") or runner.get("fixedOddsWin") or 0)
            rating =ratings.get(hid) if hid else None
            mf     =mkt.get(hid,{})
            mp2    =fp.get(hid,0)
            tj     =runner.get("trainerJockeyA2E_Career") or {}
            tj_a2e =safe_float(tj.get("a2E",0))
            
            ps=f"${price:.2f}" if price>0 else "N/A"
            ms=f"  Model {round(mp2*100,1)}%" if mp2 else ""
            label=f"#{rank}  {name}   {ps}{ms}"

            with st.expander(label):
                if rating and mf and mp2:
                    verdict=value_check(mp2,mf["true_pct"],price,rating["pct"],tj_a2e,st.session_state.min_rating)
                    if verdict["bet"]:
                        rec=calc_stake(st.session_state.bank,mp2,price,st.session_state.staking_method,
                            st.session_state.kelly_fraction,st.session_state.flat_stake_pct,
                            st.session_state.level_stake,st.session_state.max_stake_pct)
                        st.markdown(f'<div class="stake-card"><div class="ml">Stake</div><div class="stake-amt">${rec["stake"]:.2f}</div></div>',unsafe_allow_html=True)
                        if st.button(f"Log Bet — {name}",key=f"log_{hid}"):
                            log_bet(name,f"Race {rnum}",rec["stake"],price,verdict["edge_pct"])
                            st.success("Logged")
                    else:
                        st.markdown(f'<div class="alert alert-red">No bet: {", ".join(verdict["reasons"])}</div>',unsafe_allow_html=True)

# ════════════════════════════════════════════════
# OTHER TABS (Simplified for stability)
# ════════════════════════════════════════════════
with t_staking:
    st.markdown("## Bet Log")
    if st.session_state.bet_log:
        df=pd.DataFrame(st.session_state.bet_log)
        st.dataframe(df,use_container_width=True)
    else:
        st.write("No bets logged.")

with t_bankroll:
    st.metric("Current Bank", f"${st.session_state.bank:.2f}")

with t_guide:
    st.write("Using PuntingForm V2 API. Ensure your key is valid.")

st.markdown('<div style="text-align:center;padding:36px 0;font-size:.6rem;color:#9ca3af">RACING EDGE · ANALYSER</div>',unsafe_allow_html=True)
