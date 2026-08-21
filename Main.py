import random as rand
import math
import time
import os
import sys
import pygame
import csv
import pandas as pd
from tkinter import *
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence

def resource_path(relative_path):
    # Bundled read-only assets: PyInstaller extracts --add-data files to sys._MEIPASS at runtime.
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def writable_path(relative_path):
    # Files that must persist across runs: sys._MEIPASS is wiped after the exe exits, so save
    # data has to live next to the actual executable instead.
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

ASSETS_DIR = resource_path("Assets")
SAVE_FILE = writable_path("save.csv")
SAVE_HEADERS = ["aquas", "autoclickers", "upgrades"]

def load_data():
    data = pd.read_csv(os.path.join(ASSETS_DIR, "ClickerData.csv"))
    return data


def load_save():
    try:
        with open(SAVE_FILE, newline="") as f:
            row = next(csv.DictReader(f))
            return int(row["aquas"])
    except (FileNotFoundError, StopIteration, KeyError):
        return 0


def save_aquas(aquas):
    with open(SAVE_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SAVE_HEADERS)
        writer.writeheader()
        writer.writerow({"aquas": aquas, "autoclickers": 0, "upgrades": 0})


def autoClicker_CostCalc(cost, owned):
    newPrice = cost * (1.087 ** owned)

    return newPrice

def aquaClicker(res):
    #global aquas
    print("Entered aquaClicker")
    aquas = load_save()
    addedAquaClickValue = 0
    autoClickValue = 0
    

    autoClickers = {"Sad_Dog": 0, "Best_Friend": 0, "Petal_Boy": 0}
    '''
    future reference of autoclicker data storage and retrieval.
    age = user.get("age")
    '''

    

    pygame.mixer.init()
    click_sound = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "dahellBoom.mp3"))

    root2 = tk.Tk()
    root2.title("Aqua Clicker")

    try:
        bg_width, bg_height = (int(v) for v in res.split("x"))
    except ValueError:
        bg_width, bg_height = 800, 600

    # Clamp to the actual screen so a resolution bigger than the monitor
    # doesn't open partially off-screen.
    screen_w, screen_h = root2.winfo_screenwidth(), root2.winfo_screenheight()
    bg_width = min(bg_width, screen_w)
    bg_height = min(bg_height, screen_h - 80)
    root2.geometry(f"{bg_width}x{bg_height}")
    root2.minsize(500, 400)

    bg_source = Image.open(os.path.join(ASSETS_DIR, "Cliffs_location.png"))
    bg_label = tk.Label(root2, borderwidth=0)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    aquaAmounttext = tk.Label(root2, text="Aqua Clicker")
    aquaAmountinteger = tk.Label(root2, text=f"{aquas}")
    aquaAmounttext.place(relx=0.5, rely=0.03, anchor="n")
    aquaAmountinteger.place(relx=0.5, rely=0.10, anchor="n")


    aqua_1 = tk.Canvas(root2, highlightthickness=0)
    aqua_1.place(relx=0.5, rely=0.18, anchor="n", relwidth=0.4, relheight=0.75)

    aqua_gif = Image.open(os.path.join(ASSETS_DIR, "aqua-deltarune.gif"))
    frame_w, frame_h = aqua_gif.size
    aqua_raw_frames = []
    aqua_frame_delays = []
    for frame in ImageSequence.Iterator(aqua_gif):
        aqua_raw_frames.append(frame.convert("RGBA"))
        aqua_frame_delays.append(frame.info.get("duration", 100))
    aqua_frames = []
    aqua_1_image = None
    aqua_1_label = None

    def rebuild_aqua(canvas_w, canvas_h):
        # Re-renders the character at a scale that fits the current canvas
        # size, since the canvas itself grows/shrinks with the window.
        nonlocal aqua_frames, aqua_1_image, aqua_1_label
        scale = max(1, min(canvas_w // frame_w, (canvas_h - 80) // frame_h))
        aqua_frames = [
            ImageTk.PhotoImage(frame.resize((frame_w * scale, frame_h * scale), Image.NEAREST))
            for frame in aqua_raw_frames
        ]
        aqua_1.delete("all")
        aqua_1_image = aqua_1.create_image(canvas_w // 2, 20, anchor="n", image=aqua_frames[0])
        aqua_1_label = aqua_1.create_text(
            canvas_w // 2, 20 + frame_h * scale + 30,
            fill="white", font=("Arial", 14), justify="center"
        )

    def animate_aqua(index=0):
        if aqua_frames:
            aqua_1.itemconfig(aqua_1_image, image=aqua_frames[index % len(aqua_frames)])
        root2.after(aqua_frame_delays[index % len(aqua_frame_delays)], animate_aqua, (index + 1) % len(aqua_frame_delays))

    def on_resize(event=None):
        nonlocal bg_width, bg_height
        if event is not None and event.widget is root2:
            bg_width, bg_height = event.width, event.height

        resized = bg_source.resize((max(bg_width, 1), max(bg_height, 1)))
        bg_photo = ImageTk.PhotoImage(resized)
        bg_label.configure(image=bg_photo)
        bg_label.image = bg_photo

        rebuild_aqua(max(int(bg_width * 0.4), 1), max(int(bg_height * 0.75), 1))

        font_size = max(12, min(28, bg_width // 40))
        aquaAmounttext.config(font=("Arial", font_size))
        aquaAmountinteger.config(font=("Arial", font_size))

    on_resize()
    root2.bind("<Configure>", on_resize)
    animate_aqua()

    def onAquaClick(event):
        #runs every click, it's self explanatory. nonlocal because global refuses to work.
        nonlocal aquas
        click_sound.play()
        aquas += (1 + addedAquaClickValue)
        aquaAmountinteger.config(text=f"{aquas}")
        if aqua_1_label is not None:
            aqua_1.itemconfig(aqua_1_label, text="Click Her!")
        save_aquas(aquas)

    aqua_1.bind("<Button-1>", onAquaClick)

    bg_label.lower()




    #future ref of auto clicker stuffs
    '''
        # jarona_1_img = tk.PhotoImage(file="CookieClicker/Assets/aquaFace_1.png")
        # jarona_1 = tk.Canvas(root2, width=375, height=600, highlightthickness=0)
        # jarona_1.image = jarona_1_img
        # jarona_1.create_image(0, 0, anchor="nw", image=jarona_1_img)
        # jarona_1_label = jarona_1.create_text(
        #     250, 625,
        #     text=f"Jarona\n{autoClicker_CostCalc(100000, autoClickers.get('Petal_Boy'))} Aquas",
        #     fill="white", font=("Arial", 14), justify="center"
        # )

        # def onJaronaClick(event):
        #     nonlocal aquas
        #     cost = autoClicker_CostCalc(100000, autoClickers.get('Petal_Boy'))
        
        keep line below as furture reference of failure to resolve an if statement in a function, 
        and return to the main function.
            if aquas < cost:
                return

        #     if aquas < cost:
        #         return
        #     aquas -= cost
        #     autoClickers['Petal_Boy'] += 1
        #     aquaAmountinteger.config(text=f"{aquas}")
        #     jarona_1.itemconfig(jarona_1_label,
        #         text=f"Jarona\n{autoClicker_CostCalc(100000, autoClickers.get('Petal_Boy'))} Aquas")

        # jarona_1.bind("<Button-1>", onJaronaClick)
        # jarona_1.grid(padx=5, pady=5)
    '''
    print("success?")

    root2.mainloop()



def main():
    print("entered main")
    root1 = tk.Tk()
    root1.title("Select window size")
    root1.geometry(f"{350}x{200}")
    x, y, start = 0, 0, False

    listbox = tk.Listbox(root1, selectmode=tk.SINGLE, width=30, height=3)
    listbox.grid(pady=10)
    resolutions = ["1280x720", "800x600", "1920x1080"]
    for i in resolutions:
        listbox.insert(tk.END, i)

    def resSelec(listbox):
        # curselection() returns tuple of the selected index numbers
        selected_indices = listbox.curselection()

        # Map indices back to the actual text values
        selected_items = [listbox.get(i) for i in selected_indices]

        print(f"Selected: {', '.join(selected_items)}")

        return selected_items[0] if selected_items else None

    def onAccept():
        # Closes window after accepting res
        res = resSelec(listbox)
        root1.destroy()
        aquaClicker(f"{res}")

    acceptInput = tk.Button(root1,
                            text="Accept",
                            command=onAccept
    )

    acceptInput.grid(padx=150, pady=0)
    
    print("success?")
    root1.mainloop()





main()






