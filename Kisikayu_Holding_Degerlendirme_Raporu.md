# Kisikayu Holding - Sustainage Yazılımı Değerlendirme Raporu

**Tarih:** 27.02.2026  
**Hazırlayan:** Sürdürülebilirlik Bölümü Koordinatörü  
**Konu:** Sustainage Yazılımı Satın Alma Öncesi Teknik ve Sektörel Uyumluluk Denetimi

---

## 1. Yönetici Özeti

Kisikayu Holding bünyesindeki Banka ve 5 ana sanayi sektörü (Çimento, Demir-Çelik, Alüminyum, Gübre, Elektrik/Hidrojen) için "Sustainage" yazılımı üzerinde yapılan detaylı kod incelemesi tamamlanmıştır.

**Genel Karar:** **ŞARTLI UYGUNLUK**

Yazılım, genel sürdürülebilirlik raporlaması (GRI, ESG, SDG, TCFD) konusunda oldukça yetkin ve geniş kapsamlıdır. Ancak Holdingimizin ana faaliyet alanları olan **Bankacılık (Finanse Edilen Emisyonlar)** ve **Ağır Sanayi (Üretim Prosesi Emisyonları)** konularında kritik "hesaplama motoru" eksiklikleri tespit edilmiştir. Yazılım bu haliyle bir "Raporlama Aracı"dır, ancak bir "Mühendislik/Hesaplama Aracı" değildir.

---

## 2. Sektörel Uyumluluk Analizi

### 2.1. Bankacılık ve Finans Sektörü (Kritik Eksiklik)
Holdingimizin bankası için en kritik metrik olan **Scope 3 Kategori 15 (Yatırımlar / Finanse Edilen Emisyonlar)** ve **PCAF (Partnership for Carbon Accounting Financials)** standartları kod tabanında **bulunmamaktadır**.

*   **Mevcut Durum:** `Scope 3` modülü genel bir veri giriş ekranına sahiptir. "Yatırımlar" adında bir kategori açılabilir ancak hesaplama mantığı (Örn: `Kredi Tutarı / Şirket Değeri * Şirket Emisyonu`) kodlanmamıştır.
*   **Risk:** Bankamızın portföy emisyonlarını hesaplamak için bu yazılımı mevcut haliyle kullanamayız. Sadece dışarıda hesaplanan veriyi buraya girebiliriz.
*   **Gereksinim:** PCAF uyumlu bir hesaplama motorunun (Varlık sınıflarına göre ayrılmış) eklenmesi şarttır.

### 2.2. Sanayi Sektörleri (Çimento, Demir-Çelik, Alüminyum, Gübre, Elektrik)
Yazılım, AB Sınırda Karbon Düzenleme Mekanizması (SKDM/CBAM) için özel bir modüle (`backend/modules/cbam`) sahiptir ve Holdingimizin faaliyet gösterdiği 5 sektörü de (Çimento, Demir-Çelik, Alüminyum, Gübre, Elektrik/Hidrojen) kapsamaktadır.

*   **Olumlu Yönler:**
    *   İthalat miktarı ve gömülü emisyon verileri girildiğinde CBAM yükümlülüğünü (Euro cinsinden) hesaplayabilmektedir.
    *   "De-minimis" (eşik değer) muafiyetlerini tanımaktadır.
    *   Doğrudan ve Dolaylı emisyon ayrımı vardır.

*   **Eksiklikler (Proses Derinliği):**
    *   **Çimento:** Klinker üretimi sırasındaki kalsinasyon (`CaCO3 -> CaO + CO2`) kaynaklı proses emisyonlarını hesaplayan formüller yoktur.
    *   **Alüminyum:** Elektroliz sürecindeki `PFC` emisyonlarını veya anot etkisini hesaplayan modüller yoktur.
    *   **Genel:** Yazılım, fabrikalarımızdaki üretim verisinden (hammadde girişi, enerji tüketimi) emisyonu hesaplamak yerine, bizden "ton başına emisyon" verisini hazır istemektedir.

### 2.3. Sınırda Karbon Düzenleme Mekanizması (SKDM / CBAM)
Yazılımda hem `skdm` hem de `cbam` adında iki ayrı modül bulunmaktadır.
*   **CBAM Modülü:** AB uyumluluğu için tasarlanmış, ithalat ve vergi odaklıdır. Doğru yapıdadır.
*   **SKDM Modülü:** İsimlendirme karışıklığı vardır. İçeriği genel karbon yönetimi gibidir. Bu durum kullanıcı tarafında kafa karışıklığı yaratabilir.

---

## 3. Teknik ve Fonksiyonel İnceleme

### 3.1. Modül Çeşitliliği (Güçlü Yön)
Yazılımın en güçlü yönü, 19'dan fazla modülü barındırmasıdır. Aşağıdaki standartlar hazır durumdadır:
*   **Raporlama:** GRI, SASB, TCFD, TNFD, IFRS, IIRC, CSRD, ESRS.
*   **Konular:** Çevre, Sosyal, Yönetişim (ESG), Su, Atık, Biyoçeşitlilik.
*   **Hedefler:** UNGC (Global Compact), SDG (Sürdürülebilir Kalkınma Amaçları).

### 3.2. Dil ve Yerelleştirme
*   Yazılımın Türkçe dil desteği (`locales/tr.json`) tamdır.
*   "Sınırda Karbon", "Kapsam 1-2-3" gibi terimler doğru çevrilmiştir.

### 3.3. Veri Güvenliği ve Altyapı
*   Yazılım kendi sunucularımızda (`/var/www/sustainage`) çalışacak şekilde tasarlanmıştır. Bu, Holdingimizin finansal ve ticari sırlarının güvenliği için uygundur.
*   Veritabanı yapısı (SQLite/PostgreSQL uyumlu) şirketleri izole etmeye uygundur.

---

## 4. Sonuç ve Öneriler

Kisikayu Holding olarak **Sustainage** yazılımını satın alabiliriz, ancak aşağıdaki **"Olmazsa Olmaz"** geliştirmelerin yapılmasını sözleşmeye eklemeliyiz:

1.  **Finans Modülü Eklentisi:** Bankamız için PCAF standartlarına uygun, kredi ve yatırım portföyümüzü analiz edebilen bir "Financed Emissions" hesaplama motoru geliştirilmelidir.
2.  **Sanayi Proses Hesaplayıcıları:** Fabrikalarımız için sadece sonuç girmek yerine, üretim verilerini (klinker miktarı, doğalgaz tüketimi, hurda oranı vb.) girerek emisyonu hesaplayan "Mühendislik Hesaplama Katmanı" eklenmelidir.
3.  **SKDM/CBAM Birleştirmesi:** İki ayrı modül yerine tek ve güçlü bir SKDM modülü yapılandırılmalıdır.

**Karar:** Yazılım altyapısı sağlamdır, ancak Holdingimizin spesifik ihtiyaçları için %20-%30 oranında özel geliştirme (customization) gerektirmektedir.
