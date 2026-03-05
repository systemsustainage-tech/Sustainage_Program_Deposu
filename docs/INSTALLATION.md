
# Sustainage Kurulum Kılavuzu

Bu kılavuz, Sustainage uygulamasını sıfırdan kurmak ve çalıştırmak için gerekli adımları içerir.

## Adım 1: Ön Hazırlıklar
Gerekli yazılımların kurulu olduğundan emin olun:
- Python 3.9 veya üzeri
- Node.js ve npm
- Git

## Adım 2: Kaynak Kodun İndirilmesi
Projeyi klonlayın veya zip dosyasını çıkarın:
```bash
git clone <repo_url>
cd SUSTAINAGESERVER
```

## Adım 3: Sanal Ortam ve Bağımlılıklar
Python sanal ortamını oluşturun ve aktif hale getirin:

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

## Adım 4: Frontend Derlemesi
Vue.js arayüzünü derleyin:
```bash
cd frontend
npm install
npm run build
cd ..
```

## Adım 5: Veritabanı Hazırlığı
Veritabanı şemasını oluşturun ve başlangıç verilerini yükleyin:
```bash
# Otomatik olarak web_app.py başlatıldığında tablolar oluşturulur.
# Ancak manuel tetiklemek isterseniz:
python web_app.py --init-db
```

## Adım 6: Uygulamayı Çalıştırma
Geliştirme sunucusunu başlatın:
```bash
python web_app.py
```
Uygulama `http://localhost:5000` adresinde çalışacaktır.

## Adım 7: Prodüksiyon Dağıtımı (Opsiyonel)
Prodüksiyon ortamı için Gunicorn veya Waitress kullanın:
```bash
# Windows için
python run_waitress.py

# Linux için
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```
Nginx ile reverse proxy yapılandırması önerilir. Örnek yapılandırma `deploy/sustainage.nginx` dosyasındadır.

## Sorun Giderme
- **500 Hatası**: `logs/` dizinindeki uygulama loglarını kontrol edin.
- **Veritabanı Kilidi**: Yüksek yük altında SQLite kilitlenebilir. `DB_POOL_SIZE` değerini artırmayı deneyin.
- **Eksik Modüller**: `pip install -r requirements.txt` komutunu tekrar çalıştırın.
