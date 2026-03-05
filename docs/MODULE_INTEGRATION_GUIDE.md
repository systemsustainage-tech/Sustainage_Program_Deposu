
# Module Integration Guide

## Overview
Sustainage uses a modular architecture. Each module (GRI, Carbon, Water, etc.) is located in `backend/modules/`.

## Adding a New Module
1. Create a directory in `backend/modules/<module_name>`.
2. Implement a `Manager` class inheriting from `BaseManager` or `BaseTenantManager`.
3. Register the module in `web_app.py` or via Blueprint.
4. Add database models in `backend/core/db_models.py` (or module-specific model file).

## Inter-Module Communication
Modules should communicate via defined interfaces or the central `DatabaseManager`.
Avoid direct imports between sibling modules if possible to reduce coupling.

## Database
- All modules must use `company_id` for multi-tenancy.
- Use `TenantAwareDB` wrapper for queries to ensure isolation.

## Security
- All new endpoints must be protected with `@login_required` or `@require_company_context`.
- Critical actions should be logged via `AuditManager`.

## Testing
- Add unit tests in `tests/` directory.
- Use `tools/test_multitenant_isolation.py` pattern to verify data isolation.
