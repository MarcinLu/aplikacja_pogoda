import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = "https://danepubliczne.imgw.pl/api/data/synop/"

class PogodaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌦 Pogoda IMGW – sortowalna i filtrowalna tabela")
        self.root.geometry("1200x650")

        self.sort_col = None
        self.sort_reverse = False
        self.all_data = []

        # --- Górny pasek ---
        top_frame = ttk.Frame(root)
        top_frame.pack(fill="x", pady=10, padx=10)

        ttk.Label(top_frame, text="Dane ze stacji IMGW", font=("Arial", 14, "bold")).pack(side="left")

        ttk.Button(top_frame, text="🔄 Odśwież", command=self.odswiez_dane).pack(side="right")

        # --- Wyszukiwarka ---
        search_frame = ttk.Frame(root)
        search_frame.pack(fill="x", pady=5, padx=10)

        ttk.Label(search_frame, text="Szukaj stacji:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", self.filtruj_stacje)

        # --- Tabela ---
        self.tree = ttk.Treeview(
            root,
            columns=("stacja", "temp", "cisnienie", "wilg", "wiatr", "kier", "opad", "data", "godzina"),
            show="headings",
            height=25
        )
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Nagłówki
        kolumny = [
            ("stacja", "Stacja"),
            ("temp", "Temperatura [°C]"),
            ("cisnienie", "Ciśnienie [hPa]"),
            ("wilg", "Wilgotność [%]"),
            ("wiatr", "Wiatr [m/s]"),
            ("kier", "Kierunek [°]"),
            ("opad", "Opady [mm]"),
            ("data", "Data"),
            ("godzina", "Godzina"),
        ]

        for col, label in kolumny:
            self.tree.heading(col, text=label, command=lambda c=col: self.sortuj_po_kolumnie(c))
            self.tree.column(col, anchor="center", width=120)

        # Pasek przewijania
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Style dla czytelności
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", rowheight=25, font=("Arial", 10))

        # Pobierz dane przy starcie
        self.odswiez_dane()

    def pobierz_dane(self):
        try:
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać danych IMGW:\n{e}")
            return []

    def odswiez_dane(self):
        self.all_data = self.pobierz_dane()
        self.wyswietl_dane(self.all_data)

    def wyswietl_dane(self, dane):
        """Czyści i wypełnia tabelę"""
        self.tree.delete(*self.tree.get_children())
        for st in dane:
            godz = f"{st.get('godzina_pomiaru', '')}:00" if st.get("godzina_pomiaru") else ""
            self.tree.insert("", "end", values=(
                st.get("stacja"),
                self._fmt(st.get("temperatura")),
                self._fmt(st.get("cisnienie")),
                self._fmt(st.get("wilgotnosc_wzgledna")),
                self._fmt(st.get("predkosc_wiatru")),
                self._fmt(st.get("kierunek_wiatru")),
                self._fmt(st.get("suma_opadu")),
                st.get("data_pomiaru"),
                godz
            ))

    def _fmt(self, val):
        try:
            return round(float(val), 1)
        except (TypeError, ValueError):
            return val if val not in [None, ""] else "-"

    def filtruj_stacje(self, event=None):
        """Filtr po nazwie stacji"""
        filtr = self.search_var.get().lower()
        if not filtr:
            dane = self.all_data
        else:
            dane = [s for s in self.all_data if filtr in s["stacja"].lower()]
        self.wyswietl_dane(dane)

    def sortuj_po_kolumnie(self, kolumna):
        """Sortuje dane po kliknięciu nagłówka"""
        mapowanie = {
            "stacja": "stacja",
            "temp": "temperatura",
            "cisnienie": "cisnienie",
            "wilg": "wilgotnosc_wzgledna",
            "wiatr": "predkosc_wiatru",
            "kier": "kierunek_wiatru",
            "opad": "suma_opadu",
            "data": "data_pomiaru",
            "godzina": "godzina_pomiaru"
        }

        klucz = mapowanie[kolumna]
        odwrotnie = False

        # kliknięcie tej samej kolumny -> odwróć sort
        if self.sort_col == kolumna:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_col = kolumna
            self.sort_reverse = False
        odwrotnie = self.sort_reverse

        def sort_key(st):
            val = st.get(klucz)
            try:
                return float(val)
            except (TypeError, ValueError):
                return str(val)

        posortowane = sorted(self.all_data, key=sort_key, reverse=odwrotnie)

        # aktualizuj dane widoczne
        self.wyswietl_dane(posortowane)

        # aktualizacja nagłówków (dodaj strzałkę)
        for col in self.tree["columns"]:
            label = col
            naglowek = self.tree.heading(col)["text"]
            naglowek_czysty = naglowek.replace(" ↑", "").replace(" ↓", "")
            if col == kolumna:
                strzalka = "↓" if odwrotnie else "↑"
                self.tree.heading(col, text=f"{naglowek_czysty} {strzalka}")
            else:
                self.tree.heading(col, text=naglowek_czysty)


if __name__ == "__main__":
    root = tk.Tk()
    app = PogodaApp(root)
    root.mainloop()
