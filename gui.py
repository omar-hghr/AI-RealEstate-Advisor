import tkinter as tk
from tkinter import scrolledtext, ttk
import webbrowser

from model import recommend


class ChatGPTStyleApp:
    def __init__(self, root, df, prefs):
        self.root, self.df, self.prefs = root, df, prefs

        root.title("Real Estate Investment Advisor — ChatGPT Style ✨🏠")
        root.geometry("1000x700")
        root.configure(bg="#f3f7f6")
        root.minsize(900, 600)

        self.page_size = 3
        self.current_page_start = 0
        self.all_results = []
        self.current_results = []
        self.shown_results = []
        self.waiting_for_choice = False
        self.user_budget = None

        self.override_weights = None

        self.build_top_filters()
        self.build_chat_area()
        self.build_input_area()

        self.bot_send(
            "Hello 👋 I'm your Real Estate Investment Advisor.\n"
            "I will show you the best 3 matches at a time.\n"
            "If you don't like them, type 9 and I'll show 3 more.\n"
            "When you like one, type its number (1–3).\n"
            "To stop, type 0.\n\n"
            "Extra commands: type roi / risk / price to prioritize, or reset to go back to normal."
        )

    def weights_text(self):
        return (
            f"Learned weights — ROI: {self.prefs.w_roi:.2f}  "
            f"Risk: {self.prefs.w_risk:.2f}  "
            f"Budget: {self.prefs.w_budget:.2f}"
        )

    def build_top_filters(self):
        top = tk.Frame(self.root, bg="#ffffff", bd=0)
        top.pack(side=tk.TOP, fill=tk.X, padx=12, pady=12)

        tk.Label(top, text="Budget (EGP):", bg="#ffffff", fg="#333", font=("Segoe UI", 10)).grid(
            row=0, column=0, sticky="w"
        )
        self.budget_entry = tk.Entry(top, bg="#fbfbfb", fg="#111", relief=tk.GROOVE, bd=1, width=12)
        self.budget_entry.grid(row=0, column=1, padx=(6, 18))

        cities = ["Any"] + sorted(set(str(c) for c in self.df["city"].dropna().unique()))
        tk.Label(top, text="City:", bg="#ffffff", fg="#333", font=("Segoe UI", 10)).grid(row=0, column=2, sticky="w")
        self.city_var = tk.StringVar(value="Any")
        ttk.OptionMenu(top, self.city_var, cities[0], *cities).grid(row=0, column=3, padx=(6, 18))

        types = ["Any"] + sorted(set(str(t) for t in self.df["property_type"].dropna().unique()))
        tk.Label(top, text="Type:", bg="#ffffff", fg="#333", font=("Segoe UI", 10)).grid(row=0, column=4, sticky="w")
        self.type_var = tk.StringVar(value="Any")
        ttk.OptionMenu(top, self.type_var, types[0], *types).grid(row=0, column=5, padx=(6, 18))

        self.search_btn = tk.Button(
            top, text="🔎 Search", bg="#10a37f", fg="white", bd=0, padx=12, pady=6, command=self.on_search_click
        )
        self.search_btn.grid(row=0, column=6, sticky="e")

        top.grid_columnconfigure(7, weight=1)

        self.weights_label = tk.Label(top, text=self.weights_text(), bg="#ffffff", fg="#666", font=("Segoe UI", 9))
        self.weights_label.grid(row=0, column=7, sticky="e")

    def build_chat_area(self):
        middle = tk.Frame(self.root, bg="#f7f7f7")
        middle.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        self.chat = scrolledtext.ScrolledText(
            middle, wrap=tk.WORD, bg="#ffffff", fg="#111",
            font=("Segoe UI", 11), padx=12, pady=12, bd=0
        )
        self.chat.pack(fill=tk.BOTH, expand=True)
        self.chat.config(state=tk.DISABLED)

        self.chat.tag_config("bot_label", foreground="#057a60", font=("Segoe UI", 9, "bold"))
        self.chat.tag_config("user_label", foreground="#6a2fb6", font=("Segoe UI", 9, "bold"))
        self.chat.tag_config(
            "bot_msg",
            background="#e9f8f4",
            foreground="#054f3f",
            lmargin1=6,
            lmargin2=6,
            rmargin=60,
            spacing3=6,
        )
        self.chat.tag_config(
            "user_msg",
            background="#f4e9ff",
            foreground="#3b0054",
            lmargin1=60,
            lmargin2=60,
            rmargin=6,
            spacing3=6,
        )

    def build_input_area(self):
        bottom = tk.Frame(self.root, bg="#ffffff")
        bottom.pack(fill=tk.X, padx=12, pady=(0, 12))

        self.entry = tk.Entry(bottom, bg="#fbfbfb", fg="#111", relief=tk.GROOVE, bd=1, font=("Segoe UI", 11))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=8)
        self.entry.bind("<Return>", self.on_send)

        tk.Button(bottom, text="💬 Send", bg="#6a2fb6", fg="white", bd=0, padx=14, pady=6, command=self.on_send).pack(
            side=tk.RIGHT
        )

    def bot_send(self, msg):
        self.chat.config(state=tk.NORMAL)
        self.chat.insert(tk.END, "\nBot:\n", "bot_label")
        self.chat.insert(tk.END, "  " + msg + "\n", "bot_msg")
        self.chat.config(state=tk.DISABLED)
        self.chat.yview(tk.END)

    def user_send(self, msg):
        self.chat.config(state=tk.NORMAL)
        self.chat.insert(tk.END, "\nYou:\n", "user_label")
        self.chat.insert(tk.END, "  " + msg + "\n", "user_msg")
        self.chat.config(state=tk.DISABLED)
        self.chat.yview(tk.END)

    def insert_clickable_link(self, text_before, url, link_text="View property"):
        self.chat.config(state=tk.NORMAL)
        self.chat.insert(tk.END, "  " + text_before, "bot_msg")

        tag = f"link_{self.chat.index(tk.END)}"
        self.chat.insert(tk.END, link_text + "\n", (tag,))
        self.chat.tag_config(tag, foreground="blue", underline=True)
        self.chat.tag_bind(tag, "<Button-1>", lambda e, u=url: webbrowser.open(u))

        self.chat.config(state=tk.DISABLED)
        self.chat.yview(tk.END)

    def on_search_click(self):
        txt = self.budget_entry.get().strip()
        self.user_budget = None
        if txt and txt.lower() != "any":
            try:
                self.user_budget = float(txt)
                if self.user_budget <= 0:
                    raise ValueError
            except ValueError:
                self.bot_send("⚠ Please enter a valid positive number for budget, or leave empty.")
                return

        city = self.city_var.get()
        ptype = self.type_var.get()

        mode = ""
        if self.override_weights:
            if self.override_weights.get("w_roi", 0) > 0.7:
                mode = " (mode: ROI)"
            elif self.override_weights.get("w_risk", 0) > 0.7:
                mode = " (mode: Risk)"
            elif self.override_weights.get("w_budget", 0) > 0.7:
                mode = " (mode: Price)"

        self.bot_send(f"🔎 Searching for {ptype} in {city}{mode} ...")

        self.all_results = recommend(self.df, self.user_budget, city, ptype, self.prefs, self.override_weights)

        self.current_page_start = 0
        self.shown_results = []
        self.waiting_for_choice = True

        if not self.all_results:
            self.bot_send("Sorry — no matches found. 😕")
            self.waiting_for_choice = False
            return

        self.show_next_page()

    def show_next_page(self):
        total = len(self.all_results)
        if self.current_page_start >= total:
            self.bot_send("No more properties. Type 0 to finish or search again.")
            return

        end = self.current_page_start + self.page_size
        page = self.all_results[self.current_page_start:end]
        self.current_results = page
        self.shown_results.extend(page)
        self.current_page_start = end

        self.chat.config(state=tk.NORMAL)
        self.chat.insert(tk.END, "\nBot:\n", "bot_label")
        self.chat.insert(tk.END, "Here are the top options for you:\n", "bot_msg")

        for i, p in enumerate(page, start=1):
            emoji = "🏢" if any(x in str(p["type"]).lower() for x in ["apartment", "flat"]) else "🏠"
            self.chat.insert(
                tk.END,
                f"{i}) {p['name']} {emoji} — {p['type']}, {p['city']}\n"
                f"   💰 Price: {p['price']:.0f} EGP   •   📈 ROI: {p['roi']*100:.1f}%   •   ⚖ Risk: {p['risk_text']}\n",
                "bot_msg"
            )

            if p.get("url"):
                tag = f"url_{self.current_page_start}_{i}"
                self.chat.insert(tk.END, "   🔗 Link: ", "bot_msg")
                self.chat.insert(tk.END, "View property\n", (tag,))
                self.chat.tag_config(tag, foreground="blue", underline=True)
                self.chat.tag_bind(tag, "<Button-1>", lambda e, u=p["url"]: webbrowser.open(u))

            self.chat.insert(tk.END, "─" * 36 + "\n", "bot_msg")

        has_more = self.current_page_start < total
        self.chat.insert(
            tk.END,
            ("Type 1-3 to choose, 9 for 3 more, or 0 to stop.\n" if has_more
             else "This is the last page. Type 1-3 to choose, or 0 to stop.\n"),
            "bot_msg"
        )
        self.chat.config(state=tk.DISABLED)
        self.chat.yview(tk.END)

    def on_send(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self.user_send(text)

        low = text.lower().strip()

        if low in ("9", "more", "next", "other", "others", "show more"):
            return self.show_next_page()

        if low in ("roi", "higher roi", "more roi"):
            self.override_weights = {"w_roi": 0.85, "w_risk": 0.10, "w_budget": 0.05}
            self.bot_send("✅ OK — prioritizing higher ROI. Searching again...")
            return self.on_search_click()

        if low in ("risk", "lower risk", "less risk", "safe", "safer"):
            self.override_weights = {"w_roi": 0.10, "w_risk": 0.85, "w_budget": 0.05}
            self.bot_send("✅ OK — prioritizing lower risk. Searching again...")
            return self.on_search_click()

        if low in ("price", "lower price", "cheaper", "budget"):
            self.override_weights = {"w_roi": 0.10, "w_risk": 0.05, "w_budget": 0.85}
            self.bot_send("✅ OK — prioritizing lower price. Searching again...")
            return self.on_search_click()

        if low in ("reset", "normal", "default"):
            self.override_weights = None
            self.bot_send("✅ Back to normal ranking (learned weights). Searching again...")
            return self.on_search_click()

        if not self.waiting_for_choice:
            return self.bot_send("Use Search to get recommendations, or type roi / risk / price / reset.")

        try:
            choice = int(low)
        except ValueError:
            return self.bot_send("Type 1-3 to choose, 9 for more, 0 to stop, or roi/risk/price/reset.")

        if choice == 0:
            self.prefs.update_from_rejection(self.shown_results, self.user_budget)
            self.weights_label.config(text=self.weights_text())
            self.waiting_for_choice = False
            return self.bot_send("Got it — I learned from your rejection. ✅")

        if 1 <= choice <= len(self.current_results):
            chosen = self.current_results[choice - 1]
            self.prefs.update_from_choice(chosen, self.user_budget)
            self.weights_label.config(text=self.weights_text())
            self.waiting_for_choice = False

            self.bot_send(f"Nice choice — {chosen['name']} ({chosen['city']}). I'll learn from that. 🤖")
            if chosen.get("url"):
                self.chat.config(state=tk.NORMAL)
                self.chat.insert(tk.END, "\nBot:\n", "bot_label")
                self.insert_clickable_link("Here is the link if you want to view your chosen property: ", chosen["url"])
            return

        return self.bot_send("Out of range. Type 1-3, 9, or 0.")
