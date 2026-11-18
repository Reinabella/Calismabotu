import streamlit as st
import google.generativeai as genai
from datetime import datetime, date
import random
import json
import os
from fpdf import FPDF

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="10. Sınıf Bulut Koçu",
    page_icon="🎓",
    layout="centered"
)

# --- GEMINI API BAĞLANTISI ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    gemini_model = None

VERI_DOSYASI = "veriler.json"

# --- VERİ YÖNETİMİ (GÜVENLİ) ---
def verileri_yukle():
    default_data = {
        "exams": [{"ders": "Matematik", "konu": "Fonksiyonlar", "tarih": "2027-06-17"}],
        "homework": [{"ders": "Fizik", "aciklama": "Elektrik Akımı Testleri", "tarih": "2026-07-15"}],
        "mistakes": [],
        "daily_program": "",
        "program_subjects": ["Matematik", "Fizik", "Kimya"]
    }
    if os.path.exists(VERI_DOSYASI):
        try:
            with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Eksik alanları tamamla
                for k, v in default_data.items():
                    if k not in data:
                        data[k] = v
                # Sınav ve ödevlerin 'tarih' anahtarına sahip olduğundan emin ol
                for s in data.get("exams", []):
                    if "tarih" not in s:
                        s["tarih"] = "2027-06-17"
                for o in data.get("homework", []):
                    if "tarih" not in o:
                        o["tarih"] = "2026-07-15"
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

# --- SOL MENÜ (SIDEBAR) ---
sayfalar = ["🏠 Ana Sayfa", "📅 Günlük Program", "❌ Yanlışlarım", "🔍 Yanlışlarına Dön", "📚 Konu Tekrarı (PDF)", "📝 Sınav & Ödev Ekle"]
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
        st.markdown(f"**📅 {en_yakin_sinav}**")
    with c3:
        if st.button("Sınava çalış", key="btn_sinav_calis", use_container_width=True):
            sayfa_degistir("📚 Konu Tekrarı (PDF)")
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
            sayfa_degistir("📝 Sınav & Ödev Ekle")
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
            sayfa_degistir("❌ Yanlışlarım")
            st.rerun()
    with b3:
        if st.button("🔍 Yanlışlarına dön", use_container_width=True):
            sayfa_degistir("🔍 Yanlışlarına Dön")
            st.rerun()
    with b4:
        if st.button("📚 Konu tekrarı", use_container_width=True):
            sayfa_degistir("📚 Konu Tekrarı (PDF)")
            st.rerun()

# ==========================================
# 2. GÜNLÜK PROGRAM SAYFASI
# ==========================================
elif st.session_state.aktif_sayfa == "📅 Günlük Program":
    if st.button("⬅️ Ana Sayfaya Dön"):
        sayfa_degistir("🏠 Ana Sayfa")
        st.rerun()
        
    st.title("📅 Akıllı Günlük Program")
    st.write("Yapay zeka yaklaşan ödevlerini ve geçmiş yanlışlarını analiz ederek sana özel günlük ders programı hazırlar.")

    if st.button("✨ Bugünün Programını Oluştur", type="primary"):
        if not gemini_model:
            st.error("API Anahtarı bağlı değil!")
        else:
            with st.spinner("Koçun ödevlerini ve eksik konularını inceliyor..."):
                odev_listesi = ", ".join([f"{o.get('ders', '')} ({o.get('aciklama', '')})" for o in st.session_state.veri["homework"]])
                yanlis_listesi = ", ".join([f"{y.get('ders', '')} - {y.get('konu', '')} ({y.get('yanlis_sayisi', 0)} yanlış)" for y in st.session_state.veri["mistakes"]])
                
                prompt = f"""
                Sen 10. sınıf öğrencisine koçluk yapan bir eğitim asistanısın.
                Öğrencinin yaklaşan ödevleri: {odev_listesi if odev_listesi else 'Yok'}
                Öğrencinin son yanlış yaptığı konular: {yanlis_listesi if yanlis_listesi else 'Henüz kayıt yok'}
                
                Buna göre öğrenciye bugün için saatlik/bloklar halinde uygulanabilir, motive edici bir günlük çalışma programı hazırla. 
                Ayrıca yanıtının en son satırına sadece bugün çalışılacak 3 ana dersin adını virgülle ayırarak 'DERSLER: Ders1, Ders2, Ders3' formatında yaz.
                """
                cevap = gemini_model.generate_content(prompt).text
                st.session_state.veri["daily_program"] = cevap
                
                for satir in cevap.split("\n"):
                    if "DERSLER:" in satir:
                        dersler = [d.strip() for d in satir.split("DERSLER:")[1].split(",")]
                        st.session_state.veri["program_subjects"] = dersler
                
                verileri_kaydet(st.session_state.veri)

    if st.session_state.veri.get("daily_program"):
        st.markdown(st.session_state.veri["daily_program"])

# ==========================================
# 3. YANLIŞLARIM SAYFASI
# ==========================================
elif st.session_state.aktif_sayfa == "❌ Yanlışlarım":
    if st.button("⬅️ Ana Sayfaya Dön"):
        sayfa_degistir("🏠 Ana Sayfa")
        st.rerun()

    st.title("❌ Yanlışlarım & Haftalık Takip")
    st.write("Bugünkü programında yer alan derslerden kaç yanlış yaptığını ve hangi konuda zorlandığını kaydet.")

    bugunku_dersler = st.session_state.veri.get("program_subjects", ["Matematik", "Fizik", "Kimya", "Biyoloji", "Edebiyat"])
    
    with st.form("yanlis_ekle_form"):
        secilen_ders = st.selectbox("Bugünkü Programdaki Ders", bugunku_dersler)
        konu_adi = st.text_input("Yanlış Yaptığın Konu (Örn: Polinomlar, Kaldırma Kuvveti)")
        yanlis_sayisi = st.number_input("Kaç Yanlış Yaptın?", min_value=1, max_value=100, value=1)
        kaydet_btn = st.form_submit_button("Hafızaya Kaydet")

        if kaydet_btn and konu_adi:
            yeni_kayit = {
                "tarih": str(date.today()),
                "ders": secilen_ders,
                "konu": konu_adi,
                "yanlis_sayisi": yanlis_sayisi
            }
            st.session_state.veri["mistakes"].append(yeni_kayit)
            verileri_kaydet(st.session_state.veri)
            st.success(f"{secilen_ders} - {konu_adi} ({yanlis_sayisi} yanlış) haftalık hafızaya eklendi!")

    st.subheader("📊 Bu Hafta Kaydedilen Yanlışlar")
    yanlislar = st.session_state.veri.get("mistakes", [])
    if yanlislar:
        for y in reversed(yanlislar):
            st.info(f"**{y.get('tarih', '')}** | **{y.get('ders', '')}** — {y.get('konu', '')} (**{y.get('yanlis_sayisi', 0)} Yanlış**)")
    else:
        st.caption("Henüz kaydedilmiş bir yanlışın yok.")

# ==========================================
# 4. YANLIŞLARINA DÖN
# ==========================================
elif st.session_state.aktif_sayfa == "🔍 Yanlışlarına Dön":
    if st.button("⬅️ Ana Sayfaya Dön"):
        sayfa_degistir("🏠 Ana Sayfa")
        st.rerun()

    st.title("🔍 Eksik Konu Analizi & Eylem Planı")
    yanlislar = st.session_state.veri.get("mistakes", [])

    if not yanlislar:
        st.warning("Önce 'Yanlışlarını not al' kısmından eksik olduğun konuları girmelisin.")
    else:
        st.subheader("🚨 Eksik Olduğun Konular Listesi")
        for y in yanlislar:
            st.write(f"- **{y.get('ders', '')}**: {y.get('konu', '')} ({y.get('yanlis_sayisi', 0)} yanlış)")

        if st.button("🧠 Yapay Zeka ile Eksik Analizi ve Görev Belirle", type="primary"):
            if gemini_model:
                with st.spinner("Bilgi seviyen ölçülüyor..."):
                    ozet_veri = json.dumps(yanlislar, ensure_ascii=False)
                    prompt = f"""
                    Aşağıda bir 10. sınıf öğrencisinin kaydettiği yanlış sayıları ve konular var:
                    {ozet_veri}
                    1. Öğrencinin bu konulardaki bilgi seviyesini yorumla.
                    2. Eksiklerini kapatması için somut, adım adım yapması gerekenleri listele.
                    """
                    analiz = gemini_model.generate_content(prompt).text
                    st.markdown(analiz)

# ==========================================
# 5. KONU TEKRARI (MİNİK PDF)
# ==========================================
elif st.session_state.aktif_sayfa == "📚 Konu Tekrarı (PDF)":
    if st.button("⬅️ Ana Sayfaya Dön"):
        sayfa_degistir("🏠 Ana Sayfa")
        st.rerun()

    st.title("📚 Akıllı Konu Tekrarı & Minik PDF")
    st.write("Eksik olduğun konuyu seç veya yaz; yapay zeka sana özel özet anlatsın ve indirilebilir minik PDF hazırlasın.")

    yanlislar = st.session_state.veri.get("mistakes", [])
    oneri_konular = [f"{y.get('ders', '')} - {y.get('konu', '')}" for y in yanlislar]
    
    konu_secimi = st.text_input(
        "Tekrar Etmek İstediğin Ders ve Konu",
        value=oneri_konular[-1] if oneri_konular else "10. Sınıf Matematik - Fonksiyonlar"
    )

    if st.button("📄 Konuyu Anlat ve Minik PDF Hazırla", type="primary"):
        if gemini_model and konu_secimi:
            with st.spinner("Özel ders notun ve PDF dosyan hazırlanıyor..."):
                prompt = f"""
                10. sınıf seviyesinde '{konu_secimi}' konusunu öğrenciye çok net, akılda kalıcı, formülleri ve püf noktaları içeren bir özet ders notu şeklinde anlat.
                """
                ders_notu = gemini_model.generate_content(prompt).text
                st.markdown(ders_notu)
                
                pdf_bytes = pdf_olustur(f"10. Sinif Konu Ozeti: {konu_secimi}", ders_notu)
                st.download_button(
                    label="📥 Minik Ders Notu PDF'ini İndir",
                    data=pdf_bytes,
                    file_name="konu_ozeti.pdf",
                    mime="application/pdf"
                )

# ==========================================
# 6. SINAV & ÖDEV YÖNETİMİ
# ==========================================
elif st.session_state.aktif_sayfa == "📝 Sınav & Ödev Ekle":
    if st.button("⬅️ Ana Sayfaya Dön"):
        sayfa_degistir("🏠 Ana Sayfa")
        st.rerun()

    st.title("📝 Sınav ve Ödev Yönetimi")
    
    tab1, tab2 = st.tabs(["Ödevler", "Sınavlar"])
    
    with tab1:
        with st.form("odev_form"):
            o_ders = st.text_input("Ders Adı")
            o_aciklama = st.text_input("Ödev Açıklaması")
            o_tarih = st.date_input("Teslim Tarihi")
            if st.form_submit_button("Ödev Ekle") and o_ders:
                st.session_state.veri["homework"].append({
                    "ders": o_ders, "aciklama": o_aciklama, "tarih": str(o_tarih)
                })
                verileri_kaydet(st.session_state.veri)
                st.rerun()
        
        for i, o in enumerate(st.session_state.veri["homework"]):
            col1, col2 = st.columns([4, 1])
            col1.write(f"📌 **{o.get('ders', '')}**: {o.get('aciklama', '')} (Tarih: {o.get('tarih', '')})")
            if col2.button("Sil", key=f"sil_odev_{i}"):
                st.session_state.veri["homework"].pop(i)
                verileri_kaydet(st.session_state.veri)
                st.rerun()

    with tab2:
        with st.form("sinav_form"):
            s_ders = st.text_input("Sınav Dersi")
            s_konu = st.text_input("Sınav Konuları")
            s_tarih = st.date_input("Sınav Tarihi")
            if st.form_submit_button("Sınav Ekle") and s_ders:
                st.session_state.veri["exams"].append({
                    "ders": s_ders, "konu": s_konu, "tarih": str(s_tarih)
                })
                verileri_kaydet(st.session_state.veri)
                st.rerun()

        for i, s in enumerate(st.session_state.veri["exams"]):
            col1, col2 = st.columns([4, 1])
            col1.write(f"🎯 **{s.get('ders', '')}**: {s.get('konu', '')} (Tarih: {s.get('tarih', '')})")
            if col2.button("Sil", key=f"sil_sinav_{i}"):
                st.session_state.veri["exams"].pop(i)
                verileri_kaydet(st.session_state.veri)
                st.rerun()