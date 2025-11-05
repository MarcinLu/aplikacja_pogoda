import tkinter as tk
from tkinter import ttk, messagebox
from tkintertable import TableCanvas, TableModel
import requests

API_URL = "https://danepubliczne.imgw.pl/api/data/synop/"

def pobierz_dane():
    """Pobiera dane z API IMGW i zwraca listę słowników"""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Błąd", f"Nie udało się pobrać danych z API:\n{e}")
        return []

def odswiez_tabele():
    """Pobiera aktualne dane i wyświetla je w tabeli"""
    global table, model

    dane = pobierz_dane()
    if not dane:
        return

    dane_tabeli = {}
    for i, stacja in enumerate(dane, start=1):
        # przygotowanie godziny z minutami (np. 14:00)
        godzina = stacja.get("godzina_pomiaru", "")
        godzina_str = f"{godzina}:00" if godzina != "" else ""

        rekord = {
            "Stacja": stacja["stacja"],
            "Temperatura [°C]": _to_float(stacja.get("temperatura")),
            "Ciśnienie [hPa]": _to_float(stacja.get("cisnienie")),
            "Wilgotność [%]": _to_float(stacja.get("wilgotnosc_wzgledna")),
            "Wiatr [m/s]": _to_float(stacja.get("predkosc_wiatru")),
            "Kierunek [°]": _to_float(stacja.get("kierunek_wiatru")),
            "Opady [mm]": _to_float(stacja.get("suma_opadu")),
            "Data": stacja["data_pomiaru"],
            "Godzina": godzina_str
        }
        dane_tabeli[str(i)] = rekord

    # czyszczenie poprzednich danych z ramki
    for widget in frame_tabela.winfo_children():
        widget.destroy()

    # utworzenie modelu tabeli
    model = TableModel()
    model.importDict(dane_tabeli)

    # tworzymy tabelę
    table = TableCanvas(
        frame_tabela,
        model=model,
        editable=False,
        read_only=True,
        width=1000,
        height=500,
        cellwidth=120,
        thefont=("Arial", 10),
        rowheight=22,
        showkeynamesinheader=True
    )
    table.createTableFrame()

    # włącz sortowanie po kliknięciu w nagłówek kolumny
    table.sortTableModel = True

def _to_float(value):
    """Konwertuje wartość na float jeśli możliwe, inaczej zwraca oryginał"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return value

# --- GUI ---
root = tk.Tk()
root.title("Pogoda IMGW – wszystkie stacje (sortowalna tabela)")
root.geometry("1100x600")

frame_top = ttk.Frame(root)
frame_top.pack(pady=10, fill="x")

ttk.Label(frame_top, text="Dane ze wszystkich stacji IMGW", font=("Arial", 14, "bold")).pack(side="left", padx=10)

ttk.Button(frame_top, text="🔄 Odśwież dane", command=odswiez_tabele).pack(side="right", padx=10)

frame_tabela = ttk.Frame(root)
frame_tabela.pack(fill="both", expand=True, padx=10, pady=10)

# załadowanie danych przy starcie
odswiez_tabele()

root.mainloop()
