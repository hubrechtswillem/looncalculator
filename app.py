# app.py — BAU Looncalculator (interactieve versie met Plotly)
# --------------------------------------------------------------

import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from payroll.werknemer import Bediende
from payroll.overzicht import maak_overzicht

# 🎨 BAU-stijl
PRIMARY = "#003366"
ACCENT = "#E0B400"
BG = "#F5F7FA"
TEXT = "#333333"

# ⚙️ Pagina-instellingen
st.set_page_config(page_title="BAU Looncalculator", page_icon="💼", layout="wide")

# 💅 CSS
st.markdown(
    f"""
    <style>
        .stApp {{background-color:{BG}; color:{TEXT};}}
        .stButton>button {{
            background-color:{PRIMARY}; color:white; border-radius:6px;
        }}
        h1, h2, h3 {{color:{PRIMARY};}}
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------------------
# 🧮 HOOFDTITEL
# --------------------------------------------------------------
st.title("BAU LOONCALCULATOR")

# --------------------------------------------------------------
# 🧾 ZIJBALK: invoer
# --------------------------------------------------------------
with st.sidebar:
    st.header("Invoer")
    bruto = st.number_input("Bruto maandloon (€)", min_value=0.0, value=3000.0, step=50.0, format="%.2f")
    prestatie = st.slider("Prestatiebreuk (0.2 - 1.0)", 0.2, 1.0, 1.0, 0.1)
    regime = st.selectbox("BBSZ regime", ["individueel", "gemeenschappelijk_met_inkomen", "gemeenschappelijk_zonder_inkomen"])

    # 🍽️ Maaltijdcheques
    st.subheader("Maaltijdcheques")
    MAX_WG_PER_DAG, MIN_WN_PER_DAG, MAX_TOTAAL_PER_DAG = 6.91, 1.09, 8.00
    mc_per_dag_wg = st.number_input("Werkgeversdeel (€)", 0.0, MAX_WG_PER_DAG, 5.91, 0.1)
    mc_per_dag_wn = st.number_input("Werknemersdeel (€)", MIN_WN_PER_DAG, MAX_TOTAAL_PER_DAG - mc_per_dag_wg, 1.09, 0.1)
    vakantie = st.number_input("Vakantiedagen", 0, 50, 20)
    ziekte = st.number_input("Ziektedagen", 0, 60, 5)
    feestdagen = st.number_input("Feestdagen", 0, 15, 10)
    onbetaald = st.number_input("Onbetaald verlof", 0, 60, 0)
    werkdagen = max(0, round((260 - (vakantie + ziekte + feestdagen + onbetaald)) * prestatie, 1))
    st.info(f"{werkdagen} gewerkte dagen per jaar")
    mg_wg, mg_wn = mc_per_dag_wg * werkdagen, mc_per_dag_wn * werkdagen

    # 🌱 Andere voordelen
    st.subheader("Andere voordelen / vergoedingen")
    ec = st.number_input("Ecocheques / jaar", 0.0, 2000.0, 250.0, 10.0)
    kosten_eigen_m = st.number_input("Kosten eigen aan WG / maand", 0.0, 197.83, 150.0, 5.0)
    gv = st.number_input("GV WG (%)", 0.0, 20.0, 5.0, 0.5) / 100.0
    ao = st.number_input("AO verzekering (%)", 0.0, 10.0, 2.0, 0.5) / 100.0

# --------------------------------------------------------------
# 👤 Berekeningen
# --------------------------------------------------------------
b = Bediende(
    bruto_maandloon=bruto,
    prestatiebreuk=prestatie,
    MG_WG_jaar=mg_wg,
    MG_WN_jaar=mg_wn,
    EC_jaar=ec,
    GV_WG_pct=gv,
    AO_pct=ao,
    maandelijkse_kostenvergoeding=kosten_eigen_m,
    regime=regime,
)
toon_maand = True
df, netto, kost = maak_overzicht(b, toon_per_maand=toon_maand)

# --------------------------------------------------------------
# 📋 Overzichtstabel
# --------------------------------------------------------------
st.subheader("Overzicht")
st.dataframe(df, use_container_width=True)

# Toggle weergave
toon_maand_toggle = st.toggle("Toon bedragen per maand", value=toon_maand)
if toon_maand_toggle != toon_maand:
    df, netto, kost = maak_overzicht(b, toon_per_maand=toon_maand_toggle)
    st.experimental_rerun()

st.markdown("---")

# --------------------------------------------------------------
# 🍩 + 📊 GRAFIEKEN — naast elkaar
# --------------------------------------------------------------
st.subheader("Kostenstructuur en koopkracht")

# Maak twee kolommen voor overzicht
col_pie, col_bar = st.columns([1, 1])

# 🍩 PIECHART — werkgeverskost
labels = ["RSZ WG", "groepsverzekering WG", "AO verzek.", "MG WG", "Ecocheques", "Kostenvergoeding thuiswerk"]
values = [
    kost.get("rsz_werkgever", 0),
    kost.get("groepsverzekering_werkgever", 0),
    kost.get("ao_verzekering", 0),
    kost.get("maaltijdcheques_wg", 0),
    kost.get("ecocheques", 0),
    kost.get("kosten_eigen", 0),

]

filtered = [(l, v) for l, v in zip(labels, values) if v > 0]
if filtered:
    labels, values = zip(*filtered)
    with col_pie:
        fig_pie = px.pie(
            names=labels,
            values=values,
            title="Verdeling werkgeverskost",
            color_discrete_sequence=[PRIMARY, "#004C99", "#0066CC", "#E0B400", "#4CAF50", "#999999", "#BDBDBD"],
            hole=0.35,
            height=400,
        )
        fig_pie.update_traces(textinfo="percent+label", pull=[0.03]*len(labels))
        fig_pie.update_layout(margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)
else:
    col_pie.info("💡 Onvoldoende gegevens voor een verdeling van werkgeverskosten.")

# 📊 BAR CHART — Totale loonkost → Bruto → Netto → Koopkracht
with col_bar:
    stappen = ["Loonkost", "Bruto", "Netto", "Koopkracht"]
    waardes = [
        kost["totaal_loonkost_maand"],  # totale werkgeverskost
        netto["bruto_maand"],
        netto["nettoloon_maand"],
        netto["koopkracht_maand"],
    ]

    kleuren = [PRIMARY, "#00509E", ACCENT, "#4CAF50"]

    fig_bar = px.bar(
        x=stappen,
        y=waardes,
        text=[f"€{v:,.0f}" for v in waardes],
        color=stappen,
        color_discrete_sequence=kleuren,
        title="Totale loonkost → Bruto → Netto → Koopkracht",
        height=400,
    )

    # Tekst boven balken en iets smallere breedte
    fig_bar.update_traces(textposition="outside", width=0.45)

    # As en opmaak
    fig_bar.update_layout(
        yaxis_title="€ per maand",
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title=None,
        yaxis=dict(showgrid=True, gridcolor="#E0E0E0"),
    )

    # Extra accentlijn voor visueel contrast (optioneel)
    max_y = max(waardes) * 1.1
    fig_bar.update_yaxes(range=[0, max_y])
    st.plotly_chart(fig_bar, use_container_width=True)


st.markdown("---")

# --------------------------------------------------------------
# 📈 SENSITIVITEITSANALYSE — interactieve evolutie brutoloon
# --------------------------------------------------------------
st.subheader("Evolutie bij wijzigend brutoloon")

col1, col2 = st.columns(2)
with col1:
    range_step = st.number_input("Bereik ± (€)", 200, 3000, 1000, 100)
with col2:
    n_steps = st.slider("Aantal stappen", 3, 15, 7, 1)

bruto_range = np.linspace(bruto - range_step, bruto + range_step, n_steps)
bruto_range = bruto_range[bruto_range > 0]

netto_values, koopkracht_values, kost_values = [], [], []

for b_val in bruto_range:
    b_tmp = Bediende(
        bruto_maandloon=b_val,
        prestatiebreuk=prestatie,
        MG_WG_jaar=mg_wg,
        MG_WN_jaar=mg_wn,
        EC_jaar=ec,
        GV_WG_pct=gv,
        AO_pct=ao,
        maandelijkse_kostenvergoeding=kosten_eigen_m,
        regime=regime,
    )
    _, netto_tmp, kost_tmp = maak_overzicht(b_tmp, toon_per_maand=True)
    netto_values.append(netto_tmp["nettoloon_maand"])
    koopkracht_values.append(netto_tmp["koopkracht_maand"])
    kost_values.append(kost_tmp["totaal_loonkost_maand"])

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=bruto_range, y=netto_values, mode="lines+markers", name="Netto loon", line=dict(color="#1f77b4", width=3)))
fig3.add_trace(go.Scatter(x=bruto_range, y=koopkracht_values, mode="lines+markers", name="Koopkracht", line=dict(color="#2ca02c", width=3, dash="dash")))
fig3.add_trace(go.Scatter(x=bruto_range, y=kost_values, mode="lines+markers", name="Loonkost werkgever", line=dict(color="#ff7f0e", width=3, dash="dot")))
fig3.update_layout(
    title="Evolutie van netto, koopkracht en werkgeverskost bij variatie van brutoloon",
    xaxis_title="Bruto maandloon (€)",
    yaxis_title="€ per maand",
    template="simple_white",
    hovermode="x unified",
)
st.plotly_chart(fig3, use_container_width=True)

# --------------------------------------------------------------
# 📄 PDF RAPPORT EXPORT (inclusief volledige tabel en sectiekoppen)
# --------------------------------------------------------------
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from datetime import datetime

st.markdown("---")
st.subheader("📄 Rapport export")

beschrijving = st.text_area(
    "Voeg optioneel een beschrijving of context toe aan het rapport:",
    placeholder="Bijvoorbeeld: Analyse van de loonkost voor een nieuwe medewerker in functie X...",
    height=120,
)

if st.button("💾 Download rapport (PDF)"):
    buffer = BytesIO()

    # PDF-document setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    elements = []  # ✅ HIER wordt elements aangemaakt

    # 🏷️ Titel
    title_style = styles["Title"]
    title_style.textColor = colors.HexColor("#003366")
    elements.append(Paragraph("BAU Looncalculator — Rapport", title_style))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(Paragraph(f"<i>Gegenereerd op {datetime.now():%d/%m/%Y}</i>", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * cm))

    # 📋 Beschrijving
    if beschrijving.strip():
        elements.append(Paragraph("<b>Beschrijving</b>", styles["Heading3"]))
        elements.append(Paragraph(beschrijving.replace("\n", "<br/>"), styles["Normal"]))
        elements.append(Spacer(1, 0.5 * cm))

    # 🧾 Samenvatting
    summary = [
        ["Bruto maandloon", f"€ {netto['bruto_maand']:.2f}"],
        ["Netto maandloon", f"€ {netto['nettoloon_maand']:.2f}"],
        ["Netto koopkracht", f"€ {netto['koopkracht_maand']:.2f}"],
        ["Totale werkgeverskost", f"€ {kost['totaal_loonkost_maand']:.2f}"],
        ["Structurele vermindering", f"€ {kost.get('structurele_vermindering', 0):.2f} per jaar"],
    ]
    t_summary = Table(summary, colWidths=[8*cm, 6*cm])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    elements.append(Paragraph("<b>Samenvatting</b>", styles["Heading3"]))
    elements.append(t_summary)
    elements.append(Spacer(1, 0.7 * cm))

    # 📊 Tabel met loonoverzicht
    elements.append(Paragraph("<b>Volledig loonoverzicht</b>", styles["Heading3"]))

    # Zet DataFrame om in tabeldata
    data = [df.columns.tolist()] + df.values.tolist()

    # Detecteer sectiekoppen zoals 'INKOMSTEN', 'INHOUDINGEN', 'KOOPKRACHT', 'WERKGEVERSKOST'
    header_rows = []
    for i, row in enumerate(df["Component"].tolist(), start=1):
        if isinstance(row, str) and row.isupper() and row.strip() != "":
            header_rows.append(i)

    # Maak de tabel
    table = Table(data, repeatRows=1, colWidths=[7*cm, 7*cm])

    # Basisstijl
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]

    # Extra opmaak voor sectiekoppen
    for r in header_rows:
        table_style += [
            ('BACKGROUND', (0, r), (-1, r), colors.HexColor("#DDE5F2")),
            ('TEXTCOLOR', (0, r), (-1, r), colors.HexColor("#003366")),
            ('FONTNAME', (0, r), (-1, r), 'Helvetica-Bold'),
            ('FONTSIZE', (0, r), (-1, r), 10),
            ('ALIGN', (0, r), (-1, r), 'LEFT'),
            ('LINEABOVE', (0, r), (-1, r), 0.75, colors.HexColor("#003366")),
            ('TOPPADDING', (0, r), (-1, r), 4),
        ]

    table.setStyle(TableStyle(table_style))
    elements.append(table)

    # Footer
    elements.append(Spacer(1, 0.7 * cm))
    elements.append(Paragraph(
        "<i>Gegenereerd met BAU Looncalculator — dit rapport is informatief en niet bindend.</i>",
        styles["Normal"],
    ))

    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()

    st.download_button(
        label="📥 Download PDF",
        data=pdf_data,
        file_name="BAU_loonrapport.pdf",
        mime="application/pdf",
    )
