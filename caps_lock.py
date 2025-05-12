import ctypes
import time
import threading
import tkinter as tk
from tkinter import ttk
from queue import Queue, Empty

# Touches à surveiller
VK_CAPITAL = 0x14
VK_NUMLOCK = 0x90

# Coin de l'écran
positions = {
    "En haut à gauche": (10, 10),
    "En haut à droite": ("right", 10),
    "En bas à gauche": (10, "bottom"),
    "En bas à droite": ("right", "bottom")
}

# Fonction état touche
def get_key_state(key_code):
    return ctypes.windll.user32.GetKeyState(key_code) & 1

# Notification personnalisée via Tkinter
def show_custom_notification(root, title, message, position):
    notif = tk.Toplevel(root)
    notif.overrideredirect(True)
    notif.attributes("-topmost", True)
    notif.configure(bg="black")

    w, h = 250, 80
    screen_w = notif.winfo_screenwidth()
    screen_h = notif.winfo_screenheight()

    pos_x, pos_y = positions[position]
    if pos_x == "right":
        pos_x = screen_w - w - 10
    if pos_y == "bottom":
        pos_y = screen_h - h - 50

    notif.geometry(f"{w}x{h}+{pos_x}+{pos_y}")

    tk.Label(notif, text=title, font=("Segoe UI", 12, "bold"), fg="white", bg="black").pack(pady=(10, 0))
    tk.Label(notif, text=message, font=("Segoe UI", 10), fg="white", bg="black").pack(pady=(5, 10))

    notif.after(3000, notif.destroy)

# Thread de surveillance
def monitor_keys(position, queue_notif):
    last_caps = get_key_state(VK_CAPITAL)
    last_num = get_key_state(VK_NUMLOCK)

    while True:
        current_caps = get_key_state(VK_CAPITAL)
        current_num = get_key_state(VK_NUMLOCK)

        if current_caps != last_caps:
            état = "activée" if current_caps else "désactivée"
            queue_notif.put(("🅰️ Majuscule", f"Caps Lock {état}"))
            last_caps = current_caps

        if current_num != last_num:
            état = "activé" if current_num else "désactivé"
            queue_notif.put(("🔢 Numérique", f"Num Lock {état}"))
            last_num = current_num

        time.sleep(0.2)

# GUI de lancement
def start_gui():
    def lancer_surveillance():
        choix = combo.get()
        root.withdraw()

        # File d’attente pour communiquer entre threads
        q = Queue()

        # Lance la surveillance dans un thread
        thread = threading.Thread(target=monitor_keys, args=(choix, q), daemon=True)
        thread.start()

        # Boucle principale d'écoute des messages
        def check_queue():
            try:
                while True:
                    title, message = q.get_nowait()
                    show_custom_notification(root, title, message, choix)
            except Empty:
                pass
            root.after(100, check_queue)

        check_queue()

    root = tk.Tk()
    root.title("Surveillance des touches système")
    root.geometry("350x150")
    root.resizable(False, False)

    label = ttk.Label(root, text="Choisissez la position des notifications :", font=("Segoe UI", 11))
    label.pack(pady=10)

    combo = ttk.Combobox(root, values=list(positions.keys()), state="readonly", font=("Segoe UI", 10))
    combo.set("En bas à droite")
    combo.pack(pady=5)

    btn = ttk.Button(root, text="Démarrer", command=lancer_surveillance)
    btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    start_gui()
