# payroll/overzicht.py

from payroll.werknemer import Bediende
from payroll.nettoloon import bereken_nettoloon
from payroll.loonkost import bereken_loonkost
import pandas as pd

# 🇧🇪 Belgisch geldformaat: punt voor duizendtallen, komma voor decimalen
def fmt_eur_be(x: float, signed: bool = True) -> str:
    s = f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if signed and x > 0:
        s = "+" + s
    return f"€ {s}"


def maak_overzicht(b: Bediende, toon_per_maand: bool = True):
    """
    Maakt één tabel (pandas DataFrame) met alle relevante looncomponenten.
    toon_per_maand=True → alle bedragen per maand
    anders toon_per_maand=False → per jaar
    """
    # ✅ Berekeningen ophalen
    netto = bereken_nettoloon(b)
    kost = bereken_loonkost(b, netto)

    rows = []
    label = "maand" if toon_per_maand else "jaar"

    def v(x):
        """Helper om maand- of jaarwaarde te kiezen"""
        return x / 12 if toon_per_maand else x

    # -------------------
    # 1️⃣ Inkomstenzijde
    # -------------------
    rows.append(("INKOMSTEN", ""))

    rows.append(("Brutoloon", v(netto["bruto_jaar"])))
    rows.append(("Sociale werkbonus (A+B)", v(netto["sociale_werkbonus"] * 12)))
    rows.append(("Fiscale werkbonus", v(netto["fiscale_werkbonus"] * 12)))

    # --------------------
    # 2️⃣ Inhoudingen
    # --------------------
    rows.append(("INHOUDINGEN", ""))

    rows.append(("RSZ werknemer", v(netto["rsz_werknemer"])))
    rows.append(("Kostenforfait (info)", v(netto["kostenforfait"])))
    rows.append(("Personenbelasting", v(netto["personenbelasting"])))
    rows.append(("BBSZ", v(netto["bbsz"])))
    rows.append(("Maaltijdcheques (WN, aftrek)", v(b.MG_WN_jaar)))

    rows.append(("NETTO UITBETAALD", v(netto["nettoloon_jaar"])))

    # --------------------
    # 3️⃣ Koopkracht
    # --------------------
    rows.append(("KOOPKRACHT", ""))
    rows.append(("Maaltijdcheques (WG)", v(b.MG_WG_jaar)))
    rows.append(("Ecocheques", v(b.EC_jaar)))
    rows.append(("Kosten eigen aan WG", v(b.maandelijkse_kostenvergoeding * 12)))
    rows.append(("NETTO KOOPKRACHT", v(netto["koopkracht_jaar"])))

    # ------------------------
    # 4️⃣ Werkgeverskost
    # ------------------------
    rows.append(("WERKGEVERSKOST", ""))
    rows.append(("RSZ werkgever", v(kost["rsz_werkgever"])))
    rows.append(("GV werkgever", v(kost["gv_werkgever"])))
    rows.append(("AO verzekering", v(kost["ao_verzekering"])))
    rows.append(("Maaltijdcheques (WG)", v(b.MG_WG_jaar)))
    rows.append(("Ecocheques", v(b.EC_jaar)))
    rows.append(("Kosten eigen aan WG", v(b.maandelijkse_kostenvergoeding * 12)))
    rows.append(("TOTALE LOONKOST", v(kost["totaal_loonkost_jaar"])))

    # ---------------------
    # ✅ DataFrame opmaken
    # ---------------------
    df = pd.DataFrame(rows, columns=["Component", "Bedrag"])

    # Geldopmaak
    def signed_or_not(name, value):
        sign = not (name in ["Brutoloon", "NETTO UITBETAALD", "NETTO KOOPKRACHT", "TOTALE LOONKOST"])
        try:
            return fmt_eur_be(float(value), signed=sign)
        except Exception:
            return value

    df["Bedrag"] = df.apply(lambda r: "" if r["Bedrag"] == "" else signed_or_not(r["Component"], r["Bedrag"]), axis=1)

    # Label in titel
    df_title = f"Overzicht per {label.capitalize()}"
    df.attrs["title"] = df_title

    return df, netto, kost


# -----------------------
# 5️⃣ Export helpers
# -----------------------
def export_to_csv(df, path: str):
    df.to_csv(path, index=False)

def export_to_excel(df, path: str):
    """Exporteert naar Excel indien openpyxl beschikbaar is"""
    try:
        import openpyxl
    except ImportError:
        pass
    df.to_excel(path, index=False)
