import streamlit as st
import google.generativeai as genai
from datetime import datetime, date
import random
import pypdf
import json
import os

# --- GEMINI API BAĞLANTISI ---
# Streamlit secrets üzerinden API anahtarını güvenli bir şekilde alıyoruz
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # En kararlı ve hızlı modeli seçiyoruz
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    st.error("⚠️ API Anahtarı bulunamadı! Lütfen .streamlit/secrets.toml dosyasına GEMINI_API_KEY eklediğinden emin ol.")

# Sayfa Yapılandırması
st.set_page_config(
    page_title="10. Sınıf Bulut Akıllı Koç",
    page_icon="🎓",
    layout="wide"
)

VERI_DOSYASI = "veriler.json"

# --- VERİLERİ DOSYADAN YÜKLEME / KAYDETME ---
def verileri_yukle():
    if os.path.exists(VERI_DOSYASI):
        try:
            with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "exams": [],
        "homework": [],
        "missing_topics": ["Trigonometri"],
        "completed_tasks": []
    }

def verileri_kaydet():
    veri = {
        "exams": [{"title": e["title"], "date": e["date"].strftime("%Y-%m-%d"), "subject": e["subject"]} for e in st.session_state.exams],
        "homework": [{"title": h["title"], "date": h["date"].strftime("%Y-%m-%d"), "subject": h["subject"], "difficulty": h.get("difficulty", "Orta"), "done": h["done"]} for h in st.session_state.homework],
        "missing_topics": st.session_state.missing_topics,
        "completed_tasks": st.session_state.completed_tasks
    }
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

# --- SESSION STATE BAŞLATMA ---
kayitli_veriler = verileri_yukle()

if "exams" not in st.session_state:
    st.session_state.exams = []
    for e in kayitli_veriler.get("exams", []):
        st.session_state.exams.append({
            "title": e["title"],
            "date": datetime.strptime(e["date"], "%Y-%m-%d").date(),
            "subject": e["subject"]
        })

if "homework" not in st.session_state:
    st.session_state.homework = []
    for h in kayitli_veriler.get("homework", []):
        st.session_state.homework.append({
            "title": h["title"],
            "date": datetime.strptime(h["date"], "%Y-%m-%d").date(),
            "subject": h["subject"],
            "difficulty": h.get("difficulty", "Orta"),
            "done": h["done"]
        })

if "missing_topics" not in st.session_state:
    st.session_state.missing_topics = kayitli_veriler.get("missing_topics", [])

if "completed_tasks" not in st.session_state:
    st.session_state.completed_tasks = kayitli_veriler.get("completed_tasks", [])

# --- YAKLAŞAN SINAV / ÖDEVLER İÇİN UYARI KONTROLÜ ---
bugun = date.today()
acil_uyarilar = []
for exam in st.session_state.exams:
    kalankun = (exam['date'] - bugun).days
    if 0 <= kalankun <= 2:
        acil_uyarilar.append(f"🚨 **DİKKAT!** {exam['subject']} dersinden '{exam['title']}' sınavına son **{kalankun} gün** kaldı!")

for hw in st.session_state.homework:
    if not hw['done']:
        kalankun_hw = (hw['date'] - bugun).days
        if 0 <= kalankun_hw <= 2:
            acil_uyarilar.append(f"⚠️ **ÖDEV UYARISI:** '{hw['title']}' ödevinin teslimine son **{kalankun_hw} gün** kaldı!")

if acil_uyarilar:
    for uyari in acil_uyarilar:
        st.warning(uyari)

# --- SOL MENÜ (NAVİGASYON) ---
st.sidebar.title("🎓 10. Sınıf Bulut Koçu")
secim = st.sidebar.selectbox(
    "Menü Seçenekleri:",
    [
        "🏠 Ana Ekran", 
        "📅 Takvimim", 
        "✍️ Sınavlarım", 
        "📝 Ödevlerim", 
        "📊 Deneme Analizi & Soru Üret", 
        "📁 PDF Ekle & Ders Çalış", 
        "📄 Hızlı PDF Özetle",
        "❌ Eksik Olduğum Konular", 
        "✅ Tamamladığım Görevler"
    ]
)

# --- 1. ANA EKRAN ---
if secim == "🏠 Ana Ekran":
    motivasyonlar = [
        ("Başarı, her gün tekrarlanan küçük çabaların toplamıdır.", "Robert Collier"),
        ("Bugün yaptığın şeyler, yarınki hayatını şekillendirir.", "Anonim"),
        ("Harika işler yapmak için tek yol, yaptığın şeyi sevmektir.", "Steve Jobs"),
        ("Zorluklar, başarıyı çekici kılan süslerdir.", "Moliere"),
        ("Gelecek, bugünden hazırlananlara aittir.", "Malcolm X")
    ]
    gun_index = date.today().toordinal() % len(motivasyonlar)
    soz, yazar = motivasyonlar[gun_index]
    
    st.markdown(f"""
    <div style="
        padding: 25px; 
        border-radius: 12px; 
        background: rgba(74, 144, 226, 0.1); 
        border: 1px solid rgba(100, 100, 100, 0.2); 
        text-align: center; 
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <p style="font-size: 22px; font-style: italic; font-weight: 500; margin-bottom: 8px;">
            "{soz}"
        </p>
        <p style="font-size: 15px; opacity: 0.8; font-weight: 600; letter-spacing: 1px;">
            — {yazar}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("👋 Hoş Geldin!")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Bekleyen Sınavlar", len(st.session_state.exams))
    with col2:
        st.metric("Bekleyen Ödevler", len([h for h in st.session_state.homework if not h['done']]))

# --- 2. TAKVİMİM ---
elif secim == "📅 Takvimim":
    st.header("📅 Takvim ve Yaklaşan Etkinlikler")
    st.markdown("1 veya 2 gün kalmış etkinlikler **kırmızı**, diğerleri **yeşil** renk ile gösterilmektedir.")
    
    tum_etkinlikler = []
    for e in st.session_state.exams:
        tum_etkinlikler.append({"tur": "Sınav", "title": e['title'], "date": e['date'], "subject": e['subject']})
    for h in st.session_state.homework:
        if not h['done']:
            tum_etkinlikler.append({"tur": "Ödev", "title": h['title'], "date": h['date'], "subject": h['subject']})
            
    tum_etkinlikler = sorted(tum_etkinlikler, key=lambda x: x['date'])
    
    if not tum_etkinlikler:
        st.info("Henüz eklenmiş sınav veya ödev bulunmuyor.")
    else:
        for item in tum_etkinlikler:
            kalan = (item['date'] - bugun).days
            border_renk = "#ff4b4b" if 0 <= kalan <= 2 else "#2ecc71"
            
            st.markdown(f"""
            <div style="
                padding: 12px 15px; 
                border-left: 6px solid {border_renk}; 
                background-color: rgba(150, 150, 150, 0.08); 
                margin-bottom: 12px; 
                border-radius: 6px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <span style="font-size: 16px;"><strong>[{item['tur']}] {item['subject']}</strong> - {item['title']}</span><br>
                <span style="font-size: 14px; opacity: 0.8;">Tarih: {item['date']} | Kalan Süre: <b>{kalan} gün</b></span>
            </div>
            """, unsafe_allow_html=True)

# --- 3. SINAVLARIM ---
elif secim == "✍️ Sınavlarım":
    st.header("✍️ Sınavlarım ve Yeni Sınav Ekle")
    
    with st.form("sinav_formu", clear_on_submit=True):
        s_ders = st.selectbox("Ders Seç", ["Matematik", "Fizik", "Kimya", "Biyoloji", "Edebiyat", "Tarih", "Coğrafya", "İngilizce"])
        s_baslik = st.text_input("Sınav Adı / Konusu (Örn: 1. Dönem 2. Yazılı)")
        s_tarih = st.date_input("Sınav Tarihi")
        s_ekle = st.form_submit_button("Sınav Ekle")
        
        if s_ekle:
            if s_baslik:
                st.session_state.exams.append({"title": s_baslik, "date": s_tarih, "subject": s_ders})
                verileri_kaydet()
                st.success("Sınav başarıyla eklendi!")
                st.rerun()
            else:
                st.warning("Lütfen sınav adını boş bırakmayın.")
            
    st.markdown("---")
    st.subheader("Mevcut Sınav Listesi")
    if not st.session_state.exams:
        st.info("Kayıtlı sınav yok.")
    else:
        for i, ex in enumerate(st.session_state.exams):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"📌 **{ex['subject']}** - {ex['title']} ({ex['date']})")
            with col2:
                if st.button("Sil", key=f"del_ex_{i}"):
                    st.session_state.exams.pop(i)
                    verileri_kaydet()
                    st.rerun()

# --- 4. ÖDEVLERİM ---
elif secim == "📝 Ödevlerim":
    st.header("📝 Ödevlerim ve Yeni Ödev Ekle")
    
    with st.form("odev_formu", clear_on_submit=True):
        o_ders = st.selectbox("Ders Seç", ["Matematik", "Fizik", "Kimya", "Biyoloji", "Edebiyat", "Tarih", "Coğrafya", "İngilizce"])
        o_baslik = st.text_input("Ödev Açıklaması / Konusu")
        o_zorluk = st.selectbox("Zorluk Derecesi", ["Kolay", "Orta", "Zor"])
        o_tarih = st.date_input("Teslim Tarihi")
        o_ekle = st.form_submit_button("Ödev Ekle")
        
        if o_ekle:
            if o_baslik:
                st.session_state.homework.append({
                    "title": o_baslik, 
                    "date": o_tarih, 
                    "subject": o_ders, 
                    "difficulty": o_zorluk, 
                    "done": False
                })
                verileri_kaydet()
                st.success("Ödev başarıyla eklendi!")
                st.rerun()
            else:
                st.warning("Lütfen ödev açıklamasını boş bırakmayın.")
            
    st.markdown("---")
    st.subheader("Ödev Listesi & Takibi")
    if not st.session_state.homework:
        st.info("Kayıtlı ödev yok.")
    else:
        for i, hw in enumerate(st.session_state.homework):
            col1, col2 = st.columns([4, 1])
            with col1:
                durum_str = "✅ (Tamamlandı)" if hw['done'] else "⏳ (Bekliyor)"
                zorluk_ikon = {"Kolay": "🟢 Kolay", "Orta": "🟡 Orta", "Zor": "🔴 Zor"}.get(hw.get('difficulty', 'Orta'), "🟡 Orta")
                st.write(f"📌 **{hw['subject']}** - {hw['title']} | *{zorluk_ikon}* (Son: {hw['date']}) {durum_str}")
            with col2:
                if not hw['done']:
                    if st.button("Tamamla", key=f"done_hw_{i}"):
                        st.session_state.homework[i]['done'] = True
                        st.session_state.completed_tasks.append(f"{hw['subject']} ödevi tamamlandı: {hw['title']}")
                        verileri_kaydet()
                        st.rerun()
                else:
                    if st.button("Geri Al", key=f"undone_hw_{i}"):
                        st.session_state.homework[i]['done'] = False
                        verileri_kaydet()
                        st.rerun()

# --- 5. DENEME ANALİZİ & SORU ÜRETİCİ ---
elif secim == "📊 Deneme Analizi & Soru Üret":
    st.header("📊 Deneme Analizi ve Kişiselleştirilmiş Soru Testi Hazırlama")
    st.markdown("Buradan ders seçebilir, eksik konularını inceleyebilir ve yükleyeceğin PDF kaynağına göre Gemini'nin sana özel **test soruları** hazırlamasını sağlayabilirsin!")
    
    secilen_analiz_dersi = st.selectbox("1️⃣ Hangi ders için deneme analizi ve soru üretimi yapmak istiyorsun?", 
                                         ["Matematik", "Fizik", "Kimya", "Biyoloji", "Edebiyat", "Tarih", "Coğrafya", "İngilizce"])
    
    st.markdown("---")
    st.subheader(f"📌 {secilen_analiz_dersi} - Eksik Konu Durumun")
    if st.session_state.missing_topics:
        st.info(f"Kayıtlı eksik konularından bazıları: {', '.join(st.session_state.missing_topics)}")
    else:
        st.success("Bu derste kayıtlı büyük bir eksik konu görünmüyor.")
        
    st.markdown("---")
    st.subheader(f"📂 2️⃣ {secilen_analiz_dersi} Dersi İçin Kaynak PDF Yükle")
    deneme_pdf = st.file_uploader(f"{secilen_analiz_dersi} ders kitabı veya konu anlatım PDF'ini seç", type=["pdf"], key="deneme_pdf_yukle")
    
    soru_tarzi = st.text_input("3️⃣ İstediğin soru tarzı veya özel talimat (Örn: ÖSYM tarzı yeni nesil sorular olsun)")
    
    if deneme_pdf and st.button("🚀 Bana Özel Test Soruları Hazırla"):
        with st.spinner("PDF taranıyor ve eksiklerine göre test soruları hazırlanıyor..."):
            try:
                reader = pypdf.PdfReader(deneme_pdf)
                pdf_metin = ""
                for sayfa in reader.pages:
                    metin = sayfa.extract_text()
                    if metin:
                        pdf_metin += metin + "\n"
                        
                prompt = f"""
                Sen 10. sınıf MEB müfredatına ve ÖSYM tarzına hakim profesyonel bir koç ve öğretmensin.
                Öğrenci {secilen_analiz_dersi} dersinden çalışmak istiyor.
                Öğrencinin eksik olduğu bilinen bazı konular: {st.session_state.missing_topics}
                Öğrencinin özel isteği / soru tarzı talimatı: {soru_tarzi if soru_tarzi else "Standart test soruları"}
                
                Yüklenen PDF Kaynağından Bazı Parçalar:
                {pdf_metin[:12000]}
                
                Lütfen bu PDF içeriğini ve eksik konuları baz alarak öğrenciye çözebileceği harika bir **TEST (Soru Kâğıdı)** hazırla. Soruların altında şıkları (A, B, C, D, E) bulunsun ve en sonda cevap anahtarını ver.
                """
                
                response = gemini_model.generate_content(prompt)
                uretilen_sorular = response.text
                
                st.markdown("### 📝 Yapay Zeka Tarafından Hazırlanan Sana Özel Test:")
                st.markdown(uretilen_sorular)
                
                st.download_button(
                    label="📥 Bu Testi Dosya Olarak İndir (.txt)",
                    data=uretilen_sorular,
                    file_name=f"{secilen_analiz_dersi}_Ozel_Test_Sorulari.txt",
                    mime="text/plain"
                )
                
            except Exception as ex:
                st.error(f"Soru üretilirken hata oluştu: {ex}")

# --- 6. PDF EKLER & DERS ÇALIŞ ---
elif secim == "📁 PDF Ekle & Ders Çalış":
    st.header("📁 Ders Bazlı PDF Ekle ve Özel Anlatım Al")
    
    secilen_ders = st.selectbox("Hangi derse ait PDF yüklemek istiyorsun?", ["Matematik", "Fizik", "Kimya", "Biyoloji", "Edebiyat", "Tarih", "Coğrafya", "Genel"])
    pdf_dosya = st.file_uploader(f"{secilen_ders} dersi için PDF dosyasını seç", type=["pdf"])
    
    if pdf_dosya:
        with st.spinner("PDF okunuyor..."):
            try:
                reader = pypdf.PdfReader(pdf_dosya)
                pdf_metin = ""
                for sayfa in reader.pages:
                    metin = sayfa.extract_text()
                    if metin:
                        pdf_metin += metin + "\n"
                
                st.success(f"{secilen_ders} dersine ait PDF başarıyla yüklendi!")
                
                kullanici_sorusu = st.text_input("Bu PDF hakkında ne öğrenmek istersin?")
                if st.button("Gemini ile Cevapla") and kullanici_sorusu:
                    with st.spinner("Gemini düşünüyor..."):
                        prompt = f"""
                        Sen 10. sınıf MEB müfredatına uygun bir uzmansın. Öğrenci {secilen_ders} dersi için şu PDF dosyasını yükledi.
                        PDF içeriği:
                        {pdf_metin[:12000]}
                        
                        Soru: {kullanici_sorusu}
                        Sadece bu PDF içeriğine göre Türkçe yanıt ver.
                        """
                        response = gemini_model.generate_content(prompt)
                        st.markdown("### 🤖 Yapay Zeka Koçun Cevabı:")
                        st.write(response.text)
            except Exception as ex:
                st.error(f"Hata oluştu: {ex}")

# --- 7. HIZLI PDF ÖZETLE ---
elif secim == "📄 Hızlı PDF Özetle":
    st.header("📄 Doğrudan PDF Özetleme ve Not Çıkarma")
    st.info("Yüklediğin PDF belgesindeki önemli notları ve özetleri Gemini modelinle çıkarırım.")
    
    hizli_pdf = st.file_uploader("Özetlenmesini istediğin PDF dosyasını seç", type=["pdf"])
    
    if hizli_pdf:
        if st.button("PDF'i Özetle ve Notları Çıkar"):
            with st.spinner("PDF analiz ediliyor..."):
                try:
                    reader = pypdf.PdfReader(hizli_pdf)
                    pdf_metin = ""
                    for sayfa in reader.pages:
                        metin = sayfa.extract_text()
                        if metin:
                            pdf_metin += metin + "\n"
                            
                    prompt = f"""
                    Aşağıdaki metni incele ve şunları yap:
                    1. Kısa genel özet.
                    2. En önemli formüller, tanımlar ve anahtar noktalar.
                    3. Kritik bilgiler.
                    
                    PDF İçeriği:
                    {pdf_metin[:12000]}
                    """
                    response = gemini_model.generate_content(prompt)
                    st.markdown("### 📌 PDF Özet ve Önemli Notlar:")
                    st.write(response.text)
                except Exception as ex:
                    st.error(f"Hata oluştu: {ex}")

# --- 8. EKSİK OLDUĞUM KONULAR ---
elif secim == "❌ Eksik Olduğum Konular":
    st.header("❌ Eksik Olduğum Konular Listesi")
    
    yeni_eksik = st.text_input("Eksik olduğun yeni bir konu ekleme alanı:")
    if st.button("Eksik Konu Ekle") and yeni_eksik:
        st.session_state.missing_topics.append(yeni_eksik)
        verileri_kaydet()
        st.success("Eklendi ve kaydedildi!")
        st.rerun()
        
    st.markdown("---")
    if not st.session_state.missing_topics:
        st.success("Harika, hiç eksik konu kalmamış!")
    else:
        for i, konu in enumerate(st.session_state.missing_topics):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"📌 {konu}")
            with col2:
                if st.button("Öğrendim (Sil)", key=f"del_mis_{i}"):
                    st.session_state.missing_topics.pop(i)
                    st.session_state.completed_tasks.append(f"Eksik konu tamamlandı: {konu}")
                    verileri_kaydet()
                    st.rerun()

# --- 9. TAMAMLANAN GÖREVLER ---
elif secim == "✅ Tamamladığım Görevler":
    st.header("✅ Tamamladığın Görevler ve Başarıların")
    if not st.session_state.completed_tasks:
        st.info("Henüz tamamlanan bir görev görünmüyor. Ödevleri bitirdikçe veya eksik konuları öğrendikçe burada listelenecek!")
    else:
        for gorev in st.session_state.completed_tasks:
            st.success(f"✔️ {gorev}")