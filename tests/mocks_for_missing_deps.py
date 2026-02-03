import sys
from types import ModuleType

# Mock flask_compress
if 'flask_compress' not in sys.modules:
    m_compress = ModuleType('flask_compress')
    class MockCompress:
        def __init__(self, *args, **kwargs):
            pass
        def init_app(self, app):
            pass
    m_compress.Compress = MockCompress
    sys.modules['flask_compress'] = m_compress

# Mock flask_limiter
if 'flask_limiter' not in sys.modules:
    m_limiter = ModuleType('flask_limiter')
    class MockLimiter:
        def __init__(self, *args, **kwargs):
            pass
        def init_app(self, app):
            pass
        def limit(self, limit_string, **kwargs):
            def decorator(f):
                return f
            return decorator
    m_limiter.Limiter = MockLimiter
    sys.modules['flask_limiter'] = m_limiter

# Mock flask_limiter.util
if 'flask_limiter.util' not in sys.modules:
    m_limiter_util = ModuleType('flask_limiter.util')
    m_limiter_util.get_remote_address = lambda: '127.0.0.1'
    sys.modules['flask_limiter.util'] = m_limiter_util

# Mock flask_talisman
if 'flask_talisman' not in sys.modules:
    m_talisman = ModuleType('flask_talisman')
    class MockTalisman:
        def __init__(self, *args, **kwargs):
            pass
        def init_app(self, app):
            pass
    m_talisman.Talisman = MockTalisman
    sys.modules['flask_talisman'] = m_talisman
