# Kurulum ve Yapılandırma Rehberi

## Sistem Gereksinimleri
- **OS:** Windows 10/11 veya Linux (Ubuntu 20.04+)
- **Python:** 3.8+
- **Veritabanı:** SQLite (Varsayılan)
- **Diğer:** Docker (Opsiyonel, izleme ve ölçeklendirme için)

## Kurulum Adımları

1. **Repoyu Klonlayın:**
   ```bash
   git clone <repo-url>
   cd SUSTAINAGESERVER
   ```

2. **Sanal Ortam Oluşturun:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Bağımlılıkları Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Çevresel Değişkenleri Ayarlayın:**
   `.env` dosyasını oluşturun ve gerekli ayarları yapın (Örnek: `.env.example`).

## Konfigürasyon

### Veritabanı
Varsayılan olarak `backend/data/sdg_desktop.sqlite` kullanılır. `config/database.py` üzerinden değiştirilebilir.

### İzleme (Monitoring)
Prometheus ve Grafana kurulumu için:
```bash
docker-compose up -d
```
Grafana paneline `http://localhost:3000` adresinden erişebilirsiniz.

### E-posta Ayarları
SMTP ayarları `config.py` veya `.env` dosyasında yapılandırılmalıdır:
- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
