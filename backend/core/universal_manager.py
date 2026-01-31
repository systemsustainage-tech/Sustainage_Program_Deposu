import inspect
import logging
from typing import Dict, Any, List

class UniversalManagerWrapper:
    def __init__(self, manager_instance):
        self.manager = manager_instance
        self.methods = {m[0]: m[1] for m in inspect.getmembers(self.manager, predicate=inspect.ismethod)}

    def get_dashboard_data(self, company_id: int = 1, year: int = 2024) -> Dict[str, Any]:
        data = {
            'stats': {},
            'records': [],
            'columns': [],
            'actions': []
        }

        # 1. Try to fetch statistics
        stats_method = self._find_method(['get_statistics', 'get_stats', 'get_dashboard_stats', 'get_metrics'])
        if stats_method:
            try:
                # Try with company_id and year
                try:
                    stats = stats_method(company_id, year)
                except TypeError:
                    try:
                        stats = stats_method(company_id)
                    except TypeError:
                        stats = stats_method()
                
                if isinstance(stats, dict):
                    data['stats'] = stats
            except Exception as e:
                logging.warning(f"Failed to fetch stats for {self.manager.__class__.__name__}: {e}")

        # 2. Try to fetch records
        records_method = self._find_method(['get_all', 'get_records', 'get_list', 'get_data', 'list_items'])
        if not records_method:
            # Try specific naming like get_waste_records
            class_name_lower = self.manager.__class__.__name__.lower().replace('manager', '')
            records_method = self._find_method([f'get_{class_name_lower}_records', f'get_{class_name_lower}_data'])

        if records_method:
            try:
                try:
                    records = records_method(company_id, year)
                except TypeError:
                    try:
                        records = records_method(company_id)
                    except TypeError:
                        records = records_method()

                if records:
                    data['records'] = records
                    # Infer columns from first record
                    if isinstance(records, list) and len(records) > 0:
                        first = records[0]
                        if isinstance(first, dict):
                            data['columns'] = list(first.keys())
                        elif isinstance(first, (list, tuple)):
                            # If tuple, we don't know column names easily unless we inspect cursor description, 
                            # but here we just have data. Let's use indices.
                            data['columns'] = [f"Col {i+1}" for i in range(len(first))]
                        elif hasattr(first, '__dict__'):
                            data['columns'] = [k for k in first.__dict__.keys() if not k.startswith('_')]
            except Exception as e:
                logging.warning(f"Failed to fetch records for {self.manager.__class__.__name__}: {e}")

        return data

    def _find_method(self, candidates: List[str]):
        for name in candidates:
            if name in self.methods:
                return self.methods[name]
        return None
