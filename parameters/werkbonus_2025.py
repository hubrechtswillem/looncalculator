# parameters/werkbonus_2025.py
WERKBONUS_PARAMS = {
    "bedienden": {
        "luikA": {
            "S_max": 2669.96, 
            "bedrag": 115.91, 
            "S_afbouw_max": 3144.45, 
            "afbouw_coef": 0.2443
            },
        "luikB": {
            "S_max": 2090.78, 
            "bedrag": 156.30, 
            "S_afbouw_max": 2669.96, 
            "afbouw_coef": 0.2699},
        "fiscale_pct_luikA": 0.3314,
        "fiscale_pct_luikB": 0.5254
    }
}
def _afbouw(S, S_max, bedrag, S_afbouw_max, afbouw_coef):
    if S <= S_max: return bedrag
    elif S <= S_afbouw_max:
        v = bedrag - afbouw_coef * (S - S_max)
        return max(0.0, v)
    else: return 0.0
def bereken_sociale_werkbonus(refertemaandloon: float, categorie: str = "bedienden"):
    p = WERKBONUS_PARAMS[categorie]
    A = _afbouw(refertemaandloon, **p["luikA"])
    B = _afbouw(refertemaandloon, **p["luikB"])
    return round(A, 2), round(B, 2)
def bereken_fiscale_werkbonus(luikA: float, luikB: float, categorie: str = "bedienden"):
    p = WERKBONUS_PARAMS[categorie]
    return round(luikA * p["fiscale_pct_luikA"], 2), round(luikB * p["fiscale_pct_luikB"], 2)

print(bereken_sociale_werkbonus(2000,"bedienden"))