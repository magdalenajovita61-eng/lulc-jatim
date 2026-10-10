import json

import folium
import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

import config as C

st.set_page_config(page_title="Data Collecting", page_icon="🗂️", layout="wide")
st.title("🗂️ Data Collecting")

# ------------------------------------------------------------------ sumber
st.header("1. Sumber data")
st.markdown(
    f"""
| Item | Keterangan |
|---|---|
| Citra | **Sentinel-2A MSI Level-2A** (reflektansi permukaan), koleksi GEE `{C.S2_COLLECTION}` |
| Platform | Google Earth Engine |
| Periode | {C.DATE_START} s.d. {C.DATE_END} |
| Filter awan | `CLOUDY_PIXEL_PERCENTAGE < {C.MAX_CLOUD}` + mask awan/bayangan/cirrus dengan band SCL |
| Komposit | **Median** seluruh citra pada periode (menekan awan & noise) |
| Wilayah | Provinsi **Jawa Timur** (FAO GAUL level-1) |
| Resolusi | {C.SCALE} m |
| Data tambahan | SRTM 30 m (`USGS/SRTMGL1_003`) untuk elevasi & kemiringan lereng |
| Sampel | Poligon digitasi manual 6 kelas (GeoJSON), diambil titik acak di dalamnya |
"""
)

# ------------------------------------------------------------------ band
st.header("2. Band Sentinel-2A")
bt = pd.DataFrame(
    C.BAND_TABLE,
    columns=["Band", "Nama", "Panjang gelombang tengah (nm)", "Bandwidth (nm)",
             "Resolusi (m)", "Dipakai", "Kegunaan"],
)
bt["Dipakai"] = bt["Dipakai"].map({True: "✅ Ya", False: "—"})
st.dataframe(bt, hide_index=True, width="stretch")
st.caption(f"{len(C.S2_BANDS)} band dipakai: {', '.join(C.S2_BANDS)}. B1, B9, B10 tidak dipakai "
           "(resolusi 60 m dan terkait atmosfer/awan).")

# ------------------------------------------------------------------ jumlah data
st.header("3. Jumlah data, kelas, training & testing")
if C.SPLIT_JSON.exists():
    s = json.load(open(C.SPLIT_JSON))
    a, b, c, d, e = st.columns(5)
    a.metric("Total data", f"{s['n_total']:,}")
    b.metric("Data training", f"{s['n_train']:,}")
    c.metric("Data testing", f"{s['n_test']:,}")
    d.metric("Jumlah kelas", s["n_classes"])
    e.metric("Jumlah fitur", s["n_features"])
    st.caption(f"Metode pembagian: **{s['mode']}** "
               + ("(split per poligon sehingga data uji tidak berdekatan dengan data latih)"
                  if s["mode"] == "polygon" else "(stratified random per titik)"))
    pc = pd.DataFrame(s["per_class"]).T.reset_index().rename(columns={"index": "Kelas"})
    pc["Total"] = pc["train"] + pc["test"]
    st.dataframe(pc.rename(columns={"train": "Training", "test": "Testing"}),
                 hide_index=True, width="stretch")
    long = pc.melt(id_vars="Kelas", value_vars=["train", "test"], var_name="Split", value_name="Jumlah")
    fig = px.bar(long, x="Kelas", y="Jumlah", color="Split", barmode="group",
                 color_discrete_map={"train": "#2E86C1", "test": "#E67E22"})
    st.plotly_chart(fig, width="stretch")
else:
    st.info("Belum ada `data/split_summary.json`. Jalankan `scripts/03_train_models.py`.")

if C.SAMPLES_POLY.exists():
    gp = gpd.read_file(C.SAMPLES_POLY)
    st.subheader("Ringkasan poligon sampel")
    summ = (gp.groupby(["class_id", "class_name"])
              .agg(Jumlah_poligon=("poly_id", "count"), Luas_ha=("luas_ha", "sum"))
              .round(1).reset_index().rename(columns={"class_id": "ID", "class_name": "Kelas"}))
    st.dataframe(summ, hide_index=True, width="stretch")

if C.DATASET_CSV.exists():
    with st.expander("Lihat contoh tabel fitur (dataset_fitur.csv)"):
        df = pd.read_csv(C.DATASET_CSV)
        st.write(f"{df.shape[0]:,} baris × {df.shape[1]} kolom")
        st.dataframe(df.head(50), width="stretch")
        st.dataframe(df[C.FEATURE_COLS].describe().T.round(4), width="stretch")

# ------------------------------------------------------------------ peta sampel
st.header("4. Sebaran poligon sampel (Google Satellite)")
if C.SAMPLES_POLY.exists():
    gp = gpd.read_file(C.SAMPLES_POLY)
    m = folium.Map(location=[-7.75, 112.75], zoom_start=8, control_scale=True)
    folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                     attr="Google Satellite", name="Google Satellite").add_to(m)
    for cid, name in C.CLASS_NAMES.items():
        sub = gp[gp.class_id == cid]
        folium.GeoJson(
            sub[["class_name", "split", "luas_ha", "geometry"]].to_json(),
            name=f"{cid}. {name}",
            style_function=lambda f, col=C.CLASS_COLORS[cid]: dict(color=col, weight=2, fillColor=col,
                                                                    fillOpacity=0.35),
            tooltip=folium.GeoJsonTooltip(fields=["class_name", "split", "luas_ha"],
                                          aliases=["Kelas", "Split", "Luas (ha)"]),
        ).add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    st_folium(m, height=560, use_container_width=True, returned_objects=[])
else:
    st.info("`data/samples_all.geojson` belum ada.")
