import streamlit as st
import google.generativeai as genai
from datetime import datetime, date
import random
import json
import os
from fpdf import FPDF

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="KOÇANKA ;)",
    page_icon="🧭",
    layout="centered"
)

# --- GEMINI API BAĞLANTISI ---
gemini_model = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        if api_key and api_key.strip():
            genai.configure(api_key=api_key)
            gemini_model = genai.GenerativeModel("gemini-3.8-flash")
except Exception as e:
    print(f"API Bağlantı Hatası: {e}")

VERI_DOSYASI = "veriler.json"

# --- VERİ YÖNETİMİ ---
def verileri_yukle():
    default_data = {
        "exams": [{"ders": "Matematik", "konu": "Fonksiyonlar", "tarih": "2027-06-17"}],
        "homework": [{"ders": "Fizik", "aciklama": "Elektrik Akımı Testleri", "tarih": "2026-07-15", "tamamlandi": False}],
        "mistakes": [],
        "error_notebook": [],
        "denemeler": [],
        "daily_tasks": [{"gorev": "Matematik 50 soru çöz", "tamamlandi": False}, {"gorev": "Fizik konu tekrarı yap", "tamamlandi": False}],
        "missing_topics": {"Matematik": ["Trigonometri"], "Fizik": ["Optik"], "Kimya": [], "Biyoloji": [], "Türkçe": []},
        "daily_program": "",
        "program_subjects": ["Matematik", "Fizik", "Kimya"]
    }
    if os.path.exists(VERI_DOSYASI):
        try:
            with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in default_data.items():
                    if k not in data:
                        data[k] = v
                return data
        except:
            pass
    return default_data

def verileri_kaydet(veri):
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

if "veri" not in st.session_state:
    st.session_state.veri = verileri_yukle()

if "aktif_sayfa" not in st.session_state:
    st.session_state.aktif_sayfa = "🏠 Ana Sayfa"

def sayfa_degistir(hedef_sayfa):
    st.session_state.aktif_sayfa = hedef_sayfa

# --- YARDIMCI FONKSİYONLAR ---
def turkce_temizle(metin):
    degisim = {"ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ş": "s", "Ş": "S", "ı": "i", "İ": "I", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    for k, v in degisim.items():
        metin = metin.replace(k, v)
    return metin

def pdf_olustur(baslik, icerik):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, turkce_temizle(baslik), ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, turkce_temizle(icerik))
    return bytes(pdf.output())

# --- SOL MENÜ (SIDEBAR) ---
sayfalar = [
    "🏠 Ana Sayfa", 
    "📅 Takvimim", 
    "📅 Günlük Program", 
    "📊 Deneme Analizi", 
    "📝 Sınavlarım & Ödevlerim", 
    "❌ Eksik Konularım", 
    "📚 Ders Çalış", 
    "📄 Hızlı PDF Özetle", 
    "❌ Yanlışlarım & Hata Defteri",
    "🤖 Yapay Zeka Koç (Asistan)"
]

secilen = st.sidebar.radio(
    "Menü",
    sayfalar,
    index=sayfalar.index(st.session_state.aktif_sayfa) if st.session_state.aktif_sayfa in sayfalar else 0
)
if secilen != st.session_state.aktif_sayfa:
    st.session_state.aktif_sayfa = secilen
    st.rerun()

# ==========================================
# SAYFA YÖNETİMİ
# ==========================================

if st.session_state.aktif_sayfa == "🏠 Ana Sayfa":
    st.markdown("<h1 style='text-align: center; font-size: 2.5rem;'>👋 HOŞ GELDİN!</h1>", unsafe_allow_html=True)

    sozler = [
        ("Harika işler yapmak için tek yol, yaptığın şeyi sevmektir.", "Steve Jobs"),
        ("Başarı, her gün tekrarlanan küçük çabaların toplamıdır.", "Robert Collier"),
        ("Gelecek, bugünden ona hazırlananlara aittir.", "Malcolm X"),
        ("Zorluklar, başarının değerini artıran süslerdir.", "Moliere")
    ]
    if "gunun_sozu" not in st.session_state:
        st.session_state.gunun_sozu = random.choice(sozler)
    
    soz, yazar = st.session_state.gunun_sozu
    st.markdown(f"""
    <div style="border: 2px solid #4A4A4A; border-radius: 15px; padding: 20px; text-align: center; background-color: rgba(255,255,255,0.03); margin-bottom: 25px;">
        <p style="font-size: 1.2rem; font-style: italic; margin-bottom: 8px;">"{soz}"</p>
        <p style="color: #A0A0A0; font-weight: bold; margin: 0;">— {yazar}</p>
    </div>
    """, unsafe_allow_html=True)

    # Bekleyen Sınavlar
    st.subheader("Bekleyen Sınavlar")
    sinavlar = st.session_state.veri.get("exams", [])
    sinav_sayisi = len(sinavlar)
    en_yakin_sinav = sorted(sinavlar, key=lambda x: x.get("tarih", "2027-01-01"))[0]["tarih"] if sinavlar else "Yok"

    c1, c2, c3 = st.columns([1, 2, 2])
    with c1:
        st.markdown(f"<div style='border:2px solid #555; border-radius:50%; width:45px; height:45px; display:flex; align-items:center; justify-content:center; font-size:1.3rem; font-weight:bold;'>{sinav_sayisi}</div>", unsafe_allow_html=True)
    with c2:
        st.caption("TARİHİ")
        if st.button(f"📅 {en_yakin_sinav}", key="btn_takvim_git", use_container_width=True):
            sayfa_degistir("📅 Takvimim")
            st.rerun()
    with c3:
        if st.button("Sınava çalış", key="btn_sinav_calis", use_container_width=True):
            sayfa_degistir("📚 Ders Çalış")
            st.rerun()

    st.write("")

    # Bekleyen Ödevler
    st.subheader("Bekleyen Ödevler")
    odevler = st.session_state.veri.get("homework", [])
    odev_sayisi = len(odevler)
    en_yakin_odev = sorted(odevler, key=lambda x: x.get("tarih", "2027-01-01"))[0]["tarih"] if odevler else "Yok"

    o1, o2, o3 = st.columns([1, 2, 2])
    with o1:
        st.markdown(f"<div style='border:2px solid #555; border-radius:50%; width:45px; height:45px; display:flex; align-items:center; justify-content:center; font-size:1.3rem; font-weight:bold;'>{odev_sayisi}</div>", unsafe_allow_html=True)
    with o2:
        st.caption("EN YAKIN TARİH")
        st.markdown(f"**📅 {en_yakin_odev}**")
    with o3:
        if st.button("Ödevi görüntüle", key="btn_odev_gor", use_container_width=True):
            sayfa_degistir("📝 Sınavlarım & Ödevlerim")
            st.rerun()

    st.divider()

    # Alt 4 Stratejik Buton
    st.markdown("<h3 style='text-align: center; letter-spacing: 2px;'>GÜNLÜK PROGRAMINI AL</h3>", unsafe_allow_html=True)
    
    b1, b2 = st.columns(2)
    b3, b4 = st.columns(2)

    with b1:
        if st.button("📅 Program al", use_container_width=True, type="primary"):
            sayfa_degistir("📅 Günlük Program")
            st.rerun()
    with b2:
        if st.button("❌ Yanlışlarını not al", use_container_width=True):
            sayfa_degistir("❌ Yanlışlarım & Hata Defteri")
            st.rerun()
    with b3:
        if st.button("🔍 Eksik konularım", use_container_width=True):
            sayfa_degistir("❌ Eksik Konularım")
            st.rerun()
    with b4:
        if st.button("📚 Konu tekrarı", use_container_width=True):
            sayfa_degistir("📚 Ders Çalış")
            st.rerun()

    st.write("")
    col_x1, col_x2, col_x3 = st.columns([1, 2, 1])
    with col_x2:
        if st.button("📊 Deneme Analizi", use_container_width=True):
            sayfa_degistir("📊 Deneme Analizi")
            st.rerun()

    st.write("")
    if st.button("🤖 Yapay Zeka Asistan ile Konuş", use_container_width=True):
        sayfa_degistir("🤖 Yapay Zeka Koç (Asistan)")
        st.rerun()

elif st.session_state.aktif_sayfa == "📅 Takvimim":
    st.title("📅 Sınav Takvimi")
    sinavlar = st.session_state.veri.get("exams", [])
    if sinavlar:
        for s in sorted(sinavlar, key=lambda x: x.get("tarih", "2027-01-01")):
            st.info(f"📌 **{s.get('ders')} Sınavı**\n\n🎯 Konu: {s.get('konu')}\n\n📅 Tarih: **{s.get('tarih')}**")
    else:
        st.warning("Kayıtlı sınav bulunmuyor.")

elif st.session_state.aktif_sayfa == "📅 Günlük Program":
    st.title("📅 Günlük Program & Görevler")
    with st.form("yeni_gorev_form"):
        yeni_g = st.text_input("Yeni Görev Ekle (Örn: Matematik 40 soru çöz)")
        if st.form_submit_button("Görev Ekle") and yeni_g:
            st.session_state.veri["daily_tasks"].append({"gorev": yeni_g, "tamamlandi": False})
            verileri_kaydet(st.session_state.veri)
            st.success("Görev eklendi!")
            st.rerun()

    st.subheader("📋 Görev Listen")
    tasks = st.session_state.veri.get("daily_tasks", [])
    for i, t in enumerate(tasks):
        col1, col2, col3 = st.columns([3, 1, 1])
        durum = col1.checkbox(t["gorev"], value=t["tamamlandi"], key=f"task_{i}")
        if durum != t["tamamlandi"]:
            tasks[i]["tamamlandi"] = durum
            verileri_kaydet(st.session_state.veri)
            st.rerun()
            
        if t["tamamlandi"]:
            col2.markdown("### 🥳")
        else:
            col2.markdown("⏳")
            
        if col3.button("🗑️ Sil", key=f"del_task_{i}"):
            tasks.pop(i)
            verileri_kaydet(st.session_state.veri)
            st.rerun()

elif st.session_state.aktif_sayfa == "📊 Deneme Analizi":
    st.title("📊 Deneme Sınavı Analizi")
    denemeler = st.session_state.veri.get("denemeler", [])

    with st.form("deneme_giris_form"):
        deneme_adi = st.text_input("Deneme Adı (Örn: 1. Deneme)")
        d_mat = st.number_input("Matematik Doğru", 0, 40, 0)
        y_mat = st.number_input("Matematik Yanlış", 0, 40, 0)
        b_mat = st.number_input("Matematik Boş", 0, 40, 0)
        
        analiz_et_btn = st.form_submit_button("Denemeyi Analiz Et & Program Oluştur", type="primary")
        if analiz_et_btn and deneme_adi:
            if gemini_model:
                with st.spinner("Analiz ediliyor..."):
                    prompt = f"Öğrencinin {deneme_adi} Matematik netleri: D:{d_mat} Y:{y_mat} B:{b_mat}. 1 haftalık saat vermeden yapması gerekenleri içeren çalışma programı hazırla."
                    program_sonuc = gemini_model.generate_content(prompt).text
                    st.session_state.veri["denemeler"].append({"ad": deneme_adi, "mat": f"D:{d_mat} Y:{y_mat} B:{b_mat}", "program": program_sonuc})
                    verileri_kaydet(st.session_state.veri)
                    st.success("Deneme kaydedildi!")

    if denemeler:
        for deneme in denemeler:
            with st.expander(f"📈 {deneme['ad']}"):
                st.write(f"Matematik: {deneme['mat']}")
                st.markdown(deneme["program"])

elif st.session_state.aktif_sayfa == "📝 Sınavlarım & Ödevlerim":
    st.title("📝 Sınav & Ödev Yönetimi")
    tab1, tab2 = st.tabs(["Ödevler", "Sınavlar"])
    with tab1:
        with st.form("odev_ekleme"):
            od_ders = st.text_input("Ders Adı")
            od_aciklama = st.text_input("Ödev Açıklaması")
            od_tarih = st.date_input("Teslim Tarihi")
            if st.form_submit_button("Ödev Ekle") and od_ders:
                st.session_state.veri["homework"].append({"ders": od_ders, "aciklama": od_aciklama, "tarih": str(od_tarih), "tamamlandi": False})
                verileri_kaydet(st.session_state.veri)
                st.rerun()
        for i, o in enumerate(st.session_state.veri.get("homework", [])):
            col1, col2 = st.columns([4, 1])
            col1.write(f"📌 **{o.get('ders')}**: {o.get('aciklama')} (Tarih: {o.get('tarih')})")
            if col2.button("Sil", key=f"del_h_{i}"):
                st.session_state.veri["homework"].pop(i)
                verileri_kaydet(st.session_state.veri)
                st.rerun()
    with tab2:
        with st.form("sinav_ekleme"):
            sn_ders = st.text_input("Sınav Dersi")
            sn_konu = st.text_input("Konular")
            sn_tarih = st.date_input("Sınav Tarihi")
            if st.form_submit_button("Sınav Ekle") and sn_ders:
                st.session_state.veri["exams"].append({"ders": sn_ders, "konu": sn_konu, "tarih": str(sn_tarih)})
                verileri_kaydet(st.session_state.veri)
                st.rerun()
        for i, s in enumerate(st.session_state.veri.get("exams", [])):
            col1, col2 = st.columns([4, 1])
            col1.write(f"🎯 **{s.get('ders')}**: {s.get('konu')} (Tarih: {s.get('tarih')})")
            if col2.button("Sil", key=f"del_e_{i}"):
                st.session_state.veri["exams"].pop(i)
                verileri_kaydet(st.session_state.veri)
                st.rerun()

elif st.session_state.aktif_sayfa == "❌ Eksik Konularım":
    st.title("❌ Eksik Konu Takibi")
    dersler = ["Matematik", "Fizik", "Kimya", "Biyoloji", "Türkçe"]
    secilen_ders_eksik = st.selectbox("Ders Seç", dersler)
    yeni_eksik = st.text_input("Eksik Konu Adı")
    if st.button("Eksik Konu Ekle") and yeni_eksik:
        if secilen_ders_eksik not in st.session_state.veri["missing_topics"]:
            st.session_state.veri["missing_topics"][secilen_ders_eksik] = []
        st.session_state.veri["missing_topics"][secilen_ders_eksik].append(yeni_eksik)
        verileri_kaydet(st.session_state.veri)
        st.success("Eklendi!")
        st.rerun()

    st.subheader("📚 Eksik Konuların ve Çözüm Takibi")
    missing = st.session_state.veri.get("missing_topics", {})
    for d, konular in missing.items():
        if konular:
            st.markdown(f"**{d}**")
            for idx, konu in enumerate(konular):
                col1, col2 = st.columns([3, 2])
                col1.write(f"• {konu}")
                if col2.button("Hallettim 😎", key=f"hallettim_{d}_{idx}"):
                    konular.pop(idx)
                    verileri_kaydet(st.session_state.veri)
                    st.rerun()

elif st.session_state.aktif_sayfa == "📚 Ders Çalış":
    st.title("📚 Akıllı Ders Çalışma Asistanı")
    ders = st.selectbox("Ders Seç", ["Matematik", "Fizik", "Kimya", "Biyoloji", "Türkçe"])
    konu = st.text_input("Konu Adı")
    if st.button("📖 Konuyu Anlat", type="primary"):
        if gemini_model and konu:
            with st.spinner("Hazırlanıyor..."):
                st.markdown(gemini_model.generate_content(f"10. sınıf {ders} - {konu} konusunu özetle.").text)
    
    soru = st.text_input("Soru Sor:")
    if st.button("Soruyu Yanıtla") and soru:
        if gemini_model:
            st.markdown(gemini_model.generate_content(f"10. sınıf öğrencisinin sorusu: {soru}").text)

elif st.session_state.aktif_sayfa == "📄 Hızlı PDF Özetle":
    st.title("📄 Hızlı PDF Özetle")
    pdf_text = st.text_area("Metni Yapıştır:")
    if st.button("Önemli Notları Çıkar", type="primary") and pdf_text:
        if gemini_model:
            st.markdown(gemini_model.generate_content(f"Özetle:\n\n{pdf_text}").text)

elif st.session_state.aktif_sayfa == "❌ Yanlışlarım & Hata Defteri":
    st.title("❌ Yanlışlarım & Hata Defteri")
    tab1, tab2 = st.tabs(["Yanlış Not Et", "📸 Hata Defteri"])
    with tab1:
        with st.form("y_form"):
            y_ders = st.selectbox("Ders", ["Matematik", "Fizik", "Kimya", "Biyoloji", "Türkçe"])
            y_konu = st.text_input("Konu")
            y_aciklama = st.text_area("Not")
            if st.form_submit_button("Kaydet") and y_konu:
                st.session_state.veri["mistakes"].append({"ders": y_ders, "konu": y_konu, "not": y_aciklama})
                verileri_kaydet(st.session_state.veri)
                st.rerun()
        for m in st.session_state.veri.get("mistakes", []):
            st.info(f"**{m.get('ders')} - {m.get('konu')}**: {m.get('not')}")
    with tab2:
        hata_notu = st.text_area("Soruyu Yaz:")
        if st.button("Yapay Zekaya Çözdür", type="primary") and hata_notu:
            if gemini_model:
                st.markdown(gemini_model.generate_content(f"Şu soruyu çöz:\n\n{hata_notu}").text)

elif st.session_state.aktif_sayfa == "🤖 Yapay Zeka Koç (Asistan)":
    st.title("🤖 Yapay Zeka Koçun")
    if st.button("📊 Haftalık Raporumu Ver", type="primary"):
        if gemini_model:
            st.markdown(gemini_model.generate_content("Öğrenciye haftalık koçluk raporu ver.").text)
    user_query = st.text_input("Koçuna Sor:")
    if st.button("Gönder") and user_query:
        if gemini_model:
            st.markdown(gemini_model.generate_content(f"Koç olarak yanıtla: {user_query}").text)