
# Sustainage Geliştirici Kılavuzu

## 1. Mimari Genel Bakış
Sustainage, modüler, çok kiracılı (multi-tenant) ve ölçeklenebilir bir sürdürülebilirlik yönetim platformudur. Backend Flask (Python) üzerine kuruludur, Frontend ise Vue.js ve Jinja2 şablonları kullanır.

### Temel Bileşenler
- **Web App (`web_app.py`)**: Uygulamanın giriş noktası. Rota tanımları, middleware'ler ve modül yüklemeleri burada yapılır.
- **Database Manager (`backend/core/database_manager.py`)**: Merkezi veritabanı bağlantı havuzu ve sorgu yöneticisi.
- **Modül Sistemi (`backend/modules/`)**: Her işlevsellik (GRI, Karbon, Su vb.) ayrı bir modül olarak tasarlanmıştır.

## 2. Multi-Tenancy (Çoklu Kiracı) Yapısı
Sistem, **Shared Database, Shared Schema** yaklaşımını kullanır.
- Tüm veriler aynı veritabanı ve tablolarda tutulur.
- Veri izolasyonu `company_id` sütunu ile sağlanır.
- **Güvenlik**: `backend/core/database.py` içindeki `inject_tenant_filter` fonksiyonu, tüm SQL sorgularına (SELECT, INSERT, UPDATE, DELETE) otomatik olarak aktif kullanıcının `company_id` değerini enjekte eder.
- **Geliştirici Notu**: Modül geliştirirken sorgularınıza manuel olarak `WHERE company_id = ?` eklemenize gerek yoktur, ancak tablonuzda `company_id` sütunu olduğundan emin olmalısınız.

## 3. Lisanslama ve Güvenlik
- **Lisans Yönetimi**: `backend/yonetim/license_manager.py` tarafından yönetilir.
- **Kısıtlamalar**: Lisanslar, `allowed_ips` ve `allowed_domains` kısıtlamalarına sahip olabilir. Bu kontroller `web_app.py` middleware'inde yapılır.
- **Rate Limiting**: Flask-Limiter kullanılarak API bazlı hız sınırları uygulanır. (Örn: Login için 20/dk).
- **Kötüye Kullanım**: Lisans sınırları aşıldığında veya şüpheli trafik tespit edildiğinde lisans otomatik olarak askıya alınabilir.

## 4. Modül Geliştirme Standartları
Yeni bir modül eklerken şu adımları izleyin:
1. **Dizin**: `backend/modules/<modul_adi>/` altında klasör oluşturun.
2. **Manager**: İş mantığını yönetecek bir `Manager` sınıfı yazın ve `BaseTenantManager`'dan türetin.
3. **Veritabanı**: Tablolarınızı `Manager.__init__` içinde `CREATE TABLE IF NOT EXISTS` ile oluşturun. `company_id` sütununu unutmayın!
4. **Kayıt**: Modülü `web_app.py` içinde kaydedin veya Blueprint kullanın.

## 5. Test ve CI/CD Süreçleri
- **Testler**: `tests/` dizininde `unittest` tabanlı testler bulunur.
  - Çalıştırma: `python -m unittest discover tests`
- **CI/CD**: GitHub Actions (`.github/workflows/ci.yml`) her push işleminde:
  - Unit testleri çalıştırır.
  - Linter kontrollerini yapar.
  - Güvenlik taramalarını gerçekleştirir.

## 6. Çeviri (i18n) Sistemi
- Dil dosyaları: `backend/locales/{tr,en,de}.json`
- Kullanım (Backend): `lang('key', 'Default Value')`
- Kullanım (Frontend/Vue): `$t('key')`
- Yeni anahtar eklediğinizde `tools/audit_translations.py` (veya benzeri) ile eksikleri tarayabilirsiniz.
