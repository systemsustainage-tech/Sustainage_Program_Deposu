
# Sustainage API Reference

## Authentication
All API requests (except login/register) require authentication.
- **Session Auth**: Use standard cookies.
- **Token Auth**: Use `Authorization: Bearer <token>` header (if applicable).

## Rate Limiting
- **Global Limit**: 120 requests per minute.
- **Critical Endpoints**:
  - `/api/generate-report`: 5 req/min
  - `/api/update-data`: 20 req/min
- **Response**: 429 Too Many Requests.

## Endpoints

### 1. General
- `GET /api/ping`: Health check. Returns 200 OK.
- `GET /metrics`: Prometheus metrics.

### 2. Dashboard
- `GET /api/dashboard-stats`: Returns summary statistics for the dashboard.
  - Requires: Valid session/license.

### 3. Reporting
- `POST /api/generate-report`: Triggers report generation.
  - Body: JSON with report parameters.

### 4. Data Management
- `POST /api/update-data`: Updates module data.
  - Body: JSON with data payload.

## Error Handling
- **400 Bad Request**: Invalid input.
- **401 Unauthorized**: Login required.
- **403 Forbidden**: License invalid or insufficient permissions.
- **429 Too Many Requests**: Rate limit exceeded.
- **500 Internal Server Error**: System error.
