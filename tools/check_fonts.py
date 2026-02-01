try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.fonts import addMapping
    import os

    print("ReportLab is installed.")
    
    font_path = os.path.join('backend', 'static', 'fonts', 'DejaVuSans.ttf')
    abs_font_path = os.path.abspath(font_path)
    
    if os.path.exists(abs_font_path):
        print(f"Font file found at: {abs_font_path}")
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', abs_font_path))
            print("Successfully registered DejaVuSans.")
        except Exception as e:
            print(f"Failed to register font: {e}")
    else:
        print(f"Font file NOT found at: {abs_font_path}")
        
except ImportError:
    print("ReportLab is NOT installed.")
