import sys
from unittest.mock import MagicMock

# Mock Tkinter
class MockTkinter:
    class Tk:
        def __init__(self, *args, **kwargs): pass
        def mainloop(self): pass
    class Label:
        def __init__(self, *args, **kwargs): pass
        def pack(self, *args, **kwargs): pass
    class Button:
        def __init__(self, *args, **kwargs): pass
        def pack(self, *args, **kwargs): pass
    class Frame:
        def __init__(self, *args, **kwargs): pass
        def pack(self, *args, **kwargs): pass
    
    # Generic catch-all for other attributes
    def __getattr__(self, name):
        return MagicMock()

# Apply mocks to sys.modules
sys.modules['tkinter'] = MockTkinter()
sys.modules['tkinter.ttk'] = MockTkinter()
sys.modules['tkinter.messagebox'] = MockTkinter()
sys.modules['tkinter.filedialog'] = MockTkinter()
sys.modules['tkinter.font'] = MockTkinter()
sys.modules['tkinter.colorchooser'] = MockTkinter()

# Also mock PIL.ImageTk if used
sys.modules['PIL.ImageTk'] = MagicMock()

print("Tkinter mocked successfully.")

# Now try to import a GUI module
try:
    # Ensure backend is in path
    import os
    sys.path.append(os.path.join(os.getcwd(), 'server'))
    
    # Try importing a known GUI module
    from backend.modules.visualization import visualization_center_gui
    print("Successfully imported visualization_center_gui")
    
    # Try initializing a class if possible (might fail if it expects real tk objects)
    # But for web app, we just need the import to succeed.
except Exception as e:
    print(f"Import failed: {e}")
