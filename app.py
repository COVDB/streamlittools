import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import os

# === Constants ===
# Zorg dat het lettertypebestand "DejaVuSans.ttf" in de repo staat (bijv. in map "fonts/").
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")

# === Streamlit App ===
st.title("Gereedschappenbeheer (offline)")

# Upload sectie
uploaded_file = st.file_uploader(
    label="Upload Excel- of CSV-export van je SharePoint-lijst",
    type=["xlsx", "csv"]
)

if uploaded_file:
    # Bestand inlezen
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Fout bij inlezen bestand: {e}")
        st.stop()

    # Toon DataFrame
    st.subheader("Ingelezen Gereedschappen")
    st.dataframe(df)

# Functie voor PDF-generatie
def create_pdf(df: pd.DataFrame) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Unicode font registreren
    if os.path.isfile(FONT_PATH):
        pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
        pdf.set_font("DejaVu", size=12)
    else:
        pdf.set_font("Arial", size=12)

    # Titel
    pdf.cell(0, 10, txt="Gereedschappenoverzicht", ln=True, align="C")
    pdf.ln(5)

    # Header
    for col in df.columns:
        pdf.cell(60, 10, str(col), border=1)
    pdf.ln()

    # Rijen
    for _, row in df.iterrows():
        for col in df.columns:
            text = str(row[col])
            pdf.multi_cell(60, 10, text, border=1)
        pdf.ln()

    # Genereer PDF als string
    pdf_str = pdf.output(dest='S')
    # PDF_output is bytes in FPDF2 when dest='S'
    return pdf_str if isinstance(pdf_str, (bytes, bytearray)) else pdf_str.encode('latin-1')

# PDF Download sectie
if uploaded_file and st.button("Genereer PDF"):
    pdf_bytes = create_pdf(df)
    st.download_button(
        label="Download PDF",
        data=pdf_bytes,
        file_name="gereedschappen.pdf",
        mime="application/pdf"
    )
else:
    if not uploaded_file:
        st.info("Upload eerst je geëxporteerde lijst om verder te gaan.")
