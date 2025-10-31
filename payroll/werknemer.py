# payroll/werknemer.py

class Bediende:
    def __init__(
        self,
        bruto_maandloon: float,          # Maandelijks brutoloon vóór inhoudingen (basis voor alles)
        prestatiebreuk: float = 1.0,     # Werkregime: 1.0 = voltijds, 0.8 = 4/5, 0.5 = halftijds ...
        MG_WG_jaar: float = 0.0,         # Werkgeversdeel maaltijdcheques per jaar (voordeel)
        MG_WN_jaar: float = 0.0,         # Werknemersdeel maaltijdcheques per jaar (aftrek)
        EC_jaar: float = 0.0,            # Ecocheques per jaar (voordeel)
        GV_WG_pct: float = 0.0,          # % werkgeversbijdrage groepsverzekering (patronaal)
        AO_pct: float = 0.0,             # % arbeidsongevallenverzekering (patronaal)
        maandelijkse_kostenvergoeding: float = 0.0,  # Kosten eigen aan werkgever (vrijgesteld)
        regime: str = "individueel"      # Regime voor BBSZ: individueel / gemeenschappelijk_met_inkomen / ...
    ):

        # Basissalaris
        self.bruto_maandloon = bruto_maandloon
        self.bruto_jaarloon = bruto_maandloon * 12   # Altijd intern ook in jaarvorm beschikbaar

        # Contractuele prestaties (voor berekening referteloon werkbonus)
        self.prestatiebreuk = prestatiebreuk        

        # Koopkracht-voordelen
        self.MG_WG_jaar = MG_WG_jaar      # Extra koopkracht van WG
        self.MG_WN_jaar = MG_WN_jaar      # Kost voor WN, dus aftrek van netto
        self.EC_jaar = EC_jaar            # Nettovoordeel

        # Werkgeverskosten
        self.GV_WG_pct = GV_WG_pct        # % op brutoloon
        self.AO_pct = AO_pct              # % op brutoloon
        self.maandelijkse_kostenvergoeding = maandelijkse_kostenvergoeding  # Extra kost + koopkracht

        # BBSZ-regime selectie (beïnvloedt inhouding)
        self.regime = regime

    def __repr__(self):
        # Representatie voor debugging of prints
        return f"Bediende(bruto={self.bruto_maandloon} EUR/maand, prestatiebreuk={self.prestatiebreuk})"
