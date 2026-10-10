"""
app.py  --  Halaman utama Sistem Informasi Klasifikasi Penutup Lahan Jawa Timur
Jalankan lokal:  streamlit run app.py
"""
import json

import pandas as pd
import streamlit as st

import config as C

st.set_page_config(page_title="LULC Jawa Timur - Sentinel-2A", page_icon="🛰️", layout="wide")

st.title("🛰️ Klasifikasi Penggunaan & Penutup Lahan Jawa Timur")
st.caption("UTS Sistem Informasi Geografis — Analisa Spasial Penggunaan Lahan dan Kebijakan  |  "
           "Citra Sentinel-2A  |  Machine Learning")

st.markdown(
    """
Aplikasi ini menampilkan **seluruh proses** klasifikasi *land use / land cover* (LULC) di Jawa Timur,
mulai dari pemahaman data, pengumpulan sampel, ekstraksi fitur Sentinel-2A, pemodelan, sampai
**peta hasil klasifikasi di atas basemap satelit Google**. Gunakan menu di sebelah kiri untuk berpindah halaman.
"""
)

# ---------------------------------------------------------------- alur proses
st.subheader("Alur proses")
st.graphviz_chart(
    """
digraph G {
  rankdir=LR; node [shape=box, style="rounded,filled", fillcolor="#EAF2F8", fontname="Helvetica"];
  A [label="Sampel GeoJSON\\n6 kelas (poligon)"];
  B [label="Pembersihan &\\nsplit per poligon"];
  C [label="Titik sampel\\nseimbang"];
  D [label="Google Earth Engine\\nComposite Sentinel-2A"];
  E [label="20 fitur\\n(band + indeks + topografi)"];
  F [label="Tabel fitur CSV"];
  G [label="Latih & bandingkan\\n8 model ML"];
  H [label="Model terbaik\\n(joblib)"];
  I [label="Prediksi raster\\nper ROI"];
  J [label="Peta Folium\\n+ Google Satellite"];
  A -> B -> C -> D -> E -> F -> G -> H -> I -> J;
}
""",
    width="stretch",
)

# ---------------------------------------------------------------- ringkasan angka
c1, c2, c3, c4 = st.columns(4)
c1.metric("Jumlah kelas", len(C.CLASSES))
c2.metric("Jumlah fitur", len(C.FEATURE_COLS))
if C.SPLIT_JSON.exists():
    s = json.load(open(C.SPLIT_JSON))
    c3.metric("Data latih", f"{s['n_train']:,}")
    c4.metric("Data uji", f"{s['n_test']:,}")
else:
    c3.metric("Data latih", "-")
    c4.metric("Data uji", "-")

if C.MODEL_META.exists():
    m = json.load(open(C.MODEL_META))
    st.success(f"Model terbaik: **{m['best_model']}** — akurasi uji **{m['accuracy']*100:.2f}%**, "
               f"kappa **{m['kappa']:.3f}**")
else:
    st.info("Hasil pemodelan belum tersedia. Jalankan `scripts/03_train_models.py` terlebih dulu.")

# ---------------------------------------------------------------- legenda kelas
st.subheader("Kelas yang diklasifikasikan")
rows = []
for c in C.CLASSES:
    rows.append({"ID": c["id"], "Kelas": c["name"], "Warna": c["color"], "Deskripsi": c["desc"]})
df = pd.DataFrame(rows)
st.dataframe(
    df.style.map(lambda v: f"background-color:{v};color:{v}", subset=["Warna"]),
    hide_index=True, width="stretch",
)

st.markdown(
    """
**Halaman:**
1. *Data Understanding* — tujuan analisis, acuan klasifikasi lahan Indonesia, kebijakan terkait
2. *Data Collecting* — sumber data, band Sentinel-2A, jumlah data latih/uji
3. *Fitur dan Rumus* — indeks spektral beserta rumusnya
4. *Modeling* — perbandingan model, confusion matrix, feature importance
5. *Peta Klasifikasi* — hasil klasifikasi di atas Google Satellite
"""
)
