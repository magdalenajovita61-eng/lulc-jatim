import json

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

import config as C

st.set_page_config(page_title="Peta Klasifikasi", page_icon="🗺️", layout="wide")
st.title("🗺️ Peta Hasil Klasifikasi")
st.caption("Basemap: Google Satellite (tile XYZ) • Overlay: hasil klasifikasi model terbaik")

GOOGLE_SAT = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
GOOGLE_HYB = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"

meta = json.load(open(C.ROI_META_JSON)) if C.ROI_META_JSON.exists() else {}
if not meta:
    st.warning("Belum ada hasil prediksi ROI. Jalankan `python scripts/04_predict_roi.py` "
               "setelah mengunduh stack GeoTIFF dari GEE ke `data/roi/`. "
               "Di bawah ini hanya ditampilkan basemap dan kotak ROI.")

# ------------------------------------------------------------------ kontrol
col1, col2 = st.columns([2, 1])
options = ["Semua ROI"] + [k for k in C.ROIS]
choice = col1.selectbox("Pilih wilayah (ROI)", options,
                        format_func=lambda k: k if k == "Semua ROI" else C.ROIS[k]["label"])
opacity = col2.slider("Transparansi overlay", 0.1, 1.0, 0.65, 0.05)


def add_legend(m):
    items = "".join(
        f"<div style='margin:2px 0'><span style='display:inline-block;width:14px;height:14px;"
        f"background:{c['color']};margin-right:6px;border:1px solid #333'></span>{c['name']}</div>"
        for c in C.CLASSES)
    html = (f"<div style='position:fixed;bottom:30px;left:30px;z-index:9999;background:white;"
            f"padding:10px 12px;border:1px solid #888;border-radius:6px;font-size:13px;"
            f"box-shadow:0 1px 4px rgba(0,0,0,.4)'><b>Legenda</b>{items}</div>")
    m.get_root().html.add_child(folium.Element(html))


def build_map(selected):
    keys = list(C.ROIS) if selected == "Semua ROI" else [selected]
    if selected == "Semua ROI":
        center, zoom = [-7.75, 112.75], 8
    else:
        w, s, e, n = C.ROIS[selected]["bbox"]
        center, zoom = [(s + n) / 2, (w + e) / 2], 12
    m = folium.Map(location=center, zoom_start=zoom, control_scale=True, tiles=None)
    folium.TileLayer(GOOGLE_SAT, attr="Google Satellite", name="Google Satellite",
                     overlay=False, max_zoom=20).add_to(m)
    folium.TileLayer(GOOGLE_HYB, attr="Google Hybrid", name="Google Hybrid (+label)",
                     overlay=False, max_zoom=20).add_to(m)
    for k in keys:
        if k in meta:
            mi = meta[k]
            folium.raster_layers.ImageOverlay(
                image=str(C.ROI_DIR / mi["png"]), bounds=mi["bounds"], opacity=opacity,
                name=f"Klasifikasi - {mi['label']}", interactive=False, zindex=5).add_to(m)
        else:
            w, s, e, n = C.ROIS[k]["bbox"]
            folium.Rectangle([[s, w], [n, e]], color="#FFFFFF", weight=2, fill=False,
                             tooltip=C.ROIS[k]["label"] + " (belum diprediksi)").add_to(m)
    add_legend(m)
    folium.LayerControl(collapsed=False).add_to(m)
    return m


st_folium(build_map(choice), height=620, use_container_width=True, returned_objects=[])

# ------------------------------------------------------------------ luas
st.header("Luas per kelas (hektar)")
rows = []
for k, mi in meta.items():
    if choice != "Semua ROI" and k != choice:
        continue
    for r in mi["area"]:
        rows.append(dict(ROI=mi["label"], Kelas=r["kelas"], class_id=r["class_id"],
                         Luas_ha=r["luas_ha"], Persen=r["persen"]))
if rows:
    df = pd.DataFrame(rows)
    pivot = df.pivot_table(index="Kelas", columns="ROI", values="Luas_ha", aggfunc="sum")
    pivot["Total"] = pivot.sum(axis=1)
    order = [C.CLASS_NAMES[i] for i in sorted(C.CLASS_NAMES)]
    pivot = pivot.reindex(order).round(2)
    st.dataframe(pivot, width="stretch")
    fig = px.bar(df, x="Kelas", y="Luas_ha", color="ROI", barmode="group",
                 labels={"Luas_ha": "Luas (ha)"}, category_orders={"Kelas": order})
    st.plotly_chart(fig, width="stretch")
    first = next(iter(meta.values()))
    st.caption(f"Model: **{first['model']}**. Luas dihitung dari jumlah piksel × luas piksel (10 m × 10 m = 0,01 ha).")
else:
    st.info("Tabel luas akan muncul setelah prediksi ROI dijalankan.")
