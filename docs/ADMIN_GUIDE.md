
# Sustainage Sistem Yöneticisi Kılavuzu

## 1. Sistem Gereksinimleri
- **OS**: Linux (Ubuntu 20.04+ önerilir) veya Windows Server
- **Runtime**: Python 3.9+, Node.js 16+
- **Veritabanı**: SQLite (Varsayılan) veya PostgreSQL (Prodüksiyon için yapılandırılabilir)

## 2. Kurulum ve Yapılandırma
Temel ayarlar `backend/config/` altındaki dosyalarda ve Çevresel Değişkenlerde (ENV) tutulur.

### Önemli Çevresel Değişkenler
- `SECRET_KEY`: Oturum güvenliği için rastgele uzun string.
- `DB_POOL_SIZE`: Veritabanı bağlantı havuzu boyutu (Varsayılan: 100).
- `JWT_SECRET`: Lisans anahtarları için imza sırrı.

## 3. İzleme ve Performans (Monitoring)
Sistem, **Prometheus** ve **Grafana** ile entegre çalışır.

### Prometheus Yapılandırması
`prometheus.yml` dosyası kök dizinde bulunur. Uygulama `/metrics` adresinden metrikleri sunar.
- **CPU/RAM Kullanımı**
- **İstek Sayıları ve Yanıt Süreleri**
- **Hata Oranları (5xx, 429)**

### Grafana
Prometheus'u veri kaynağı olarak ekleyin ve `monitoring/grafana_dashboard.json` (varsa) dosyasını import ederek panelleri oluşturun.

### Uyarılar (Alerts)
Kritik eşikler (Örn: %90 CPU, >%5 Hata Oranı) aşıldığında sistem yöneticisine bildirim gönderilir.

## 4. Güvenlik Ayarları
- **Rate Limiting**: `Flask-Limiter` ile yönetilir.
  - **Global Limit**: 120 istek/dakika ve 1000 istek/saat.
  - **Ağır İşlemler**: Rapor oluşturma gibi işlemler 20 istek/dakika ile sınırlandırılmıştır.
  - **Kapsam**: Limitler IP adresi bazlıdır, giriş yapmış kullanıcılar için `user_id` bazlı daha hassas takip yapılır.
- **CAPTCHA**: Başarısız giriş denemeleri (3+) sonrası otomatik devreye girer.
- **2FA**: Kullanıcılar profil ayarlarından Google Authenticator ile 2FA'yı etkinleştirebilir.
- **Lisans Güvenliği**:
  - **IP/Domain Kısıtlaması**: Lisans anahtarına tanımlı `allowed_ips` ve `allowed_domains` listeleri middleware seviyesinde her istekte kontrol edilir.
  - **İhlal Takibi**: İzin verilmeyen IP/Domain erişim denemeleri güvenlik loglarına (Audit Log) "LICENSE_VIOLATION" olarak kaydedilir.
  - **Kötüye Kullanım**: Anormal istek sayıları tespit edildiğinde lisans otomatik olarak askıya alınabilir.

## 5. Yedekleme ve Kurtarma
- Veritabanı (`sdg_prod.sqlite`) günlük olarak yedeklenmelidir.
- `tools/backup_sustainage.ps1` (veya .sh) scripti ile otomatik yedekleme zamanlanabilir.
- Geri yükleme için `backend/core/database_manager.py` içindeki `restore` fonksiyonları kullanılabilir.
