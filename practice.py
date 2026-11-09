import random
import tkinter as tk


GAME_SECONDS = 30
TARGET_RADIUS = 28
BACKGROUND = "#101827"
TARGET_COLOR = "#38bdf8"


class AimTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Aim Trainer")
        self.root.geometry("700x560")
        self.root.configure(bg=BACKGROUND)
        self.root.resizable(False, False)

        self.score = 0
        self.time_left = GAME_SECONDS
        self.target_id = None
        self.timer_id = None
        self.playing = False

        tk.Label(
            root,
            text="AIM TRAINER",
            font=("Segoe UI", 22, "bold"),
            fg="white",
            bg=BACKGROUND,
        ).pack(pady=(18, 8))

        stats = tk.Frame(root, bg=BACKGROUND)
        stats.pack(fill="x", padx=32, pady=(0, 12))

        self.score_label = tk.Label(
            stats, text="Score: 0", font=("Segoe UI", 14, "bold"),
            fg="#cbd5e1", bg=BACKGROUND
        )
        self.score_label.pack(side="left")

        self.timer_label = tk.Label(
            stats, text=f"Time: {GAME_SECONDS}", font=("Segoe UI", 14, "bold"),
            fg="#cbd5e1", bg=BACKGROUND
        )
        self.timer_label.pack(side="right")

        self.canvas = tk.Canvas(
            root,
            width=636,
            height=360,
            bg="#1e293b",
            highlightthickness=0,
            cursor="crosshair",
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)

        self.message_label = tk.Label(
            root,
            text="Press Start, then click the targets!",
            font=("Segoe UI", 11),
            fg="#cbd5e1",
            bg=BACKGROUND,
        )
        self.message_label.pack(pady=10)

        self.start_button = tk.Button(
            root,
            text="Start game",
            command=self.start_game,
            font=("Segoe UI", 12, "bold"),
            fg="#0f172a",
            bg="#38bdf8",
            activebackground="#7dd3fc",
            relief="flat",
            padx=24,
            pady=8,
            cursor="hand2",
        )
        self.start_button.pack()

    def start_game(self):
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        self.score = 0
        self.time_left = GAME_SECONDS
        self.playing = True
        self.score_label.config(text="Score: 0")
        self.timer_label.config(text=f"Time: {self.time_left}")
        self.message_label.config(text="Click the circles as quickly as you can!")
        self.start_button.config(state="disabled")
        self.spawn_target()
        self.timer_id = self.root.after(1000, self.tick)

    def spawn_target(self):
        if self.target_id is not None:
            self.canvas.delete(self.target_id)

        width = int(self.canvas["width"])
        height = int(self.canvas["height"])
        x = random.randint(TARGET_RADIUS, width - TARGET_RADIUS)
        y = random.randint(TARGET_RADIUS, height - TARGET_RADIUS)

        self.target_id = self.canvas.create_oval(
            x - TARGET_RADIUS,
            y - TARGET_RADIUS,
            x + TARGET_RADIUS,
            y + TARGET_RADIUS,
            fill=TARGET_COLOR,
            outline="white",
            width=3,
        )

    def handle_click(self, event):
        if not self.playing or self.target_id is None:
            return

        x1, y1, x2, y2 = self.canvas.coords(self.target_id)
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        distance_squared = (event.x - center_x) ** 2 + (event.y - center_y) ** 2

        if distance_squared <= TARGET_RADIUS**2:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.spawn_target()

    def tick(self):
        self.time_left -= 1
        self.timer_label.config(text=f"Time: {self.time_left}")

        if self.time_left <= 0:
            self.playing = False
            self.target_id = None
            self.canvas.delete("all")
            self.message_label.config(text=f"Time's up! Final score: {self.score}")
            self.start_button.config(text="Play again", state="normal")
            self.timer_id = None
            return

        self.timer_id = self.root.after(1000, self.tick)


def main():
    root = tk.Tk()
    AimTrainer(root)
    root.mainloop()


if __name__ == "__main__":
    main()