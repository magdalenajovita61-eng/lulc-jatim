import json

import pandas as pd
import plotly.express as px
import streamlit as st

import config as C

st.set_page_config(page_title="Modeling", page_icon="🤖", layout="wide")
st.title("🤖 Modeling")

st.markdown(
    """
Delapan algoritma dibandingkan pada data latih/uji yang sama: **Random Forest** (baseline), Extra Trees,
**SVM (RBF)**, KNN, Gradient Boosting, **XGBoost**, **LightGBM**, dan MLP (neural network).
Fitur untuk SVM, KNN, dan MLP distandarisasi (`StandardScaler`). Cross-validation 5-fold dilakukan
berbasis poligon agar tidak ada kebocoran spasial. Model dengan **akurasi uji tertinggi** dipilih untuk prediksi peta.
"""
)

if not C.RESULTS_CSV.exists():
    st.warning("Hasil pemodelan belum ada. Jalankan `python scripts/03_train_models.py`.")
    st.stop()

res = pd.read_csv(C.RESULTS_CSV)
meta = json.load(open(C.MODEL_META)) if C.MODEL_META.exists() else {}

if meta:
    st.success(f"🏆 Model terbaik: **{meta['best_model']}** — akurasi uji **{meta['accuracy']*100:.2f}%**, "
               f"kappa **{meta['kappa']:.4f}** (split: {meta.get('split_mode', '-')})")

st.header("1. Perbandingan model")
show = res.copy()
for col in ["accuracy", "kappa", "f1_macro", "cv_mean", "cv_std"]:
    show[col] = show[col].round(4)
show["waktu_detik"] = show["waktu_detik"].round(1)
st.dataframe(
    show.rename(columns={"model": "Model", "accuracy": "Akurasi uji", "kappa": "Kappa",
                         "f1_macro": "F1-macro", "cv_mean": "CV rata-rata",
                         "cv_std": "CV std", "waktu_detik": "Waktu (s)"}),
    hide_index=True, width="stretch",
)
fig = px.bar(res.sort_values("accuracy"), x="accuracy", y="model", orientation="h",
             text=res.sort_values("accuracy")["accuracy"].map(lambda v: f"{v*100:.2f}%"),
             labels={"accuracy": "Akurasi uji", "model": ""})
fig.update_traces(marker_color="#2E86C1", textposition="outside")
fig.update_xaxes(range=[max(0, res.accuracy.min() - 0.05), 1.02])
st.plotly_chart(fig, width="stretch")

st.header("2. Confusion matrix (model terbaik, data uji)")
if C.CONFMAT_CSV.exists():
    cm = pd.read_csv(C.CONFMAT_CSV, index_col=0)
    norm = st.toggle("Tampilkan dalam persen per baris (recall)", value=False)
    z = cm.div(cm.sum(axis=1), axis=0) * 100 if norm else cm
    fig = px.imshow(z, text_auto=".1f" if norm else True, color_continuous_scale="Blues",
                    labels=dict(x="Prediksi", y="Aktual", color="%" if norm else "Jumlah"), aspect="auto")
    st.plotly_chart(fig, width="stretch")

st.header("3. Precision, recall, F1 per kelas")
if C.REPORT_CSV.exists():
    rep = pd.read_csv(C.REPORT_CSV, index_col=0).round(4)
    st.dataframe(rep.rename(columns={"precision": "Precision", "recall": "Recall",
                                     "f1-score": "F1-score", "support": "Support"}),
                 width="stretch")

st.header("4. Feature importance")
if C.IMPORTANCE_CSV.exists():
    imp = pd.read_csv(C.IMPORTANCE_CSV)
    st.caption(f"Metode: {imp['metode'].iloc[0]}")
    fig = px.bar(imp.sort_values("importance"), x="importance", y="fitur", orientation="h",
                 labels={"importance": "Kepentingan relatif", "fitur": ""})
    fig.update_traces(marker_color="#27AE60")
    fig.update_layout(height=620)
    st.plotly_chart(fig, width="stretch")
