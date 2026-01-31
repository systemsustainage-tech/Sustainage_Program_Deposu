#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eşleştirme Diyagramı
SDG-GRI-TSRS bağlantılarını görselleştirir
"""

try:
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.info("[UYARI] matplotlib yuklu degil. 'pip install matplotlib' yapin")

import logging
import os
import sqlite3
from typing import Dict


class MappingDiagram:
    """SDG-GRI-TSRS eşleştirme diyagramı oluşturucu"""

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')

    def create_sdg_flow_diagram(self, sdg_number: int, output_path: str = None) -> str:
        """
        Tek bir SDG için akış diyagramı
        
        SDG → GRI → TSRS bağlantılarını gösterir
        
        Args:
            sdg_number: SDG numarası (1-17)
            output_path: Çıktı dosya yolu
        
        Returns:
            str: Kaydedilen dosya yolu
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib gerekli")

        # Bağlantıları al
        connections = self._get_connections(sdg_number)

        # Figür oluştur
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Başlık
        ax.text(5, 9.5, f'SDG {sdg_number} Eşleştirme Akışı',
               ha='center', fontsize=16, fontweight='bold')

        # SDG kutusu (sol)
        sdg_box = FancyBboxPatch((0.5, 7), 2, 1.5,
                                boxstyle="round,pad=0.1",
                                facecolor='#E5243B', edgecolor='black', linewidth=2)
        ax.add_patch(sdg_box)
        ax.text(1.5, 7.75, f'SDG {sdg_number}', ha='center', va='center',
               color='white', fontsize=14, fontweight='bold')

        # GRI kutuları (orta)
        gri_items = connections.get('gri', [])
        gri_y = 7.5 - (len(gri_items) * 0.3)

        for i, gri in enumerate(gri_items[:5]):  # Max 5
            y_pos = gri_y - (i * 0.6)
            gri_box = FancyBboxPatch((4, y_pos), 2, 0.5,
                                    boxstyle="round,pad=0.05",
                                    facecolor='#4C9F38', edgecolor='black')
            ax.add_patch(gri_box)
            ax.text(5, y_pos + 0.25, gri, ha='center', va='center',
                   color='white', fontsize=9)

            # Ok çiz (SDG → GRI)
            arrow = FancyArrowPatch((2.5, 7.75), (4, y_pos + 0.25),
                                   arrowstyle='->', mutation_scale=20,
                                   linewidth=2, color='#666')
            ax.add_patch(arrow)

        # TSRS kutuları (sağ)
        tsrs_items = connections.get('tsrs', [])
        tsrs_y = 7.5 - (len(tsrs_items) * 0.3)

        for i, tsrs in enumerate(tsrs_items[:5]):  # Max 5
            y_pos = tsrs_y - (i * 0.6)
            tsrs_box = FancyBboxPatch((7.5, y_pos), 2, 0.5,
                                     boxstyle="round,pad=0.05",
                                     facecolor='#00689D', edgecolor='black')
            ax.add_patch(tsrs_box)
            ax.text(8.5, y_pos + 0.25, tsrs, ha='center', va='center',
                   color='white', fontsize=9)

            # Ok çiz (GRI → TSRS)
            if gri_items:
                arrow = FancyArrowPatch((6, 7.75), (7.5, y_pos + 0.25),
                                       arrowstyle='->', mutation_scale=20,
                                       linewidth=2, color='#666')
                ax.add_patch(arrow)

        # Legend
        legend_elements = [
            mpatches.Patch(facecolor='#E5243B', label='SDG'),
            mpatches.Patch(facecolor='#4C9F38', label='GRI'),
            mpatches.Patch(facecolor='#00689D', label='TSRS')
        ]
        ax.legend(handles=legend_elements, loc='lower right')

        # Kaydet
        if not output_path:
            output_path = f'data/reports/sdg{sdg_number}_mapping_diagram.png'

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        logging.info(f"[OK] Diyagram olusturuldu: {output_path}")
        return output_path

    def _get_connections(self, sdg_number: int) -> Dict:
        """SDG bağlantılarını al"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        connections = {'gri': [], 'tsrs': []}

        try:
            # GRI bağlantıları
            cursor.execute("""
                SELECT DISTINCT gri_code FROM map_sdg_gri 
                WHERE sdg_no = ?
                LIMIT 10
            """, (sdg_number,))
            connections['gri'] = [row[0] for row in cursor.fetchall()]

            # TSRS bağlantıları
            cursor.execute("""
                SELECT DISTINCT tsrs_code FROM map_sdg_tsrs 
                WHERE sdg_no = ?
                LIMIT 10
            """, (sdg_number,))
            connections['tsrs'] = [row[0] for row in cursor.fetchall()]

        except Exception as e:
            logging.info(f"[UYARI] Baglanti sorgusu: {e}")
        finally:
            conn.close()

        return connections

