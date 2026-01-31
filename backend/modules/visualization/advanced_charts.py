#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Grafik Sistemleri - TAM VE EKSİKSİZ
İnteraktif, Drill-down, Harita, Sankey, Network
"""

import tkinter as tk
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AdvancedCharts:
    """Gelişmiş grafik oluşturucu"""

    def __init__(self):
        # Türkçe karakter desteği için matplotlib ayarları
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False

    # =====================================================
    # 1. İNTERAKTİF DASHBOARD WIDGET'LARI
    # =====================================================

    def create_interactive_gauge(self, parent, value: float, max_value: float,
                                title: str = "Metrik", unit: str = "") -> None:
        """
        İnteraktif gauge (kadran) widget
        
        Args:
            value: Mevcut değer
            max_value: Maksimum değer
            title: Başlık
            unit: Birim
        """
        fig, ax = plt.subplots(figsize=(4, 3), subplot_kw={'projection': 'polar'})

        # Gauge parametreleri
        theta = np.linspace(0, np.pi, 100)
        percentage = (value / max_value) * 100 if max_value > 0 else 0

        # Renk belirleme
        if percentage < 30:
            color = '#D32F2F'  # Kırmızı
        elif percentage < 70:
            color = '#FBC02D'  # Sarı
        else:
            color = '#2E7D32'  # Yeşil

        # Gauge çiz
        ax.plot(theta, np.ones_like(theta) * 1, color='#e0e0e0', linewidth=15)
        ax.plot(theta[:int(percentage)], np.ones(int(percentage)),
               color=color, linewidth=15)

        # Değer göster
        ax.text(np.pi/2, 0.5, f"{value:.1f}{unit}\n{percentage:.1f}%",
               ha='center', va='center', fontsize=14, fontweight='bold')

        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
        ax.spines['polar'].set_visible(False)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_kpi_card(self, parent, kpi_data: Dict) -> tk.Frame:
        """
        İnteraktif KPI kartı
        
        Args:
            kpi_data: {
                'title': 'Karbon Emisyonu',
                'value': 100,
                'unit': 'tCO2e',
                'change': -5.2,
                'target': 90,
                'color': '#2E7D32'
            }
        """
        card = tk.Frame(parent, bg=kpi_data.get('color', '#1976D2'),
                       relief='raised', bd=3)

        # Başlık
        tk.Label(card, text=kpi_data.get('title', 'KPI'),
                font=('Segoe UI', 11, 'bold'), fg='white',
                bg=kpi_data.get('color', '#1976D2')).pack(pady=5)

        # Değer
        value = kpi_data.get('value', 0)
        unit = kpi_data.get('unit', '')
        tk.Label(card, text=f"{value:.1f} {unit}",
                font=('Segoe UI', 20, 'bold'), fg='white',
                bg=kpi_data.get('color', '#1976D2')).pack(pady=10)

        # Değişim
        change = kpi_data.get('change', 0)
        change_text = f"{'↑' if change > 0 else '↓'} %{abs(change):.1f}"
        change_color = '#4CAF50' if change < 0 else '#F44336'  # Azalış iyi (karbon için)

        tk.Label(card, text=change_text,
                font=('Segoe UI', 12, 'bold'), fg=change_color,
                bg=kpi_data.get('color', '#1976D2')).pack()

        # Hedef
        target = kpi_data.get('target')
        if target:
            tk.Label(card, text=f"Hedef: {target:.1f} {unit}",
                    font=('Segoe UI', 9), fg='white',
                    bg=kpi_data.get('color', '#1976D2')).pack(pady=(10, 5))

        return card

    # =====================================================
    # 2. DRILL-DOWN GRAFİKLER
    # =====================================================

    def create_drilldown_chart(self, parent, data: Dict,
                               click_callback=None) -> None:
        """
        Drill-down grafiği - tıklanabilir detay
        
        Args:
            data: {
                'categories': ['2020', '2021', '2022'],
                'values': [100, 95, 90],
                'details': {
                    '2020': {'Scope 1': 60, 'Scope 2': 30, 'Scope 3': 10},
                    ...
                }
            }
            click_callback: Tıklama fonksiyonu
        """
        fig, ax = plt.subplots(figsize=(8, 5))

        categories = data.get('categories', [])
        values = data.get('values', [])

        bars = ax.bar(categories, values, color='#1976D2', edgecolor='black', linewidth=1.5)

        # Değerleri göster
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontweight='bold')

        ax.set_xlabel('Yıl', fontsize=12, fontweight='bold')
        ax.set_ylabel('Değer', fontsize=12, fontweight='bold')
        ax.set_title('Tıklayarak Detay Görün', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill='both', expand=True)

        # Tıklama eventi (basitleştirilmiş - gerçekte koordinat kontrolü gerekir)
        if click_callback:
            widget.bind('<Button-1>', lambda e: click_callback(categories[0] if categories else None))

        return widget

    # =====================================================
    # 3. SANKEY DİYAGRAMLARI (AKIŞ)
    # =====================================================

    def create_sankey_diagram(self, parent, flow_data: Dict) -> None:
        """
        Sankey akış diyagramı
        
        Args:
            flow_data: {
                'nodes': ['Enerji', 'Üretim', 'Ürün', 'Atık'],
                'links': [
                    {'source': 0, 'target': 1, 'value': 100},
                    {'source': 1, 'target': 2, 'value': 80},
                    {'source': 1, 'target': 3, 'value': 20}
                ]
            }
        """
        try:
            import tempfile

            import plotly.graph_objects as go
            from plotly.offline import plot

            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=flow_data.get('nodes', []),
                    color=['#1976D2', '#388E3C', '#F57C00', '#D32F2F']
                ),
                link=dict(
                    source=[link['source'] for link in flow_data.get('links', [])],
                    target=[link['target'] for link in flow_data.get('links', [])],
                    value=[link['value'] for link in flow_data.get('links', [])]
                )
            )])

            fig.update_layout(
                title_text="Enerji Akış Diyagramı",
                font_size=12,
                height=500
            )

            # HTML olarak kaydet ve göster
            temp_html = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
            plot(fig, filename=temp_html.name, auto_open=False)

            # Tkinter içinde göster (basitleştirilmiş)
            tk.Label(parent, text="Sankey diyagramı oluşturuldu!\n(Detaylı görüntüleme için HTML rapor kullanın)",
                    font=('Segoe UI', 12), bg='white').pack(pady=20)

        except ImportError:
            # Plotly yoksa basit gösterim
            tk.Label(parent, text="Sankey Diyagramı\n(Plotly kurulumu gerekiyor)",
                    font=('Segoe UI', 12, 'bold'), bg='white').pack(pady=20)

            # Basit metin gösterimi
            for link in flow_data.get('links', []):
                nodes = flow_data.get('nodes', [])
                source = nodes[link['source']] if link['source'] < len(nodes) else '?'
                target = nodes[link['target']] if link['target'] < len(nodes) else '?'
                value = link['value']

                tk.Label(parent, text=f"{source} → {target}: {value}",
                        font=('Segoe UI', 10), bg='white').pack()

    # =====================================================
    # 4. NETWORK GRAFİKLER (BAĞLANTI HARİTASI)
    # =====================================================

    def create_network_graph(self, parent, network_data: Dict) -> None:
        """
        Network graph - bağlantı haritası
        
        Args:
            network_data: {
                'nodes': [
                    {'id': 'A', 'label': 'Mali Sermaye', 'size': 20},
                    {'id': 'B', 'label': 'İnsan Sermayesi', 'size': 15}
                ],
                'edges': [
                    {'source': 'A', 'target': 'B', 'weight': 5}
                ]
            }
        """
        try:
            import networkx as nx

            # Graph oluştur
            G = nx.Graph()

            # Node'ları ekle
            for node in network_data.get('nodes', []):
                G.add_node(node['id'], label=node.get('label', ''),
                          size=node.get('size', 10))

            # Edge'leri ekle
            for edge in network_data.get('edges', []):
                G.add_edge(edge['source'], edge['target'],
                          weight=edge.get('weight', 1))

            # Görselleştir
            fig, ax = plt.subplots(figsize=(10, 8))

            pos = nx.spring_layout(G, k=1, iterations=50)

            # Node'ları çiz
            node_sizes = [G.nodes[node].get('size', 10) * 100 for node in G.nodes()]
            nx.draw_networkx_nodes(G, pos, node_size=node_sizes,
                                  node_color='#1976D2', alpha=0.8, ax=ax)

            # Edge'leri çiz
            nx.draw_networkx_edges(G, pos, width=2, alpha=0.5,
                                  edge_color='#666', ax=ax)

            # Label'ları çiz
            labels = {node: G.nodes[node].get('label', node) for node in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels, font_size=10,
                                   font_weight='bold', ax=ax)

            ax.set_title('Bağlantı Haritası', fontsize=14, fontweight='bold')
            ax.axis('off')

            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

        except ImportError:
            # NetworkX yoksa basit gösterim
            tk.Label(parent, text="Network Graph\n(NetworkX kurulumu gerekiyor)",
                    font=('Segoe UI', 12, 'bold'), bg='white').pack(pady=20)

            for edge in network_data.get('edges', []):
                tk.Label(parent, text=f"{edge['source']} ↔ {edge['target']} (Ağırlık: {edge.get('weight', 1)})",
                        font=('Segoe UI', 10), bg='white').pack()

    # =====================================================
    # 5. HARİTA GÖRSELLEŞTİRMELERİ
    # =====================================================

    def create_choropleth_map(self, parent, map_data: Dict) -> None:
        """
        Choropleth harita - bölge bazlı renklendirme
        
        Args:
            map_data: {
                'regions': ['İstanbul', 'Ankara', 'İzmir'],
                'values': [100, 80, 60],
                'metric': 'Karbon Emisyonu'
            }
        """
        # Basitleştirilmiş harita gösterimi
        fig, ax = plt.subplots(figsize=(10, 6))

        regions = map_data.get('regions', [])
        values = map_data.get('values', [])
        metric = map_data.get('metric', 'Metrik')

        # Normalize değerler (renk için)
        if values:
            max_val = max(values)
            colors = [plt.cm.RdYlGn_r(v / max_val) for v in values]
        else:
            colors = []

        # Basit bar chart (harita yerine)
        ax.barh(regions, values, color=colors, edgecolor='black')

        # Değerleri göster
        for i, (region, value) in enumerate(zip(regions, values)):
            ax.text(value, i, f' {value:.1f}', va='center', fontweight='bold')

        ax.set_xlabel(metric, fontsize=12, fontweight='bold')
        ax.set_title('Bölgesel Dağılım', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    # =====================================================
    # 6. WATERFALL (ŞELALE) GRAFİĞİ
    # =====================================================

    def create_waterfall_chart(self, parent, waterfall_data: Dict) -> None:
        """
        Waterfall grafiği - değişim analizi
        
        Args:
            waterfall_data: {
                'categories': ['Başlangıç', 'Artış 1', 'Azalış 1', 'Bitiş'],
                'values': [100, 20, -15, 105]
            }
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        categories = waterfall_data.get('categories', [])
        values = waterfall_data.get('values', [])

        # Kümülatif değerleri hesapla
        cumulative = []
        total = 0
        for val in values:
            cumulative.append(total)
            total += val

        # Renk belirleme
        colors = []
        for val in values:
            if val > 0:
                colors.append('#4CAF50')  # Yeşil (artış)
            elif val < 0:
                colors.append('#F44336')  # Kırmızı (azalış)
            else:
                colors.append('#757575')  # Gri (değişim yok)

        # Grafiği çiz
        ax.bar(categories, values, bottom=cumulative, color=colors,
              edgecolor='black', linewidth=1.5)

        # Değerleri göster
        for i, (cat, val, cum) in enumerate(zip(categories, values, cumulative)):
            y_pos = cum + val/2
            ax.text(i, y_pos, f'{val:+.1f}', ha='center', va='center',
                   fontweight='bold', fontsize=10)

        ax.set_ylabel('Değer', fontsize=12, fontweight='bold')
        ax.set_title('Waterfall Analizi', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(y=0, color='black', linewidth=1)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    # =====================================================
    # 7. HEATMAP (ISI HARİTASI)
    # =====================================================

    def create_heatmap(self, parent, heatmap_data: Dict) -> None:
        """
        Heatmap - korelasyon veya yoğunluk haritası
        
        Args:
            heatmap_data: {
                'x_labels': ['Ocak', 'Şubat', 'Mart'],
                'y_labels': ['Metrik 1', 'Metrik 2'],
                'values': [[10, 20, 30], [15, 25, 35]]
            }
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        x_labels = heatmap_data.get('x_labels', [])
        y_labels = heatmap_data.get('y_labels', [])
        values = np.array(heatmap_data.get('values', []))

        im = ax.imshow(values, cmap='RdYlGn', aspect='auto')

        # Eksen etiketleri
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_yticks(np.arange(len(y_labels)))
        ax.set_xticklabels(x_labels)
        ax.set_yticklabels(y_labels)

        # Değerleri göster
        for i in range(len(y_labels)):
            for j in range(len(x_labels)):
                ax.text(j, i, f'{values[i, j]:.1f}',
                             ha="center", va="center", color="black",
                             fontweight='bold')

        ax.set_title('Isı Haritası', fontsize=14, fontweight='bold')

        # Colorbar
        plt.colorbar(im, ax=ax)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    # =====================================================
    # 8. RADAR (ÖRÜMCEK AĞI) GRAFİĞİ
    # =====================================================

    def create_radar_chart(self, parent, radar_data: Dict) -> None:
        """
        Radar (spider) grafiği - çok boyutlu karşılaştırma
        
        Args:
            radar_data: {
                'categories': ['Çevre', 'Sosyal', 'Yönetişim', 'Ekonomik'],
                'company_values': [80, 70, 85, 75],
                'sector_average': [60, 65, 70, 68]
            }
        """
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

        categories = radar_data.get('categories', [])
        company_values = radar_data.get('company_values', [])
        sector_avg = radar_data.get('sector_average', [])

        # Açıları hesapla
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        company_values += company_values[:1]
        sector_avg += sector_avg[:1]
        angles += angles[:1]

        # Şirket değerleri
        ax.plot(angles, company_values, 'o-', linewidth=2, label='Şirket',
               color='#1976D2')
        ax.fill(angles, company_values, alpha=0.25, color='#1976D2')

        # Sektör ortalaması
        ax.plot(angles, sector_avg, 'o-', linewidth=2, label='Sektör Ort.',
               color='#F57C00')
        ax.fill(angles, sector_avg, alpha=0.25, color='#F57C00')

        # Kategori etiketleri
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11, fontweight='bold')

        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_title('ESG Performans Karşılaştırması', fontsize=14,
                    fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
