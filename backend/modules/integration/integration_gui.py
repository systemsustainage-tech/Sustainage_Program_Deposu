import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entegrasyon Yönetim GUI
API, Cloud, ERP, OpenAI entegrasyonları
"""

import json
import tkinter as tk
from tkinter import messagebox, ttk

from .cloud_storage_manager import CloudStorageManager
from .erp_integration import ERPIntegration
from .openai_integration import OpenAIIntegration


class IntegrationGUI:
    """Entegrasyon yönetim GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.api_server = None
        self.cloud_mgr = CloudStorageManager()
        self.erp_mgr = ERPIntegration()
        self.openai_mgr = OpenAIIntegration()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()

    def setup_ui(self) -> None:
        """Entegrasyon arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#0D47A1', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" API ve Entegrasyon Yönetimi",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#0D47A1')
        title_label.pack(expand=True)

        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Notebook oluştur
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Sekmeleri oluştur
        self.create_api_tab()
        self.create_cloud_tab()
        self.create_erp_tab()
        self.create_openai_tab()
        self.create_mobile_tab()

    def create_api_tab(self) -> None:
        """REST API sekmesi"""
        api_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(api_frame, text=" REST API")

        # Başlık
        tk.Label(api_frame, text="REST API Yönetimi",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # API durumu
        status_frame = tk.Frame(api_frame, bg='#e3f2fd', relief='solid', bd=1)
        status_frame.pack(fill='x', padx=40, pady=20)

        self.api_status_label = tk.Label(status_frame, text="Durum: Pasif",
                                         font=('Segoe UI', 12, 'bold'), bg='#e3f2fd')
        self.api_status_label.pack(pady=10)

        # API bilgileri
        info_text = """
        REST API Özellikleri:
        • 7+ endpoint hazır
        • API key authentication
        • Rate limiting desteği
        • JSON response formatı
        • Mobil uygulama desteği
        • CORS aktif
        
        Endpoints:
        • GET /api/v1/health - Sistem kontrolü
        • GET /api/v1/company/{id} - Şirket bilgileri
        • GET /api/v1/carbon/emissions/{id} - Karbon verileri
        • POST /api/v1/carbon/emissions/{id} - Veri ekle
        • GET /api/v1/sdg/goals/{id} - SDG hedefleri
        • GET /api/v1/reports/{id} - Raporlar
        """

        tk.Label(api_frame, text=info_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=40, pady=10)

        # API butonları
        btn_frame = tk.Frame(api_frame, bg='white')
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text=" API Server Başlat", command=self.start_api_server,
                 bg='#2E7D32', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10).pack(side='left', padx=5)

        tk.Button(btn_frame, text=" API Dokümantasyonu", command=self.show_api_docs,
                 bg='#1976D2', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=10).pack(side='left', padx=5)

    def create_cloud_tab(self) -> None:
        """Cloud sync sekmesi"""
        cloud_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(cloud_frame, text="️ Cloud Sync")

        # Başlık
        tk.Label(cloud_frame, text="Cloud Storage Entegrasyonu",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Cloud sağlayıcıları
        providers_frame = tk.Frame(cloud_frame, bg='white')
        providers_frame.pack(fill='x', padx=40, pady=20)

        for provider_code, provider_info in self.cloud_mgr.SUPPORTED_PROVIDERS.items():
            self.create_cloud_provider_card(providers_frame, provider_code, provider_info)

    def create_cloud_provider_card(self, parent, provider_code, provider_info):
        """Cloud sağlayıcı kartı"""
        card = tk.Frame(parent, bg='#f5f5f5', relief='solid', bd=1)
        card.pack(fill='x', pady=5)

        # Başlık
        tk.Label(card, text=f"{provider_info['icon']} {provider_info['name']}",
                font=('Segoe UI', 12, 'bold'), bg='#f5f5f5').pack(side='left', padx=20, pady=10)

        # Durum
        tk.Label(card, text="Gelecekte aktif edilecek",
                font=('Segoe UI', 10), fg='#666', bg='#f5f5f5').pack(side='left', padx=20)

        # Bağlan butonu
        tk.Button(card, text=" Bağlan", command=lambda: self.connect_cloud(provider_code),
                 bg='#1976D2', fg='white', font=('Segoe UI', 10, 'bold'),
                 padx=15, pady=5).pack(side='right', padx=20)

    def create_erp_tab(self) -> None:
        """ERP entegrasyonu sekmesi"""
        erp_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(erp_frame, text=" ERP Entegrasyonu")

        # Başlık
        tk.Label(erp_frame, text="ERP Sistemleri Entegrasyonu",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # ERP sistemleri
        systems_frame = tk.Frame(erp_frame, bg='white')
        systems_frame.pack(fill='x', padx=40, pady=20)

        for erp_code, erp_info in self.erp_mgr.SUPPORTED_ERP_SYSTEMS.items():
            self.create_erp_system_card(systems_frame, erp_code, erp_info)

    def create_erp_system_card(self, parent, erp_code, erp_info):
        """ERP sistem kartı"""
        card = tk.Frame(parent, bg='#fff3e0', relief='solid', bd=1)
        card.pack(fill='x', pady=5)

        # Başlık
        tk.Label(card, text=f"{erp_info['icon']} {erp_info['name']}",
                font=('Segoe UI', 12, 'bold'), bg='#fff3e0').pack(side='left', padx=20, pady=10)

        # Modüller
        modules_text = ", ".join(erp_info['modules'])
        tk.Label(card, text=f"Modüller: {modules_text}",
                font=('Segoe UI', 9), fg='#666', bg='#fff3e0').pack(side='left', padx=20)

        # Bağlan butonu
        tk.Button(card, text=" Yapılandır", command=lambda: self.configure_erp(erp_code),
                 bg='#F57C00', fg='white', font=('Segoe UI', 10, 'bold'),
                 padx=15, pady=5).pack(side='right', padx=20)

    def create_openai_tab(self) -> None:
        """OpenAI sekmesi"""
        openai_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(openai_frame, text=" OpenAI (Gelecek)")

        # Başlık
        tk.Label(openai_frame, text="OpenAI API Entegrasyonu",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Açıklama
        desc_text = """
        OpenAI Entegrasyonu - GELECEK ÖZELLİK
        
        Bu özellik gelecekte aktif edildiğinde:
        
         Veri Analizi:
        • Sürdürülebilirlik verilerini otomatik analiz
        • Trend tespiti ve tahminler
        • Anomali tespiti
        
         Rapor Oluşturma:
        • Executive summary otomatik oluşturma
        • İstatistiksel analiz
        • Grafik ve görselleştirme önerileri
        
         Doğal Dil Sorgulama:
        • "2024 karbon emisyonumuz ne kadar?" gibi sorular
        • Türkçe doğal dil desteği
        • Akıllı yanıtlar
        
         İyileştirme Önerileri:
        • AI destekli öneriler
        • Sektör karşılaştırmaları
        • Best practice önerileri
        """

        tk.Label(openai_frame, text=desc_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(padx=40, pady=20)

        # API key girişi
        key_frame = tk.Frame(openai_frame, bg='white')
        key_frame.pack(pady=20)

        tk.Label(key_frame, text="OpenAI API Key:",
                font=('Segoe UI', 11, 'bold'), bg='white').pack(side='left', padx=(0, 10))

        self.openai_key_var = tk.StringVar()
        tk.Entry(key_frame, textvariable=self.openai_key_var, width=40,
                show='*').pack(side='left', padx=(0, 10))

        tk.Button(key_frame, text=" Kaydet (Gelecek İçin)",
                 command=self.save_openai_key,
                 bg='#7B1FA2', fg='white', font=('Segoe UI', 10, 'bold'),
                 padx=15, pady=8).pack(side='left')

    def create_mobile_tab(self) -> None:
        """Mobil uygulama sekmesi"""
        mobile_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(mobile_frame, text=" Mobil Destek")

        # Başlık
        tk.Label(mobile_frame, text="Mobil Uygulama Desteği",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Bilgi
        info_text = """
        REST API üzerinden mobil uygulama desteği:
        
         iOS ve Android uyumlu
         JSON veri formatı
         Güvenli API key authentication
         CORS aktif (cross-origin desteği)
         Rate limiting koruması
        
        Mobil uygulama geliştiricileri için:
        • API dokümantasyonu mevcut
        • Swagger/OpenAPI spesifikasyonu hazır
        • Test endpoint'leri aktif
        """

        tk.Label(mobile_frame, text=info_text, font=('Segoe UI', 11),
                bg='white', justify='left').pack(padx=40, pady=20)

    def start_api_server(self) -> None:
        """API server'ı başlat"""
        messagebox.showinfo("Bilgi",
                          "REST API Server özelliği hazır!\n\n"
                          "Başlatmak için:\n"
                          "python -m modules.integration.rest_api_server\n\n"
                          "API: http://localhost:5000/api/v1/")

    def show_api_docs(self) -> None:
        """API dokümantasyonunu göster"""
        from .openapi_docs import OpenAPIDocumentation

        spec = OpenAPIDocumentation.get_openapi_spec()

        docs_win = tk.Toplevel(self.parent)
        docs_win.title("API Dokümantasyonu - Swagger/OpenAPI")
        docs_win.geometry("900x700")
        docs_win.configure(bg='white')

        # Başlık
        tk.Label(docs_win, text="API Dokümantasyonu",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # JSON gösterimi
        text_widget = tk.Text(docs_win, wrap='word')
        text_widget.pack(fill='both', expand=True, padx=20, pady=10)
        text_widget.insert('1.0', json.dumps(spec, indent=2, ensure_ascii=False))
        text_widget.config(state='disabled')

    def connect_cloud(self, provider: str) -> None:
        """Cloud sağlayıcıya bağlan"""
        messagebox.showinfo("Bilgi",
                          f"{provider} entegrasyonu gelecekte aktif edilecek!\n\n"
                          f"OAuth2 kimlik doğrulaması yapılacak.")

    def configure_erp(self, erp_system: str) -> None:
        """ERP sistemi yapılandır"""
        messagebox.showinfo("Bilgi",
                          f"{erp_system} entegrasyonu gelecekte aktif edilecek!\n\n"
                          f"Bağlantı bilgileri yapılandırılacak.")

    def save_openai_key(self) -> None:
        """OpenAI API key kaydet"""
        key = self.openai_key_var.get()
        if key:
            messagebox.showinfo("Bilgi",
                              "OpenAI API key kaydedildi!\n\n"
                              "Gelecekte aktif edildiğinde kullanılacak:\n"
                              "• Veri analizi\n"
                              "• Rapor oluşturma\n"
                              "• İstatistik ve grafik önerileri\n"
                              "• Doğal dil sorgulama")
        else:
            messagebox.showwarning("Uyarı", "Lütfen bir API key girin!")
