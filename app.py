import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF

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
        pdf.set_font("Arial", size=12)

        # Titel
        pdf.cell(0, 10, txt="Gereedschappenoverzicht", ln=True, align='C')
        pdf.ln(5)

        # Header
        for col in df.columns:
            pdf.cell(60, 10, str(col), border=1)
        pdf.ln()

        # Rijen
        for _, row in df.iterrows():
            for col in df.columns:
                pdf.cell(60, 10, str(row[col]), border=1)
            pdf.ln()

        buffer = BytesIO()
        pdf.output(buffer)
        return buffer.getvalue()

    # PDF Download
    if st.button("Genereer PDF"):
        pdf_bytes = create_pdf(df)
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name="gereedschappen.pdf",
            mime="application/pdf"
        )
else:
    st.info("Upload eerst je geëxporteerde lijst om verder te gaan.")
