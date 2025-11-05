import tkinter as tk
from tkinter import ttk, messagebox
from tkintertable import TableCanvas, TableModel
import requests

API_URL = "https://danepubliczne.imgw.pl/api/data/synop/"

class SortowalnaTabela:
    def __init__(self, root):
        self.root = root
        self.root.title("Pogoda IMGW – sortowalna i filtrowalna tabela")
        self.root.geometry("1150x650")

        self.sort_col = None
        self.sort_reverse = False
        self.all_data = []
        self.filtered_data = []

        # --- GÓRNY PANEL ---
        top_frame = ttk.Frame(root)
        top_frame.pack(fill="x", pady=5, padx=10)

        ttk.Label(
            top_frame, text="🌤 Dane ze stacji IMGW", font=("Arial", 14, "bold")
        ).pack(side="left", padx=5)

        ttk.Button(
            top_frame, text="🔄 Odśwież", command=self.odswiez_dane
        ).pack(side="right", padx=5)

        # --- FILTR STACJI ---
        filter_frame = ttk.Frame(root)
        filter_frame.pack(fill="x", pady=5, padx=10)

        ttk.Label(filter_frame, text="Szukaj stacji:").pack(side="left", padx=(0,5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", self.filtruj_stacje)

        # --- TABELA ---
        self.table_frame = ttk.Frame(root)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.model = None
        self.table = None

        # Pobranie danych
        self.odswiez_dane()

    def pobierz_dane(self):
        """Pobiera dane z API IMGW"""
        try:
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać danych z API:\n{e}")
            return []

    def odswiez_dane(self):
        """Aktualizuje dane i odświeża tabelę"""
        self.all_data = self.pobierz_dane()
        self.filtered_data = self.all_data
        self.sort_col = None
        self.sort_reverse = False
        self.stworz_tabele(self.filtered_data)

    def filtruj_stacje(self, event=None):
        """Filtruje dane po nazwie stacji"""
        filtr = self.search_var.get().lower().strip()
        if not filtr:
            self.filtered_data = self.all_data
        else:
            self.filtered_data = [
                st for st in self.all_data if filtr in st["stacja"].lower()
            ]
        self.stworz_tabele(self.filtered_data)

    def stworz_tabele(self, dane):
        """Tworzy tabelę w ramce"""
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        if not dane:
            ttk.Label(
                self.table_frame, text="Brak danych do wyświetlenia.", font=("Arial", 12)
            ).pack(pady=20)
            return

        dane_tabeli = {}
        for i, stacja in enumerate(dane, start=1):
            godzina = stacja.get("godzina_pomiaru", "")
            godzina_str = f"{godzina}:00" if godzina != "" else ""
            rekord = {
                "Stacja": stacja["stacja"],
                "Temperatura [°C]": self._to_float(stacja.get("temperatura")),
                "Ciśnienie [hPa]": self._to_float(stacja.get("cisnienie")),
                "Wilgotność [%]": self._to_float(stacja.get("wilgotnosc_wzgledna")),
                "Wiatr [m/s]": self._to_float(stacja.get("predkosc_wiatru")),
                "Kierunek [°]": self._to_float(stacja.get("kierunek_wiatru")),
                "Opady [mm]": self._to_float(stacja.get("suma_opadu")),
                "Data": stacja["data_pomiaru"],
                "Godzina": godzina_str,
            }
            dane_tabeli[str(i)] = rekord

        # --- Dodanie strzałek do nagłówków ---
        base_columns = [
            "Stacja",
            "Temperatura [°C]",
            "Ciśnienie [hPa]",
            "Wilgotność [%]",
            "Wiatr [m/s]",
            "Kierunek [°]",
            "Opady [mm]",
            "Data",
            "Godzina",
        ]

        headers = []
        for col in base_columns:
            if self.sort_col and col.startswith(self.sort_col):
                arrow = "↓" if self.sort_reverse else "↑"
                headers.append(f"{col} {arrow}")
            else:
                headers.append(col)

        self.model = TableModel()
        self.model.importDict(dane_tabeli)
        self.model.columnNames = headers

        self.table = TableCanvas(
            self.table_frame,
            model=self.model,
            editable=False,
            read_only=True,
            width=1100,
            height=500,
            cellwidth=120,
            thefont=("Arial", 10),
            rowheight=22,
        )
        self.table.createTableFrame()
        self.table.bind("<Button-1>", self.on_header_click)

    def on_header_click(self, event):
        """Kliknięcie w nagłówek kolumny"""
        col_clicked = self.table.get_col_clicked(event)
        if not col_clicked:
            return

        colname = self.table.model.columnNames[col_clicked]
        colname = colname.replace(" ↑", "").replace(" ↓", "")

        # jeśli kliknięto ponownie ten sam nagłówek → zmiana kierunku
        if self.sort_col == colname:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_col = colname
            self.sort_reverse = False

        self.sortuj_po_kolumnie(colname)

    def sortuj_po_kolumnie(self, kolumna):
        """Sortowanie po wybranej kolumnie"""
        def klucz_sort(x):
            val = x.get(kolumna)
            try:
                return float(val)
            except (ValueError, TypeError):
                return str(val)

        posortowane = sorted(
            [rek for rek in self.model.getAllCells().values()],
            key=klucz_sort,
            reverse=self.sort_reverse,
        )
        self.stworz_tabele(posortowane)

    def _to_float(self, value):
        """Konwertuje wartość na float jeśli to możliwe"""
        try:
            return round(float(value), 1)
        except (ValueError, TypeError):
            return value


if __name__ == "__main__":
    root = tk.Tk()
    app = SortowalnaTabela(root)
    root.mainloop()
