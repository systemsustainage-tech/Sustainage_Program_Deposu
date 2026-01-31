import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSRS/ESRS Ek Formlar
- Çift Önemlilik (Double Materiality) Analizi
- ESRS Gereklilikleri (ESRS 1, 2, E1-E5, S1-S4, G1)
- AB Taksonomisi Uygunluk Kontrolü
- Değer Zinciri Analizi (SupplyChainGUI entegrasyonu)
- İklim Risk Değerlendirmesi
"""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Any, Optional

from .tsrs_manager import TSRSManager

try:
    from modules.standards.tsrs_esrs import TSRSESRSManager
except Exception as e:
    # Bazı ortamlarda relatif import gerekebilir
    logging.debug(f"Standard import failed, trying relative import: {e}")
    from .modules.standards.tsrs_esrs import TSRSESRSManager  # type: ignore

_SupplyChainGUI: Any = None
try:
    from modules.supply_chain.supply_chain_gui import SupplyChainGUI as _SupplyChainGUI
except Exception as e:
    logging.error(f"Silent error caught: {str(e)}")
if TYPE_CHECKING:
    pass


class DoubleMaterialityWindow:
    """Çift önemlilik analizi formu"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.manager = TSRSESRSManager()

        self.window = tk.Toplevel(parent)
        self.window.title("TSRS - Çift Önemlilik Analizi")
        self.window.geometry("700x600")
        self.window.configure(bg='white')

        tk.Label(self.window, text="Çift Önemlilik Analizi", font=('Segoe UI', 16, 'bold'),
                 fg='#2c3e50', bg='white').pack(pady=15)

        form = tk.Frame(self.window, bg='white')
        form.pack(fill='both', expand=True, padx=25, pady=10)

        self.topic_name = self._add_entry(form, "Konu Adı")
        self.assessment_year = self._add_entry(form, "Değerlendirme Yılı", default=str(datetime.now().year))

        # Puanlar
        tk.Label(form, text="Etki Önemliliği (0-5)", font=('Segoe UI', 10), bg='white').pack(anchor='w', pady=(8, 0))
        self.impact_score = ttk.Scale(form, from_=0, to=5, orient='horizontal')
        self.impact_score.pack(fill='x')
        tk.Label(form, text="Finansal Önemlilik (0-5)", font=('Segoe UI', 10), bg='white').pack(anchor='w', pady=(8, 0))
        self.financial_score = ttk.Scale(form, from_=0, to=5, orient='horizontal')
        self.financial_score.pack(fill='x')

        self.esrs_rel = self._add_text(form, "ESRS İlgisi (ilgili standartlar/konular)")
        self.stakeholder_impact = self._add_text(form, "Paydaş Etkisi")
        self.business_impact = self._add_text(form, "İş Etkisi")

        btn = tk.Button(self.window, text="Kaydet", font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white',
                        relief='flat', padx=20, pady=8, command=self.save)
        btn.pack(pady=10)

    def _add_entry(self, parent, label, default: str = "") -> tk.Entry:
        tk.Label(parent, text=label, font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        e = tk.Entry(parent)
        e.insert(0, default)
        e.pack(fill='x')
        return e

    def _add_text(self, parent, label) -> tk.Text:
        tk.Label(parent, text=label, font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        t = tk.Text(parent, height=4)
        t.pack(fill='x')
        return t

    def save(self) -> None:
        try:
            topic = self.topic_name.get().strip()
            year = int(self.assessment_year.get().strip() or datetime.now().year)
            impact = float(f"{self.impact_score.get():.2f}")
            financial = float(f"{self.financial_score.get():.2f}")

            # Basit seviye hesaplama
            total = impact + financial
            if total >= 8:
                level = 'Yüksek'
            elif total >= 5:
                level = 'Orta'
            else:
                level = 'Düşük'

            esrs_rel = self.esrs_rel.get("1.0", tk.END).strip() or None
            stakeholder = self.stakeholder_impact.get("1.0", tk.END).strip() or None
            business = self.business_impact.get("1.0", tk.END).strip() or None

            ok = self.manager.add_double_materiality_assessment(
                company_id=self.company_id,
                assessment_year=year,
                topic_name=topic,
                impact_materiality_score=impact,
                financial_materiality_score=financial,
                double_materiality_level=level,
                esrs_relevance=esrs_rel or "",
                stakeholder_impact=stakeholder or "",
                business_impact=business or ""
            )
            if ok:
                messagebox.showinfo("Başarılı", "Çift önemlilik değerlendirmesi kaydedildi.")
                self.window.destroy()
            else:
                messagebox.showerror("Hata", "Kayıt sırasında bir hata oluştu.")
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydetme hatası: {e}")


class ESRSRequirementsWindow:
    """ESRS gereklilikleri formu"""

    ESRS_STANDARDS = [
        'ESRS 1', 'ESRS 2',
        'ESRS E1', 'ESRS E2', 'ESRS E3', 'ESRS E4', 'ESRS E5',
        'ESRS S1', 'ESRS S2', 'ESRS S3', 'ESRS S4',
        'ESRS G1'
    ]

    COMPLIANCE = ['Uyumlu', 'Kısmi', 'Uyumsuz']
    ASSURANCE = ['Yok', 'Sınırlı Güvence', 'Makul Güvence']

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.manager = TSRSESRSManager()

        self.window = tk.Toplevel(parent)
        self.window.title("TSRS - ESRS Gereklilikleri")
        self.window.geometry("780x640")
        self.window.configure(bg='white')

        tk.Label(self.window, text="ESRS Gereklilikleri", font=('Segoe UI', 16, 'bold'),
                 fg='#2c3e50', bg='white').pack(pady=15)

        form = tk.Frame(self.window, bg='white')
        form.pack(fill='both', expand=True, padx=25, pady=10)

        self.reporting_period = self._add_entry(form, "Raporlama Dönemi", default=str(datetime.now().year))

        tk.Label(form, text="ESRS Standardı", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        self.standard_cb = ttk.Combobox(form, values=self.ESRS_STANDARDS, state='readonly')
        self.standard_cb.current(0)
        self.standard_cb.pack(fill='x')

        self.std_extra_frame = tk.Frame(form, bg='white')
        self.std_extra_frame.pack(fill='both', expand=True, pady=(5, 5))
        self._render_standard_specific(self.ESRS_STANDARDS[0])
        self.standard_cb.bind('<<ComboboxSelected>>', lambda e: self._render_standard_specific(self.standard_cb.get()))

        self.req_number = self._add_entry(form, "Gereklilik No")
        self.req_title = self._add_entry(form, "Gereklilik Başlığı")

        tk.Label(form, text="Uyumluluk Durumu", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        self.compliance_cb = ttk.Combobox(form, values=self.COMPLIANCE, state='readonly')
        self.compliance_cb.current(0)
        self.compliance_cb.pack(fill='x')

        self.reporting_content = self._add_text(form, "Raporlama İçeriği")
        self.data_sources = self._add_text(form, "Veri Kaynakları")

        tk.Label(form, text="Güvence", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        self.assurance_cb = ttk.Combobox(form, values=self.ASSURANCE, state='readonly')
        self.assurance_cb.current(0)
        self.assurance_cb.pack(fill='x')

        ttk.Button(self.window, text="Kaydet", style='Primary.TButton', command=self.save).pack(pady=10)

    def _add_entry(self, parent, label, default: str = "") -> tk.Entry:
        tk.Label(parent, text=label, font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        e = tk.Entry(parent)
        e.insert(0, default)
        e.pack(fill='x')
        return e

    def _add_text(self, parent, label) -> tk.Text:
        tk.Label(parent, text=label, font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        t = tk.Text(parent, height=4)
        t.pack(fill='x')
        return t

    def _clear_extra(self) -> None:
        for w in self.std_extra_frame.winfo_children():
            w.destroy()

    def _render_standard_specific(self, std: str) -> None:
        self._clear_extra()
        self.extra_fields = {}
        if std == 'ESRS E1':
            tk.Label(self.std_extra_frame, text='E1 Emisyonlar ve Enerji', font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(8, 4))
            self.extra_fields['scope1'] = tk.Entry(self.std_extra_frame)
            self.extra_fields['scope2'] = tk.Entry(self.std_extra_frame)
            self.extra_fields['scope3'] = tk.Entry(self.std_extra_frame)
            self.extra_fields['renew_pct'] = tk.Entry(self.std_extra_frame)
            tk.Label(self.std_extra_frame, text='Scope 1 (tCO2e)', bg='white').pack(anchor='w')
            self.extra_fields['scope1'].pack(fill='x')
            tk.Label(self.std_extra_frame, text='Scope 2 (tCO2e)', bg='white').pack(anchor='w')
            self.extra_fields['scope2'].pack(fill='x')
            tk.Label(self.std_extra_frame, text='Scope 3 (tCO2e)', bg='white').pack(anchor='w')
            self.extra_fields['scope3'].pack(fill='x')
            tk.Label(self.std_extra_frame, text='Yenilenebilir Enerji (%)', bg='white').pack(anchor='w')
            self.extra_fields['renew_pct'].pack(fill='x')
        elif std == 'ESRS E2':
            tk.Label(self.std_extra_frame, text='E2 Kirlilik', font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(8, 4))
            self.extra_fields['pollutant'] = tk.Entry(self.std_extra_frame)
            self.extra_fields['value'] = tk.Entry(self.std_extra_frame)
            self.extra_fields['unit'] = tk.Entry(self.std_extra_frame)
            tk.Label(self.std_extra_frame, text='Kirletici', bg='white').pack(anchor='w')
            self.extra_fields['pollutant'].pack(fill='x')
            tk.Label(self.std_extra_frame, text='Değer', bg='white').pack(anchor='w')
            self.extra_fields['value'].pack(fill='x')
            tk.Label(self.std_extra_frame, text='Birim', bg='white').pack(anchor='w')
            self.extra_fields['unit'].pack(fill='x')
        elif std == 'ESRS E3':
            tk.Label(self.std_extra_frame, text='E3 Su ve Deniz Kaynakları', font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(8, 4))
            self.extra_fields['water_use'] = tk.Entry(self.std_extra_frame)
            self.extra_fields['water_intensity'] = tk.Entry(self.std_extra_frame)
            tk.Label(self.std_extra_frame, text='Su Tüketimi (m3)', bg='white').pack(anchor='w')
            self.extra_fields['water_use'].pack(fill='x')
            tk.Label(self.std_extra_frame, text='Su Yoğunluğu', bg='white').pack(anchor='w')
            self.extra_fields['water_intensity'].pack(fill='x')

    def save(self) -> None:
        try:
            ok = self.manager.add_esrs_requirement(
                company_id=self.company_id,
                reporting_period=self.reporting_period.get().strip(),
                esrs_standard=self.standard_cb.get().strip(),
                requirement_number=self.req_number.get().strip(),
                requirement_title=self.req_title.get().strip(),
                compliance_status=self.compliance_cb.get().strip(),
                reporting_content=self._compose_reporting_content(),
                data_sources=self.data_sources.get("1.0", tk.END).strip() or "",
                assurance_status=self.assurance_cb.get().strip()
            )
            if ok:
                messagebox.showinfo("Başarılı", "ESRS gerekliliği kaydedildi.")
                self.window.destroy()
            else:
                messagebox.showerror("Hata", "Kayıt sırasında bir hata oluştu.")
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydetme hatası: {e}")

    def _compose_reporting_content(self) -> str:
        base = self.reporting_content.get("1.0", tk.END).strip() or ""
        std = self.standard_cb.get().strip()
        extras = []
        for k, w in getattr(self, 'extra_fields', {}).items():
            try:
                v = w.get().strip()
            except Exception:
                v = ''
            if v:
                extras.append(f"{k}={v}")
        if extras:
            return base + ("\n" if base else "") + f"[{std} extras] " + "; ".join(extras)
        return base


class EUTaxonomyWindow:
    """AB Taksonomisi uygunluk formu"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.manager = TSRSESRSManager()

        self.window = tk.Toplevel(parent)
        self.window.title("TSRS - AB Taksonomisi Uygunluk")
        self.window.geometry("780x640")
        self.window.configure(bg='white')

        tk.Label(self.window, text="AB Taksonomisi Uygunluk", font=('Segoe UI', 16, 'bold'),
                 fg='#2c3e50', bg='white').pack(pady=15)

        form = tk.Frame(self.window, bg='white')
        form.pack(fill='both', expand=True, padx=25, pady=10)

        self.reporting_period = self._add_entry(form, "Raporlama Dönemi", default=str(datetime.now().year))
        self.economic_activity = self._add_entry(form, "Ekonomik Faaliyet (örn. NACE)")
        self.taxonomy_code = self._add_entry(form, "Taksonomi Kodu")

        tk.Label(form, text="Uyumluluk (%)", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        self.alignment_pct = ttk.Scale(form, from_=0, to=100, orient='horizontal')
        self.alignment_pct.pack(fill='x')

        self.turnover_share = self._add_entry(form, "Ciro Payı (%)", default="")
        self.capex_share = self._add_entry(form, "Yatırım (CAPEX) Payı (%)", default="")
        self.opex_share = self._add_entry(form, "İşletme Gideri (OPEX) Payı (%)", default="")

        self.nfrd_req = self._add_text(form, "NFRD/CSRD Gereklilik Notu")

        tk.Button(self.window, text="Kaydet", font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white',
                  relief='flat', padx=20, pady=8, command=self.save).pack(pady=10)

    def _add_entry(self, parent, label, default: str = "") -> tk.Entry:
        tk.Label(parent, text=label, font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        e = tk.Entry(parent)
        e.insert(0, default)
        e.pack(fill='x')
        return e

    def _add_text(self, parent, label) -> tk.Text:
        tk.Label(parent, text=label, font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        t = tk.Text(parent, height=3)
        t.pack(fill='x')
        return t

    def save(self) -> None:
        try:
            ap = float(f"{self.alignment_pct.get():.2f}")
            def to_float(s: str) -> Optional[float]:
                try:
                    return float(s)
                except Exception:
                    return None

            ok = self.manager.add_eu_taxonomy_compliance(
                company_id=self.company_id,
                reporting_period=self.reporting_period.get().strip(),
                economic_activity=self.economic_activity.get().strip(),
                taxonomy_code=self.taxonomy_code.get().strip(),
                alignment_percentage=ap,
                turnover_share=to_float(self.turnover_share.get().strip()) or 0.0,
                capex_share=to_float(self.capex_share.get().strip()) or 0.0,
                opex_share=to_float(self.opex_share.get().strip()) or 0.0,
                nfrd_requirement=self.nfrd_req.get("1.0", tk.END).strip() or ""
            )
            if ok:
                messagebox.showinfo("Başarılı", "AB Taksonomisi kaydı eklendi.")
                self.window.destroy()
            else:
                messagebox.showerror("Hata", "Kayıt sırasında bir hata oluştu.")
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydetme hatası: {e}")


class ValueChainAnalysisWindow:
    """Değer zinciri analizi - SupplyChainGUI entegrasyonu veya özet"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        from typing import Any
        self.manager: Any = None

        self.window = tk.Toplevel(parent)
        self.window.title("TSRS - Değer Zinciri Analizi")
        self.window.geometry("900x700")
        self.window.configure(bg='white')

        tk.Label(self.window, text="Değer Zinciri Analizi", font=('Segoe UI', 16, 'bold'),
                 fg='#2c3e50', bg='white').pack(pady=15)

        info = tk.Label(self.window, text=(
            "Bu ekran tedarik zinciri sürdürülebilirlik özetini gösterir. "
            "Detaylı değerlendirme için Tedarik Zinciri GUI açılabilir."),
            font=('Segoe UI', 10), fg='#7f8c8d', bg='white')
        info.pack()

        # Opsiyonel: Mevcut SupplyChainGUI'yi yeni bir pencerede aç
        if _SupplyChainGUI is not None:
            ttk.Button(self.window, text="Tedarik Zinciri GUI'yi Aç", style='Primary.TButton',
                       command=self._open_supply_chain_gui).pack(pady=10)

        # Özet alanı
        self.text = tk.Text(self.window, height=25, bg='#f8f9fa')
        self.text.pack(fill='both', expand=True, padx=20, pady=10)

        self._load_summary()

    def _open_supply_chain_gui(self) -> None:
        try:
            sc_window = tk.Toplevel(self.window)
            _SupplyChainGUI(sc_window, self.company_id)
        except Exception as e:
            messagebox.showerror("Hata", f"SupplyChainGUI açma hatası: {e}")

    def _load_summary(self) -> None:
        try:
            from modules.supply_chain.supply_chain_manager import SupplyChainManager as SCM
            self.manager = SCM()
            suppliers = self.manager.get_suppliers(self.company_id)
            metrics = self.manager.get_metrics(self.company_id)

            self.text.insert(tk.END, f"Toplam Tedarikçi: {len(suppliers)}\n")
            if metrics:
                self.text.insert(tk.END, "\nKPI'lar:\n")
                for m in metrics:
                    name = m.get('metric_name') or m.get('name')
                    value = m.get('metric_value') or m.get('value')
                    self.text.insert(tk.END, f"- {name}: {value}\n")
        except Exception as e:
            self.text.insert(tk.END, f"Özet yükleme hatası: {e}")


class ClimateRiskAssessmentWindow:
    """İklim risk değerlendirmesi formu (tsrs_risks)"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.tsrs = TSRSManager()

        self.window = tk.Toplevel(parent)
        self.window.title("TSRS - İklim Risk Değerlendirmesi")
        self.window.geometry("780x640")
        self.window.configure(bg='white')

        tk.Label(self.window, text="İklim Risk Değerlendirmesi", font=('Segoe UI', 16, 'bold'),
                 fg='#2c3e50', bg='white').pack(pady=15)

        form = tk.Frame(self.window, bg='white')
        form.pack(fill='both', expand=True, padx=25, pady=10)

        self.risk_title = self._add_entry(form, "Risk Başlığı", default="İklim Senaryosu")
        self.risk_desc = self._add_text(form, "Risk Açıklaması")

        tk.Label(form, text="Kategori", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        self.cat_cb = ttk.Combobox(form, values=['Çevresel', 'Sosyal', 'Yönetişim'], state='readonly')
        self.cat_cb.current(0)
        self.cat_cb.pack(fill='x')

        tk.Label(form, text="Olasılık", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        self.prob_cb = ttk.Combobox(form, values=['Düşük', 'Orta', 'Yüksek'], state='readonly')
        self.prob_cb.current(1)
        self.prob_cb.pack(fill='x')

        tk.Label(form, text="Etki", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        self.impact_cb = ttk.Combobox(form, values=['Düşük', 'Orta', 'Yüksek'], state='readonly')
        self.impact_cb.current(1)
        self.impact_cb.pack(fill='x')

        tk.Label(form, text="Risk Seviyesi", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        self.level_cb = ttk.Combobox(form, values=['Düşük', 'Orta', 'Yüksek', 'Kritik'], state='readonly')
        self.level_cb.current(1)
        self.level_cb.pack(fill='x')

        self.mitigation = self._add_text(form, "Azaltım Stratejisi")
        self.responsible = self._add_entry(form, "Sorumlu Kişi")
        self.target_date = self._add_entry(form, "Hedef Tarih (YYYY-MM-DD)")
        tk.Label(form, text="Durum", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        self.status_cb = ttk.Combobox(form, values=['Open', 'In Progress', 'Closed'], state='readonly')
        self.status_cb.current(0)
        self.status_cb.pack(fill='x')

        tk.Button(self.window, text="Kaydet", font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white',
                  relief='flat', padx=20, pady=8, command=self.save).pack(pady=10)

    def _add_entry(self, parent, label, default: str = "") -> tk.Entry:
        tk.Label(parent, text=label, font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        e = tk.Entry(parent)
        e.insert(0, default)
        e.pack(fill='x')
        return e

    def _add_text(self, parent, label) -> tk.Text:
        tk.Label(parent, text=label, font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 0))
        t = tk.Text(parent, height=4)
        t.pack(fill='x')
        return t

    def _get_climate_risk_standard_id(self) -> int:
        """İklim riskleri için ilgili TSRS standard ID'yi bulmaya çalış"""
        try:
            standards = self.tsrs.get_tsrs_standards()
            # Başlık veya alt kategori üzerinden basit arama
            for s in standards:
                title = (s.get('title') or '').lower()
                subcat = (s.get('subcategory') or '').lower()
                if 'iklim' in title or 'çevresel risk' in subcat:
                    return s['id']
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        # Bulunamazsa ilk risk yönetimi kategorisinden birini seç
        try:
            for s in standards:
                if (s.get('category') or '') == 'Risk Yönetimi':
                    return s['id']
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        return 1  # Fallback (varsayım: 1 mevcut)

    def save(self) -> None:
        try:
            standard_id = self._get_climate_risk_standard_id()
            ok = self.tsrs.add_tsrs_risk(
                company_id=self.company_id,
                standard_id=standard_id,
                risk_title=self.risk_title.get().strip(),
                risk_description=self.risk_desc.get("1.0", tk.END).strip() or None,
                risk_category=self.cat_cb.get().strip(),
                probability=self.prob_cb.get().strip(),
                impact=self.impact_cb.get().strip(),
                risk_level=self.level_cb.get().strip(),
                mitigation_strategy=self.mitigation.get("1.0", tk.END).strip() or None,
                responsible_person=self.responsible.get().strip() or None,
                target_date=self.target_date.get().strip() or None,
                status=self.status_cb.get().strip()
            )
            if ok:
                messagebox.showinfo("Başarılı", "İklim riski kaydedildi.")
                self.window.destroy()
            else:
                messagebox.showerror("Hata", "Kayıt sırasında bir hata oluştu.")
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydetme hatası: {e}")
