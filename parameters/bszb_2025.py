# parameters/bszb_2025.py
from typing import Literal
Regime = Literal["gemeenschappelijk_met_inkomen", "gemeenschappelijk_zonder_inkomen", "individueel"]
BSZB_PARAMS_2024 = {
    "maandgrenzen": {
        "g1": 1945.38, 
        "g2": 2190.18, 
        "g3": 3737.00, 
        "g4": 4100.00, 
        "g5": 6038.82
        },
    "kwartaalgrenzen": {
        "k1": 3285.29, 
        "k2": 5836.14, 
        "k3": 6570.54, 
        "k4": 11211.00, 
        "k5": 12300.00, 
        "k6": 18116.46
        },
    "percentages": {
        "gemeenschappelijk_met_inkomen": {
            "zone1_q": 15.45, 
            "zone2_pct": 0.0590, 
            "min_q": 15.45, 
            "zone3_pct": 0.0110, 
            "max_q": 154.92
            },
        "gemeenschappelijk_zonder_inkomen": {
            "zone2_pct": 0.0590, 
            "zone3_pct": 0.0110, 
            "max_q": 182.82
            },
        "individueel": {
            "z2_pct": 0.0422, 
            "z3_q": 30.99, 
            "z3_pct": 0.0110, 
            "z4_q": 82.05, 
            "z4_pct": 0.0338, 
            "z5_q": 118.83, 
            "z5_pct": 0.0110, 
            "z6_q": 182.82
            }
    },
}

def _within(x, low, high): 
    return max(0.0, min(x, high) - low)

def bereken_bszb(maandloon: float, regime: Regime = "individueel") -> dict:

    S = maandloon; K = S * 3
    g = BSZB_PARAMS_2024["maandgrenzen"]; k = BSZB_PARAMS_2024["kwartaalgrenzen"]; pc = BSZB_PARAMS_2024["percentages"]; p = pc[regime]
    q = 0.0

    if regime == "gemeenschappelijk_met_inkomen":
        if k["k1"] <= K < k["k2"]: q = p["zone1_q"]
        elif k["k2"] <= K <= k["k3"]:
            base = _within(S, g["g1"], g["g2"]); q = max(p["min_q"], base * p["zone2_pct"])
        elif K > k["k3"]:
            excedent = max(0.0, S - g["g2"]); q = 43.32 + excedent * p["zone3_pct"]; q = min(q, p["max_q"])
    elif regime == "gemeenschappelijk_zonder_inkomen":
        if k["k2"] <= K <= k["k3"]:
            base = _within(S, g["g1"], g["g2"]); q = base * p["zone2_pct"]
        elif K > k["k3"]:
            excedent = max(0.0, S - g["g2"]); q = 43.32 + excedent * p["zone3_pct"]; q = min(q, p["max_q"])
    elif regime == "individueel":
        if k["k2"] <= K <= k["k3"]:
            base = _within(S, g["g1"], g["g2"]); q = base * p["z2_pct"]
        elif k["k3"] < K <= k["k4"]:
            base = _within(S, g["g2"], g["g3"]); q = p["z3_q"] + base * p["z3_pct"]
        elif k["k4"] < K <= k["k5"]:
            base = _within(S, g["g3"], g["g4"]); q = p["z4_q"] + base * p["z4_pct"]
        elif k["k5"] < K <= k["k6"]:
            base = _within(S, g["g4"], g["g5"]); q = p["z5_q"] + base * p["z5_pct"]
        elif K > k["k6"]: q = p["z6_q"]

    maand = round(q/3.0 + 1e-9, 2); 
    jaar = round(maand*12 + 1e-9, 2)
    
    return {"bszb_kwartaal": round(q + 1e-9, 2), "bszb_maand": maand, "bszb_jaar": jaar}
