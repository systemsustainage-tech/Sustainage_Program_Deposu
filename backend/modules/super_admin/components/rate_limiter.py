#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rate Limiter Component
Request rate limiting and tracking
"""

import logging
import sqlite3
from datetime import datetime
from typing import Any, Dict, List
from config.database import DB_PATH


class RateLimiter:
    """Rate limiting manager"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def check_rate_limit(
        self,
        resource_type: str,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> Dict[str, Any]:
        """
        Check if rate limit is exceeded
        
        Returns:
            {
                'allowed': bool,
                'current_count': int,
                'limit': int,
                'reset_in': int (seconds),
                'blocked': bool
            }
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get current rate limit record
            cursor.execute("""
                SELECT request_count, window_start, is_blocked
                FROM rate_limits
                WHERE resource_type = ? AND identifier = ?
            """, (resource_type, identifier))

            result = cursor.fetchone()

            if not result:
                # First request - create record
                cursor.execute("""
                    INSERT INTO rate_limits (resource_type, identifier, request_count, window_start, is_blocked)
                    VALUES (?, ?, 1, ?, 0)
                """, (resource_type, identifier, datetime.now()))
                conn.commit()
                conn.close()

                return {
                    'allowed': True,
                    'current_count': 1,
                    'limit': max_requests,
                    'reset_in': window_seconds,
                    'blocked': False
                }

            request_count, window_start_str, is_blocked = result
            # Handle potential millisecond precision difference
            try:
                window_start = datetime.fromisoformat(window_start_str)
            except ValueError:
                # Fallback for simple format
                window_start = datetime.strptime(window_start_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
                
            now = datetime.now()

            # Check if window has expired
            time_passed = (now - window_start).total_seconds()

            if time_passed > window_seconds:
                # Reset window
                cursor.execute("""
                    UPDATE rate_limits
                    SET request_count = 1, window_start = ?, is_blocked = 0
                    WHERE resource_type = ? AND identifier = ?
                """, (datetime.now(), resource_type, identifier))
                conn.commit()
                conn.close()

                return {
                    'allowed': True,
                    'current_count': 1,
                    'limit': max_requests,
                    'reset_in': window_seconds,
                    'blocked': False
                }

            # Within window - check limit
            if request_count >= max_requests:
                # Limit exceeded
                reset_in = int(window_seconds - time_passed)

                cursor.execute("""
                    UPDATE rate_limits
                    SET is_blocked = 1, last_request = datetime('now')
                    WHERE resource_type = ? AND identifier = ?
                """, (resource_type, identifier))
                conn.commit()
                conn.close()

                return {
                    'allowed': False,
                    'current_count': request_count,
                    'limit': max_requests,
                    'reset_in': reset_in,
                    'blocked': True
                }

            # Increment count
            cursor.execute("""
                UPDATE rate_limits
                SET request_count = request_count + 1, last_request = ?
                WHERE resource_type = ? AND identifier = ?
            """, (datetime.now(), resource_type, identifier))
            conn.commit()
            conn.close()

            return {
                'allowed': True,
                'current_count': request_count + 1,
                'limit': max_requests,
                'reset_in': int(window_seconds - time_passed),
                'blocked': False
            }

        except Exception as e:
            logging.error(f"Rate limit error: {e}")
            return {
                'allowed': True,  # Fail open
                'current_count': 0,
                'limit': max_requests,
                'reset_in': 0,
                'blocked': False
            }

    def reset_limit(self, resource_type: str, identifier: str) -> bool:
        """Reset rate limit for a specific resource/identifier"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM rate_limits
                WHERE resource_type = ? AND identifier = ?
            """, (resource_type, identifier))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def get_rate_limit_stats(self) -> List[Dict[str, Any]]:
        """Get current rate limit statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT resource_type, identifier, request_count, window_start, is_blocked
                FROM rate_limits
                WHERE window_start > datetime('now', '-1 hour')
                ORDER BY window_start DESC
            """)

            results = []
            for row in cursor.fetchall():
                results.append({
                    'resource': row[0],
                    'identifier': row[1],
                    'count': row[2],
                    'window_start': row[3],
                    'blocked': bool(row[4])
                })

            conn.close()
            return results
        except Exception:
            return []

    def cleanup_old_records(self, hours: int = 24) -> int:
        """Clean up old rate limit records"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM rate_limits
                WHERE window_start < datetime('now', ?)
            """, (f'-{hours} hours',))

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            return deleted_count
        except Exception:
            return 0

