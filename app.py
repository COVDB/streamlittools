import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import os
import base64
import requests

# === Constants ===
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
PAGE_WIDTH = 210
MARGIN = 10
IMAGE_WIDTH = 40
IMAGE_HEIGHT = 30
CODE_WIDTH = 30
DESC_WIDTH = PAGE_WIDTH - 2*MARGIN - IMAGE_WIDTH - CODE_WIDTH - 2
ROW_SPACING = 2

# === Streamlit App ===
st.title("Gereedschappenbeheer (offline)")

uploaded_file = st.file_uploader(
    "Upload Excel- of CSV-export (met kolommen FotoURL, CS CODE, Description, Base64)",
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

    # Zorg dat kolommen bestaan
    for col in ["FotoURL", "CS CODE", "Description", "Base64"]:
        if col not in df.columns:
            df[col] = ""
    df = df[["FotoURL", "CS CODE", "Description", "Base64"]]

    st.subheader("Gereedschappenoverzicht (wijzigbaar)")
    df = st.data_editor(df, num_rows="dynamic")

    # Voorbeeld preview van eerste afbeelding
    st.subheader("Voorbeeld afbeelding preview")
    sample = df.iloc[0]
    if sample.get("Base64"):
        st.image(sample.get("Base64"), width=150, caption="Base64 preview")
    elif isinstance(sample.get("FotoURL"), str) and sample.get("FotoURL").startswith("http"):
        st.image(sample.get("FotoURL"), width=150, caption="URL preview")
    else:
        st.write("Geen geldige afbeelding in eerste rij om te previewen.")

    # PDF-generator functie
def create_pdf(df: pd.DataFrame) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Font
    if os.path.isfile(FONT_PATH):
        pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
        pdf.set_font("DejaVu", size=10)
    else:
        pdf.set_font("Arial", size=10)

    # Header\ n    pdf.set_fill_color(200,200,200)
    pdf.cell(IMAGE_WIDTH, 8, "Foto", border=1, fill=True, align='C')
    pdf.cell(CODE_WIDTH, 8, "CS CODE", border=1, fill=True, align='C')
    pdf.cell(DESC_WIDTH, 8, "Description", border=1, fill=True, align='C')
    pdf.ln()

    for _, row in df.iterrows():
        x0, y0 = MARGIN, pdf.get_y()
        pdf.set_x(x0)
        # placeholder rect
        pdf.rect(x0, y0, IMAGE_WIDTH, IMAGE_HEIGHT)
        # Base64 of URL
        b64 = row.get("Base64", "") or ""
        url = row.get("FotoURL", "") or ""
        if b64:
            raw = b64.split(",",1)[-1]
            clean = "".join(raw.split())
            try:
                img_bytes = base64.b64decode(clean)
                pdf.image(BytesIO(img_bytes), x=x0+1, y=y0+1, w=IMAGE_WIDTH-2)
            except Exception as e:
                # mark invalid
                pdf.cell(IMAGE_WIDTH, IMAGE_HEIGHT, "[Invalid Base64]", border=1, ln=0)
        elif url.startswith("http"):
            try:
                resp = requests.get(url)
                resp.raise_for_status()
                pdf.image(BytesIO(resp.content), x=x0+1, y=y0+1, w=IMAGE_WIDTH-2)
            except Exception:
                pdf.cell(IMAGE_WIDTH, IMAGE_HEIGHT, "[URL fout]", border=1, ln=0)
        # CS CODE
        pdf.set_xy(x0+IMAGE_WIDTH, y0)
        pdf.multi_cell(CODE_WIDTH, 6, str(row.get("CS CODE", "")), border=1)
        # Description
        pdf.set_xy(x0+IMAGE_WIDTH+CODE_WIDTH, y0)
        pdf.multi_cell(DESC_WIDTH, 6, str(row.get("Description", "")), border=1)
        # nieuwe y
        bottom = max(pdf.get_y(), y0+IMAGE_HEIGHT)
        pdf.set_xy(MARGIN, bottom+ROW_SPACING)

    out = pdf.output(dest='S')
    return out if isinstance(out,(bytes,bytearray)) else out.encode('latin-1')

if st.button("Genereer PDF"):
    pdf_bytes = create_pdf(df)
    st.download_button("Download PDF", data=pdf_bytes, file_name="gereedschappen.pdf", mime="application/pdf")
else:
    st.info("Bewerk de lijst en klik op 'Genereer PDF' wanneer je klaar bent.")
