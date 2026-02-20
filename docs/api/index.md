# API Dokümantasyonu

SustainAge RESTful API, sistemin tüm fonksiyonlarına programatik erişim sağlar.

## Temel Bilgiler
- **Base URL:** `/api/v1`
- **Authentication:** Bearer Token (JWT) veya API Key (`X-API-Key`).
- **Response Format:** JSON

## Authentication
Token almak için:
`POST /api/auth/login`
```json
{
  "username": "admin",
  "password": "password"
}
```

## Hata Kodları
- `200 OK`: Başarılı.
- `400 Bad Request`: Hatalı istek formatı.
- `401 Unauthorized`: Yetkisiz erişim.
- `403 Forbidden`: Erişim izni yok.
- `404 Not Found`: Kaynak bulunamadı.
- `500 Internal Server Error`: Sunucu hatası.

## Detaylı Endpoint Listesi
Detaylar için [Endpoints](endpoints.md) sayfasına bakınız.
