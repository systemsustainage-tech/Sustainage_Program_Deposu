# Geliştirici Kılavuzu

## Proje Yapısı
- `backend/`: Python Flask tabanlı backend kodları.
- `backend/api/`: REST API uç noktaları (JSON).
- `backend/core/`: Veritabanı erişimi, çoklu kiracı (multi-tenant) altyapısı.
- `backend/modules/`: ESG, GRI, TCFD vb. iş modülleri.
- `frontend/`: Vue tabanlı web arayüzü.
- `templates/`: Jinja2 HTML şablonları.
- `static/`: CSS, JS ve resim dosyaları.
- `docs/`: Kullanıcı ve geliştirici dokümantasyonu.

## Yeni Modül Ekleme
1. `backend/modules/` altında yeni bir klasör oluşturun.
2. `__init__.py` ve gerekli manager sınıflarını oluşturun.
3. Veritabanı modellerini tanımlayın veya mevcut şemayı kullanın.
4. İlgili iş mantığını `BaseTenantManager` türeyen bir manager sınıfına koyun.
5. API endpointlerini `backend/api/` veya `web_app.py` içindeki uygun blueprint'e ekleyin.
6. `templates/` altında gerekli HTML sayfalarını ve Vue bileşenlerini oluşturun.

## API Uç Noktaları (Geliştirici Perspektifi)
- Tüm public API'ler `/api/` prefix'i ile başlar.
- Kimlik doğrulama:
  - `X-License-Key` header'ı veya
  - Oturum (session) tabanlı login ile yapılır.
- Çoklu kiracı izolasyonu:
  - `company_id` her istekte zorunludur ve `g.company_id` üzerinden erişilir.
- Detaylı uç nokta listesi için: `docs/api/endpoints.md`.

## Lisans Sistemi ve Güvenlik
Proje, JWT tabanlı bir lisans sistemi kullanır.
- **Middleware**: `web_app.py` içinde `check_license` middleware'i her isteği kontrol eder.
- **JWT Payload**: Lisans anahtarları şu alanları içerir:
  - `company_id`: Lisansın ait olduğu şirket.
  - `allowed_ips`: (Opsiyonel) Erişim izni verilen IP listesi.
  - `allowed_domains`: (Opsiyonel) Erişim izni verilen domain listesi.
  - `exp`: Son kullanma tarihi.
- **Kısıtlamalar**: Eğer `allowed_ips` veya `allowed_domains` tanımlıysa, istek yapan IP/Domain ile uyuşmazsa `403 Forbidden` döner.
- **Kötüye Kullanım (Abuse)**: `LicenseManager` istek sayılarını takip eder. Dakikada 300 istek (varsayılan) aşılırsa lisans otomatik askıya alınır.

## Çoklu Kiracı (Multi-Tenancy)
Veritabanı erişimi `DatabaseManager` üzerinden yapılır.
- **Otomatik Filtreleme**: `backend/core/database.py` içindeki `inject_tenant_filter` fonksiyonu, tüm SELECT/UPDATE/DELETE sorgularına otomatik olarak `company_id` filtresi ekler.
- **Güvenli Kodlama**: Sorgularınızı yazarken `company_id` eklemenize gerek yoktur, sistem `g.company_id` veya `g.license['company_id']` değerini kullanarak bunu sizin yerinize yapar. Ancak `GLOBAL_TABLES` listesindeki tablolar (örn. `companies`, `users`) filtrelenmez.

## Rate Limiting ve CAPTCHA
- **Rate Limiting**: `Flask-Limiter` kullanılır. Varsayılan limit `120 per minute`. Kritik endpointler (login, rapor üretme) için daha katı limitler (`5 per minute`) tanımlanmıştır. Limit aşımında `429 Too Many Requests` döner.
- **CAPTCHA**: Login formunda 3 başarısız denemeden sonra basit matematiksel CAPTCHA devreye girer. `verify_captcha` fonksiyonu ile doğrulanır.

## İzleme (Monitoring)
- **Prometheus**: `/metrics` endpoint'i Prometheus formatında metrikler sunar (CPU, RAM, İstek Sayıları).
- **Grafana**: `monitoring/prometheus/alerts.yml` dosyasında tanımlı kurallara göre alarmlar üretilir.

## Testler
Testleri çalıştırmak için:
```bash
tools\run_ci_checks.bat
```
Komut, birim testleri, çeviri kontrollerini ve temel statik analizleri otomatik çalıştırır.

## Kod Standartları
- PEP 8 standartlarına uyun.
- Tip ipuçlarını (Type Hints) kullanın.
- Her modül için dokümantasyon yazın.

## Deployment
- `docker-compose.yml` dosyasını kullanarak konteynerleri yönetin.
- CI/CD süreçleri için `tools/` altındaki scriptleri kullanın.
