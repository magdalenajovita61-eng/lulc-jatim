import pandas as pd
import streamlit as st

import config as C

st.set_page_config(page_title="Data Understanding", page_icon="📖", layout="wide")
st.title("📖 Data Understanding")

# ------------------------------------------------------------------ tujuan
st.header("1. Tujuan analisis Land Use & Land Cover (LULC)")
st.markdown(
    """
**Penutup lahan (land cover)** adalah tutupan fisik permukaan bumi (vegetasi, air, bangunan, tanah terbuka),
sedangkan **penggunaan lahan (land use)** adalah pemanfaatan lahan oleh manusia (pertanian, permukiman, dll).
Klasifikasi LULC dari citra satelit bertujuan untuk:

1. **Memetakan sebaran** sawah, area terbangun, mangrove, lahan hijau, laut, dan danau di Jawa Timur secara
   cepat, berulang, dan murah dibanding survei lapangan.
2. **Menghitung luas** tiap kelas (hektar) sebagai dasar statistik tata guna lahan.
3. **Memantau perubahan lahan** (alih fungsi sawah menjadi bangunan, abrasi/penyusutan mangrove, perubahan
   tubuh air) dengan membandingkan peta antar periode.
4. **Mendukung kebijakan & perencanaan tata ruang**: evaluasi kesesuaian dengan RTRW, perlindungan lahan
   pertanian pangan berkelanjutan (LP2B), rehabilitasi mangrove, dan pengelolaan sempadan danau/ranu.
5. **Membandingkan algoritma machine learning** untuk memilih model dengan akurasi klasifikasi tertinggi.
"""
)

# ------------------------------------------------------------------ acuan
st.header("2. Acuan klasifikasi lahan di Indonesia")
st.markdown(
    """
Klasifikasi lahan di Indonesia tidak hanya *sawah vs non-sawah*. Dua acuan utama:

**a. SNI 7645:2010 / SNI 7645-1:2014 — Klasifikasi penutup lahan** (BIG / Badan Standardisasi Nasional).
Membagi penutup lahan menjadi *daerah bervegetasi* (pertanian dan bukan pertanian: hutan, semak, dll)
dan *daerah tak bervegetasi* (lahan terbuka, permukiman dan lahan bukan pertanian, perairan).

**b. Klasifikasi penutupan lahan KLHK** (Kementerian Lingkungan Hidup dan Kehutanan) — 23 kelas yang dipakai
dalam peta penutupan lahan nasional, antara lain:
"""
)
klhk = pd.DataFrame(
    [
        ("Hutan lahan kering primer / sekunder", "Hutan alami di daratan"),
        ("Hutan mangrove primer / sekunder", "Hutan pasang-surut di pesisir"),
        ("Hutan rawa primer / sekunder", "Hutan di lahan basah"),
        ("Hutan tanaman", "Hutan hasil penanaman (jati, pinus, dll)"),
        ("Perkebunan", "Kebun tanaman tahunan (kopi, tebu, karet, dll)"),
        ("Semak / belukar", "Vegetasi rendah campuran"),
        ("Savana / padang rumput", "Lahan rumput"),
        ("Pertanian lahan kering / campur semak", "Tegalan, ladang, kebun campur"),
        ("Sawah", "Lahan pertanian padi beririgasi/tadah hujan"),
        ("Tambak", "Budidaya perairan payau"),
        ("Permukiman", "Area terbangun"),
        ("Bandara / pelabuhan", "Fasilitas transportasi"),
        ("Pertambangan", "Lahan tambang terbuka"),
        ("Tanah terbuka", "Lahan tanpa vegetasi"),
        ("Tubuh air", "Laut, danau, sungai, waduk"),
        ("Rawa", "Lahan basah"),
    ],
    columns=["Kelas KLHK (ringkas)", "Keterangan"],
)
st.dataframe(klhk, hide_index=True, width="stretch")
st.caption("Daftar ringkas untuk ilustrasi; rujuk dokumen resmi KLHK/BIG untuk legenda lengkap 23 kelas "
           "beserta kode numeriknya.")

st.subheader("Pemetaan 6 kelas penelitian ke acuan nasional")
map_df = pd.DataFrame(
    [{"ID": c["id"], "Kelas penelitian": c["name"], "Padanan KLHK": c["klhk"],
      "Padanan SNI 7645": c["sni"]} for c in C.CLASSES]
)
st.dataframe(map_df, hide_index=True, width="stretch")

# ------------------------------------------------------------------ kebijakan
st.header("3. Keterkaitan dengan kebijakan")
st.markdown(
    """
| Kelas | Isu kebijakan | Contoh landasan |
|---|---|---|
| Sawah | Perlindungan lahan pangan, pengendalian alih fungsi | UU No. 41/2009 tentang Perlindungan Lahan Pertanian Pangan Berkelanjutan (LP2B) |
| Bangunan | Pengendalian ekspansi permukiman, tata ruang | RTRW provinsi/kabupaten/kota |
| Mangrove | Perlindungan & rehabilitasi ekosistem pesisir | Perpres No. 120/2020 tentang Percepatan Rehabilitasi Mangrove |
| Lahan hijau | Konservasi hutan, ruang terbuka hijau | UU Kehutanan, RTRW |
| Laut | Pengelolaan wilayah pesisir dan laut | UU Pengelolaan Wilayah Pesisir dan Pulau-Pulau Kecil |
| Danau (ranu) | Perlindungan sempadan danau, DAS | Peraturan pengelolaan sumber daya air & sempadan |
"""
)
st.caption("Rujukan peraturan dicantumkan sebagai konteks; verifikasi nomor dan versi terbaru sebelum dikutip di laporan.")

# ------------------------------------------------------------------ kelas
st.header("4. Enam kelas yang dianalisis (wilayah: Jawa Timur)")
for c in C.CLASSES:
    st.markdown(
        f"<span style='display:inline-block;width:14px;height:14px;background:{c['color']};"
        f"border-radius:3px;margin-right:8px'></span>**{c['id']}. {c['name']}** — {c['desc']}",
        unsafe_allow_html=True,
    )
