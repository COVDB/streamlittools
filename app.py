import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import os
import base64

# === Constants ===
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
PAGE_WIDTH = 210  # A4 width in mm
MARGIN = 10
IMAGE_WIDTH = 40  # mm
CODE_WIDTH = 30   # mm
DESC_WIDTH = PAGE_WIDTH - 2*MARGIN - IMAGE_WIDTH - CODE_WIDTH - 2

# === Streamlit App ===
st.title("Gereedschappenbeheer (offline)")

uploaded_file = st.file_uploader(
    "Upload Excel- of CSV-export (met kolommen Image, CS CODE, Description)",
    type=["xlsx", "csv"]
)

if uploaded_file:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Fout bij inlezen bestand: {e}")
        st.stop()

    # Enkel relevante kolommen
    cols = [c for c in ["Base64 picture", "CS CODE", "DISCRIPTION"] if c in df.columns]
    df = df[cols]

    st.subheader("Gereedschappenoverzicht")
    st.dataframe(df)

    # Functie voor PDF-generatie
def create_pdf(df: pd.DataFrame) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Font setup
    if os.path.isfile(FONT_PATH):
        pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
        pdf.set_font("DejaVu", size=10)
    else:
        pdf.set_font("Arial", size=10)

    # Header row
    pdf.set_fill_color(200,200,200)
    pdf.cell(IMAGE_WIDTH, 8, "Image", border=1, fill=True)
    pdf.cell(CODE_WIDTH, 8, "CS CODE", border=1, fill=True)
    pdf.cell(DESC_WIDTH, 8, "Description", border=1, fill=True)
    pdf.ln()

    # Rows
    for _, row in df.iterrows():
        x_before = pdf.get_x()
        y_before = pdf.get_y()

        # Image
        img_data = row.get("Base64 picture", "")
        if img_data:
            try:
                b64 = img_data.split(',')[-1]
                img_bytes = base64.b64decode(b64)
                img_buf = BytesIO(img_bytes)
                pdf.image(img_buf, x=x_before, y=y_before, w=IMAGE_WIDTH)
            except Exception:
                pdf.cell(IMAGE_WIDTH, 30, "[Invalid image]", border=1)
        else:
            pdf.cell(IMAGE_WIDTH, 30, "", border=1)

        # CS CODE
        pdf.set_xy(x_before + IMAGE_WIDTH, y_before)
        pdf.multi_cell(CODE_WIDTH, 10, str(row.get("CS CODE", "")), border=1)

        # Description
        pdf.set_xy(x_before + IMAGE_WIDTH + CODE_WIDTH, y_before)
        pdf.multi_cell(DESC_WIDTH, 10, str(row.get("DISCRIPTION", "")), border=1)

        # Move cursor to end of row
        new_y = pdf.get_y()
        pdf.set_xy(MARGIN, new_y)

    # Output PDF
    pdf_str = pdf.output(dest='S')
    return pdf_str if isinstance(pdf_str, (bytes, bytearray)) else pdf_str.encode('latin-1')

    # Download knop
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
