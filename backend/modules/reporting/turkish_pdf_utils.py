"""
Türkçe PDF Rapor Yardımcı Modülü
Tüm PDF raporlarında Türkçe karakter desteği için ortak fonksiyonlar
"""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet


class TurkishPDFUtils:
    """Türkçe PDF rapor yardımcı sınıfı"""

    def __init__(self):
        self.turkish_font = 'DejaVuSans'  # Türkçe karakterleri destekleyen font
        self.styles = getSampleStyleSheet()
        self._setup_turkish_styles()

    def _setup_turkish_styles(self):
        """Türkçe karakter destekli stilleri oluştur"""

        # Ana başlık stili
        self.styles.add(ParagraphStyle(
            name='TurkishTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=f'{self.turkish_font}-Bold'
        ))

        # Bölüm başlığı stili
        self.styles.add(ParagraphStyle(
            name='TurkishHeading',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=15,
            spaceBefore=25,
            fontName=f'{self.turkish_font}-Bold'
        ))

        # Alt başlık stili
        self.styles.add(ParagraphStyle(
            name='TurkishSubHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#1d4ed8'),
            spaceAfter=10,
            spaceBefore=15,
            fontName=f'{self.turkish_font}-Bold'
        ))

        # Normal metin stili
        self.styles.add(ParagraphStyle(
            name='TurkishNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            fontName=self.turkish_font
        ))

        # Küçük metin stili
        self.styles.add(ParagraphStyle(
            name='TurkishSmall',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=6,
            fontName=self.turkish_font
        ))

        # Tablo başlık stili
        self.styles.add(ParagraphStyle(
            name='TurkishTableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            fontName=f'{self.turkish_font}-Bold',
            textColor=colors.white
        ))

        # Tablo içerik stili
        self.styles.add(ParagraphStyle(
            name='TurkishTableContent',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT,
            fontName=self.turkish_font
        ))

    def get_style(self, style_name: str) -> ParagraphStyle:
        """Stil adına göre stil döndür"""
        return self.styles[style_name]

    def get_turkish_font(self) -> str:
        """Türkçe font adını döndür"""
        return self.turkish_font

    def create_custom_style(self, name: str, parent: str = 'Normal', **kwargs) -> ParagraphStyle:
        """Özel stil oluştur"""
        # Varsayılan font ayarı
        if 'fontName' not in kwargs:
            kwargs['fontName'] = self.turkish_font

        return ParagraphStyle(name, parent=self.styles[parent], **kwargs)


# Global instance
turkish_pdf = TurkishPDFUtils()
