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

## 9. Kullanıcı Arayüzü İyileştirmeleri (Tamamlandı)
- [x] **Geri Tuşu Standardizasyonu:** Tüm sayfalarda sağ üst köşeye standart "Geri" butonu eklendi.

## 13. Role Management & Email Service (Session: 2026-01-28)
- [x] **Role Management UI:** Created `roles.html` and `role_edit.html` for managing user roles.
- [x] **Backend Logic:** Updated `user_manager.py` with role CRUD operations (Create, Read, Update, Delete).
- [x] **Route Integration:** Added role management routes to `web_app.py` with error handling.
- [x] **Translations:** Added missing translation keys for role management to `locales/tr.json`.
- [x] **Email Service:** Updated `email_service.py` to use centralized `smtp_config.json`.
- [x] **Deployment:** Deployed all role management files and email service configuration to remote server.
- [x] **Verification:** Verified SMTP connection/login and service status.

## 12. Fixes & Verifications (Session: 2026-01-28)
- [x] **ESRS Schema Fix:** Added missing note columns to `esrs_assessments` locally and remotely.
- [x] **Dashboard Stats Verification:** Verified `active_surveys` and `total_responses` on remote server.
- [x] **Unified Report Logic Fix:** Adapted `/reports/unified` survey query to match SQLite schema.
- [x] **Unified Report Survey Integration:** Survey data is now fetched from `online_surveys` and displayed in the unified report (DOCX).
- [x] **Unified Report ESRS Verification:** Verified `esrs_assessments` notes are correctly saved and retrieved in report generation.
- [x] **Remote Deployment & Verification:** All changes deployed and verified on 72.62.150.207.
- [x] **Survey Module 500 Error Fix:** Removed undefined `mode` variable from `surveys_module` in `web_app.py` that caused NameError.
- [x] **Remote System Check:** Verified `surveys` module status, DB schema, and data counts remotely. Service is running normally.

## 14. Multi-Tenant/SaaS Adaptation (Session: 2026-01-29)
- [x] **Tenant Isolation (Data):** Added `WHERE company_id = ?` filters to all user data queries in `web_app.py` and `remote_web_app.py` (verified via audit).
- [x] **Access Control:** Enforced `@require_company_context` decorator on all module and data routes.
- [x] **Session Security:** Removed insecure `session.get('company_id', 1)` defaults; enforced strict session handling.
- [x] **Super Admin Security:** Fixed audit log queries to prevent cross-tenant data leaks (using JOINs).
- [x] **User Management:** Isolated user listing and editing to ensure admins only see their own company's users.
- [x] **Route Cleanup:** Removed duplicate and scaffold routes; standardized module access.

## 15. Social Module Enhancements (Session: 2026-01-30)
- [x] **Database Update:** Added `employee_satisfaction` and `community_investment` tables with columns for trend analysis.
- [x] **Backend Logic:** Updated `SocialManager` with CRUD operations and `get_satisfaction_trends` for year-wise analysis.
- [x] **Frontend Visualization:** Integrated Chart.js in `social.html` to display Satisfaction Score and Turnover Rate trends.
- [x] **Data Entry:** Added modal forms for adding new social data types.
- [x] **Deployment:** Deployed changes and verified schema on remote server (72.62.150.207).
- [x] **Verification:** Verified data insertion and trend calculation functionality.

## 16. System Stabilization & Survey Fixes (Session: 2026-01-31)
- [x] **SDG Module Fix:** Resolved 500 error (variable shadowing) and fixed button UI/UX.
- [x] **Login Error Fix:** Resolved 500 error by initializing `g.company_id` in `before_request`.
- [x] **Survey Schema Fix:** Recreated missing `online_surveys` tables and added sample survey data on remote.
- [x] **Public Survey Route:** Fixed `public_survey` route logic and added logging for 404 debugging.
- [x] **Template Syntax Fixes:** Corrected malformed Jinja2 conditionals in 7 admin/module templates.
- [x] **Stakeholder Module Fix:** Created missing tables and populated initial statistics.
- [x] **System Health Check:** Added `/system/health` endpoint and pre-flight template validation.
- [x] **Survey Route Verification:** Debugging 404 error on `/survey/sample_survey` resolved. (Added missing `demographics_config` column and inserted sample survey with correct link).

## 17. SaaS Transition - Strict Isolation Phase
- [x] **Remove Default Company ID:** Remove `session['company_id'] = 1` fallbacks in `login` and `verify_2fa` routes to prevent unauthorized access to default company data.
- [x] **Decorator Propagation:** Audit and apply `@require_company_context` to all module routes (Carbon, Energy, Water, etc.) in `web_app.py`.
- [x] **API Isolation:** Ensure all `/api/` endpoints are protected with `@require_company_context`.
- [x] **Deploy & Verify:** Deploy changes to remote server and verify login behavior for users with and without company assignment.
