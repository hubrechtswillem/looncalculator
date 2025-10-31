# payroll/nettoloon.py
from payroll.werknemer import Bediende
from parameters.belasting_2025 import bereken_personenbelasting
from parameters.werkbonus_2025 import bereken_sociale_werkbonus, bereken_fiscale_werkbonus
from parameters.bszb_2025 import bereken_bszb
RSZ_WERKNEMER_PERCENT = 0.1307
def round2(x): return round(x + 1e-9, 2)
def bereken_nettoloon(b: Bediende) -> dict:
    bruto_jaar = b.bruto_jaarloon; 
    bruto_maand = b.bruto_maandloon
    rsz_basis = bruto_jaar * RSZ_WERKNEMER_PERCENT

    luikA, luikB = bereken_sociale_werkbonus(bruto_maand);
    sociale_wb = luikA + luikB
    fisA, fisB = bereken_fiscale_werkbonus(luikA, luikB); 
    fiscale_wb = fisA + fisB
    rsz_wn = rsz_basis - sociale_wb
    KOSTENFORFAIT_PLAFOND = 5930.0
    kostenforfait = min(KOSTENFORFAIT_PLAFOND, 0.30 * (bruto_jaar - rsz_wn))
    belastbaar = bruto_jaar - rsz_wn - kostenforfait
    personenbelasting = bereken_personenbelasting(belastbaar) - fiscale_wb
    nettoloon_jaar = bruto_jaar - rsz_wn - personenbelasting
    bbsz = bereken_bszb(bruto_maand, b.regime)["bszb_jaar"]
    netto_jaar = nettoloon_jaar - bbsz - b.MG_WN_jaar; netto_maand = netto_jaar/12.0
    koopkracht_jaar = netto_jaar + b.MG_WG_jaar + b.EC_jaar + b.maandelijkse_kostenvergoeding * 12.0
    koopkracht_maand = koopkracht_jaar/12.0
    return {
        "bruto_maand": round2(bruto_maand), "bruto_jaar": round2(bruto_jaar),
        "rsz_werknemer": round2(rsz_wn),
        "sociale_werkbonus": round2(sociale_wb), "fiscale_werkbonus": round2(fiscale_wb),
        "kostenforfait": round2(kostenforfait), "belastbaar_inkomen": round2(belastbaar),
        "personenbelasting": round2(personenbelasting), "bbsz": round2(bbsz),
        "nettoloon_maand": round2(netto_maand), "nettoloon_jaar": round2(netto_jaar),
        "koopkracht_maand": round2(koopkracht_maand), "koopkracht_jaar": round2(koopkracht_jaar)
    }
