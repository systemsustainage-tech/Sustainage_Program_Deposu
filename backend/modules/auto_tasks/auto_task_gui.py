import logging
"""
Otomatik Görev Oluşturma Modülü GUI
"""
import sqlite3
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk
from utils.language_manager import LanguageManager


class AutoTaskGUI:
    """Otomatik Görev Oluşturma GUI Sınıfı"""

    def __init__(self, parent, company_id, user_id):
        self.lm = LanguageManager()
        self.parent = parent
        self.company_id = company_id
        self.user_id = user_id
        # Ana dizini bul
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(current_dir))
        self.db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')

        self.setup_ui()
        self.load_tasks()

    def setup_ui(self):
        """UI'yi oluştur"""
        # Ana çerçeve
        main_frame = tk.Frame(self.parent, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_label = tk.Label(main_frame, text="Otomatik Görev Oluşturma",
                              font=('Segoe UI', 16, 'bold'), bg='white', fg='#1e40af')
        title_label.pack(pady=(0, 20))

        # Görev oluşturma bölümü
        create_frame = tk.LabelFrame(main_frame, text="Yeni Görev Oluştur",
                                   font=('Segoe UI', 12, 'bold'), bg='white', fg='#1e40af')
        create_frame.pack(fill='x', pady=(0, 20))

        # Görev adı
        tk.Label(create_frame, text="Görev Adı:", bg='white').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.task_name_var = tk.StringVar()
        tk.Entry(create_frame, textvariable=self.task_name_var, width=40).grid(row=0, column=1, padx=10, pady=5)

        # Görev açıklaması
        tk.Label(create_frame, text="Açıklama:", bg='white').grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.task_desc_var = tk.StringVar()
        tk.Entry(create_frame, textvariable=self.task_desc_var, width=40).grid(row=1, column=1, padx=10, pady=5)

        # Departman seçimi
        tk.Label(create_frame, text="Departman:", bg='white').grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.department_var = tk.StringVar()
        self.department_combo = ttk.Combobox(create_frame, textvariable=self.department_var, values=[], state='readonly')
        self.department_combo.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        # Departmanları yükle
        self.load_departments()

        # Görev tipi
        tk.Label(create_frame, text="Görev Tipi:", bg='white').grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.task_type_var = tk.StringVar(value="Genel")
        task_type_combo = ttk.Combobox(create_frame, textvariable=self.task_type_var,
                                     values=["Genel", "Raporlama", "Veri Girişi", "Analiz", "İzleme"])
        task_type_combo.grid(row=3, column=1, padx=10, pady=5, sticky='w')

        # Öncelik
        tk.Label(create_frame, text="Öncelik:", bg='white').grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.priority_var = tk.StringVar(value="Orta")
        priority_combo = ttk.Combobox(create_frame, textvariable=self.priority_var,
                                    values=["Düşük", "Orta", "Yüksek", "Kritik"])
        priority_combo.grid(row=4, column=1, padx=10, pady=5, sticky='w')

        # Tarih
        tk.Label(create_frame, text="Bitiş Tarihi:", bg='white').grid(row=5, column=0, sticky='w', padx=10, pady=5)
        self.due_date_var = tk.StringVar(value=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))
        tk.Entry(create_frame, textvariable=self.due_date_var, width=15).grid(row=5, column=1, padx=10, pady=5, sticky='w')

        # Oluştur butonu
        create_btn = tk.Button(create_frame, text="Görev Oluştur", command=self.create_task,
                             bg='#1e40af', fg='white', font=('Segoe UI', 10, 'bold'))
        create_btn.grid(row=6, column=1, padx=10, pady=10, sticky='w')

        # Mevcut görevler bölümü
        tasks_frame = tk.LabelFrame(main_frame, text="Mevcut Görevler",
                                  font=('Segoe UI', 12, 'bold'), bg='white', fg='#1e40af')
        tasks_frame.pack(fill='both', expand=True)

        # Görevler tablosu
        columns = ('ID', 'Görev Adı', 'Tip', 'Öncelik', 'Durum', 'Bitiş Tarihi')
        self.tasks_tree = ttk.Treeview(tasks_frame, columns=columns, show='headings', height=10)

        for col in columns:
            self.tasks_tree.heading(col, text=col)
            self.tasks_tree.column(col, width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tasks_frame, orient='vertical', command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscrollcommand=scrollbar.set)

        self.tasks_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

        # Görev işlemleri
        actions_frame = tk.Frame(tasks_frame, bg='white')
        actions_frame.pack(fill='x', padx=10, pady=(0, 10))

        tk.Button(actions_frame, text=self.lm.tr("btn_update", "Güncelle"), command=self.update_task,
                 bg='#10b981', fg='white').pack(side='left', padx=5)
        tk.Button(actions_frame, text=self.lm.tr("btn_delete", "Sil"), command=self.delete_task,
                 bg='#ef4444', fg='white').pack(side='left', padx=5)
        tk.Button(actions_frame, text=self.lm.tr("btn_refresh", "Yenile"), command=self.load_tasks,
                 bg='#6b7280', fg='white').pack(side='left', padx=5)

    def create_task(self):
        """Yeni görev oluştur"""
        try:
            task_name = self.task_name_var.get().strip()
            task_desc = self.task_desc_var.get().strip()
            department = (self.department_var.get() or '').strip()
            task_type = self.task_type_var.get()
            priority = self.priority_var.get()
            due_date = self.due_date_var.get()

            if not task_name:
                messagebox.showerror("Hata", "Görev adı boş olamaz!")
                return

            # Veritabanına kaydet
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tablo yoksa oluştur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auto_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    user_id INTEGER,
                    task_name TEXT NOT NULL,
                    task_description TEXT,
                    department TEXT,
                    task_type TEXT,
                    priority TEXT,
                    status TEXT DEFAULT 'Açık',
                    due_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Eski tablolar için departman sütunu ekle (varsa hata yoksayılır)
            try:
                cursor.execute("ALTER TABLE auto_tasks ADD COLUMN department TEXT")
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

            cursor.execute("""
                INSERT INTO auto_tasks (company_id, user_id, task_name, task_description, department,
                                      task_type, priority, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (self.company_id, self.user_id, task_name, task_desc, department,
                  task_type, priority, due_date))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Görev başarıyla oluşturuldu!")

            # Formu temizle
            self.task_name_var.set("")
            self.task_desc_var.set("")
            self.department_var.set("")
            self.task_type_var.set("Genel")
            self.priority_var.set("Orta")
            self.due_date_var.set((datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))

            # Departman seçildiyse e-mail gönder
            if department:
                try:
                    self._notify_department_users(department, task_name, task_desc, due_date)
                except Exception as e:
                    messagebox.showwarning("Uyarı", f"Departman e-mail bildirimi sırasında hata: {e}")

            # Listeyi yenile
            self.load_tasks()

        except Exception as e:
            messagebox.showerror("Hata", f"Görev oluşturma hatası: {e}")

    def load_departments(self):
        """Departmanları veritabanından yükle ve dropdown'a ekle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # is_active sütunu bazı şemalarda mevcut; yoksa fallback
            try:
                cursor.execute("SELECT name FROM departments WHERE is_active = 1 ORDER BY name")
            except Exception:
                cursor.execute("SELECT name FROM departments ORDER BY name")
            rows = cursor.fetchall()
            conn.close()
            departments = [r[0] for r in rows] if rows else []
            self.department_combo['values'] = departments
        except Exception as e:
            logging.info(f"Departmanlar yüklenemedi: {e}")

    def _notify_department_users(self, department: str, task_name: str, task_desc: str, due_date: str) -> None:
        """Seçilen departmandaki kullanıcılara e-mail gönder"""
        # Kullanıcıları çek
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT display_name, email FROM users WHERE department = ? AND is_active = 1",
                (department,)
            )
        except Exception:
            cursor.execute(
                "SELECT username AS display_name, email FROM users WHERE department = ?",
                (department,)
            )
        recipients = cursor.fetchall()
        conn.close()

        if not recipients:
            logging.info(f"[BILGI] Departmanda kayıtlı kullanıcı bulunamadı: {department}")
            return

        # E-mail gönderimi
        try:
            from tasks.email_service import EmailService
            es = EmailService()
        except Exception as e:
            logging.info(f"[UYARI] Email servisi yüklenemedi: {e}")
            return

        subject = f"Yeni Otomatik Görev: {task_name}"
        body = (
            f"<h3>Yeni Görev Oluşturuldu</h3>"
            f"<p><b>Görev:</b> {task_name}</p>"
            f"<p><b>Açıklama:</b> {task_desc or '-'}"
            f"<p><b>Departman:</b> {department}</p>"
            f"<p><b>Bitiş Tarihi:</b> {due_date}</p>"
            f"<p>Bu görev departmanınıza otomatik olarak oluşturulmuştur.</p>"
        )

        sent = 0
        for display_name, email in recipients:
            if not email:
                logging.info(f"[UYARI] E-mail adresi yok: {display_name}")
                continue
            try:
                if es.send_email(to_email=email, subject=subject, body=body, to_name=display_name):
                    sent += 1
            except Exception as e:
                logging.error(f"[HATA] E-mail gönderilemedi {email}: {e}")
        logging.info(f"[OK] Departman e-mail bildirimleri gönderildi: {sent}/{len(recipients)}")

    def load_tasks(self):
        """Görevleri yükle"""
        try:
            # Mevcut öğeleri temizle
            for item in self.tasks_tree.get_children():
                self.tasks_tree.delete(item)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, task_name, task_type, priority, status, due_date
                FROM auto_tasks 
                WHERE company_id = ?
                ORDER BY created_at DESC
            """, (self.company_id,))

            tasks = cursor.fetchall()
            conn.close()

            for task in tasks:
                self.tasks_tree.insert('', 'end', values=task)

        except Exception as e:
            logging.error(f"Görev yükleme hatası: {e}")

    def update_task(self):
        """Görevi güncelle"""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen güncellenecek görevi seçin!")
            return

        # Basit güncelleme - durum değiştirme
        item = self.tasks_tree.item(selected[0])
        task_id = item['values'][0]
        current_status = item['values'][4]

        new_status = "Tamamlandı" if current_status == "Açık" else "Açık"

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE auto_tasks 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_status, task_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", f"Görev durumu '{new_status}' olarak güncellendi!")
            self.load_tasks()

        except Exception as e:
            messagebox.showerror("Hata", f"Güncelleme hatası: {e}")

    def delete_task(self):
        """Görevi sil"""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen silinecek görevi seçin!")
            return

        if messagebox.askyesno("Onay", "Bu görevi silmek istediğinizden emin misiniz?"):
            item = self.tasks_tree.item(selected[0])
            task_id = item['values'][0]

            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("DELETE FROM auto_tasks WHERE id = ?", (task_id,))

                conn.commit()
                conn.close()

                messagebox.showinfo("Başarılı", "Görev silindi!")
                self.load_tasks()

            except Exception as e:
                messagebox.showerror("Hata", f"Silme hatası: {e}")
