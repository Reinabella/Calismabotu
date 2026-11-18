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

# --- VERİ YÖNETİMİ (GÜVENLİ & KAPSAMLI) ---
def verileri_yukle():
    default_data = {
        "exams": [{"ders": "Matematik", "konu": "Fonksiyonlar", "tarih": "2027-06-17"}],
        "homework": [{"ders": "Fizik", "aciklama": "Elektrik Akımı Testleri", "tarih": "2026-07-15", "tamamlandi": False}],
        "mistakes": [],
        "error_notebook": [], # Hata defteri (görsel/soru notları)
        "denemeler": [], # Geçmiş deneme analizleri
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

# --- PDF OLUŞTURUCU ---
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

# --- SOL MENÜ (ÇİZİMİNE GÖRE DÜzenlendi) ---
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
# 1. ANA SAYFA
# ==========================================
if st.session_state.aktif_sayfa == "🏠 Ana Sayfa":
    st.markdown("<h1 style='text-align: center; font-size: 2.5rem;'>🧭 KOÇANKA ;)</h1>", unsafe_allow_html=True)

    # Motivasyon Sözü
    sozler = [
        ("Harika işler yapmak için tek yol, yaptığın şeyi sevmektir.", "Steve Jobs"),
        ("Başarı, her gün tekrarlanan küçük çabaların toplamıdır.", "Robert Collier"),
        ("Gelecek, bugünden ona hazırlananlara aittir.", "Malcolm X")
    ]
    if "gunun_sozu" not in st.session_state:
        st.session_state.gunun_sozu = random.choice(sozler)
    soz, yazar = st.session_state.gunun_sozu
    st.markdown(f"""
    <div style="border: 2px solid #4A4A4A; border-radius: 15px; padding: 15px; text-align: center; background-color: rgba(255,255,255,0.03); margin-bottom: 20px;">
        <p style="font-size: 1.1rem; font-style: italic; margin-bottom: 5px;">"{soz}"</p>
        <p style="color: #A0A0A0; font-weight: bold; margin: 0; font-size: 0.9rem;">— {yazar}</p>
    </div>
    """, unsafe_allow_html=True)

    # Çizimindeki Buton Yapısı (Ana Menü Kısayolları)
    st.markdown("### 📌 Hızlı Menü")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📅 Takvimim", use_container_width=True):
            sayfa_degistir("📅 Takvimim"); st.rerun()
        if st.button("📊 Deneme Analizi", use_container_width=True):
            sayfa_degistir("📊 Deneme Analizi"); st.rerun()
        if st.button("❌ Eksik Konularım", use_container_width=True):
            sayfa_degistir("❌ Eksik Konularım"); st.rerun()
        if st.button("📄 Hızlı PDF Özetle", use_container_width=True):
            sayfa_degistir("📄 Hızlı PDF Özetle"); st.rerun()
    with col2:
        if st.button("📅 Günlük Program", use_container_width=True, type="primary"):
            sayfa_degistir("📅 Günlük Program"); st.rerun()
        if st.button("📝 Sınavlarım & Ödevlerim", use_container_width=True):
            sayfa_degistir("📝 Sınavlarım & Ödevlerim"); st.rerun()
        if st.button("📚 Ders Çalış", use_container_width=True):
            sayfa_degistir("📚 Ders Çalış"); st.rerun()
        if st.button("❌ Yanlışlarım", use_container_width=True):
            sayfa_degistir("❌ Yanlışlarım & Hata Defteri"); st.rerun()

    st.divider()

    # Çiziminin Sağ Altındaki Yapay Zeka Asistan Butonu / Widget'ı
    st.markdown("""
    <div style="background-color: rgba(255,100,100,0.1); border: 2px dashed #ff4b4b; border-radius: 12px; padding: 15px; text-align: center;">
        <h4 style="margin: 0; color: #ff4b4b;">🤖 Hızlı Yapay Zeka Asistanı</h4>
        <p style="font-size: 0.9rem; margin: 5px 0 10px 0;">Ders durumunu öğrenmek ve haftalık rapor almak için tıkla!</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("💬 Yapay Zeka ile Sohbeti Aç", use_container_width=True, type="primary"):
        sayfa_degistir("🤖 Yapay Zeka Koç (Asistan)")
        st.rerun()

# ==========================================
# 2. TAKVİMİM (Sınavlar & Takvim Görünümü)
# ==========================================
elif st.session_state.aktif_sayfa == "📅 Takvimim":
    if st.button("⬅️ Ana Sayfaya Dön"):
        sayfa_degistir("🏠 Ana Sayfa"); st.rerun()

    st.title("📅 Sınav Takvimi")
    st.write("Yaklaşan tüm sınavların ve tarihlerin takvim görünümü:")

    sinavlar = st.session_state.veri.get("exams", [])
    if sinavlar:
        # Tarihe göre sırala
        sirali_sinavlar = sorted(sinavlar, key=lambda x: x.get("tarih", "2027-01-01"))
        for s in sirali_sinavlar:
            st.info(f"📌 **{s.get('ders')} Sınavı**\n\n🎯 Konu: {s.get('konu')}\n\n📅 Tarih: **{s.get('tarih')}**")
    else:
        st.warning("Henüz kayıtlı sınav bulunmuyor. 'Sınavlarım & Ödevlerim' bölümünden ekleyebilirsin.")

# ==========================================
# 3. GÜNLÜK PROGRAM (To-Do List & Kalıcı Görevler)
# ==========================================
elif st.session_state.aktif_sayfa == "📅 Günlük Program":
    if st.button("⬅️ Ana Sayfaya Dön"):
        sayfa_degistir("🏠 Ana Sayfa"); st.rerun()

    st.title("📅 Günlük Program & Görevler")
    st.write("Uygulamadan çıkıp girsen bile kayıtlı kalan günlük to-do list ve görevlerin:")

    # Yeni görev ekleme
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
        col1, col2 = st.columns([4, 1])
        durum = col1.checkbox(t["gorev"], value=t["tamamlandi"], key=f"task_{i}")
        if durum != t["tamamlandi"]:
            tasks[i]["tamamlandi"] = durum
            verileri_kaydet(st.session_state.veri)
            st.rerun()
        
        if t["tamamlandi"]:
            col2.markdown("### 🥳")
        else:
            col2.markdown("⏳")

    st.divider()
    if st.button("✨ Yapay Zeka ile Bugünün Özel Programını Oluştur", type="primary"):
        if not gemini_model:
            st.error("API Bağlantı hatası!")
        else:
            with st.spinner("Yapay zeka ödevlerini ve eksiklerini inceliyor..."):
                prompt = "10. sınıf öğrencisi için saat vermeden yapması gerekenleri net maddeler halinde belirten 1 günlük çalışma programı hazırla."
                cevap = gemini_model.generate_content(prompt).text
                st.markdown(cevap)

# ==========================================
# 4. DENEME ANALİZİ
# ==========================================
elif st.session_state.aktif_sayfa == "📊 Deneme Analizi":
    if st.button("⬅️ Ana Sayfaya Dön"):
        sayfa_degistir("🏠 Ana Sayfa"); st.rerun()

    st.title("📊 Deneme Sınavı Analizi")
    st.write("Dersleri seçerek netlerini, doğru, yanlış ve boş sayılarını gir; yapay zeka sana özel 1 haftalık program çıkarsın.")

    denemeler = st.session_state.veri.get("denemeler", [])

    with st.form("deneme_giris_form"):
        deneme_adi = st.text_input("Deneme Adı (Örn: 1. Deneme, Özdebir TYT vb.)")
        st.write("--- Ders Sonuçları ---")
        d_mat = st.number_input("Matematik Doğru", 0, 40, 0)
        y_mat = st.number_input("Matematik Yanlış", 0, 40, 0)
        b_mat = st.number_input("Matematik Boş", 0, 40, 0)
        
        d_fiz = st.number_input("Fizik Doğru", 0, 20, 0)
        y_fiz = st.number_input("Fizik Yanlış", 0, 20, 0)
        
        analiz_et_btn = st.form_submit_button("Denemeyi Analiz Et & Program Oluştur", type="primary")

        if analiz_et_btn and deneme_adi:
            if gemini_model:
                with st.spinner("Deneme analiz ediliyor ve çalışma programı hazırlanıyor..."):
                    prompt = f"""
                    Öğrencinin {deneme_adi} sonuçları:
                    Matematik: {d_mat} Doğru, {y_mat} Yanlış, {b_mat} Boş
                    Fizik: {d_fiz} Doğru, {y_fiz} Yanlış
                    
                    Bu sonuçlara göre öğrencinin eksiklerini analiz et ve saat vermeden sadece yapması gerekenleri net bir şekilde belirten 1 haftalık çalışma programı ve öneriler sun.
                    """
                    program_sonuc = gemini_model.generate_content(prompt).text
                    
                    # Kaydet
                    yeni_deneme = {
                        "ad": deneme_adi,
                        "mat": f"D:{d_mat} Y:{y_mat} B:{b_mat}",
                        "fizik": f"D:{d_fiz} Y:{y_fiz}",
                        "program": program_sonuc
                    }
                    st.session_state.veri["denemeler"].append(yeni_deneme)
                    verileri_kaydet(st.session_state.veri)
                    st.success("Deneme kaydedildi ve analiz edildi!")

    st.subheader("📁 Geçmiş Denemelerim")
    if denemeler:
        for idx, deneme in enumerate(denemeler):
            with st.expander(f"📈 {deneme['ad']}"):
                st.write(f"**Matematik:** {deneme['mat']} | **Fizik:** {deneme['fizik']}")
                st.markdown(deneme["program"])
    else:
        st.caption("Henüz analiz edilen deneme yok.")

# ==========================================
# 5. SINAVLARIM & ÖDEVLERİM
# ==========================================
elif st.session_state.aktif_sayfa == "📝 Sınavlarım & Ödevlerim":
    if st.button("⬅️ Ana Sayfaya Dön"):
        sayfa_degistir("🏠 Ana Sayfa"); st.rerun()

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
                st.success("Ödev eklendi!")
                st.rerun()
        
        for i, o in enumerate(st.session_state.veri.get("homework", [])):
            st.write(f"📌 **{o.get('ders')}**: {o.get('aciklama')} (Tarih: {o.get('tarih')})")

    with tab2:
        with st.form("sinav_ekleme"):
            sn_ders = st.text_input("Sınav Dersi")
            sn_konu = st.text_input("Konular")
            sn_tarih = st.date_input("Sınav Tarihi")
            if st.form_submit_button("Sınav Ekle") and sn_ders:
                st.session_state.veri["exams"].append({"ders": sn_ders, "konu": sn_konu, "tarih": str(sn_tarih)})
                verileri_kaydet(st.session_state.veri)
                st.success("Sınav eklendi!")
                st.rerun()

        for s in st.session_state.veri.get("exams", []):
            st.write(f"🎯 **{s.get('ders')}**: {s.get('konu')} (Tarih: {s.get('tarih')})")

# ==========================================
# 6. EKSİK KONULARIM
# ==========================================
elif st.session_state.aktif_sayfa == "❌ Eksik Konularım":
    if st.button("⬅️ Ana Sayfaya Dön"):
        sayfa_degistir("🏠 Ana Sayfa"); st.rerun()

    st.title("❌ Eksik Konu Takibi")
    st.write("Ders ders eksik olduğun konuları ekleyebilir ve takip edebilirsin.")

    dersler = ["Matematik", "Fizik", "Kimya", "Biyoloji", "Türkçe"]
    secilen_ders_eksik = st.selectbox("Ders Seç", dersler)

    yeni_eksik = st.text_input("Eksik Olduğun Konu Adı")
    if st.button("Eksik Konu Ekle"):
        if yeni_eksik:
            if secilen_ders_eksik not in st.session_state.veri["missing_topics"]:
                st.session_state.veri["missing_topics"][secilen_ders_eksik] = []
            st.session_state.veri["missing_topics"][secilen_ders_eksik].append(yeni_eksik)
            verileri_kaydet(st.session_state.veri)
            st.success("Eksik konu eklendi!")
            st.rerun()

    st.subheader("📚 Kayıtlı Eksik Konuların")
    missing = st.session_state.veri.get("missing_topics", {})
    for d, konular in missing.items():
        if konular:
            st.markdown(f"**{d}:** " + ", ".join(konular))

# ==========================================
# 7. DERS ÇALIŞ (Yapay Zeka Konu Anlatımı & Soru Sorma)
# ==========================================
elif st.session_state.aktif_sayfa == "📚 Ders Çalış":
    if st.button("⬅️ Ana Sayfaya Dön"):
        sayfa_degistir("🏠 Ana Sayfa"); st.rerun()

    st.title("📚 Akıllı Ders Çalışma Asistanı")
    st.write("Güncel müfredata uygun ders ve konu seçerek yapay zekadan ders anlatımı alabilir, takıldığın soruları sorabilirsin.")

    ders = st.selectbox("Ders Seç", ["Matematik", "Fizik", "Kimya", "Biyoloji", "Türkçe"])
    konu = st.text_input("Çalışmak İstediğin Konu (Örn: Fonksiyonlar, Newton Kanunları)")

    if st.button("📖 Konuyu Anlat", type="primary"):
        if gemini_model and konu:
            with st.spinner("Özel ders notları hazırlanıyor..."):
                prompt = f"10. sınıf müfredatına uygun olarak '{ders}' dersinden '{konu}' konusunu çok net, akılda kalıcı formüller ve püf noktalarıyla anlat."
                anlatim = gemini_model.generate_content(prompt).text
                st.markdown(anlatim)
                st.session_state.son_konu_anlatimi = anlatim

    st.divider()
    st.subheader("❓ Bu Konuyla İlgili Soru Sor")
    soru = st.text_input("Takıldığın bir soru veya kafana takılan bir şey mi var? Buraya yaz:")
    if st.button("Soruyu Yanıtla"):
        if gemini_model and soru:
            with st.spinner("Yapay zeka yanıtlıyor..."):
                cevap = gemini_model.generate_content(f"Öğrencinin sorduğu soru: {soru}. 10. sınıf seviyesinde açıkça açıkla.").text
                st.markdown(cevap)

# ==========================================
# 8. HIZLI PDF ÖZETLE
# ==========================================
elif st.session_state.aktif_sayfa == "📄 Hızlı PDF Özetle":
    if st.button("⬅️ Ana Sayfaya Dön"):
        sayfa_degistir("🏠 Ana Sayfa"); st.rerun()

    st.title("📄 Hızlı PDF Özetle")
    st.write("Ders notu veya PDF yükle, önemli notları ve özetini hızlıca çıkaralım.")

    pdf_text = st.text_area("PDF veya Ders Notu İçeriğini Buraya Yapıştır:")
    if st.button("Önemli Notları Çıkar", type="primary"):
        if gemini_model and pdf_text:
            with st.spinner("Özetleniyor..."):
                ozet = gemini_model.generate_content(f"Aşağıdaki ders metnini öğrencinin sınavda işine yarayacak en önemli püf noktaları ve maddeler halinde özetle:\n\n{pdf_text}").text
                st.markdown(ozet)

# ==========================================
# 9. YANLIŞLARIM & HATA DEFTERİ
# ==========================================
elif st.session_state.aktif_sayfa == "❌ Yanlışlarım & Hata Defteri":
    if st.button("⬅️ Ana Sayfaya Dön"):
        sayfa_degistir("🏠 Ana Sayfa"); st.rerun()

    st.title("❌ Yanlışlarım & Hata Defteri")
    
    tab1, tab2 = st.tabs(["Soru Yanlışları Not Et", "📸 Hata Defteri (Soru Çözüm Analizi)"])

    with tab1:
        with st.form("yanlis_not_form"):
            y_ders = st.selectbox("Ders", ["Matematik", "Fizik", "Kimya", "Biyoloji", "Türkçe"])
            y_konu = st.text_input("Konu Adı")
            y_aciklama = st.text_area("Neden Yanlış Yaptın? / Notun")
            if st.form_submit_button("Yanlışı Kaydet") and y_konu:
                st.session_state.veri["mistakes"].append({"ders": y_ders, "konu": y_konu, "not": y_aciklama})
                verileri_kaydet(st.session_state.veri)
                st.success("Hafızaya kaydedildi!")
                st.rerun()

        for m in st.session_state.veri.get("mistakes", []):
            st.info(f"📌 **{m.get('ders')} - {m.get('konu')}**: {m.get('not')}")

    with tab2:
        st.write("Hata defterine soru ekleyebilir veya yapay zekaya analiz ettirebilirsin.")
        hata_notu = st.text_area("Çözemediğin veya yanlış yaptığın sorunun metnini yaz:")
        if st.button("🤖 Yapay Zekaya Soru Çözdür & Analiz Ettir", type="primary"):
            if gemini_model and hata_notu:
                with st.spinner("Soru çözülüyor ve inceleniyor..."):
                    cozum = gemini_model.generate_content(f"Şu sorunun çözümünü adım adım ve çok anlaşılır şekilde açıkla:\n\n{hata_notu}").text
                    st.markdown(cozum)

# ==========================================
# 10. YAPAY ZEKA KOÇ (ASİSTAN)
# ==========================================
elif st.session_state.aktif_sayfa == "🤖 Yapay Zeka Koç (Asistan)":
    if st.button("⬅️ Ana Sayfaya Dön"):
        sayfa_degistir("🏠 Ana Sayfa"); st.rerun()

    st.title("🤖 Yapay Zeka Koçun")
    st.write("Ders durumun hakkında konuşabilir, haftalık rapor alabilir ve koçunla sohbet edebilirsin.")

    if st.button("📊 Haftalık Raporumu Ver", type="primary"):
        if gemini_model:
            with st.spinner("Rapor hazırlanıyor..."):
                rapor = gemini_model.generate_content("Öğrencinin haftalık genel ders durumu, görevleri ve eksikleri hakkında motive edici bir koçluk raporu hazırla.").text
                st.markdown(rapor)

    user_query = st.text_input("Koçuna birşey sor (Örn: Bugün hangi konulara çalışmalıyım?):")
    if st.button("Gönder") and user_query:
        if gemini_model:
            with st.spinner("Koç yanıtlıyor..."):
                cevap = gemini_model.generate_content(f"Sen 10. sınıf öğrencisinin samimi ve motive edici koçusun. Öğrencinin sorusu: {user_query}").text
                st.markdown(cevap)