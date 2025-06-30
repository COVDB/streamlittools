import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import os
import base64
import requests

# === Constants ===
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
PAGE_WIDTH = 210  # A4 width in mm
MARGIN = 10
IMAGE_WIDTH = 40  # mm (square image)
IMAGE_HEIGHT = 30  # mm
CODE_WIDTH = 30   # mm
DESC_WIDTH = PAGE_WIDTH - 2*MARGIN - IMAGE_WIDTH - CODE_WIDTH - 2
ROW_SPACING = 2   # mm extra spacing after each row

# === Streamlit App ===
st.title("Gereedschappenbeheer (offline)")

# Upload CSV/XLSX met kolommen FotoURL, CS CODE, Description, optioneel Base64
uploaded_file = st.file_uploader(
    "Upload Excel- of CSV-export (met kolommen FotoURL, CS CODE, Description, Base64)",
    type=["xlsx", "csv"]
)

if uploaded_file:
    # Inlezen
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Fout bij inlezen bestand: {e}")
        st.stop()

    # Alleen relevante kolommen
    for col in ["FotoURL", "CS CODE", "DISCRIPTION", "Base64 picture"]:
        if col not in df.columns:
            df[col] = ""
    df = df[["FotoURL", "CS CODE", "DISCRIPTION", "Base64 picture"]]

    st.subheader("Gereedschappenoverzicht (wijzigbaar)")
    df = st.data_editor(df, num_rows="dynamic")

    # PDF-generator functie
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
    pdf.cell(IMAGE_WIDTH, 8, "Foto", border=1, fill=True, align='C')
    pdf.cell(CODE_WIDTH, 8, "CS CODE", border=1, fill=True, align='C')
    pdf.cell(DESC_WIDTH, 8, "Description", border=1, fill=True, align='C')
    pdf.ln()

    # Rows
    for _, row in df.iterrows():
        x0, y0 = MARGIN, pdf.get_y()
        pdf.set_x(x0)

        # Draw image placeholder
        b64 = row.get("Base64", "") or ""
        url = row.get("FotoURL", "") or ""
        # reserve cell
        pdf.rect(x0, y0, IMAGE_WIDTH, IMAGE_HEIGHT)
        if b64:
            try:
                data = b64.split(",")[-1]
                img_bytes = base64.b64decode(data)
                pdf.image(BytesIO(img_bytes), x=x0+1, y=y0+1, w=IMAGE_WIDTH-2)
            except:
                pass
        elif isinstance(url, str) and url.startswith("http"):
            try:
                resp = requests.get(url)
                resp.raise_for_status()
                pdf.image(BytesIO(resp.content), x=x0+1, y=y0+1, w=IMAGE_WIDTH-2)
            except:
                pass

        # CS CODE
        pdf.set_xy(x0 + IMAGE_WIDTH, y0)
        pdf.multi_cell(CODE_WIDTH, 6, str(row.get("CS CODE", "")), border=1)

        # Description
        # align top of description cell to same y0
        pdf.set_xy(x0 + IMAGE_WIDTH + CODE_WIDTH, y0)
        pdf.multi_cell(DESC_WIDTH, 6, str(row.get("Description", "")), border=1)

        # move to next row (max of image height and cell heights)
        row_bottom = max(pdf.get_y(), y0 + IMAGE_HEIGHT)
        pdf.set_y(row_bottom + ROW_SPACING)
        pdf.set_x(x0)

    # Output
    out = pdf.output(dest='S')
    return out if isinstance(out, (bytes, bytearray)) else out.encode('latin-1')

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
