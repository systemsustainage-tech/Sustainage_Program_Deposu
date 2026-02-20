# Geliştirici Kılavuzu

## Proje Yapısı
- `backend/`: Python Flask tabanlı backend kodları.
- `frontend/`: (Varsa) Frontend kaynak kodları.
- `templates/`: Jinja2 HTML şablonları.
- `static/`: CSS, JS ve resim dosyaları.
- `docs/`: Dokümantasyon.

## Yeni Modül Ekleme
1. `backend/modules/` altında yeni bir klasör oluşturun.
2. `__init__.py` ve gerekli manager sınıflarını oluşturun.
3. Veritabanı modellerini tanımlayın.
4. API endpointlerini `web_app.py` veya ilgili route dosyasına ekleyin.
5. `templates/` altında gerekli HTML sayfalarını oluşturun.

## Testler
Testleri çalıştırmak için:
```bash
python -m unittest discover tests
```

## Kod Standartları
- PEP 8 standartlarına uyun.
- Tip ipuçlarını (Type Hints) kullanın.
- Her modül için dokümantasyon yazın.

## Deployment
- `docker-compose.yml` dosyasını kullanarak konteynerleri yönetin.
- CI/CD süreçleri için `tools/` altındaki scriptleri kullanın.
