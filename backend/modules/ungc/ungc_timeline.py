import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UN Global Compact - Timeline Visualizer
Historical progress tracking and visualization
"""
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import Dict, List

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from modules.ungc.ungc_manager_enhanced import UNGCManagerEnhanced
from config.database import DB_PATH


class UNGCTimelineVisualizer(ttk.Frame):
    """Timeline visualization for UNGC progress"""

    def __init__(self, parent, db_path: str, company_id: int, **kwargs):
        super().__init__(parent, **kwargs)
        self.db_path = db_path
        self.company_id = company_id
        self.manager = UNGCManagerEnhanced(db_path)

        self._create_ui()

    def _create_ui(self):
        """Create UI"""
        # Control panel
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(control_frame, text="Görselleştirme Tipi:").pack(side='left', padx=5)

        self.viz_type = tk.StringVar(value="overall")
        ttk.Radiobutton(
            control_frame,
            text="Genel Skor",
            variable=self.viz_type,
            value="overall",
            command=self._update_visualization
        ).pack(side='left', padx=5)

        ttk.Radiobutton(
            control_frame,
            text="Kategori Skorları",
            variable=self.viz_type,
            value="categories",
            command=self._update_visualization
        ).pack(side='left', padx=5)

        ttk.Radiobutton(
            control_frame,
            text="İlke Skorları",
            variable=self.viz_type,
            value="principles",
            command=self._update_visualization
        ).pack(side='left', padx=5)

        ttk.Button(
            control_frame,
            text="Yenile",
            command=self._update_visualization
        ).pack(side='right', padx=5)

        # Chart frame
        self.chart_frame = ttk.Frame(self)
        self.chart_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Initial chart
        self._update_visualization()

    def _get_historical_data(self, start_year: int, end_year: int) -> List[Dict]:
        """Get historical data for years"""
        data = []
        for year in range(start_year, end_year + 1):
            period = str(year)
            try:
                result = self.manager.calculate_overall_score(self.company_id, period)
                data.append({
                    'year': year,
                    'period': period,
                    'overall_score': result['overall_score'],
                    'level': result['level'],
                    'category_scores': result['category_scores'],
                    'principle_scores': result['principle_scores']
                })
            except Exception as e:
                # No data for this year
                logging.error(f"Silent error caught: {str(e)}")
        return data

    def _plot_overall_trend(self, ax, data: List[Dict]):
        """Plot overall score trend"""
        if not data:
            ax.text(0.5, 0.5, 'Veri Yok', ha='center', va='center', transform=ax.transAxes)
            return

        years = [d['year'] for d in data]
        scores = [d['overall_score'] for d in data]

        ax.plot(years, scores, marker='o', linewidth=2, markersize=8, color='#3b82f6')
        ax.fill_between(years, scores, alpha=0.3, color='#3b82f6')

        # Level lines
        ax.axhline(y=40, color='#CD7F32', linestyle='--', alpha=0.5, label='Learner')
        ax.axhline(y=70, color='#C0C0C0', linestyle='--', alpha=0.5, label='Active')

        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Score (%)', fontsize=12)
        ax.set_title('UNGC Overall Compliance Score - Historical Trend', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(0, 100)

    def _plot_category_trends(self, ax, data: List[Dict]):
        """Plot category score trends"""
        if not data:
            ax.text(0.5, 0.5, 'Veri Yok', ha='center', va='center', transform=ax.transAxes)
            return

        years = [d['year'] for d in data]

        # Get categories
        categories = list(data[0]['category_scores'].keys())
        colors = ['#ef4444', '#f59e0b', '#10b981', '#6366f1']

        for idx, category in enumerate(categories):
            scores = [d['category_scores'].get(category, 0) for d in data]
            ax.plot(years, scores, marker='o', linewidth=2, markersize=6,
                   label=category, color=colors[idx % len(colors)])

        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Score (%)', fontsize=12)
        ax.set_title('UNGC Category Scores - Historical Trends', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(0, 100)

    def _plot_principle_heatmap(self, ax, data: List[Dict]):
        """Plot principle scores as heatmap"""
        if not data:
            ax.text(0.5, 0.5, 'Veri Yok', ha='center', va='center', transform=ax.transAxes)
            return

        years = [d['year'] for d in data]
        principles = [f"P{p['principle_number']}" for p in data[0]['principle_scores']]

        # Create matrix
        matrix = []
        for d in data:
            row = [p['score'] for p in d['principle_scores']]
            matrix.append(row)

        # Transpose for better view
        matrix_t = list(zip(*matrix))

        im = ax.imshow(matrix_t, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)

        # Set ticks
        ax.set_xticks(range(len(years)))
        ax.set_xticklabels(years)
        ax.set_yticks(range(len(principles)))
        ax.set_yticklabels(principles)

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Score (%)', rotation=270, labelpad=15)

        # Add text annotations
        for i in range(len(principles)):
            for j in range(len(years)):
                ax.text(j, i, f'{matrix_t[i][j]:.0f}',
                             ha="center", va="center", color="black", fontsize=8)

        ax.set_title('UNGC Principle Scores - Heatmap', fontsize=14, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Principle', fontsize=12)

    def _update_visualization(self):
        """Update visualization"""
        # Clear existing widgets
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Get historical data (last 5 years)
        current_year = datetime.now().year
        data = self._get_historical_data(current_year - 4, current_year)

        if not data:
            ttk.Label(
                self.chart_frame,
                text="Henüz veri yok. Lütfen KPI verilerini girin.",
                font=('Helvetica', 12)
            ).pack(pady=50)
            return

        # Create figure
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)

        # Plot based on selection
        viz_type = self.viz_type.get()
        if viz_type == "overall":
            self._plot_overall_trend(ax, data)
        elif viz_type == "categories":
            self._plot_category_trends(ax, data)
        elif viz_type == "principles":
            self._plot_principle_heatmap(ax, data)

        fig.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)


class UNGCProgressComparison(tk.Toplevel):
    """Window for comparing progress between periods"""

    def __init__(self, parent, db_path: str, company_id: int):
        super().__init__(parent)
        self.db_path = db_path
        self.company_id = company_id
        self.manager = UNGCManagerEnhanced(db_path)

        self.title("UNGC Progress Comparison")
        self.geometry("800x600")

        self._create_ui()

    def _create_ui(self):
        """Create UI"""
        # Period selection
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(control_frame, text="Başlangıç:").pack(side='left', padx=5)
        self.start_year = ttk.Spinbox(
            control_frame,
            from_=2020,
            to=2030,
            width=10
        )
        self.start_year.set(datetime.now().year - 1)
        self.start_year.pack(side='left', padx=5)

        ttk.Label(control_frame, text="Bitiş:").pack(side='left', padx=5)
        self.end_year = ttk.Spinbox(
            control_frame,
            from_=2020,
            to=2030,
            width=10
        )
        self.end_year.set(datetime.now().year)
        self.end_year.pack(side='left', padx=5)

        ttk.Button(
            control_frame,
            text="Karşılaştır",
            command=self._compare_periods
        ).pack(side='left', padx=10)

        # Results frame
        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(fill='both', expand=True, padx=10, pady=10)

    def _compare_periods(self):
        """Compare two periods"""
        # Clear results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        start = self.start_year.get()
        end = self.end_year.get()

        try:
            result = self.manager.track_progress(self.company_id, start, end)

            # Display results
            # Overall improvement
            ttk.Label(
                self.results_frame,
                text="Progress Comparison",
                font=('Helvetica', 14, 'bold')
            ).pack(pady=10)

            overall_text = f"Overall Score: {result['start_score']:.1f}% → {result['end_score']:.1f}%\n"
            overall_text += f"Improvement: {result['overall_improvement']:+.1f}%\n"
            overall_text += f"Level: {result['start_level']} → {result['end_level']}"

            ttk.Label(
                self.results_frame,
                text=overall_text,
                font=('Helvetica', 12)
            ).pack(pady=10)

            # Category improvements table
            ttk.Label(
                self.results_frame,
                text="Category Improvements",
                font=('Helvetica', 12, 'bold')
            ).pack(pady=10)

            table_data = [['Category', 'Improvement']]
            for category, improvement in result['category_improvements'].items():
                table_data.append([category, f"{improvement:+.1f}%"])

            tree = ttk.Treeview(self.results_frame, columns=('Category', 'Improvement'),
                               show='headings', height=5)
            tree.heading('Category', text='Category')
            tree.heading('Improvement', text='Improvement')

            for row in table_data[1:]:
                tree.insert('', 'end', values=row)

            tree.pack(pady=10)

        except Exception as e:
            ttk.Label(
                self.results_frame,
                text=f"Error: {str(e)}",
                foreground='red'
            ).pack(pady=20)


if __name__ == '__main__':
    # Test
    root = tk.Tk()
    root.title("UNGC Timeline Test")
    root.geometry("1000x700")

    db_path = DB_PATH
    visualizer = UNGCTimelineVisualizer(root, db_path, company_id=1)
    visualizer.pack(fill='both', expand=True)

    root.mainloop()

