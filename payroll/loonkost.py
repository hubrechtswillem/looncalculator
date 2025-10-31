# payroll/loonkost.py

from payroll.werknemer import Bediende
from parameters.structurele_vermindering_2025 import bereken_structurele_vermindering_maand

# Belgisch afronden op 2 cijfers (met klein epsilon-Dodging)
def round2(x): 
    return round(x + 1e-9, 2)


def bereken_loonkost(
    b: Bediende,
    nettoloon_result: dict,
    categorie: int = 1,       # categorie structurele vermindering (1 = algemene categorie)
    RSZ_WG_PCT: float = 0.25  # standaard patronale bijdrage: 25%
) -> dict:
    """
    Berekent de totale werkgeverskost voor een bediende.

    Inbegrepen:
    ✅ Bruto loon
    ✅ Patronale RSZ-bijdrage (25% standaard)
    ✅ Groepsverzekering WG-deel (percentage op brutoloon)
    ✅ Arbeidsongevallenverzekering (percentage op brutoloon)
    ✅ Werkgeversdeel maaltijdcheques
    ✅ Ecocheques
    ✅ Kosten eigen aan werkgever (zoals thuiswerkvergoeding)
    ✅ Structurele vermindering als aftrek

    Return:
    Dict met detail + totaal kost (per jaar en per maand)
    """

    # Basismassa
    bruto_jaar = b.bruto_jaarloon

    # ✅ Werkgeversbijdragen bovenop brutoloon
    rsz_wg = bruto_jaar * RSZ_WG_PCT          # patronale RSZ
    gv_wg = bruto_jaar * b.GV_WG_pct          # groepsverzekering WG
    ao = bruto_jaar * b.AO_pct                # arbeidsongevallenverzekering

    # ✅ Andere WG-kosten
    mg_wg = b.MG_WG_jaar                      # voordeel voor werknemer, maar kost voor WG
    ec = b.EC_jaar                             # idem: ecocheques volledig ten laste WG
    kosten_eigen = b.maandelijkse_kostenvergoeding * 12.0  # fiscaal vrijgesteld, wel kosten

   # ✅ Structurele vermindering (aftrek werkgeverslasten)
    sv_maand = bereken_structurele_vermindering_maand(categorie, b.bruto_maandloon, b.prestatiebreuk)
    sv_jaar = sv_maand * 12.0

    # 🚫 Nooit meer aftrekken dan de totale patronale bijdrage
    sv_jaar = min(sv_jaar, rsz_wg)

    # ✅ Totale werkgeverskost
    # Alles optellen wat WG betaalt, min de structurele korting
    totaal_kost_jaar = (
        bruto_jaar +
        rsz_wg +
        gv_wg +
        ao +
        mg_wg +
        ec +
        kosten_eigen -
        sv_jaar       # aftrek!
    )

    # ✅ Resultaat rapporteren (ook per maand)
    return {
        "rsz_werkgever": round2(rsz_wg-sv_jaar),
        "gv_werkgever": round2(gv_wg),
        "ao_verzekering": round2(ao),
        "maaltijdcheques_wg": round2(mg_wg),
        "ecocheques": round2(ec),
        "kosten_eigen": round2(kosten_eigen),
        
        "totaal_loonkost_jaar": round2(totaal_kost_jaar),
        "totaal_loonkost_maand": round2(totaal_kost_jaar / 12.0),
    }
