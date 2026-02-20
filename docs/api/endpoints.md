# API Uç Noktaları (Endpoints)

## Veri Girişi

### Enerji Verisi Ekleme
`POST /api/v1/environmental/energy`
- **Body:**
  ```json
  {
    "date": "2023-10-01",
    "facility_id": 1,
    "type": "electricity",
    "amount": 1000,
    "unit": "kWh"
  }
  ```

### Atık Verisi Ekleme
`POST /api/v1/environmental/waste`
- **Body:**
  ```json
  {
    "date": "2023-10-01",
    "type": "plastic",
    "amount": 50,
    "unit": "kg",
    "disposal_method": "recycling"
  }
  ```

## Raporlama

### Rapor Oluşturma
`POST /api/v1/reports/generate`
- **Body:**
  ```json
  {
    "report_type": "GRI",
    "year": 2023,
    "format": "pdf"
  }
  ```

### Rapor Listesi
`GET /api/v1/reports`
- **Query Params:** `type`, `year`

## Sistem Durumu

### Sağlık Kontrolü
`GET /health`
- Sistem durumunu döndürür.

### Metrikler
`GET /metrics`
- Prometheus metriklerini döndürür.
