
import re
import logging
from typing import Dict, List, Any, Tuple

class ReportValidator:
    """
    Validates AI generated report content against source data.
    Checks for numerical consistency and potential hallucinations.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_report_content(self, ai_text: str, source_data: Dict[str, Any]) -> List[str]:
        """
        Validates the AI text against the source data.
        Returns a list of warnings/inconsistencies.
        """
        warnings = []
        
        # 1. Extract numbers from text
        text_numbers = self._extract_numbers_from_text(ai_text)
        
        # 2. Extract numbers from source data (flattened)
        data_numbers = self._extract_numbers_from_data(source_data)
        
        # 3. Compare
        # This is a heuristic: If the text contains a specific number that is NOT in the source data,
        # it might be a hallucination. However, AI might round numbers or calculate percentages.
        # We will flag numbers that are completely off (not present and not close to any source number).
        
        for num_val, original_str in text_numbers:
            if not self._is_number_supported_by_data(num_val, data_numbers):
                # Check for year-like numbers (e.g. 2024, 2025) which might be just dates
                if 2020 <= num_val <= 2030:
                    continue
                    
                warnings.append(f"Potential hallucination: Found number '{original_str}' ({num_val}) in text which does not appear in source data.")
                
        return warnings

    def _extract_numbers_from_text(self, text: str) -> List[Tuple[float, str]]:
        """
        Finds all numbers in text. Returns list of (value, string_representation).
        """
        # Matches integers and floats, also percentages like 45.5%
        # Regex for numbers: \d+([.,]\d+)?
        matches = []
        # Simple regex for finding numbers
        pattern = r'\b\d+(?:[.,]\d+)?\b'
        
        for match in re.finditer(pattern, text):
            val_str = match.group()
            try:
                # Handle comma decimal separator
                clean_str = val_str.replace(',', '.')
                val = float(clean_str)
                matches.append((val, val_str))
            except ValueError:
                pass
                
        return matches

    def _extract_numbers_from_data(self, data: Any) -> List[float]:
        """
        Recursively extracts all numbers from a dictionary/list.
        """
        numbers = []
        
        if isinstance(data, dict):
            for v in data.values():
                numbers.extend(self._extract_numbers_from_data(v))
        elif isinstance(data, list):
            for item in data:
                numbers.extend(self._extract_numbers_from_data(item))
        elif isinstance(data, (int, float)):
            if not isinstance(data, bool): # Skip booleans
                numbers.append(float(data))
        elif isinstance(data, str):
            # Try to parse string as number if it looks like one
            try:
                val = float(data)
                numbers.append(val)
            except ValueError:
                pass
                
        return numbers

    def _is_number_supported_by_data(self, target: float, data_numbers: List[float], tolerance: float = 0.05) -> bool:
        """
        Checks if the target number exists in data_numbers, or is close enough (rounding),
        or is a derived value (sum, percentage - hard to check without context, so we stick to direct match/approx match).
        """
        for num in data_numbers:
            # Direct match
            if num == target:
                return True
            
            # Approximate match (rounding errors)
            if abs(num - target) < 0.001:
                return True
                
            # Percentage check (if target is like 0.45 and data has 45, or vice versa)
            # This is risky but common
            
        return False
