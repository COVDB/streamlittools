import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import os

# === Constants ===
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
PAGE_WIDTH = 210  # A4 width in mm
MARGIN = 10
IMAGE_WIDTH = 40  # mm
IMAGE_HEIGHT = 30  # mm
CODE_WIDTH = 30   # mm
DESC_WIDTH = PAGE_WIDTH - 2*MARGIN - IMAGE_WIDTH - CODE_WIDTH - 2
ROW_SPACING = 2   # mm extra spacing after each row

st.title("Gereedschappenbeheer (offline)")

# Upload CSV/XLSX met kolommen CS CODE, DISCRIPTION (schrijffout in SharePoint)
uploaded_file = st.file_uploader(
    "Upload Excel- of CSV-export (met kolommen CS CODE, DISCRIPTION)",
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

    # Vervang kolomnaam 'DISCRIPTION' door 'Description' in code
    if 'DISCRIPTION' in df.columns:
        df.rename(columns={'DISCRIPTION': 'Description'}, inplace=True)
    # Zorg dat beide kolommen bestaan
    for col in ['CS CODE', 'Description']:
        if col not in df.columns:
            df[col] = ''
    df = df[['CS CODE', 'Description']]
    df.reset_index(drop=True, inplace=True)

    st.subheader("Gereedschappenoverzicht (handmatige upload afbeeldingen)")
    st.dataframe(df)

    # Upload per rij
    st.write("### Upload per gereedschap een afbeelding (.jpg/.png)")
    image_files = []
    for idx, row in df.iterrows():
        label = f"Afbeelding voor {row['CS CODE'] or 'rij ' + str(idx)}"
        img = st.file_uploader(label, type=["jpg", "jpeg", "png"], key=f"img_{idx}")
        image_files.append(img)
    df['ImageFile'] = image_files

    # PDF-generator functie
def create_pdf(df: pd.DataFrame) -> bytes:
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Font setup
    if os.path.isfile(FONT_PATH):
        pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
        pdf.set_font('DejaVu', size=10)
    else:
        pdf.set_font('Arial', size=10)

    # Header row
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(IMAGE_WIDTH, 8, 'Foto', border=1, fill=True, align='C')
    pdf.cell(CODE_WIDTH, 8, 'CS CODE', border=1, fill=True, align='C')
    pdf.cell(DESC_WIDTH, 8, 'Description', border=1, fill=True, align='C')
    pdf.ln()

    threshold = pdf.h - pdf.b_margin

    # Rows
    for _, row in df.iterrows():
        y0 = pdf.get_y()
        if y0 + IMAGE_HEIGHT + ROW_SPACING > threshold:
            pdf.add_page()
            y0 = pdf.get_y()
        x0 = MARGIN
        pdf.set_xy(x0, y0)

        # Afbeelding
        pdf.rect(x0, y0, IMAGE_WIDTH, IMAGE_HEIGHT)
        img_file = row['ImageFile']
        if img_file is not None:
            try:
                img_data = img_file.read()
                pdf.image(BytesIO(img_data), x=x0+1, y=y0+1, w=IMAGE_WIDTH-2)
            except Exception:
                pdf.cell(IMAGE_WIDTH, IMAGE_HEIGHT, '[Afbeelding fout]', border=1, ln=0)

        # CS CODE
        pdf.set_xy(x0 + IMAGE_WIDTH, y0)
        pdf.multi_cell(CODE_WIDTH, 6, str(row['CS CODE']), border=1)

        # Description
        pdf.set_xy(x0 + IMAGE_WIDTH + CODE_WIDTH, y0)
        pdf.multi_cell(DESC_WIDTH, 6, str(row['Description']), border=1)

        # Cursor naar onderkant rij
        new_y = pdf.get_y()
        bottom = max(y0 + IMAGE_HEIGHT, new_y)
        pdf.set_xy(MARGIN, bottom + ROW_SPACING)

    return pdf.output(dest='S')

if st.button('Genereer PDF'):
    pdf_bytes = create_pdf(df)
    st.download_button(
        label='Download PDF',
        data=pdf_bytes,
        file_name='gereedschappen.pdf',
        mime='application/pdf'
    )
else:
    if not uploaded_file:
        st.info('Upload eerst je geëxporteerde lijst om verder te gaan.')
