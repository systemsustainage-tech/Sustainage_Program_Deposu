
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.database import inject_tenant_filter
import logging

logging.basicConfig(level=logging.DEBUG)

query = """
            SELECT count(*) as count, sum(total_emissions) as total 
            FROM scope1_emissions 
            WHERE year = 2024
        """
params = ()
company_id = 1

print(f"Original SQL:\n{query}")
print(f"Original Params: {params}")

try:
    new_sql, new_params = inject_tenant_filter(query, params, company_id)
    print("-" * 20)
    print(f"New SQL:\n{new_sql}")
    print(f"New Params: {new_params}")
except Exception as e:
    print(f"Error: {e}")
