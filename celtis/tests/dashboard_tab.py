import tkinter as tk
from tkinter import ttk
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ..ui.base_tab import BaseTab


class DashboardTab(BaseTab):
    tab_label = "📊 Dashboard"

    def build(self):
        for widget in self.winfo_children():
            widget.destroy()

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(
            btn_frame,
            text="🔄 Refresh Data (Click me after adding a test)",
            command=self.refresh,
        ).pack(side=tk.LEFT)

        stats = self._stats()
        sf = ttk.LabelFrame(self, text="Laboratory Statistics", padding=10)
        sf.pack(fill=tk.X, pady=8, padx=8)

        for ci, (k, v) in enumerate(stats.items()):
            card = tk.Frame(sf, relief=tk.RAISED, bd=2, bg="white",
                            padx=10, pady=8)
            card.grid(row=0, column=ci, padx=8, pady=4)
            tk.Label(card, text=k, bg="white",
                     font=("Times New Roman", 12)).pack()
            tk.Label(card, text=str(v), bg="white",
                     font=("Times New Roman", 12, "bold"),
                     fg="#2c3e50").pack()

        cf = ttk.Frame(self)
        cf.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=90)
        self.fig.patch.set_facecolor("#f8f8f8")

        counts = self._counts()
        vals = list(counts.values())
        if any(v > 0 for v in vals):
            ax1.pie(vals, labels=list(counts.keys()), autopct="%1.0f%%",
                    colors=["#3498db", "#2ecc71", "#e74c3c", "#f39c12"])
        else:
            ax1.text(0.5, 0.5, "No test data yet", ha="center", va="center",
                     transform=ax1.transAxes, fontsize=12, color="gray")
        ax1.set_title("Test Distribution by Category", fontweight="bold")

        monthly = self._monthly()
        ax2.bar(list(monthly.keys()), list(monthly.values()),
                color="#3498db", edgecolor="white", linewidth=0.5)
        ax2.set_title("Monthly Test Count", fontweight="bold")
        ax2.set_xlabel("Month")
        ax2.set_ylabel("Count")

        if sum(monthly.values()) == 0:
            ax2.set_ylim(0, 5)
        else:
            ax2.set_ylim(bottom=0)

        plt.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, cf)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        """Update the dashboard with new database data."""
        # Destroy canvas widget first, then close the figure.
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()
            del self.canvas
        if hasattr(self, "fig"):
            plt.close(self.fig)
            del self.fig

        for widget in self.winfo_children():
            widget.destroy()

        self.build()

    # ---- data helpers ------------------------------------------------

    def _stats(self):
        d = {}
        for n, t in [("Concrete", "concrete_tests"),
                     ("Soil", "soil_tests"),
                     ("Asphalt", "asphalt_tests"),
                     ("Aggregate", "aggregate_tests")]:
            try:
                d[n] = self.db.execute(
                    f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                print(f"[DEBUG] {t}: {d[n]}")
            except Exception as e:
                print(f"[ERROR] {t}: {e}")
                d[n] = 0

        d["Total"] = sum(d.values())

        try:
            a = self.db.execute(
                "SELECT AVG(compressive_strength) FROM concrete_tests"
            ).fetchone()[0]
            d["Avg Concrete Str."] = f"{a:.1f} MPa" if a else "N/A"
        except Exception as e:
            print(f"[ERROR] avg: {e}")
            d["Avg Concrete Str."] = "N/A"

        return d

    def _counts(self):
        d = {}
        for n, t in [("Concrete", "concrete_tests"),
                     ("Soil", "soil_tests"),
                     ("Asphalt", "asphalt_tests"),
                     ("Aggregate", "aggregate_tests")]:
            try:
                d[n] = self.db.execute(
                    f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            except Exception as e:
                print(f"[ERROR] counts {t}: {e}")
                d[n] = 0
        return d

    def _monthly(self):
        yr = str(datetime.now().year)
        d = {}
        for m in range(1, 13):
            name = datetime(int(yr), m, 1).strftime("%b")
            d[name] = 0
            for t in ["concrete_tests", "soil_tests",
                      "asphalt_tests", "aggregate_tests"]:
                try:
                    d[name] += self.db.execute(
                        f"SELECT COUNT(*) FROM {t} "
                        f"WHERE strftime('%m',date)=? AND strftime('%Y',date)=?",
                        (f"{m:02d}", yr)
                    ).fetchone()[0]
                except Exception as e:
                    print(f"[ERROR] monthly {t} month {m}: {e}")
        return d