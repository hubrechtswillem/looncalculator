# parameters/structurele_vermindering_2025.py

# 📌 Parameters voor structurele vermindering werkgeversbijdrage
# Momenteel enkel categorie 1 (algemene categorie)
# Gebaseerd op parameters Q3 2025 uit RSZ-documentatie
PARAMS = {
    1: {
        "F": 0.0,         # Vast forfaitair bedrag (voor cat.1 voorlopig 0)
        "alpha": 0.1400,  # hellingscoëfficiënt voor lage lonen (S < S0)
        "gamma": 0.1500,  # hellingscoëfficiënt voor zeer lage lonen (S < S2)
        "delta": 0.0,     # voor hogelonencomponent (niet gebruikt in cat.1)
        "S0": 11233.89,   # loongrens lage lonen (op jaarbasis/omgerekend)
        "S2": 9360.00,    # loongrens zeer lage lonen
        "S1": None        # grens voor hogelonencomponent (niet gebruikt)
    }
}


def _comp(value):
    """
    Afronden op 2 cijfers (99,5 → 100, correct Belgisch afronden)
    maar negatieve resultaten worden als 0 beschouwd.
    
    Dit volgt exact de RSZ-regel:
    → elk component wordt afzonderlijk afgerond
    → nooit negatieve vermindering!
    """
    v = round(value + 1e-9, 2)
    return max(0.0, v)


def bereken_R(categorie: int, maandloon: float, prestatiebreuk: float) -> float:
    """
    Berekent het forfaitaire verminderingsbedrag R (per kwartaal) volgens:
    
    🧮 R = F + α(S0 - S) + γ(S2 - S) + δ(W - S1)

    Waar:
    - S = referteloon (per maand omgerekend)
    - W = werkelijk loon (idem als S in deze vereenvoudiging)

    ❗ Dit is enkel het R-bedrag → moet nog vermenigvuldigd
    worden met prestatiebreuk en factor µ (bij ons 1)
    """
    p = PARAMS[categorie]
    S=maandloon*3*prestatiebreuk
    R = p["F"]
    R += _comp(p["alpha"] * (p["S0"] - S))   # lage lonen
    R += _comp(p["gamma"] * (p["S2"] - S))   # zeer lage lonen
    # hogelonencomponent δ wordt nu niet toegepast in categorie 1
    return round(R + 1e-9, 2)



def bereken_structurele_vermindering_maand(categorie: int, maandloon: float, prestatiebreuk: float = 1.0) -> float:
    """
    Berekent de structurele vermindering per maand

    Ps = R × µ × βs
    in RSZ-formule:
    - µ (vaste vermenigvuldigingsfactor) = 1
    - βs = prestatiebreuk (deeltijd → minder vermindering)

    ⚠️ R is gebaseerd op refertemaandloon → jaargrenzen zijn omgerekend

    Return:
    ✅ maandelijkse vermindering werkgeversbijdragen
    """
    R = bereken_R(categorie, maandloon, prestatiebreuk)
    mu=prestatiebreuk
    if mu<0.55:
        beta=1.18
    elif mu<0.9:
        beta=1.18+(mu-0.55)*0.28
    else:
        beta=1/mu   
    Ps = R * prestatiebreuk*beta/3

    return round(Ps + 1e-9, 2)

print(bereken_structurele_vermindering_maand(1,2000,1))
