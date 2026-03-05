import sqlite3
import re
import logging
from flask import g, has_request_context
import threading

# Tables that are global and should NOT have company_id injected
GLOBAL_TABLES = {
    'companies', 
    'sqlite_sequence', 
    'schema_migrations',
    'translation_dictionary',
    'users',
    'permissions',
    'roles',
    'user_roles',
    'role_permissions',
    'user_permissions',
    'user_profiles',
    'departments',
    'user_companies',
    'report_templates',
    'report_sections',
    'languages',
    'translations',
    'system_settings',
    'framework_mapping',
    'sdg_goals',
    'gri_standards',
    'gri_indicators',
    'map_sdg_gri',
    'report_templates',
    'report_sections',
    'api_endpoints',
    'api_keys',
    'company_info',
    'company_profiles',
    'waste_types',
    'sector_averages',
    'best_performers',
    'sector_trends',
    'benchmark_metrics',
    'sasb_sectors',
    'sasb_disclosure_topics',
    'sasb_metrics',
    'sasb_gri_mapping',
    'cbam_factors',
    'tsrs_standards',
    'tsrs_indicators',
    'gri_categories',
    'gri_kpis',
    'gri_targets',
    'gri_benchmarks',
    'gri_digital_tools',
    'gri_reporting_formats',
    'gri_validation_rules',
    'gri_units',
    'gri_sources',
    'gri_risks',
    'gri_user_roles', 'gri_permissions', 'gri_audit_log', 'scope3_categories',
    'standard_mappings', 'policy_categories', 'message_templates', 'ip_whitelist', 'ip_blacklist',
    'backup_history', 'recovery_history',
    'licenses' # License table is global
}

def inject_tenant_filter(sql, params, company_id):
    """
    Injects company_id filter into SQL query.
    Refactored from TenantAwareCursor for reusability.
    """
    if not company_id:
        return sql, params

    # Use stripped for startswith checks
    sql_stripped = sql.strip()
    sql_stripped_lower = sql_stripped.lower()
    
    # 0. Skip DDL and PRAGMA
    if sql_stripped_lower.startswith(('create', 'alter', 'drop', 'pragma', 'begin', 'commit', 'rollback')):
        return sql, params
        
    # Use full SQL lower for regex searching to maintain correct indices
    sql_lower = sql.lower()

    # 1. Determine operation type and table
    op_match = re.search(r'\b(select|insert|update|delete)\b', sql_lower)
    if not op_match:
        return sql, params
        
    operation = op_match.group(1)
    
    # Extract table name(s)
    # Simple regex, might fail on complex joins, but good enough for 90%
    if operation == 'insert':
        table_match = re.search(r'into\s+([a-zA-Z0-9_]+)', sql_lower)
    elif operation == 'update':
        table_match = re.search(r'update\s+([a-zA-Z0-9_]+)', sql_lower)
    elif operation == 'delete':
        table_match = re.search(r'from\s+([a-zA-Z0-9_]+)', sql_lower)
    else: # SELECT
        table_match = re.search(r'from\s+([a-zA-Z0-9_]+)', sql_lower)
        
    if not table_match:
        return sql, params
        
    table_name = table_match.group(1)
    
    if table_name in GLOBAL_TABLES:
        return sql, params
        
    # 2. Check if company_id is already in SQL (to avoid double injection)
    # This is a bit risky if company_id is used in a subquery or join condition
    # But for simple CRUD it's okay.
    if 'company_id' in sql_lower:
        return sql, params
        
    # 3. Handle INSERT
    if operation == 'insert':
        # Find columns part
        cols_match = re.search(r'\((.*?)\)\s*values', sql_lower, re.DOTALL)
        if cols_match:
            cols_str = cols_match.group(1)
            # If company_id already in columns, skip
            if 'company_id' in cols_str:
                return sql, params
            
            # Inject column
            # We need to find the closing parenthesis of columns and values
            # This is hard with regex due to nested parens.
            # Simplified approach: Append to end of lists
            
            # Reconstruct SQL
            # INSERT INTO table (col1, col2) VALUES (?, ?)
            # -> INSERT INTO table (col1, col2, company_id) VALUES (?, ?, ?)
            
            # Find the first closing paren before VALUES
            values_idx = sql_lower.find('values')
            cols_end = sql.rfind(')', 0, values_idx)
            
            # Find the last closing paren
            vals_end = sql.rfind(')')
            
            if cols_end > 0 and vals_end > 0:
                new_sql = sql[:cols_end] + ", company_id" + sql[cols_end:vals_end] + ", ?" + sql[vals_end:]
                new_params = list(params) if params else []
                new_params.append(company_id)
                return new_sql, tuple(new_params)
        return sql, params

    # 4. Handle SELECT, UPDATE, DELETE
    # Inject WHERE clause
    new_params = list(params) if params else []
    
    where_match = re.search(r'\bwhere\b', sql_lower)
    
    if where_match:
        # Insert "company_id = ? AND" after WHERE
        start, end = where_match.span()
        new_sql = sql[:end] + " company_id = ? AND" + sql[end:]
        # new_params.insert(0, company_id) # Prepend param? No, depends on position.
        # Actually, if we insert at WHERE, it's before existing WHERE params.
        # But wait, existing params order matches ? placeholders.
        # If we insert SQL text, we must insert param at correct index.
        
        # Count ? before WHERE
        pre_where = sql[:start]
        param_idx = pre_where.count('?')
        new_params.insert(param_idx, company_id)
        
    else:
        # No WHERE clause. Append to end, but before GROUP BY/ORDER BY/LIMIT
        suffix_match = re.search(r'\b(group by|order by|limit)\b', sql_lower)
        
        if suffix_match:
            start = suffix_match.start()
            new_sql = sql[:start] + " WHERE company_id = ? " + sql[start:]
            
            # Count ? before suffix
            pre_suffix = sql[:start]
            param_idx = pre_suffix.count('?')
            new_params.insert(param_idx, company_id)
        else:
            # Append at end
            clean_sql = sql.rstrip(';')
            new_sql = clean_sql + " WHERE company_id = ?"
            new_params.append(company_id)
            
    return new_sql, tuple(new_params)

class TenantAwareDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self._local = threading.local()

    def _get_conn(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path)
            # Enable WAL mode for concurrency
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
            self._local.conn.execute("PRAGMA foreign_keys=ON")
            self._local.conn.execute("PRAGMA temp_store=MEMORY")
            self._local.conn.execute("PRAGMA cache_size=-64000")
            
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def close(self):
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            del self._local.conn

    def commit(self):
        self._get_conn().commit()

    def rollback(self):
        self._get_conn().rollback()

    def cursor(self):
        return TenantAwareCursor(self._get_conn().cursor(), self)

    def execute(self, sql, params=()):
        return self.cursor().execute(sql, params)

    def get_company_id(self):
        if has_request_context() and hasattr(g, 'company_id') and g.company_id:
            return g.company_id
        return None

class TenantAwareCursor:
    def __init__(self, cursor, db):
        self.cursor_obj = cursor
        self.db = db

    def __getattr__(self, name):
        return getattr(self.cursor_obj, name)

    def __iter__(self):
        return iter(self.cursor_obj)

    def execute(self, sql, params=()):
        try:
            company_id = self.db.get_company_id()
            new_sql, new_params = inject_tenant_filter(sql, params, company_id)
            
            # Log modifications for debugging
            if new_sql != sql:
                logging.debug(f"TenantAwareDB: Modified SQL: {new_sql} | Params: {new_params}")
            return self.cursor_obj.execute(new_sql, new_params)
        except Exception as e:
            logging.error(f"TenantAwareDB Error: {e} | SQL: {sql}")
            raise e

    def fetchone(self):
        return self.cursor_obj.fetchone()

    def fetchall(self):
        return self.cursor_obj.fetchall()
