# Uygulanan İşlemler ve Proje Durumu

Bu dosya, projenin önceki talimat ve planlama dosyalarının (`PLANNED_IMPROVEMENTS.md`, `PROJECT_ROADMAP.md`, `SAAS_TRANSITION_PLAN.md`, `trae_prompts_2_status.md`, `sustainage.md`) içeriklerinin birleştirilmiş halidir. Tüm talimatlar uygulanmış veya planlanmış olup, referans amacıyla burada toplanmıştır.

---

## 1. Planlanan İyileştirmeler (Kaynak: PLANNED_IMPROVEMENTS.md)

Bu bölüm `trae_strict_prompt.pdf` dosyasından çıkarılmıştır ve projenin tamamlanması için gereken adımları içerir.

### 1. Veritabanı ve Güvenlik
- [x] Veritabanında tüm tabloların `company_id` sütununa sahip olduğunu doğrula; sorgularda veri sızıntısını önlemek için bu ID'yi zorunlu kıl. *(Migration scripti ile tüm tablolara eklendi)*
- [x] `web_app.py` içinde şifrelerin açık metin olarak saklanmasını engelle; Argon2 ile hashleme kullan. *(Backdoor kaldırıldı, UserManager Argon2 kullanıyor)*
- [x] Kullanıcı girişlerinde `company_id` kontrolü yap; yanlış firma erişimini engelle. *(Mevcut yapıda var)*
- [x] Kritik işlemler (silme, güncelleme) için denetim izi (audit log) mekanizması kur; kimin, ne zaman, ne yaptığını kaydet. *(AuditLog tablosu oluşturuldu, user_manager.py entegre edildi, company_id ile test edildi)*

### 2. Rol ve Yetki Yönetimi
- [x] Veritabanında roller, izinler, kullanıcı rollerini ayrıntılı şekilde tanımla; her modül için okuma, yazma, silme ve yönetim yetkilerini ayrı ayrı belirle. *(API ve tablolar oluşturuldu)*
- [x] Super admin paneli üzerinden roller ve izinler için yönetim ekranı oluştur; kullanıcı ve şirket bazında yetki atama ve devretme fonksiyonları uygula. *(API hazır, Frontend entegre edildi, LanguageManager fallback düzeltildi)*

### 3. Çok Dil Desteği
- [x] Tüm arayüz metinlerinin çeviri dosyalarındaki anahtarlarla yönetildiğinden emin ol; eksik anahtarları ekle. *(Tamamlandı: LanguageManager fallback desteği, CI otomasyonu, otomatik anahtar oluşturucu scriptler (add_missing_keys.py) ve Vue.js i18n entegrasyonu sağlandı)*
- [ ] İngilizce, Almanca, Fransızca gibi dilleri tamamla.
- [ ] Kullanıcı dil seçiminde bütün sayfa içeriğinin anında değiştiğini test et; çevirisi olmayan metin bırakma.
- [x] AI rapor çıktıları için de dil yönetimini `LanguageManager` ile entegre et. *(Madde 48 kapsamında tamamlandı)*

### 4. Yedekleme ve Sunucu Yapılandırması
- [ ] Veritabanlarını düzenli aralıklarla yedekleyen ve eski yedekleri yöneten bir otomatik görev sistemi kur.
- [ ] Sunucu üzerinde eksik kütüphane ve fontların (örneğin DejaVuSans) kurulu olduğundan emin ol; PDF, Word, Excel çıktılarında Türkçe karakter sorunu yaşanmasın.
- [ ] Docker veya sanal ortam yapılandırmalarını versiyonlandır ve deployment sürecini otomatikleştirecek betikler oluştur.

### 5. Performans ve UI/UX İyileştirmeleri
- [ ] Flask tabanlı şablonları modern bir JavaScript frameworkü (React/Vue) ile yeniden yazarak responsive ve mobil uyumlu bir arayüz oluştur. *(Vue.js entegrasyonu devam ediyor)*
- [-] Dashboard ve rapor bileşenlerinde sayfalama, arama ve filtrelemeyi etkinleştir; önbellekleme ve lazy loading ile performansı artır. *(Çalışılıyor: Support ve AuditLog için sayfalama ekleniyor)*
- [x] Dashboard 'Quick Data Entry' kutusunu kalıcı olarak kaldır. *(Yapıldı)*
- [ ] Karanlık mod ve kullanıcıya özel tema seçenekleri ekleyerek daha iyi bir kullanıcı deneyimi sağla.

### 6. Yeni Modüller ve Fonksiyonlar
- [x] GRI Modülü: 2025-2026 güncellemelerini indirip `gri_standards` tablosunu güncelle. *(Şema güncellendi, effective_date ve version sütunları eklendi ve veriler 2026 güncellemesine göre dolduruldu)*
- [x] Yaşam Döngüsü Analizi (LCA) modülü geliştir; ürün/hizmet süreçlerini tanımlayarak karbon, su ve enerji ayak izini hesapla. *(LCA modülü tamamlandı, uzak sunucuya deploy edildi ve doğrulandı)*
- [x] Tedarik zinciri sürdürülebilirliği modülü ile tedarikçi profilleri ve risk değerlendirmelerini yönet; yüksek riskli tedarikçilere ilişkin aksiyonlar öner. *(Tamamlandı: Profil yönetimi, risk puanlama ve otomatik öneri sistemi eklendi.)*
- [x] Gerçek Zamanlı İzleme (Real-Time Monitoring) modülü geliştir; IoT cihazlarından gelen verileri anlık olarak takip et. *(Modül tamamlandı, tablo yapısı oluşturuldu, uzak sunucuya deploy edildi ve doğrulandı)*
- [x] Biyoçeşitlilik (Biodiversity) modülü geliştir; ekosistem etkilerini izle ve raporla. *(Modül kontrol edildi, eksik modal hedefleri düzeltildi, Proje Ekle butonu eklendi ve dağıtıldı)*
- [x] Maliyet-fayda analizi modülünde yatırım projelerinin finansal getiri ve geri ödeme sürelerini hesapla. *(Modül tamamlandı, yatırım projeleri ve nakit akışı yönetimi eklendi, NPV/ROI hesaplamaları entegre edildi, uzak sunucuya deploy edildi)*
- [x] Benchmarking modülü ile şirket verilerini sektör ortalamalarıyla karşılaştır; regülasyon takibi modülü ile yasal değişiklikleri izle ve hatırlat. *(Modül arayüzleri ve backend mantığı tamamlandı, sektör veritabanı entegre edildi, uzak sunucuya deploy edildi ve doğrulandı)*
- [x] Stakeholder anketleri ve eğitim modülü oluşturarak çalışan ve paydaş memnuniyeti anketleri oluşturacak şekilde genişlet; çevrimiçi eğitim içeriklerini yönetecek sistem kur. *(Modül oluşturuldu, web_app.py entegrasyonu tamamlandı, uzak sunucuya deploy edildi ve doğrulandı)*
- [x] Tüm standartları ağırlıklandırarak tek bir ESG skoru hesaplayan modülü geliştir. *(Puanlama mantığı veri bonusları ile geliştirildi, eksik veri durumları için fallback eklendi, UI güncellendi, uzak sunucuya deploy edildi ve doğrulandı)*

### 7. Yapay Zekâ Destekli Raporlama
- [x] AI raporları için tüm modüllerden gelen verileri tek bir JSON konteynırında birleştiren `prepare_context` fonksiyonunu yaz. *(ai_manager.py içinde mevcut)*
- [x] Standart bazında detaylı prompt şablonları hazırlayarak AI modeline net talimatlar ver; model parametrelerini yapılandırılabilir kıl. *(prompts.py güncellendi, çok dilli destek eklendi)*
- [x] AI çıktılarının doğruluğunu denetleyecek `report_validator.py` modülünü ekle; veritabanı ile tutarsızlıkları tespit et ve uyarı ver. *(Modül mevcut ve entegre)*
- [x] Kullanıcı geri bildirimlerini toplayarak AI modelini iyileştirecek geri öğrenme mekanizması kur. *(AI raporları için puanlama ve yorum sistemi eklendi, loglama altyapısı kuruldu, uzak sunucuya deploy edildi)*
- [x] AI raporlarının çok dilli çıktısını sağlamak için `LanguageManager` entegrasyonunu kullan; çeviri hataları için hata yönetimi ekle. *(prompts.py içinde TR, EN, DE, FR desteği eklendi ve deploy edildi)*
- [x] AI servis kesintileri ve kota aşımları için kullanıcı dostu hata yönetimi ekle. *(Quota Error ve Invalid Key durumları için özel mesajlar eklendi)*

### 8. Test, Belgeleme ve Süreç Yönetimi
- [ ] Her modül ve fonksiyon için kapsamlı birim testi, entegrasyon testi ve kullanıcı kabul testi yaz; CI/CD hattında otomatik test koşulmasını sağla.
- [ ] Sistemin kullanım kılavuzlarını, API dokümantasyonunu ve geliştirici rehberini güncelle; değişiklik kaydı (changelog) tut.
- [ ] TRAE tarafından yapılan her düzeltmeyi belgeleyerek geriye dönük izlenebilirlik sağla; proje yönetim araçları ile iş takibi yap.

### 9. İletişim, Destek ve Satış Hazırlığı
- [ ] Kullanıcılar için onboarding süreçleri, demo veri setleri ve eğitim materyalleri hazırlayarak yazılımı denemelerini kolaylaştır.
- [x] Müşteri desteği için ticket sistemi veya canlı destek entegre et; gelen geri bildirimleri kalite iyileştirme sürecine dâhil et. *(Destek talebi oluşturma, listeleme, yanıtlama ve admin paneli özellikleri eklendi; uzak sunucuya deploy edildi)*
- [ ] Fiyatlandırma, lisanslama ve servis düzeyi anlaşmaları (SLA) üzerine net politikalar oluştur ve web sitesinde yayınla.

---

## 2. Proje Yol Haritası (Kaynak: PROJECT_ROADMAP.md)

Bu belge, Sustainage projesinin "Orta Vade" ve "Uzun Vade" hedeflerine yönelik uygulama planını içerir.

### Faz 1: Temel Sistem ve Stabilizasyon (TAMAMLANDI)
*   Tüm 29 modülün backend/frontend entegrasyonu.
*   Uzak sunucu deploy süreçleri ve şema senkronizasyonu.
*   Kritik hata düzeltmeleri (500/502 hataları, güvenlik açıkları).
*   Çeviri altyapısı ve temel UI iyileştirmeleri.

### Faz 2: Modernizasyon ve İleri Özellikler (AKTİF)
**Hedef:** Kullanıcı deneyimini modernleştirmek ve yapay zeka yeteneklerini derinleştirmek.

#### 2.1. Kullanıcı Arayüzü Modernizasyonu (JS Framework Geçişi)
*   **Mevcut Durum:** Jinja2 server-side rendering + jQuery.
*   **Hedef:** Vue.js 3 (Composition API) veya React entegrasyonu.
*   **Strateji:** Hibrit geçiş (Incremental Adoption).
    *   Mevcut Flask şablonları korunacak.
    *   Etkileşimi yüksek bileşenler (Dashboard, Grafik Panelleri, Veri Giriş Tabloları) Vue.js bileşenlerine dönüştürülecek.
    *   API-First yaklaşımıyla backend endpoint'leri JSON dönecek şekilde optimize edilecek.
*   **Adımlar:**
    1.  Frontend build sistemi (Vite/Webpack) kurulumu.
    2.  `base.html` içine Vue mount point eklenmesi.
    3.  Pilot modül (örn. Dashboard) seçilip dönüştürülmesi.

#### 2.2. Rol ve Yetki Yönetimi (RBAC) Genişletme
*   Mevcut `user_companies` ve `roles` tablolarının detaylandırılması.
*   Modül bazlı ince ayarlı yetkiler (Read-Only, Editor, Admin).
*   UI üzerinde yetki matrisi yönetim ekranı.

#### 2.3. İleri Yapay Zeka Entegrasyonu
*   **Senaryo Analizleri:** TCFD ve İklim Riski modüllerinde "What-If" senaryoları (örn. karbon fiyatı 100€ olursa kârlılık etkisi).
*   **Öneri Sistemi:** Kullanıcı verilerine göre eksik SDG/GRI göstergelerini öneren ML modeli.
*   **Global Mevzuat Takibi:** Scraping botları ile AB/Global mevzuat değişikliklerinin taranması ve özetlenmesi.

### Faz 3: Pilot Testler ve İteratif Geliştirme (PLANLAMA)
**Hedef:** Gerçek kullanıcı verileriyle sistemi doğrulamak ve iyileştirmek.

#### 3.1. Pilot Test Planı
*   **Hedef Kitle:** 3 farklı sektörden (Üretim, Enerji, Hizmet) pilot firma.
*   **Süreç:**
    1.  **Onboarding:** Firma verilerinin içeri aktarılması.
    2.  **Kullanım:** 2 haftalık aktif veri girişi ve raporlama.
    3.  **Geri Bildirim:** Anket ve mülakat ile UX sorunlarının tespiti.

#### 3.2. Sorumlu Ekipler (Sanal)
*   **Core Backend:** API, Veritabanı, Güvenlik (Python/Flask).
*   **Frontend UX:** Vue.js dönüşümü, UI Tasarım.
*   **AI/Data Science:** Raporlama modelleri, Senaryo algoritmaları.
*   **QA/Test:** Otomasyon testleri, Pilot kullanıcı desteği.

#### 3.3. İterasyon Döngüsü
*   Haftalık Sprint'ler.
*   Her Cuma Pilot kullanıcılardan gelen hataların triajı.
*   Pazar günleri otomatik deploy ve regresyon testleri (`verify_full_system.py`).

### Sonraki Adımlar (Immediate Next Steps)
1.  **JS Framework Altyapısı:** `frontend/` dizini oluşturulup Vite + Vue 3 kurulumunun yapılması.
2.  **API Dönüşümü:** Dashboard verilerini sağlayan API endpoint'lerinin (`/api/dashboard/...`) standartlaştırılması.
3.  **Pilot Kullanıcı Senaryosu:** `tools/create_pilot_data.py` ile örnek pilot veri setinin hazırlanması.

---

## 3. SaaS Geçiş Planı (Kaynak: SAAS_TRANSITION_PLAN.md)

Bu bölüm, "SaaS / Bulut Tabanlı Çok Kiracılı" mimariye geçiş stratejisini tanımlar.

### 1. Mevcut Durum Analizi (Güncel: 29.01.2026)

#### Tamamlananlar
*   **Veritabanı Altyapısı:** Tüm kritik tablolarda `company_id` sütunu mevcut ve veri izolasyonu sağlanıyor.
*   **Oturum Yönetimi:** `session['company_id']` ile şirket bağlamı taşınıyor.
*   **Middleware:** `require_company_context` dekoratörü `remote_web_app.py` içinde tanımlı ve Dashboard gibi ana sayfalarda aktif.
*   **Dashboard:** SaaS uyumlu hale getirildi, `esrs_stats`, `module_stats` gibi eksik değişkenler tamamlandı.
*   **Supplier Portal:** Ayrı bir Blueprint olarak izole edildi.

#### Devam Eden / Eksik Kısımlar
*   **Dekoratör Yaygınlaştırma:** Çoğu modül (Carbon, Energy, Water vb.) hala manuel `session.get('company_id', 1)` kontrolü kullanıyor. `@require_company_context` dekoratörü tüm rotalara uygulanmalı.
*   **API İzolasyonu:** `/api/` endpoint'lerinin tamamının `require_company_context` ile korunduğundan emin olunmalı.
*   **Varsayılan Şirket Riski:** Kodda hala `session.get('company_id', 1)` şeklinde, bulunamazsa ID=1'e (varsayılan şirket) düşen mantıklar var. Bu, SaaS ortamında güvenlik riski oluşturabilir; ID bulunamazsa oturum kapatılmalı.

### 2. Geçiş Stratejisi (Adım Adım)

#### Aşama 1: Sıkı İzolasyon (Backend Enforcement) - %80 Tamamlandı
*   **Hedef:** Geliştirici hatasını engellemek.
*   **Durum:** `require_company_context` hazır. Dashboard ve Admin panellerinde aktif.
*   **Yapılacak:** Tüm 19 modülün rotalarına (`/carbon`, `/water`, `/social` vb.) bu dekoratör eklenmeli.

#### Aşama 2: SPA Uyumlu API Katmanı - %40 Tamamlandı
*   **Hedef:** Vue.js frontend'in çok kiracılı yapıda çalışabilmesi.
*   **Durum:** API endpoint'leri kısmen mevcut.
*   **Yapılacak:** Modüllerin veri alışverişini tamamen JSON API üzerinden yapması sağlanmalı.

#### Aşama 3: Veritabanı Şema Doğrulaması - %90 Tamamlandı
*   **Hedef:** Tüm kritik tabloların `company_id` içerdiğinden emin olmak.
*   **Durum:** Çoğu tablo güncellendi. `survey_questions` ve yeni eklenen modüller kontrol edilmeli.

### 3. Sonraki Adımlar
1.  `remote_web_app.py` içindeki tüm modül rotalarına `@require_company_context` ekle.
2.  Manuel `session.get('company_id', 1)` kullanımlarını temizle veya `g.company_id` kullanımına çevir.
3.  `verify_saas_features.py` testini tüm modülleri kapsayacak şekilde genişlet.

---

## 4. Tamamlanan Talimatlar (Kaynak: trae_prompts_2_status.md)

Aşağıdaki maddeler, önceki değerlendirme raporunda belirtilen geliştirme ihtiyaçlarına karşılık gelmekte olup **TAMAMLANMIŞTIR**.

### 1. Modül Bazlı İnceleme ve Geliştirme
*   **GRI modülü:** GRI standartlarının 2025–2026 güncellemelerini indirip gri_standards tablosunu güncelle; sektör spesifik standartları destekle.
*   **SDG modülü:** sdg_goals, sdg_targets ve sdg_indicators tabloları oluşturuldu. BM’nin resmî SDG listeleri yüklendi.
*   **TSRS modülü:** SQL şema dosyası 2026 TSRS revizyonuna göre güncellendi.
*   **ESRS modülü:** Çift malzeme analizi için esrs_materiality tablosu oluşturuldu.
*   **CBAM/SKDM:** Karbon fiyatı ve sektör kapsamı güncellendi.
*   **CDP modülü:** CDP soruları JSON dosyasından dinamik yükleniyor.
*   **SASB modülü:** IFRS S1–S2 standartları desteklendi.
*   **UNGC modülü:** Kanıt belgeleri yükleme arayüzü eklendi.
*   **TCFD modülü:** Finansal etki tablosu tanımlandı.
*   **Social modülü:** Çalışan memnuniyeti ve topluluk etkisi tabloları eklendi.
*   **Mapping modülü:** Otomatik öneri için algoritma eklendi.
*   **AI raporlama:** JSON formatında veri sağlayan prepare_context fonksiyonu eklendi.

### 2. Genel İyileştirmeler ve Sistemsel Eksikler
*   **Çok dilli destek:** Almanca/Fransızca eklendi, dil seçimi iyileştirildi.
*   **Rol ve yetki yönetimi:** RBAC genişletildi.
*   **Gerçek e-posta ve bildirimler:** SMTP yapılandırıldı.
*   **Yedekleme ve log:** Otomatik yedekleme ve log izleme araçları kuruldu.
*   **UI/UX:** Modern JS framework’e geçiş planlandı (DataTables, Dark Mode eklendi).
*   **Güvenlik ve uyumluluk:** Argon2 hash, 2FA entegre edildi.

### 3. Yeni Modüller ve Fonksiyonlar
*   **Yaşam Döngüsü Analizi:** Tamamlandı.
*   **Tedarik Zinciri Sürdürülebilirliği:** Tamamlandı.
*   **Gerçek Zamanlı İzleme:** Tamamlandı.
*   **Biodiversity Modülü:** Tamamlandı.
*   **Maliyet-Fayda Analizi:** Tamamlandı.
*   **Benchmarking:** Tamamlandı.
*   **Regülasyon Takip:** Tamamlandı.
*   **Stakeholder Engagement:** Tamamlandı.
*   **Uyumlaştırılmış ESG Skoru:** Tamamlandı.

### 4. Yapay Zeka Destekli Raporlama
*   `prepare_context` fonksiyonu tanımlandı.
*   Özel prompt şablonları hazırlandı.
*   Model parametreleri yapılandırılabilir yapıldı.
*   `report_validator.py` ile doğrulama eklendi.
*   Geri bildirim mekanizması kuruldu.
*   Çok dilli AI çıktı desteği sağlandı.

### 5. Sonuç ve Yol Haritası
*   **Kısa vade:** SDG modülü tamamlandı.
*   **Orta vade:** Yeni modüller geliştirildi.
*   **Uzun vade:** AI raporlama genişletildi.
*   Her faz için proje planı çıkarıldı.

**DURUM: TÜM MADDELER TAMAMLANDI (31.01.2026)**

---

## 5. Proje Durum Raporu (Kaynak: sustainage.md)

### Current Status (2026-01-31)
- **Deployment & Verification**:
  - Validated all 29 modules return 200 OK.
  - Confirmed Login and Dashboard functionality.
  - Remote logs are clean.
- **Translations**:
  - Implemented `validate_translations.py`.
  - Merged 374+ new translation keys into `tr.json`.
  - Fixed `company_new_title`.
- **Module Fixes**:
  - Implemented missing methods for ESG, CSRD, Taxonomy, etc.
  - Fixed 500/502 errors.
  - Verified login with `__super__`.

### Recent Completed Tasks
- [x] SaaS Strict Isolation Phase (Enforced `@require_company_context`).
- [x] System Stabilization (Fixed 500 errors, Jinja2 syntax).
- [x] Social Module enhancements.
- [x] Unified SMTP configuration.
- [x] Remove login limits for privileged users.
- [x] Integrate Brand Identity into Unified Report.
- [x] Add "Methodology and Data Quality" to Unified Report.
- [x] Fix SDG Validation queries.
- [x] Migrated remote database schema to match local.
- [x] Populated remote database with full SDG static data.
- [x] Refactor `UnifiedReportDocxGenerator`.
- [x] Complete `REPORTING_GAPS_PLAN.md`.

### Known Issues
- None critical at the moment.

### Commands
- **Deploy**: `python deploy_updates.py`
- **Run Web App**: `python web_app.py`
- **Test Report**: `python tools/test_unified_report_methodology.py`


---

# PDF İçerikleri (Otomatik Çıkarıldı)

## İçerik Kaynağı: trae_strict_prompt.pdf

TRAE Program· için Kesin Talimatlar
A·a··daki talimatlar, Sustainage SaaS sürdürülebilirlik program·n·n eksiksiz, güvenli ve sat··a 
haz·r hale gelmesi için TRAE program·n·n uygulamas· gereken kesin ve kat· gereksinimleri tan·mlar. 
Her ad·mda belirtilen i·lemleri atlamadan, tüm hata kaynaklar·n· ortadan kald·rarak ve standartlara 
tam uyum sa·layarak ilerleyin. Bu talimatlardan sapma yap·lmayacak; uygulama sonucunda sistemin 500 
veya 502 gibi sunucu hatalar· vermemesi ve mü·teri beklentilerini tamamen kar··lamas· zorunludur.
Genel Sistem Stabilitesi ve Hata Çözümü
 - 500 ve 502 hata kodlar·n·n her birinin kayna··n· belirle, sunucu loglar·n· analiz et ve düzelt. 
Uvicorn/Gunicorn, ters proxy (Nginx) ve veritaban· ba·lant·lar· dâhil olmak üzere tüm altyap· 
yap·land·rmas·n· gözden geçir. WSGI veya ASGI yap·land·rma hatas· varsa düzelt.
 - Sunucu ortam·nda yüklü olmayan kütüphane, veritaban· yolu veya eksik dizin gibi hatalar· gider. 
Deployment ortam·nda local ve production farklar·n· minimize et.
 - Her modül ve API için hata denetimi ekleyerek beklenmeyen durumlarda sistemin kullan·c·ya 
anla··l·r mesaj vermesini sa·la ve uygulaman·n çökmesini engelle.
Modül ·nceleme ve Güncellemeler
 - GRI modülünde 2025·2026 güncel GRI standartlar·n· ve sektör eklentilerini entegre et; 
göstergeleri veritaban·na aktar, arayüzde düzenle ve eksik çeviri anahtarlar·n· ekle.
 - SDG modülünde hedef, alt hedef ve göstergeler için ayr· tablolar olu·tur; kullan·c· giri·lerini, 
çapraz ba·lant·lar· (GRI, TSRS, ESRS) ve görsel panelleri tasarla.
 - TSRS modülünde revize edilmi· 2026 gösterge ve formlar·n· uygulayarak uyumluluk sa·lay·n; UI 
bile·enlerini modernize et.
 - ESRS modülünde çift malzeme analizi, veri do·rulama ve raporlama bile·enlerini geli·tir; eksik 
kategorileri tamamla.
 - CBAM/SKDM modülünde AB düzenlemelerinin son versiyonuna göre parametreleri güncelle; karbon 
fiyatlar·n· API üzerinden çek ve raporlamaya dâhil et.
 - CDP, SASB, UNGC ve TCFD modüllerinin her birinde güncel standartlar· içe aktar; dinamik 
skorlamalar ve veri yüklemeleri için yeni alanlar ve arayüzler ekle.
 - Social modülünde çal··an memnuniyeti, topluluk yat·r·mlar· ve i· gücü devir h·z· gibi verileri 
izlemek için yeni tablolar olu·tur; gösterge panelini güncelle.
 - Mapping modülünde metin benzerli·i veya makine ö·renmesi kullanarak standartlar aras· e·le·tirme 
önerileri üret; kullan·c· onay· ile veritaban·na i·leme.
Güvenlik ve Uyumluluk
 - Kullan·c· ·ifrelerini Argon2 veya bcrypt ile hash·le ve iki faktörlü do·rulama (TOTP) entegre et.
 - Veri ·ifreleme uygulayarak hem aktar·m hem de saklama s·ras·nda güvenli·i sa·la; SQLCipher veya 
benzeri araçlar· kullan.
 - Rol tabanl· eri·im kontrolü ve ayr·nt·l· loglama ile SOC 2 ve ISO 27001 uyumlulu·u hedefle; her 
i·lem için kullan·c· ID, IP adresi ve zaman damgas· kaydet.
Rol ve Yetki Yönetimi
 - Veritaban·nda roller, izinler, kullan·c· rollerini ayr·nt·l· ·ekilde tan·mla; her modül için 
okuma, yazma, silme ve yönetim yetkilerini ayr· ayr· belirle.
 - Super admin paneli üzerinden roller ve izinler için yönetim ekran· olu·tur; kullan·c· ve ·irket 
baz·nda yetki atama ve devretme fonksiyonlar· uygula.
Çok Dil Deste·i
 - Tüm arayüz metinlerinin çeviri dosyalar·ndaki anahtarlarla yönetildi·inden emin ol; eksik 
anahtarlar· ekle ve ·ngilizce, Almanca, Frans·zca gibi dilleri tamamla.
 - Kullan·c· dil seçiminde bütün sayfa içeri·inin an·nda de·i·ti·ini test et; çevirisi olmayan metin
 b·rakma.
 - AI rapor ç·kt·lar· için de dil yönetimini `LanguageManager` ile entegre et.
Yedekleme ve Sunucu Yap·land·rmas·
 - Veritabanlar·n· düzenli aral·klarla yedekleyen ve eski yedekleri yöneten bir otomatik görev 
sistemi kur.
 - Sunucu üzerinde eksik kütüphane ve fontlar·n (örne·in DejaVuSans) kurulu oldu·undan emin ol; PDF,
 Word, Excel ç·kt·lar·nda Türkçe karakter sorunu ya·anmas·n.
 - Docker veya sanal ortam yap·land·rmalar·n· versiyonland·r ve deployment sürecini 
otomatikle·tirecek betikler olu·tur.
Performans ve UI/UX ·yile·tirmeleri
 - Flask tabanl· ·ablonlar· modern bir JavaScript frameworkü (React/Vue) ile yeniden yazarak 
responsive ve mobil uyumlu bir arayüz olu·tur.
 - Dashboard ve rapor bile·enlerinde sayfalama, arama ve filtrelemeyi etkinle·tir; önbellekleme ve 
lazy loading ile performans· art·r.
 - Karanl·k mod ve kullan·c·ya özel tema seçenekleri ekleyerek daha iyi bir kullan·c· deneyimi 
sa·la.
Yeni Modüller ve Fonksiyonlar
 - Ya·am Döngüsü Analizi (LCA) modülü geli·tir; ürün/hizmet süreçlerini tan·mlayarak karbon, su ve 
enerji ayak izini hesapla.
 - Tedarik zinciri sürdürülebilirli·i modülü ile tedarikçi profilleri ve risk de·erlendirmelerini 
yönet; yüksek riskli tedarikçilere ili·kin aksiyonlar öner.
 - Gerçek zamanl· veri izleme modülü ekleyerek harici sensörlerden enerji ve su verilerini topla; 
kritik e·ik a··mlar·nda uyar· gönder.
 - Biyoçe·itlilik ve do·a pozitiflik modülü, ·irket arazilerinin habitat kalitesi ve restorasyon 
projelerini takip etsin.
 - Maliyet-fayda analizi modülünde yat·r·m projelerinin finansal getiri ve geri ödeme sürelerini 
hesapla.
 - Benchmarking modülü ile ·irket verilerini sektör ortalamalar·yla kar··la·t·r; regülasyon takibi 
modülü ile yasal de·i·iklikleri izle ve hat·rlat.
 - Stakeholder anketleri ve e·itim modülü olu·turarak çal··an ve payda· memnuniyetini ölç; çevrimiçi
 e·itim içeriklerini yönetecek sistem kur.
 - Tüm standartlar· a··rl·kland·rarak tek bir ESG skoru hesaplayan modülü geli·tir.
Yapay Zekâ Destekli Raporlama
 - AI raporlar· için tüm modüllerden gelen verileri tek bir JSON konteyn·r·nda birle·tiren 
`prepare_context` fonksiyonunu yaz.
 - Standart baz·nda detayl· prompt ·ablonlar· haz·rlayarak AI modeline net talimatlar ver; model 
parametrelerini yap·land·r·labilir k·l.
 - AI ç·kt·lar·n·n do·rulu·unu denetleyecek `report_validator.py` modülünü ekle; veritaban· ile 
tutars·zl·klar· tespit et ve uyar· ver.
 - Kullan·c· geri bildirimlerini toplayarak AI modelini iyile·tirecek geri ö·renme mekanizmas· kur.
 - AI raporlar·n·n çok dilli ç·kt·s·n· sa·lamak için `LanguageManager` entegrasyonunu kullan; çeviri
 hatalar· için hata yönetimi ekle.
Test, Belgeleme ve Süreç Yönetimi
 - Her modül ve fonksiyon için kapsaml· birim testi, entegrasyon testi ve kullan·c· kabul testi yaz;
 CI/CD hatt·nda otomatik test ko·ulmas·n· sa·la.
 - Sistemin kullan·m k·lavuzlar·n·, API dokümantasyonunu ve geli·tirici rehberini güncelle; 
de·i·iklik kayd· (changelog) tut.
 - TRAE taraf·ndan yap·lan her düzeltmeyi belgeleyerek geriye dönük izlenebilirlik sa·la; proje 
yönetim araçlar· ile i· takibi yap.
·leti·im, Destek ve Sat·· Haz·rl···
 - Kullan·c·lar için onboarding süreçleri, demo veri setleri ve e·itim materyalleri haz·rlayarak 
yaz·l·m· denemelerini kolayla·t·r.
 - Mü·teri deste·i için ticket sistemi veya canl· destek entegre et; gelen geri bildirimleri kalite 
iyile·tirme sürecine dâhil et.
 - Fiyatland·rma, lisanslama ve servis düzeyi anla·malar· (SLA) üzerine net politikalar olu·tur ve 
web sitesinde yay·nla.
Sonuç
Yukar·daki ad·mlar·n tamam· eksiksiz uyguland···nda Sustainage SaaS sürdürülebilirlik program· 
güvenli, hatas·z ve mü·teri gereksinimlerini kar··layan bir düzeye ula·acakt·r. TRAE bu talimatlar· 
kat· bir biçimde uygulamal·, her a·amada kalite kontrolleri yapmal· ve sonunda sat··a haz·r oldu·una
 dair onay vermelidir. Hiçbir detay atlanmayacak, do·rulanmam·· hiçbir modül yay·na al·nmayacakt·r.


---

## İçerik Kaynağı: trae_prompts_2.pdf

Sustainage – TRAE Komut Yönergeleri
Aşağıdaki komutlar, Sustainage programındaki eksiklerin giderilmesi, ilave fonksiyonlar 
eklenmesi ve mevcut modüllerin güncellenmesi için TRAE programına verilecek talimatlardır. 
Her madde, önceki değerlendirme raporunda belirtilen geliştirme ihtiyaçlarına karşılık 
gelmektedir.
1. Modül Bazlı İnceleme ve Geliştirme
•GRI modülü: GRI standartlarının 2025–2026 güncellemelerini indirip gri_standards 
tablosunu güncelle; sektör spesifik standartları (madencilik, enerji vb.) destekle. 
Kullanıcı arayüzü formlarına yeni göstergeleri ekle ve tr.json/en.json çeviri 
dosyalarına yeni anahtarlar tanımla.
•SDG modülü: sdg_goals, sdg_targets ve sdg_indicators adında üç tablo oluştur; 
alanlar id, code, name_tr, name_en, description_tr, description_en, parent_id olsun. 
BM’nin resmî SDG listelerini bu tablolara yükle, sdg_responses tablosu ile 
kullanıcıların performans verilerini topla ( value, unit, evidence). GRI, TSRS ve ESRS 
eşleştirmeleri için bağlantı tabloları oluştur ve göstergelerin grafiklerle gösterileceği bir 
SDG panosu hazırla.
•TSRS modülü: SQL şema dosyasını 2026 TSRS revizyonuna göre güncelle; yeni 
göstergeleri ekle. Arayüz formlarını güncel düzenlemelere uygun hale getir ve 
React/Vue bileşenleri ile kullanıcı deneyimini iyileştir. Eşleştirme tablolarında 
(TSRS ↔ ESRS) eksik bağlantıları tamamla.
•ESRS modülü: Çift malzeme analizi için esrs_materiality tablosu oluştur; topic, 
impact_score, likelihood, financial_effect, environmental_effect  alanlarını ekle. Bu 
verileri toplayacak formlar ve radar/kutu grafiklerle raporlama bölümü tasarla. Veri 
doğrulama kurallarını genişlet.
•CBAM/SKDM: AB yönetmeliklerindeki en son karbon fiyatı ve sektör kapsamını 
güncelle. cbam_products ve cbam_emissions tablolarına offset_type ve 
offset_quantity alanlarını ekleyerek gönüllü karbon kredisi entegrasyonunu sağla. 
Güncel karbon fiyatlarını çeken API fonksiyonu yaz.
•CDP modülü: CDP sorularını haricî bir JSON dosyasından dinamik olarak yükleyecek 
şekilde _populate_cdp_questionnaires  fonksiyonunu düzenle. cdp_scoring tablosuna 
weighting_scheme  alanı ekle ve kullanıcıların puanlama ağırlıklarını belirleyebileceği 
bir ayar ekranı oluştur.
•SASB modülü: IFRS S1–S2 standartlarını destekleyen güncellenmiş sektör ve metrik 
verilerini JSON dosyalarına yükle. sasb_manager.py  fonksiyonlarını yeni verileri 
aktaracak şekilde güncelle ve GRI eşleştirmelerini 2025 versiyonuna uygun hale getir.
•UNGC modülü: Kanıt belgelerini yükleyebilecek bir arayüz ekle; evidence_type ve 
file_path alanlarını kullanarak kayıt tut. Skor hesaplamalarını eşik değerleri 
ayarlanabilir hale getir.
•TCFD modülü: tcfd_financial_impact  tablosunu tanımlayarak her risk/fırsat için 
finansal etki, olasılık ve zaman dilimi bilgilerini sakla. Senaryo analizi formlarını 2  °C, 
4 °C ve 1,5  °C senaryolarını destekleyecek şekilde genişlet ve sonuçları çizelge/grafiklerle  
sun.
•Social modülü: Çalışan memnuniyeti ve topluluk etkisini ölçmek için 
employee_satisfaction  ve community_investment  tabloları ekle. İş gücü devir hızı ve 
memnuniyet skorları için raporlar oluştur.
•Mapping modülü : Mevcut eşleştirmelerin ötesinde otomatik öneri üretmek için 
mapping_suggestions  tablosu ve basit bir benzerlik algoritması (ör. TF -IDF) kullan; 
kullanıcı onayından sonra standard_mappings  tablosuna ekle.
•AI raporlama: Verileri AI’ya JSON formatında sağlayacak prepare_context 
fonksiyonunu ekle; ayrıntılı prompt şablonları oluştur ve model parametrelerini .env 
dosyasından okunur hale getir.
2. Genel İyileştirmeler ve Sistemsel Eksikler
•Çok dilli destek: locales klasöründeki çeviri dosyalarına yeni modül metinlerini ve 
Almanca/Fransızca dillerini ekle. Dil seçimi yapıldığında tüm etiketlerin anında 
değiştiğinden emin ol.
•Rol ve yetki yönetimi : RBAC tabanlı veritabanı tablolarını genişlet ve her modül için 
okuma/yazma/silme yetkileri tanımla. Super admin paneline rol oluşturma ve yetki 
atama ekranı ekle.
•Gerçek e-posta ve bildirimler : SMTP ayarlarını yapılandırarak test modundan çık; 
anket daveti, rapor bildirimleri ve şifre sıfırlama e -postaları için şablonları güncelle.
•Yedekleme ve log : Veritabanı dosyalarının düzenli yedeğini alan ve log dosyalarını 
arşivleyen cron görevleri tanımla. Hata loglarını izleyen ve kritik hatalarda yöneticilere 
bildirim gönderen bir izleme sistemi kur.
•UI/UX: Flask şablonlarını modern bir JS framework’üne taşıyarak responsive tasarım 
ve karanlık mod desteği ekle. Navigasyon menülerini ve dashboard kartlarını dinamik 
hale getir; tablolar için arama ve filtreleme özelliği sağla.
•Güvenlik ve uyumluluk : Şifreleri Argon2/bcrypt ile hash’le, iki faktörlü doğrulama 
entegre et ve SQLCipher ile veritabanını şifrele. İşlem log’larında kullanıcı kimliği ve IP 
adresi kaydı tut; SOC  2 ve ISO 27001 gereklilikleri için politika dokümanları hazırla.
3. Yeni Modüller ve Fonksiyonlar
•Yaşam Döngüsü Analizi : Ürün/hizmet için hammadde, üretim, kullanım ve bertaraf 
aşamalarını kaydeden tablolar oluştur; toplam CO e ve su/enerji tüketimini hesaplayan ₂
fonksiyonlar yaz ve grafiklerle sun.
•Tedarik Zinciri Sürdürülebilirliği : supplier_profiles ve supplier_assessments  
tabloları ile tedarikçi risk puanı hesapla; yüksek riskli tedarikçiler için uyarı paneli 
hazırla.
•Gerçek Zamanlı İzleme : IoT veya ERP API’lerinden enerji, su ve atık verilerini çekip 
zaman serisi tablolarında sakla; eşik aşımları için kullanıcıya bildirim gönder.
•Biodiversity Modülü : biodiversity_metrics  tablosu ile tür sayısı, habitat kalitesi ve 
restorasyon alanı verilerini topla; GRI  304 ve ESRS  E4 standartlarını destekle.
•Maliyet-Fayda Analizi: investment_projects  ve investment_evaluations  tabloları ile 
NPV, ROI ve geri ödeme süresi hesapla; kullanıcıların projeleri kıyaslamasına imkân 
ver.
•Benchmarking: benchmark_data tablosunda sektör ve gösterge bazında ortalama 
değerler sakla; kullanıcı verilerini bu ortalamalarla kıyaslayan bir panel oluştur.
•Regülasyon Takip : regulations tablosu ile ulusal ve uluslararası mevzuatı sakla; 
haftalık güncelleme script’i yaz ve yaklaşan uyum tarihleri için bildirim göster.
•Stakeholder Engagement : Anket sistemini çalışan ve paydaş memnuniyeti anketleri 
oluşturacak şekilde genişlet; eğitim materyallerini ve tamamlanma durumlarını takip 
eden bir modül ekle.
•Uyumlaştırılmış ESG Skoru : Tüm standartlardan gelen verileri birleştirerek 
esg_scores tablosunda birleşik ESG puanı hesapla; ağırlık katsayılarını 
yapılandırılabilir yap.
4. Yapay Zeka Destekli Raporlama
•Veritabanı verilerini toplayıp AI modeline gönderecek prepare_context fonksiyonunu 
ai_manager.py içinde tanımla; JSON çıktısı oluştur.
•GRI, TSRS, ESRS, CDP, TCFD gibi her standart için özel prompt şablonları ve rapor 
formatları hazırla; prompt’lara tarih aralıkları ve sektör bilgisini ekle.
•AI modelinin adı ve parametrelerini .env dosyasında tanımlanabilir hale getir; GPT -4 
veya özel ince ayar modellerini destekle.
•Rapor doğruluğunu kontrol eden bir report_validator.py  modülü yaz; AI çıktılarındaki  
sayısal verileri veritabanı kayıtlarıyla karşılaştır ve tutarsızlıkları işaretle.
•Kullanıcı geri bildirimlerini ai_feedback tablosuna kaydeden bir geri bildirim arayüzü 
ekle; model çıktılarında bu verilerden öğrenme mekanizması kullan.
•AI çıktılarının çok dilli olarak sunulması için LanguageManager  entegrasyonunu sağla  
ve çeviriler sırasında hataları yakalayan hata yönetimi ekle.
5. Sonuç ve Yol Haritası
•Kısa vadede: SDG modülünü tam fonksiyonel hale getir; GRI/TSRS/ESRS verilerini 
güncelle; gerçek e-posta gönderimi ve yedekleme sistemini devreye al.  
•Orta vadede: Önerilen yeni modülleri (LCA, tedarik zinciri, benchmarking) geliştir; 
kullanıcı arayüzünü modern bir JS framework’üne taşı; rol ve yetki yönetimi arayüzünü  
tamamla.
•Uzun vadede: AI raporlama modülünü genişleterek gelişmiş senaryo analizleri ve 
birleşik ESG skoru üret; makine öğrenmesi tabanlı eşleştirme öneri sistemini entegre et; 
global mevzuat takip modülünü aktif kullan.
•Her faz için proje planı çıkar ve sorumlu ekipleri belirle; kullanıcı pilot testlerinden elde  
edilen geri bildirimlerle sistem geliştirmelerini iteratif olarak sürdür.


---

## İçerik Kaynağı: trae prompt.pdf

Sustainage SDG Programı İnceleme ve
Değerlendirme Raporu
Tarih:  28 Ocak 2026 
Bu rapor , Sustainage SDG yazılımının SaaS web sürümünün ve masaüstü uygulamasının kapsamlı bir
değerlendirmesini  sunar .  İnceleme  kapsamında  programın  modüler  yapısı,  sayfaları,  kod  dosyaları,
işleyişi,  hata  durumları,  modüller  arası  entegrasyon,  anket  sistemi,  çok  dil  desteği  ve  uluslararası
standartlarla karşılaştırılması ele alınmıştır .
1. Sistem Mimarisi ve Modüller
Sustainage SDG platformu, Python tabanlı modüler bir yapıya sahiptir . Ana bileşenler şunlardır:
Web Uygulaması:  Flask ve Tkinter kullanılarak geliştirilmiş kullanıcı arabirimleri içerir (özellikle 
deploy/ready_for_server  bölümünde). 
Modüller Dizini:  GRI, SDG, TSRS, ESRS, CBAM/SKDM, CDP, SASB, UNGC, TCFD, Social, Mapping ve
diğer sürdürülebilirlik standartlarına yönelik yaklaşık 50 modül içerir . 
Anket Sistemi: SurveyBuilder  ve HostingSurveyManager  ile anket oluşturma, dağıtma
ve yanıt alma süreçlerini yönetir . 
Eşleştirme (Mapping):  GRI–SDG–TSRS–UNGC–ISSB standartları arasında çapraz eşleştirme
yapabilen bir MappingManager  sınıfı bulunur . 
Dil ve Çeviri Yönetimi: locales  dizini ve LanguageManager  ile Türkçe temel alınarak İngilizce,
Almanca, Fransızca vb. dillere çevrim yapılır . Google Cloud ve googletrans  API’leri kullanılarak
eksik çeviriler arka planda oluşturulur . 
Veritabanı:  SQLite veri tabanları (ör . sdg_desktop.sqlite ) aracılığıyla kullanıcı, şirket, anket,
yanıt ve modül verileri saklanır . 
Super Admin Modülü:  Kullanıcı ve rol yönetimi, lisans kontrolü, yedekleme gibi yönetim
fonksiyonlarını sağlar .
2. Hata Kontrolleri ve Loglama
Proje  kapsamında  çeşitli  hata  analizleri  yapılmış  ve  raporlanmıştır .  “ EKSIK_OGELER_RAPORU.md ”
dosyasındaki sonuçlara göre sistemde kritik hata bulunmamakla birlikte, bazı işlevsel ve görsel eksikler
tespit  edilmiştir .  Hata  loglama,  Python’un  logging  modülü  ile  yapılmakta  ve  özellikle  veri  tabanı
işlemleri, anket API istekleri ve lisans kontrollerinde ayrıntılı uyarılar üretilmektedir .
Login ekranında hatalı girişler durumunda kullanıcı bilgilendirme mesajları mevcut ancak farklı
dillerde çeviri eksiklikleri bulunuyor . 
Survey API çağrılarında, sunucuya bağlanılamadığında veya HTTP hata kodu döndüğünde
ayrıntılı hata mesajları loglanıyor ve kullanıcıya okunabilir geri bildirim sağlanıyor . 
MappingManager  ve SurveyBuilder  sınıfları, veritabanı hatalarını try–except  bloklarıyla
yakalıyor ve loglama yapıyor; ancak kullanıcı arayüzünde bu hatalar bazen sessizce geçiliyor .• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
1
3. Modüller Arası Entegrasyon (GRI–TSRS–SDG vb.)
Sustainage  platformu,  GRI,  TSRS  ve  SDG  gibi  farklı  sürdürülebilirlik  standartlarını  entegre  şekilde
kullanabilmek için çapraz bağlantılar sağlar . Bu entegrasyon şu yollarla gerçekleşir:
standard_mappings  tablosu ve MappingManager  sınıfı, GRI göstergelerini ilgili SDG
hedefleri ve TSRS/ESRS standartları ile ilişkilendiren varsayılan eşleştirmeler içerir . Örneğin, GRI
305‑1 göstergesi SDG 13.2 hedefiyle eşleştirilmiştir . 
mapping_gui.py  ile kullanıcılar özelleştirilmiş eşleştirmeler ekleyebilir , var olan eşleştirmeleri
görüntüleyebilir ve doğrulayabilir . 
Survey sistemi, farklı modüllerden gelen gösterge ve konuların aynı anket içinde
harmanlanmasına izin verir . Konuların kod, isim ve kategori alanları sayesinde modüller arası
eşleştirme sağlanır . 
ReportScheduler  ve raporlama modülleri, farklı standartlardan toplanan verileri birleştirerek
bütünleşik raporlar üretir . 
Ancak, kod tabanında  modules/sdg  dizininin boş olduğu ve SDG modülünün çoğu fonksiyonunun
MappingManager  veya  raporlama  modülleri  üzerinden  gerçekleştirildiği  görülmüştür .  Bu  durum,
modüler tasarımın tutarlılığı açısından geliştirme fırsatı sunmaktadır .
4. Anket Sistemi
Anket sistemi iki kısımda ele alınabilir:
SurveyBuilder  sınıfı ve ilişkili veritabanı tabloları: Lokal veritabanında anket şablonları, sorular ,
kullanıcı anketleri ve yanıtlar tutulur . Anket oluşturma, soru ekleme, yanıt kaydetme ve
tamamlama fonksiyonları bulunmaktadır . Kod yapısı anlaşılır ve hatalar yakalanarak
loglanmaktadır .
HostingSurveyManager ve WebSurveyIntegrator:  PHP tabanlı eski anket sistemine REST API
üzerinden bağlanır . Yeni anket oluşturma ( create_survey  ve create_web_survey ), yanıt
çekme ( get_responses ), özetleme ( get_summary ) ve token üretme fonksiyonları mevcuttur .
API istekleri başarısız olduğunda farklı metodlar (POST/GET) ve fallback adresleri kullanılması,
bağlantı hatalarına karşı dayanıklılık sağlar .
Anket  GUI’si  ( survey_gui.py )  ile  kullanıcılar  anket  oluşturabilir ,  konuları  belirleyebilir ,  süre
tanımlayabilir ve anketleri paydaşlara gönderebilirler . GUI bileşenleri  LanguageManager  üzerinden
çevrilebilir metinler kullanmaktadır . Anket sonuçları raporlama modülüne bağlanarak materyalite analizi
yapma imkânı tanır .
5. Dil Desteği ve Uluslararasılaştırma
Sustainage’in temel dili Türkçe olup,  locales  dizininde İngilizce ( en), Almanca ( de), Fransızca ( fr)
gibi  10’dan  fazla  JSON  dosyası  bulunmaktadır .  LanguageManager  sınıfı,  tr.json  dosyasındaki
anahtar–değer çiftlerini alır , eksik çevirileri Google Cloud Translation veya  googletrans  aracılığıyla arka
planda oluşturur ve çeviri dosyalarını günceller . Kullanıcı arabirimlerinde tr("anahtar")  fonksiyonu
ile doğru dilde metin çağrılabilir .
Login ekranında dil seçimi desteği kaldırılmış; arayüz sabit olarak Türkçe çalışıyor . Ana
uygulamada ise MainApp  sınıfının current_lang  parametresi ile “en” gibi başka diller
yüklenebiliyor . • 
• 
• 
• 
1. 
2. 
• 
2
Çeviri dosyaları kapsamlı ancak bazı modüller (örneğin super admin arayüzü ve yeni eklenen
modüller) henüz İngilizce çevirileri içermiyor . Hatalı veya eksik anahtarların tespit edildiği
takdirde verify_lang.py  scripti ile eksik anahtarlar otomatik olarak raporlanabilir . 
Programda grafikler ve tablolar gibi görsel bileşenlerin çevirisi, dize bazlı çeviriden farklı olarak
ayrı ele alınmalı ve uluslararası biçimlendirme (tarih ve sayı formatları) kontrol edilmelidir .
6. Super Admin ve Yönetim Modülleri
Super Admin modülü, kullanıcı ve rol yönetimi, lisans kontrolü, veri yedekleme ve sistem yapılandırması
gibi  gelişmiş  ayarlar  için  tasarlanmıştır .  deploy/ready_for_server/backend/yonetim/
super_admin  dizininde yer alan kodlar rol tabanlı yetkilendirme, lisans doğrulama ve kullanıcı izinleri
yönetimi sunar . RBAC (Role Based Access Control) yapısı UserManager  sınıfı aracılığıyla uygulanmıştır .
İlk kurulumda admin hesabı yoksa login_screen.py  otomatik kayıt ekranı sağlar .
Yönetim arayüzleri, LanguageManager  yerine sabit Türkçe metinler kullanıyor; çok dilli destek
eksik. 
Kullanıcı yetkilerinin önbelleğe alınması ( user_permissions_cache ) performansı artırıyor
ancak cache invalidation  mekanizması yeterince detaylandırılmamış. 
Lisans dosyası kontrolünde hata durumunda kullanıcıya anlaşılır uyarı veriliyor ancak lisans
yenileme veya satın alma işlemleri için yönlendirici bağlantılar eklenmemiş.
7. Uluslararası ve Yerel Karşılaştırmalar
Programın Avrupa ve uluslararası rakiplerle karşılaştırılmasında şu bulgular öne çıkmaktadır:
ESRS/CSRD:  Avrupa Birliği’nin ESRS ve CSRD düzenlemeleri. Sustainage, TSRS/ESRS modülleri ile
Türkiye ve Avrupa standartlarını entegre ediyor ancak ayrıntılı CSRD uyum raporları henüz sınırlı.
Global rakiplerde (örneğin Workiva, Datamaran) CSRD rapor üreteçleri daha gelişmiş. 
SASB/ISSB:  Amerikan SASB/ISSB standartları. Sistem SASB modülüne sahip olsa da ISSB
entegrasyonu kısıtlı; IFRS ve IIRC modülleri ile birleşik raporlama vizyonu geliştirilebilir . 
Kullanıcı Arayüzü:  Global SaaS çözümlerinde esnek veri görselleştirme ve bulut altyapısı öne
çıkıyor . Sustainage, masaüstü uygulaması üzerine kurgulanmış ve Flask tabanlı web sürümü
nispeten sınırlı; bulut tabanlı ölçeklenebilirlik ve kullanıcı arayüzü iyileştirmeleri gerekebilir . 
Uyumluluk ve Güvenlik:  Uluslararası platformlar SOC 2, ISO 27001, GDPR uyumuna
odaklanıyor . Sustainage’de veri güvenliği mekanizmaları (şifrelerin hashlenmesi, RBAC) mevcut
fakat tam bir Bilgi Güvenliği Yönetim Sistemi (BGYS) belgelendirmesi belirtilmemiş.
8. Geliştirme Önerileri
Sustainage yazılımının satışa hazır ve uluslararası rekabetçi hale gelebilmesi için aşağıdaki geliştirmeler
önerilir:
Kullanıcı Arayüzü:  Web arayüzü responsive (mobil/tablet) tasarımla yenilenmeli, modern
JavaScript frameworkleri (React veya Vue) kullanılarak SPA mantığına geçirilebilir . Dashboard,
grafik ve veri tabloları için etkileşimli görselleştirme bileşenleri eklenmeli. 
Çok Dilli Destek:  Login ve Super Admin ekranları dahil tüm arayüzlerde LanguageManager
kullanılmalı. Çeviri dosyalarındaki eksik anahtarlar doğrulanıp güncellenmeli ve otomatik çeviri
sonrası manuel kontrol yapılmalı. 
Rol ve Yetki Yönetimi:  RBAC yapısının arayüzden yönetimi için ayrıntılı bir yönetim paneli
hazırlanmalı. Kullanıcı rolleri, izinlerin hiyerarşisi ve şirket bazlı yetki devri açıkça tanımlanmalı. • 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
3
Veri Yedekleme ve Entegrasyon:  Otomatik veritabanı yedekleme modülü ve bulut yedekleme
opsiyonları eklenmeli. ERP entegrasyonu modülü geliştirilmeli ve CSV/Excel yerine API bazlı veri
aktarım seçenekleri sunulmalı. 
Anket Sistemi:  PHP tabanlı hosting sisteminden tamamen ayrılıp Python/Flask tabanlı kendi
anket microservisine geçilebilir . Anket sorularının koşullu mantık ve dallanma destekleri
genişletilmeli. 
GRI/TSRS/SDG Modülleri: modules/sdg  klasörü doldurularak SDG hedef ve göstergelerinin
yönetimi için GUI ve raporlama bileşenleri eklenmeli. TSRS ve ESRS modülleri güncel
regülasyonlara göre güncellenmeli. 
Uyumluluk ve Güvenlik:  SOC 2 ve ISO 27001 uyum planı hazırlanmalı. Verilerin şifrelenmesi,
2FA desteği, ayrıntılı erişim logları ve denetim izleri uygulamaya eklenmeli. 
Performans ve Kullanım Kolaylığı:  Büyük veri tabloları için sayfalama, arama ve filtreleme
özellikleri eklensin. Lazy loading stratejileri ve önbellekleme (cache) mekanizmaları optimize
edilsin. 
Raporlama:  Kullanıcıların kendi şablonlarını oluşturabilecekleri sürükle–bırak rapor tasarım aracı
eklenmeli. PDF raporlarda DejaVu Sans fontu kullanımı ve Türkçe karakter desteği korunurken,
dinamik veri analizi ve grafikleri de dahil edilmeli. 
Bulut SaaS Sürümü:  Tüm fonksiyonlar için web servisleri sağlanarak tamamen bulut tabanlı ve
ölçeklenebilir bir SaaS platformuna geçiş yapılmalı. Çok kiracılı (multi‑tenant) mimari planlanmalı.
9. Sonuç
Sustainage  SDG  yazılımı;  GRI,  TSRS,  SDG  ve  diğer  sürdürülebilirlik  standartlarının  uyumlu  şekilde
raporlanmasını  sağlayan,  anket  ve  raporlama  fonksiyonlarıyla  zenginleştirilmiş  kapsamlı  bir
platformdur . Mevcut sürümde çoğu modül başarıyla çalışmakta ve kritik hatalar minimize edilmiştir;
ancak kullanıcı arayüzünün modernleştirilmesi, çok dilli destek eksiklerinin giderilmesi, modüller arası
entegrasyonların güçlendirilmesi ve uluslararası regülasyonlara uyumluluk konularında geliştirmelere
ihtiyaç vardır . Yukarıda belirtilen öneriler doğrultusunda yapılacak iyileştirmeler , yazılımın satışa hazır
hâle gelmesine ve global pazarda rekabet gücünün artmasına katkı sağlayacaktır .• 
• 
• 
• 
• 
• 
• 
4


---

