# Yapılacak Düzenlemeler ve İyileştirmeler

Bu dosya, projenin sıralı geliştirme planını içerir. Her madde tamamlanıp, deploy edilip, test edildikten sonra üzeri çizilerek bir sonrakine geçilecektir.

## 1. ESRS Modülü Detaylandırması
- [x] **Veritabanı Şeması:** `esrs_assessments` tablosuna detaylı not alanlarının (Yönetişim, Strateji, Risk/Etki, Metrikler) eklenmesi.
- [x] **Backend Mantığı:** `ESRSManager` sınıfının yeni alanları destekleyecek şekilde güncellenmesi (`update_assessment`, `get_assessment_details`).
- [x] **Arayüz (UI):** `esrs.html` modal penceresinin detaylı metin girişlerini (textarea) alacak şekilde düzenlenmesi.
- [x] **Route:** `web_app.py` içindeki güncelleme endpoint'inin yeni verileri işlemesi.
- [x] **Deploy ve Test:** Değişikliklerin sunucuya atılması ve kontrollerin yapılması.

## 2. Kapsamlı Emisyon Faktörleri Kütüphanesi (DEFRA/IPCC)
- [x] **Veri Yapısı:** Emisyon faktörleri için veritabanı tablosunun (`emission_factors`) tasarlanması (Kaynak, Kategori, Birim, Faktör vb.). `category` kolonu eklendi.
- [x] **Veri İçe Aktarma:** Geniş kapsamlı uluslararası verilerin (DEFRA/IPCC) SQL formatına getirilmesi ve sisteme gömülmesi. `CarbonManager` sınıfına import özelliği eklendi ve veriler yüklendi.
- [x] **Deploy:** Veriler uzak sunucuya başarıyla yüklendi.

## 3. Çifte Önemlilik (Double Materiality) Matrisi
- [x] **Veri Modeli:** Finansal önemlilik ve Etki önemliliği puanlarının ayrı ayrı tutulması. (`materiality_topics` tablosuna `stakeholder_impact` ve `business_impact` eklendi).
- [x] **Görselleştirme:** X ve Y eksenli detaylı matris grafiğinin (Chart.js) `prioritization.html` sayfasına eklenmesi.
- [x] **Arayüz:** Kullanıcının her iki boyutu da puanlayabileceği veri giriş ekranı.
- [x] **Deploy ve Test:** Kodun sunucuya atılması ve çalışır durumda olduğunun teyidi. (Doğru IP: 72.62.150.207 ile yapıldı).

## 4. Sistem Genel Kontrolleri
- [x] **Deploy Sonrası Doğrulama:** Tüm modüllerin HTTP 200 döndürdüğünün teyidi. (verify_full_system.py ile doğrulandı).

## 5. PHP Anket Sistemi Entegrasyonu (KRİTİK)
- [x] **Dosya Hazırlığı:** `c:\sdg\anket` klasöründeki PHP dosyalarının (api.php, index.php vb.) sunucuya deploy için hazırlanması. (c:\SUSTAINAGESERVER\anket hazırlandı, config.php güncellendi)
- [x] **Sunucu Konfigürasyonu:** Sunucuda `/var/www/sustainage/anket` dizininin oluşturulması ve Nginx ayarlarının (PHP işleme) yapılması. (`deploy/nginx_anket_location.conf` oluşturuldu)
- [x] **Veritabanı Ayarı:** `config.php` dosyasının sunucu veritabanı bilgilerine göre düzenlenmesi. (SQLite ve path ayarı yapıldı)
- [x] **Entegrasyon Testi:** Python backend (`HostingSurveyManager`) ile PHP frontend arasındaki iletişimin test edilmesi. (Kod seviyesinde entegrasyon sağlandı, canlı test deploy sonrası yapılacak)

## 6. Dashboard Entegrasyonu (Item 6)
- [x] **Anket Verileri:** Dashboard'da anket özet verilerinin (aktif anket sayısı, yanıt sayısı) gösterilmesi.
- [x] **Modül Durumları:** 19 modülün doluluk oranlarının dashboard'a yansıtılması. (`dashboard.html` güncellendi ve `DashboardStatsManager` entegre edildi)

## 7. Birleşik Rapor Güncellemesi (Item 7)
- [x] **Rapor Endpoint:** `/reports/unified` endpoint'inin anket verilerini de kapsayacak şekilde güncellenmesi.

## 8. c:\sdg Klasör Analizi ve Eksiklerin Giderilmesi (ÖNCELİKLİ)
Bu bölüm `c:\sdg` klasörü ile yapılan karşılaştırma sonucu tespit edilen eksikleri içerir.

### 8.1. Kritik Yapılandırma ve Veri Dosyaları
- [x] **SMTP Konfigürasyonu:** `config\smtp_config.json` dosyasının eksikliği. (E-posta gönderimi için kritik)
- [x] **GRI Göstergeleri:** `data\gri_indicators.json` dosyasının eksikliği. (GRI raporlaması için kritik)
- [x] **SDG Verileri:** `data\sdg_data.json` dosyasının eksikliği. (SDG modülü için kritik)
- [x] **Python Bağımlılık Kontrolü:** `data\.deps_ok.json` dosyasının durumu.

### 8.2. Eksik Modüller (Python Backend)
Masaüstü sürümde olup web sürümünde (`modules/` veya `backend/modules/`) bulunmayan modüllerin taşınması:
- [x] **CBAM Modülü:** `modules\cbam` klasörü ve `modules\cbam_manager.py`.
- [x] **AI Modülleri:** `modules\ai` ve `modules\ai_reports` klasörleri.
- [x] **Gelişmiş Hesaplama:** `modules\advanced_calculation` ve `modules\advanced_inventory`.
- [x] **Denetçi Modülü:** `modules\auditor` klasörü.
- [x] **CDP Modülü:** `modules\cdp` klasörü.
- [x] **TSRS Dashboard:** `modules\tsrs_dashboard.py`.
- [x] **Şirket Yönetimi:** `modules\company` ve `modules\company_info`.

### 8.3. Eksik Raporlama Şablonları ve Verileri
`data\reports` altında bulunan eksik rapor şablonları:
- [x] **AI Raporları:** `data\reports\ai`
- [x] **Çevresel Raporlar:** `data\reports\karbon`, `data\reports\su`, `data\reports\atik`
- [x] **Standart Raporlar:** `data\reports\gri`, `data\reports\cdp`, `data\reports\tcfd`, `data\reports\esrs`

### 8.4. Dokümantasyon Dosyaları
- [x] **Docs Klasörü:** `docs\` altındaki tüm alt klasörlerin (eu_cbam, gri, ungc vb.) taşınması.
