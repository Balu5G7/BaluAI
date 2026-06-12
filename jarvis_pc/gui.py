import customtkinter as ctk
import math
import time
import psutil
import platform
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("J.A.R.V.I.S. — Core Interface")

# --- Borderless Transparent Overlay Settings ---
root.overrideredirect(True)
root.attributes("-topmost", True)
root.wm_attributes("-transparentcolor", "black")

# Position dynamically at center-right of screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
WIN_W, WIN_H = 320, 350
x = screen_width - WIN_W - 40
y = (screen_height // 2) - (WIN_H // 2)
root.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")
root.configure(fg_color="black")

# --- Draggable Window ---
def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def do_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    nx = root.winfo_x() + deltax
    ny = root.winfo_y() + deltay
    root.geometry(f"+{nx}+{ny}")

root.bind("<ButtonPress-1>", start_move)
root.bind("<ButtonRelease-1>", stop_move)
root.bind("<B1-Motion>", do_move)

# ═══════════════════════════════════════════════════
# ANIMATED ARC REACTOR CANVAS
# ═══════════════════════════════════════════════════
canvas = ctk.CTkCanvas(root, width=300, height=300, bg="black", highlightthickness=0)
canvas.pack(pady=(15, 5))

# ═══════════════════════════════════════════════════
# STATUS LABEL
# ═══════════════════════════════════════════════════
status = ctk.CTkLabel(
    root, text="Initializing...",
    font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
    text_color="#00e5ff"
)
status.pack(pady=(2, 5))

# ═══════════════════════════════════════════════════
# ANIMATION STATE MACHINE
# ═══════════════════════════════════════════════════
angle = 0
pulse_dir = 1
pulse_radius = 0
anim_state = "idle"
current_model_name = "Gemini 2.5 Flash"

def set_animation_state(state: str):
    global anim_state
    anim_state = state

def set_current_model(name: str):
    global current_model_name
    current_model_name = name

def animate_core():
    global angle, pulse_dir, pulse_radius, anim_state
    canvas.delete("all")

    cx, cy = 150, 150

    if anim_state == "idle":
        speed, pulse_speed = 1, 0.3
        color_main, color_sec, color_glow = "#00e5ff", "#0088aa", "#003344"
        pulse_max = 5
    elif anim_state == "listening":
        speed, pulse_speed = 4, 1.0
        color_main, color_sec, color_glow = "#00ff66", "#00cc55", "#004422"
        pulse_max = 12
    elif anim_state == "processing":
        speed, pulse_speed = 12, 2.0
        color_main, color_sec, color_glow = "#ffaa00", "#ff6600", "#552200"
        pulse_max = 8
    elif anim_state == "angry":
        speed, pulse_speed = 6, 3.0
        color_main, color_sec, color_glow = "#ff0000", "#aa0000", "#440000"
        pulse_max = 15
    elif anim_state == "alert":
        speed, pulse_speed = 5, 1.5
        color_main, color_sec, color_glow = "#ffff00", "#aaaa00", "#444400"
        pulse_max = 10
    elif anim_state == "speaking":
        speed, pulse_speed = 3, 2.5
        color_main, color_sec, color_glow = "#00e5ff", "#ffffff", "#005577"
        pulse_max = 18
    elif anim_state == "browsing":
        speed, pulse_speed = 6, 1.5
        color_main, color_sec, color_glow = "#7000ff", "#a020f0", "#300050"
        pulse_max = 14
    elif anim_state == "typing":
        speed, pulse_speed = 8, 2.0
        color_main, color_sec, color_glow = "#00e5ff", "#ff007f", "#004040"
        pulse_max = 10
    elif anim_state == "clicking":
        speed, pulse_speed = 15, 3.5
        color_main, color_sec, color_glow = "#ffffff", "#00e5ff", "#ffffff"
        pulse_max = 20
    else:
        speed, pulse_speed = 1, 0.5
        color_main, color_sec, color_glow = "#00e5ff", "#00ffcc", "#003344"
        pulse_max = 10

    # Glow Background
    for g in range(3):
        gr = 45 + pulse_radius + (g * 14)
        canvas.create_oval(cx-gr, cy-gr, cx+gr, cy+gr, outline=color_glow, width=2)

    # Techy Outer Boundary
    canvas.create_oval(cx-140, cy-140, cx+140, cy+140, outline=color_glow, width=1, dash=(2, 4))
    canvas.create_oval(cx-130, cy-130, cx+130, cy+130, outline=color_sec, width=2, dash=(10, 5))

    # Rotating Outer Arcs
    for i in range(6):
        sa = angle + (i * 60)
        canvas.create_arc(cx-120, cy-120, cx+120, cy+120, start=sa, extent=30, outline=color_main, width=3, style="arc")
        sa_rev = -(angle * 1.2) + (i * 60)
        canvas.create_arc(cx-110, cy-110, cx+110, cy+110, start=sa_rev, extent=20, outline=color_sec, width=1, style="arc")

    # Heavy Data Ring
    for i in range(4):
        sa = (angle * 2) + (i * 90)
        canvas.create_arc(cx-86, cy-86, cx+86, cy+86, start=sa, extent=45, outline=color_main, width=5, style="arc")

    # Rotating Hexagram
    for offset in [0, 60]:
        pts = []
        for i in range(3):
            rad = math.radians(-(angle * 1.5) + offset + (i * 120))
            px = cx + 60 * math.cos(rad)
            py = cy + 60 * math.sin(rad)
            pts.extend([px, py])
        canvas.create_polygon(pts, outline=color_sec, fill="", width=2)

    # Pulsing Inner Core
    r = 30 + pulse_radius
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=color_main, width=3)
    canvas.create_oval(cx-(r-4), cy-(r-4), cx+(r-4), cy+(r-4), outline=color_sec, width=1, dash=(2, 2))

    # Center Dot
    dot_r = 10 + (pulse_radius * 0.3)
    canvas.create_oval(cx-dot_r, cy-dot_r, cx+dot_r, cy+dot_r, fill=color_main, outline="#ffffff")

    angle += speed
    if angle >= 360:
        angle -= 360

    pulse_radius += pulse_speed * pulse_dir
    if pulse_radius > pulse_max:
        pulse_dir = -1
    elif pulse_radius < 0:
        pulse_dir = 1

    root.after(30, animate_core)

animate_core()


# ═══════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════
def update_status(text):
    status.configure(text=text)


def start_ipc_polling(speak_queue, status_queue, speak_done_event):
    """Poll IPC queues from worker processes and drive TTS / HUD updates."""
    from core.ipc import MsgType
    from core.stt_tts import speak

    def poll_ipc():
        while True:
            try:
                msg_type, payload = status_queue.get_nowait()
            except Exception:
                break

            if msg_type == MsgType.STATUS:
                update_status(payload)
            elif msg_type == MsgType.ANIMATION:
                set_animation_state(payload)
            elif msg_type == MsgType.SHUTDOWN:
                root.quit()
                return

        try:
            msg_type, text = speak_queue.get_nowait()
        except Exception:
            msg_type = None

        if msg_type == MsgType.SPEAK:
            speak(text)
            speak_done_event.set()

        root.after(50, poll_ipc)

    root.after(50, poll_ipc)


if __name__ == "__main__":
    root.mainloop()
