"""
config.py
=========
Konfigurasi terpusat proyek: path, kelas, band Sentinel-2A, fitur + rumus, dan ROI.
Dipakai oleh semua script (scripts/*.py) dan aplikasi Streamlit (app.py, pages/*.py).
File ini TIDAK boleh meng-import streamlit / ee supaya ringan dan aman dipakai di mana saja.
"""
from pathlib import Path

# ----------------------------------------------------------------------------
# PATH
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ROI_DIR = DATA_DIR / "roi"            # tempat GeoTIFF stack dari GEE + hasil prediksi
MODEL_DIR = ROOT / "models"
RAW_DIR = DATA_DIR / "raw"            # taruh 6 file .geojson asli di sini

SAMPLES_POLY = DATA_DIR / "samples_all.geojson"      # poligon sampel (gabungan 6 kelas)
SAMPLES_PTS = DATA_DIR / "titik_sampel.geojson"      # titik sampel hasil sampling poligon
DATASET_CSV = DATA_DIR / "dataset_fitur.csv"         # tabel fitur hasil ekstraksi GEE
RESULTS_CSV = DATA_DIR / "model_results.csv"
CONFMAT_CSV = DATA_DIR / "confusion_matrix.csv"
REPORT_CSV = DATA_DIR / "classification_report.csv"
IMPORTANCE_CSV = DATA_DIR / "feature_importance.csv"
SPLIT_JSON = DATA_DIR / "split_summary.json"
ROI_META_JSON = DATA_DIR / "roi_meta.json"
BEST_MODEL = MODEL_DIR / "best_model.joblib"
MODEL_META = MODEL_DIR / "model_meta.json"

RANDOM_STATE = 42

# ----------------------------------------------------------------------------
# KELAS (6 kelas, wilayah Jawa Timur)
# ----------------------------------------------------------------------------
# raw_file = nama file geojson asli yang diupload
CLASSES = [
    dict(id=1, name="Sawah", raw_file="sawah_Jawa_Timur.geojson", color="#FFD500",
         klhk="Sawah (20093)", sni="Pertanian - sawah (daerah bervegetasi)",
         desc="Lahan pertanian yang digenangi/diairi secara periodik untuk padi."),
    dict(id=2, name="Bangunan", raw_file="bangunan.geojson", color="#E31A1C",
         klhk="Permukiman (2012)", sni="Permukiman & lahan bukan pertanian (tak bervegetasi)",
         desc="Area terbangun: permukiman, industri, jalan, fasilitas umum."),
    dict(id=3, name="Mangrove", raw_file="Mangrove.geojson", color="#006D2C",
         klhk="Hutan mangrove primer/sekunder (2004/2005)", sni="Hutan - mangrove (daerah bervegetasi)",
         desc="Vegetasi hutan pasang-surut di pesisir (Surabaya, Sidoarjo, Probolinggo, Banyuwangi, dll)."),
    dict(id=4, name="Lahan Hijau", raw_file="Lahan_ijo2.geojson", color="#74C476",
         klhk="Hutan lahan kering / perkebunan / pertanian lahan kering (2001/2002/2010/20091)",
         sni="Hutan, perkebunan, pertanian lahan kering (daerah bervegetasi)",
         desc="Vegetasi non-sawah dan non-mangrove: hutan, kebun, tegalan, semak."),
    dict(id=5, name="Perairan Terbuka (Laut)", raw_file="laut.geojson", color="#08306B",
         klhk="Tubuh air (5001)", sni="Perairan (daerah tak bervegetasi)",
         desc="Laut/selat terbuka (Laut Jawa, Selat Madura, Selat Bali, Samudra Hindia)."),
    dict(id=6, name="Danau (Ranu)", raw_file="Danau.geojson", color="#41B6E6",
         klhk="Tubuh air (5001)", sni="Perairan (daerah tak bervegetasi)",
         desc="Danau/ranu/waduk daratan (mis. Ranu Klakah, Ranu Bedali, Ranu Pani, Ranu Grati)."),
]
CLASS_NAMES = {c["id"]: c["name"] for c in CLASSES}
CLASS_COLORS = {c["id"]: c["color"] for c in CLASSES}

# ----------------------------------------------------------------------------
# BAND SENTINEL-2A (MSI)  -- panjang gelombang tengah & bandwidth untuk S2A
# ----------------------------------------------------------------------------
BAND_TABLE = [
    # band, nama, lambda tengah (nm), bandwidth (nm), resolusi (m), dipakai?, kegunaan
    ("B1",  "Coastal aerosol",        442.7, 21,  60, False, "Koreksi aerosol & studi pesisir"),
    ("B2",  "Blue",                   492.4, 66,  10, True,  "Pembeda air/tanah, komponen EVI"),
    ("B3",  "Green",                  559.8, 36,  10, True,  "Puncak pantulan vegetasi, NDWI/MNDWI"),
    ("B4",  "Red",                    664.6, 31,  10, True,  "Serapan klorofil, NDVI"),
    ("B5",  "Vegetation Red Edge 1",  704.1, 15,  20, True,  "Kondisi klorofil vegetasi"),
    ("B6",  "Vegetation Red Edge 2",  740.5, 15,  20, True,  "Struktur kanopi"),
    ("B7",  "Vegetation Red Edge 3",  782.8, 20,  20, True,  "Struktur kanopi"),
    ("B8",  "NIR",                    832.8, 106, 10, True,  "Biomassa vegetasi, batas air-darat"),
    ("B8A", "Narrow NIR",             864.7, 21,  20, True,  "Vegetasi (NIR sempit)"),
    ("B9",  "Water vapour",           945.1, 20,  60, False, "Uap air atmosfer"),
    ("B10", "SWIR - Cirrus",         1373.5, 31,  60, False, "Deteksi awan cirrus (tidak ada di produk L2A)"),
    ("B11", "SWIR 1",                1613.7, 91,  20, True,  "Kadar air vegetasi/tanah, area terbangun"),
    ("B12", "SWIR 2",                2202.4, 175, 20, True,  "Kadar air, tanah terbuka, bangunan"),
]
S2_BANDS = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]   # 10 band dipakai

# ----------------------------------------------------------------------------
# FITUR TURUNAN: indeks spektral + topografi
# ----------------------------------------------------------------------------
INDEX_TABLE = [
    dict(name="NDVI",  formula="(B8 - B4) / (B8 + B4)",
         latex=r"NDVI=\frac{B8-B4}{B8+B4}", fungsi="Kehijauan/kerapatan vegetasi"),
    dict(name="NDWI",  formula="(B3 - B8) / (B3 + B8)",
         latex=r"NDWI=\frac{B3-B8}{B3+B8}", fungsi="Badan air terbuka (McFeeters)"),
    dict(name="MNDWI", formula="(B3 - B11) / (B3 + B11)",
         latex=r"MNDWI=\frac{B3-B11}{B3+B11}", fungsi="Air, menekan noise bangunan (Xu)"),
    dict(name="NDBI",  formula="(B11 - B8) / (B11 + B8)",
         latex=r"NDBI=\frac{B11-B8}{B11+B8}", fungsi="Area terbangun"),
    dict(name="NDMI",  formula="(B8 - B11) / (B8 + B11)",
         latex=r"NDMI=\frac{B8-B11}{B8+B11}", fungsi="Kadar air vegetasi (sawah/mangrove)"),
    dict(name="EVI",   formula="2.5 * (B8 - B4) / (B8 + 6*B4 - 7.5*B2 + 1)",
         latex=r"EVI=2.5\times\frac{B8-B4}{B8+6\cdot B4-7.5\cdot B2+1}",
         fungsi="Vegetasi dengan koreksi atmosfer & saturasi"),
    dict(name="SAVI",  formula="1.5 * (B8 - B4) / (B8 + B4 + 0.5)",
         latex=r"SAVI=\frac{B8-B4}{B8+B4+L}\times(1+L),\ L=0.5",
         fungsi="Vegetasi dengan koreksi pengaruh tanah"),
    dict(name="CMRI",  formula="NDVI - NDWI",
         latex=r"CMRI=NDVI-NDWI", fungsi="Combined Mangrove Recognition Index (membantu mangrove)"),
]
TOPO_TABLE = [
    dict(name="elevation", formula="SRTM GL1 (USGS/SRTMGL1_003), 30 m", latex=None,
         fungsi="Ketinggian (m dpl): danau/ranu di dataran tinggi, mangrove ~0 m"),
    dict(name="slope", formula="ee.Terrain.slope(elevation)", latex=None,
         fungsi="Kemiringan lereng (derajat): sawah datar, lahan hijau bisa curam"),
]
INDEX_NAMES = [i["name"] for i in INDEX_TABLE]
TOPO_NAMES = [t["name"] for t in TOPO_TABLE]

# URUTAN FITUR -- HARUS SAMA di GEE, training, dan prediksi raster
FEATURE_COLS = S2_BANDS + INDEX_NAMES + TOPO_NAMES      # 10 + 8 + 2 = 20 fitur

# ----------------------------------------------------------------------------
# PARAMETER CITRA (GEE)
# ----------------------------------------------------------------------------
S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"
DATE_START = "2025-01-01"
DATE_END = "2025-12-31"
MAX_CLOUD = 30                    # CLOUDY_PIXEL_PERCENTAGE
SCALE = 10                        # meter
EXPORT_CRS = "EPSG:32749"         # UTM 49S, piksel 10 m -> luas piksel = 0.01 ha
JATIM_GAUL = ("FAO/GAUL/2015/level1", "ADM1_NAME", "Jawa Timur")

# ----------------------------------------------------------------------------
# ROI untuk prediksi peta  [west, south, east, north]  (ukuran ~15 km agar ringan)
# Sesuaikan jika perlu. Dipilih dari sebaran poligon sampelmu.
# ----------------------------------------------------------------------------
ROIS = {
    "surabaya_sidoarjo": dict(label="Surabaya - Gresik - Sidoarjo (pesisir)",
                              bbox=[112.60, -7.26, 112.74, -7.12]),
    "lumajang_ranu":     dict(label="Lumajang (Ranu Klakah/Bedali)",
                              bbox=[113.30, -8.10, 113.46, -7.94]),
    "mojokerto_jombang": dict(label="Mojokerto - Jombang (sawah)",
                              bbox=[112.50, -7.46, 112.66, -7.30]),
    "malang_selatan":    dict(label="Malang Selatan (lahan hijau & ranu)",
                              bbox=[112.34, -8.10, 112.50, -7.94]),
}
