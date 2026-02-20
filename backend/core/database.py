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
    'backup_history', 'recovery_history'
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
    
    # Use UNSTRIPPED lower for regex to preserve indices
    sql_lower = sql.lower()
    
    # 0. Skip DDL and PRAGMA
    if sql_stripped_lower.startswith(('create', 'alter', 'drop', 'pragma', 'begin', 'commit', 'rollback')):
        return sql, params

    # 1. Skip if company_id is already in SQL
    if 'company_id' in sql_lower:
        return sql, params
        
    # 2. Handle INSERT statements
    if sql_stripped_lower.startswith('insert'):
        insert_match = re.search(r'insert\s+into\s+([a-zA-Z0-9_]+)\s*\((.*?)\)\s*values\s*\((.*?)\)', sql_lower, re.IGNORECASE | re.DOTALL)
        
        if insert_match:
            table_name = insert_match.group(1)
            columns_str = insert_match.group(2)
            
            if table_name in GLOBAL_TABLES:
                return sql, params
            
            if 'company_id' in columns_str.lower():
                return sql, params
            
            # Injection needed
            cols_span = insert_match.span(2)
            values_span = insert_match.span(3)
            
            part1 = sql[:cols_span[1]]
            part2 = ", company_id"
            part3 = sql[cols_span[1]:values_span[1]]
            part4 = ", ?"
            part5 = sql[values_span[1]:]
            
            new_sql = part1 + part2 + part3 + part4 + part5
            
            new_params = list(params)
            new_params.append(company_id)
            
            return new_sql, tuple(new_params)
        
        return sql, params

    # 3. Extract Table Name (for SELECT, UPDATE, DELETE)
    table_match = re.search(r'\b(from|update|into)\s+(?:[a-zA-Z0-9_]+\.)?([a-zA-Z0-9_]+)', sql_lower)
    if not table_match:
        return sql, params
    
    table_name = table_match.group(2)
    if table_name in GLOBAL_TABLES:
        return sql, params

    # 4. Inject Logic
    new_sql = sql
    new_params = list(params) if params else []
    
    # Determine injection point
    where_match = re.search(r'\bwhere\b', sql_lower)
    
    if where_match:
        start, end = where_match.span()
        
        # Calculate param index
        pre_sql = sql[:end]
        param_index = pre_sql.count('?')
        
        # Insert SQL
        new_sql = sql[:end] + " company_id = ? AND" + sql[end:]
        
        # Insert Param
        new_params.insert(param_index, company_id)
        
    else:
        # No WHERE clause
        suffix_match = re.search(r'\b(group by|order by|limit)\b', sql_lower)
        
        if suffix_match:
            start = suffix_match.start()
            pre_sql = sql[:start]
            param_index = pre_sql.count('?')
            
            new_sql = sql[:start] + " WHERE company_id = ? " + sql[start:]
            new_params.insert(param_index, company_id)
        else:
            # Just append
            clean_sql = sql.rstrip(';')
            param_index = clean_sql.count('?')
            
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
