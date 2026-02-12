import tkinter as tk
from tkinter import simpledialog

from data import load_properties
from agent import AgentPreferences
from gui import ChatGPTStyleApp


def main():
    # 1) Create root (hidden first)
    root = tk.Tk()
    root.withdraw()  # hide main window

    # 2) Ask for user name
    user_id = simpledialog.askstring(
        "User Login",
        "Enter your name:"
    )

    if not user_id or not user_id.strip():
        user_id = "guest"

    user_id = user_id.strip().lower()

    # 3) Load data & preferences
    df = load_properties()
    prefs = AgentPreferences(user_id)

    # 4) Show main app
    root.deiconify()
    ChatGPTStyleApp(root, df, prefs)
    root.mainloop()


if __name__ == "__main__":
    main()

