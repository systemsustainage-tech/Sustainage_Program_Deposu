import logging
from typing import Any, List, Optional, Dict, Union
from backend.core.database_manager import DatabaseManager
from backend.core.database import inject_tenant_filter

class BaseTenantManager:
    """
    Multi-tenant ORM Layer / Base Manager.
    Automatically enforces company_id filtering on database operations.
    """
    def __init__(self, db_path: str, company_id: Optional[int] = None):
        self.db = DatabaseManager(db_path)
        self.company_id = company_id
        self.logger = logging.getLogger(self.__class__.__name__)

    def set_company_context(self, company_id: int) -> None:
        """Sets the company context for subsequent operations."""
        self.company_id = company_id

    def _ensure_context(self, company_id: Optional[int]) -> int:
        """
        Resolves company_id from argument, instance context, or Flask global context.
        """
        cid = company_id if company_id is not None else self.company_id
        
        if cid is None:
            # Try to get from Flask g
            try:
                from flask import g
                if hasattr(g, 'company_id'):
                    cid = g.company_id
            except ImportError:
                pass
                
        if cid is None:
            # Check if we can proceed without context (e.g. for purely global operations)
            # But for safety, BaseTenantManager expects a context.
            # We will allow None ONLY if the caller handles it, but here we raise Error
            # to be safe as per "Bu katman olmadan sorgular çalışmamalı".
            raise ValueError(f"Company ID context is missing for {self.__class__.__name__}")
        return cid

    def select(self, table: str, company_id: Optional[int] = None, 
               columns: Union[List[str], str] = "*", 
               where: Optional[str] = None, params: tuple = (),
               order_by: Optional[str] = None, limit: Optional[int] = None) -> List[dict]:
        """
        Executes a SELECT query filtered by company_id.
        """
        cid = self._ensure_context(company_id)
        
        col_str = ", ".join(columns) if isinstance(columns, list) else columns
        
        # Note: We manually construct the query here, but execute_query will also
        # attempt to inject. Since we add 'WHERE company_id = ?' manually,
        # inject_tenant_filter will detect it and skip double injection.
        query = f"SELECT {col_str} FROM {table} WHERE company_id = ?"
        query_params = [cid]
        
        if where:
            query += f" AND ({where})"
            query_params.extend(params)
            
        if order_by:
            query += f" ORDER BY {order_by}"
            
        if limit:
            query += f" LIMIT {limit}"
            
        return self.db.execute_query(query, tuple(query_params))

    def select_one(self, table: str, company_id: Optional[int] = None, 
                   columns: Union[List[str], str] = "*", 
                   where: Optional[str] = None, params: tuple = (),
                   order_by: Optional[str] = None) -> Optional[dict]:
        """Fetches a single row."""
        results = self.select(table, company_id, columns, where, params, order_by=order_by, limit=1)
        return results[0] if results else None

    def insert(self, table: str, data: Dict[str, Any], company_id: Optional[int] = None) -> int:
        """
        Inserts a record linked to the company.
        Automatically adds company_id to the data.
        """
        cid = self._ensure_context(company_id)
        
        data_copy = data.copy()
        data_copy['company_id'] = cid
        
        cols = ", ".join(data_copy.keys())
        placeholders = ", ".join(["?"] * len(data_copy))
        values = tuple(data_copy.values())
        
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        # Delegates to execute_update which will check injection (and skip if present)
        return self.execute_update(query, values, company_id=cid)

    def update(self, table: str, data: Dict[str, Any], 
               company_id: Optional[int] = None, 
               where: Optional[str] = None, params: tuple = ()) -> int:
        """
        Updates records for a specific company.
        """
        cid = self._ensure_context(company_id)
        
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = list(data.values())
        
        query = f"UPDATE {table} SET {set_clause} WHERE company_id = ?"
        query_params = values + [cid]
        
        if where:
            query += f" AND ({where})"
            query_params.extend(params)
            
        return self.execute_update(query, tuple(query_params), company_id=cid)

    def delete(self, table: str, company_id: Optional[int] = None, 
               where: Optional[str] = None, params: tuple = ()) -> int:
        """
        Deletes records for a specific company.
        """
        cid = self._ensure_context(company_id)
        
        query = f"DELETE FROM {table} WHERE company_id = ?"
        query_params = [cid]
        
        if where:
            query += f" AND ({where})"
            query_params.extend(params)
            
        return self.execute_update(query, tuple(query_params), company_id=cid)

    def count(self, table: str, company_id: Optional[int] = None, 
              where: Optional[str] = None, params: tuple = ()) -> int:
        """Counts records for a company."""
        result = self.select(table, company_id, columns="COUNT(*) as cnt", where=where, params=params)
        return result[0]['cnt'] if result else 0

    def execute_query(self, query: str, params: tuple = (), company_id: Optional[int] = None, skip_tenant_filter: bool = False) -> List[dict]:
        """
        Executes a raw SELECT query with AUTOMATIC company_id filtering.
        """
        # Allow DDL/PRAGMA without context
        if query.strip().lower().startswith(('create', 'alter', 'drop', 'pragma')):
             return self.db.execute_query(query, params)

        if skip_tenant_filter:
            return self.db.execute_query(query, params)

        try:
            cid = self._ensure_context(company_id)
            new_query, new_params = inject_tenant_filter(query, params, cid)
            return self.db.execute_query(new_query, new_params)
        except ValueError:
            # If no context is available, but the query targets a GLOBAL table, it might be safe.
            # inject_tenant_filter handles GLOBAL_TABLES check, but it requires cid to be passed 
            # or it does nothing (returns original).
            # If we want to allow global queries without context, we must check the table name here.
            # But simpler is: REQUIRE context for BaseTenantManager.
            raise

    def execute_update(self, query: str, params: tuple = (), company_id: Optional[int] = None, skip_tenant_filter: bool = False) -> int:
        """
        Executes a raw INSERT/UPDATE/DELETE query with AUTOMATIC company_id filtering.
        """
        # Allow DDL/PRAGMA without context
        if query.strip().lower().startswith(('create', 'alter', 'drop', 'pragma')):
             return self.db.execute_update(query, params)

        if skip_tenant_filter:
            return self.db.execute_update(query, params)

        cid = self._ensure_context(company_id)
        new_query, new_params = inject_tenant_filter(query, params, cid)
        return self.db.execute_update(new_query, new_params)
