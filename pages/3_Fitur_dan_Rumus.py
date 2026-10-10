import pandas as pd
import plotly.express as px
import streamlit as st

import config as C

st.set_page_config(page_title="Fitur dan Rumus", page_icon="🧮", layout="wide")
st.title("🧮 Fitur dan Rumus")
st.markdown(
    f"Model memakai **{len(C.FEATURE_COLS)} fitur**: {len(C.S2_BANDS)} band reflektansi Sentinel-2A, "
    f"{len(C.INDEX_TABLE)} indeks spektral turunan, dan {len(C.TOPO_TABLE)} fitur topografi."
)

st.header("1. Band reflektansi (10)")
st.markdown(
    "Nilai DN produk L2A dibagi **10000** sehingga menjadi reflektansi permukaan (0–1). "
    "Penjelasan tiap band ada di halaman *Data Collecting*."
)
used = [b for b in C.BAND_TABLE if b[5]]
st.dataframe(pd.DataFrame(used, columns=["Band", "Nama", "λ tengah (nm)", "Bandwidth (nm)",
                                         "Resolusi (m)", "Dipakai", "Kegunaan"])
             .drop(columns="Dipakai"), hide_index=True, width="stretch")

st.header("2. Indeks spektral (8)")
for it in C.INDEX_TABLE:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"**{it['name']}**  \n{it['fungsi']}")
    with c2:
        st.latex(it["latex"])
        st.code(it["formula"], language=None)
    st.divider()

st.info("Keterangan: B2 = Blue, B3 = Green, B4 = Red, B8 = NIR, B11 = SWIR-1 (semua dalam reflektansi). "
        "Pada SAVI, L = 0,5 (faktor koreksi tanah). CMRI = NDVI − NDWI.")

st.header("3. Fitur topografi (2)")
st.dataframe(pd.DataFrame(C.TOPO_TABLE)[["name", "formula", "fungsi"]]
             .rename(columns={"name": "Fitur", "formula": "Sumber / rumus", "fungsi": "Fungsi"}),
             hide_index=True, width="stretch")

st.header("4. Daftar lengkap urutan fitur")
fl = pd.DataFrame({"No": range(1, len(C.FEATURE_COLS) + 1), "Fitur": C.FEATURE_COLS})
fl["Kelompok"] = ["Band"] * len(C.S2_BANDS) + ["Indeks"] * len(C.INDEX_NAMES) + ["Topografi"] * len(C.TOPO_NAMES)
st.dataframe(fl, hide_index=True, width="stretch")

if C.DATASET_CSV.exists():
    st.header("5. Perilaku fitur per kelas")
    df = pd.read_csv(C.DATASET_CSV)
    feat = st.selectbox("Pilih fitur", C.FEATURE_COLS, index=C.FEATURE_COLS.index("NDVI"))
    fig = px.box(df, x="class_name", y=feat, color="class_name",
                 color_discrete_map={C.CLASS_NAMES[i]: c for i, c in C.CLASS_COLORS.items()},
                 labels={"class_name": "Kelas"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")
    st.caption("Boxplot memperlihatkan seberapa baik fitur membedakan antar kelas.")
