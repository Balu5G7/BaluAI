import customtkinter as ctk

ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.geometry("800x500")
app.title("JARVIS")

label = ctk.CTkLabel(
    app,
    text="JARVIS ONLINE",
    font=("Arial", 30)
)
label.pack(pady=20)

textbox = ctk.CTkTextbox(app, width=700, height=300)
textbox.pack(pady=20)

textbox.insert("end", "Welcome Sir...\n")

app.mainloop()
