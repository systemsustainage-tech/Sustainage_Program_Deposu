"""
Custom exception'lar - Daha iyi error handling için
"""

class SDGException(Exception):
    """Temel SDG exception"""
    pass

class DatabaseException(SDGException):
    """Database ile ilgili hatalar"""
    pass

class AuthenticationException(SDGException):
    """Kimlik doğrulama hataları"""
    pass

class AuthorizationException(SDGException):
    """Yetkilendirme hataları"""
    pass

class ValidationException(SDGException):
    """Veri validasyon hataları"""
    pass

class ModuleNotFoundException(SDGException):
    """Modül bulunamadı hatası"""
    pass

class ConfigurationException(SDGException):
    """Konfigürasyon hataları"""
    pass

class ReportGenerationException(SDGException):
    """Rapor oluşturma hataları"""
    pass

class FileOperationException(SDGException):
    """Dosya işlem hataları"""
    pass

class ImportException(SDGException):
    """Veri import hataları"""
    pass

class ExportException(SDGException):
    """Veri export hataları"""
    pass

# Error handler decorator
def handle_errors(error_message: str = "İşlem başarısız") -> None:
    """
    Error handling decorator
    
    Kullanım:
        @handle_errors("Kullanıcı kaydedilemedi")
        def save_user(user_data) -> None:
            # Kod
    """
    def decorator(func) -> None:
        def wrapper(*args, **kwargs) -> None:
            try:
                return func(*args, **kwargs)
            except SDGException:
                # SDG custom exception'ları
                raise
            except Exception as e:
                # Diğer exception'ları wrap et
                raise SDGException(f"{error_message}: {str(e)}") from e
        return wrapper
    return decorator

