import customtkinter as ctk
import math

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("J.A.R.V.I.S. - Core Interface")

# --- Borderless Transparent Overlay Settings ---
root.overrideredirect(True) # Remove borders and title bar
root.attributes("-topmost", True) # Always stay on top of other windows
root.wm_attributes("-transparentcolor", "black") # Make black background completely transparent

# Position it dynamically at the center of the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (400 // 2)
y = (screen_height // 2) - (550 // 2)
root.geometry(f"400x550+{x}+{y}")
root.configure(fg_color="black")

# --- Draggable Window Functionality ---
def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def do_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")

root.bind("<ButtonPress-1>", start_move)
root.bind("<ButtonRelease-1>", stop_move)
root.bind("<B1-Motion>", do_move)

# Title
title = ctk.CTkLabel(
    root,
    text="J.A.R.V.I.S.",
    font=ctk.CTkFont(family="Helvetica", size=36, weight="bold"),
    text_color="#00e5ff"  # Neon Cyan
)
title.pack(pady=(30, 10))

# Animated Canvas (Arc Reactor Style)
canvas = ctk.CTkCanvas(root, width=300, height=300, bg="black", highlightthickness=0)
canvas.pack(pady=20)

# Status Label (Top)
status = ctk.CTkLabel(
    root,
    text="System Ready",
    font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
    text_color="#aaaaaa"
)
status.pack(pady=5)

# Animation Variables
angle = 0
pulse_dir = 1
pulse_radius = 0
anim_state = "idle"

def set_animation_state(state: str):
    """Sets the animation state: 'idle', 'listening', 'processing', 'speaking'."""
    global anim_state
    anim_state = state

def animate_core():
    global angle, pulse_dir, pulse_radius, anim_state
    canvas.delete("all")
    
    cx, cy = 150, 150
    
    # State dependent parameters
    if anim_state == "idle":
        speed = 1
        pulse_speed = 0.3
        color_main = "#00e5ff"
        color_sec = "#0088aa"
        color_glow = "#003344"
        pulse_max = 5
    elif anim_state == "listening":
        speed = 4
        pulse_speed = 1.0
        color_main = "#00ff66"
        color_sec = "#00cc55"
        color_glow = "#004422"
        pulse_max = 12
    elif anim_state == "processing":
        speed = 12
        pulse_speed = 2.0
        color_main = "#ffaa00"
        color_sec = "#ff6600"
        color_glow = "#552200"
        pulse_max = 8
    elif anim_state == "angry":
        speed = 6
        pulse_speed = 3.0
        color_main = "#ff0000"
        color_sec = "#aa0000"
        color_glow = "#440000"
        pulse_max = 15
    elif anim_state == "alert":
        speed = 5
        pulse_speed = 1.5
        color_main = "#ffff00"
        color_sec = "#aaaa00"
        color_glow = "#444400"
        pulse_max = 10
    elif anim_state == "speaking":
        speed = 3
        pulse_speed = 2.5
        color_main = "#00e5ff"
        color_sec = "#ffffff"
        color_glow = "#005577"
        pulse_max = 18
    else:
        speed = 1
        pulse_speed = 0.5
        color_main = "#00e5ff"
        color_sec = "#00ffcc"
        color_glow = "#003344"
        pulse_max = 10

    # 1. Glow Background (Simulated with expanding faint circles)
    for g in range(3):
        gr = 40 + pulse_radius + (g * 15)
        canvas.create_oval(cx-gr, cy-gr, cx+gr, cy+gr, outline=color_glow, width=2)

    # 2. Techy Dashed Outer Boundary
    canvas.create_oval(cx-140, cy-140, cx+140, cy+140, outline=color_glow, width=1, dash=(2, 4))
    canvas.create_oval(cx-130, cy-130, cx+130, cy+130, outline=color_sec, width=2, dash=(10, 5))
    
    # 3. Rotating Outer Arcs (Fragmented)
    for i in range(6):
        start_angle = angle + (i * 60)
        canvas.create_arc(cx-115, cy-115, cx+115, cy+115, start=start_angle, extent=30, outline=color_main, width=3, style="arc")
        # Inner counter-rotating thin dashes
        start_angle_rev = -(angle * 1.2) + (i * 60)
        canvas.create_arc(cx-105, cy-105, cx+105, cy+105, start=start_angle_rev, extent=20, outline=color_sec, width=1, style="arc")
        
    # 4. Heavy Data Ring (Inner)
    for i in range(4):
        start_angle = (angle * 2) + (i * 90)
        canvas.create_arc(cx-85, cy-85, cx+85, cy+85, start=start_angle, extent=45, outline=color_main, width=6, style="arc")

    # 5. Rotating Geometric Core (Hexagram simulation)
    geo_radius = 60
    points = []
    for i in range(3):
        # Calculate 3 points for a triangle, rotating with `angle`
        rad = math.radians(-(angle * 1.5) + (i * 120))
        px = cx + geo_radius * math.cos(rad)
        py = cy + geo_radius * math.sin(rad)
        points.extend([px, py])
    canvas.create_polygon(points, outline=color_sec, fill="", width=2)
    
    # Second inverted triangle
    points_inv = []
    for i in range(3):
        rad = math.radians(-(angle * 1.5) + 60 + (i * 120))
        px = cx + geo_radius * math.cos(rad)
        py = cy + geo_radius * math.sin(rad)
        points_inv.extend([px, py])
    canvas.create_polygon(points_inv, outline=color_sec, fill="", width=2)

    # 6. Pulsing Inner Core
    r = 30 + pulse_radius
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=color_main, width=4)
    canvas.create_oval(cx-(r-5), cy-(r-5), cx+(r-5), cy+(r-5), outline=color_sec, width=1, dash=(2, 2))
    
    # 7. Center Energy Dot
    dot_r = 10 + (pulse_radius * 0.3)
    canvas.create_oval(cx-dot_r, cy-dot_r, cx+dot_r, cy+dot_r, fill=color_main, outline="#ffffff")

    # Update state for next frame
    angle += speed
    if angle >= 360:
        angle -= 360
        
    pulse_radius += pulse_speed * pulse_dir
    if pulse_radius > pulse_max:
        pulse_dir = -1
    elif pulse_radius < 0:
        pulse_dir = 1
        
    root.after(30, animate_core)

# Start the animation loop
animate_core()

def update_status(text):
    """Updates the main status indicator."""
    status.configure(text=text)

if __name__ == "__main__":
    root.mainloop()

