import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = "https://danepubliczne.imgw.pl/api/data/synop/"

def pobierz_dane():
    """Pobiera dane z API IMGW i zwraca jako listę słowników"""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Błąd", f"Nie udało się pobrać danych z API:\n{e}")
        return []

def pokaz_dane():
    """Wyświetla dane o wybranej stacji"""
    nazwa_stacji = combo_stacje.get()
    if not nazwa_stacji:
        messagebox.showwarning("Uwaga", "Wybierz stację pogodową!")
        return

    stacja = next((s for s in dane if s["stacja"] == nazwa_stacji), None)
    if not stacja:
        messagebox.showerror("Błąd", "Nie znaleziono danych dla tej stacji.")
        return

    tekst = (
        f"🌦️ {stacja['stacja']}\n\n"
        f"Temperatura: {stacja['temperatura']} °C\n"
        f"Ciśnienie: {stacja['cisnienie']} hPa\n"
        f"Wilgotność: {stacja.get('wilgotnosc_wzgledna', 'brak danych')} %\n"
        f"Wiatr: {stacja.get('predkosc_wiatru', 'brak danych')} m/s\n"
        f"Kierunek wiatru: {stacja.get('kierunek_wiatru', 'brak danych')}°\n"
        f"Opady: {stacja.get('suma_opadu', 'brak danych')} mm\n"
        f"Data pomiaru: {stacja['data_pomiaru']} {stacja['godzina_pomiaru']}:00"
    )
    label_dane.config(text=tekst)

# --- GUI ---
root = tk.Tk()
root.title("Pogoda IMGW – dane z API")
root.geometry("400x400")
root.resizable(False, False)

ttk.Label(root, text="Wybierz stację pogodową:", font=("Arial", 12)).pack(pady=10)

# Pobranie danych i lista stacji
dane = pobierz_dane()
stacje = sorted([s["stacja"] for s in dane])

combo_stacje = ttk.Combobox(root, values=stacje, width=30, state="readonly")
combo_stacje.pack(pady=5)

ttk.Button(root, text="Pokaż dane", command=pokaz_dane).pack(pady=10)

label_dane = ttk.Label(root, text="", font=("Arial", 10), justify="left")
label_dane.pack(pady=10)

root.mainloop()
