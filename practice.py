import math
import random
import tkinter as tk


GAME_SECONDS = 30
MIN_TARGET_RADIUS = 16
MAX_TARGET_RADIUS = 38
MAX_TARGETS = 3
MOVING_TARGET_CHANCE = 0.35
STATIONARY_SHRINK_PER_FRAME = 0.04
BACKGROUND = "#101827"
TARGET_COLOR = "#38bdf8"
POP_COLORS = ("#ffffff", "#bae6fd", "#7dd3fc", "#38bdf8")


class AimTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Aim Trainer")
        self.root.geometry("700x560")
        self.root.configure(bg=BACKGROUND)
        self.root.resizable(False, False)

        self.score = 0
        self.shots = 0
        self.time_left = GAME_SECONDS
        self.targets = {}
        self.timer_id = None
        self.movement_id = None
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

        self.accuracy_label = tk.Label(
            stats, text="Accuracy: 0%", font=("Segoe UI", 14, "bold"),
            fg="#cbd5e1", bg=BACKGROUND
        )
        self.accuracy_label.pack(side="left", expand=True)

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
        if self.movement_id is not None:
            self.root.after_cancel(self.movement_id)
            self.movement_id = None

        self.score = 0
        self.shots = 0
        self.time_left = GAME_SECONDS
        self.playing = True
        self.score_label.config(text="Score: 0")
        self.accuracy_label.config(text="Accuracy: 0%")
        self.timer_label.config(text=f"Time: {self.time_left}")
        self.message_label.config(text="Hit the targets! Some will move.")
        self.start_button.config(state="disabled")
        self.canvas.delete("all")
        self.targets.clear()
        for _ in range(MAX_TARGETS):
            self.spawn_target()
        self.movement_id = self.root.after(20, self.move_targets)
        self.timer_id = self.root.after(1000, self.tick)

    def spawn_target(self):
        if len(self.targets) >= MAX_TARGETS:
            return

        width = int(self.canvas["width"])
        height = int(self.canvas["height"])
        radius = random.randint(MIN_TARGET_RADIUS, MAX_TARGET_RADIUS)

        for _ in range(50):
            x = random.randint(radius, width - radius)
            y = random.randint(radius, height - radius)
            if all(
                (x - (x1 + x2) / 2) ** 2 + (y - (y1 + y2) / 2) ** 2
                >= (radius + target["radius"]) ** 2
                for target_id, target in self.targets.items()
                for x1, y1, x2, y2 in [self.canvas.coords(target_id)]
            ):
                break

        target_id = self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=TARGET_COLOR,
            outline="white",
            width=3,
        )

        if random.random() < MOVING_TARGET_CHANCE:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 3.5)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
        else:
            velocity = (0.0, 0.0)

        self.targets[target_id] = {"radius": radius, "velocity": velocity}

    def move_targets(self):
        if not self.playing:
            self.movement_id = None
            return

        width = int(self.canvas["width"])
        height = int(self.canvas["height"])

        for target_id, target in self.targets.items():
            dx, dy = target["velocity"]
            x1, y1, x2, y2 = self.canvas.coords(target_id)

            if dx == 0 and dy == 0:
                target["radius"] = max(
                    MIN_TARGET_RADIUS,
                    target["radius"] - STATIONARY_SHRINK_PER_FRAME,
                )
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                radius = target["radius"]
                self.canvas.coords(
                    target_id,
                    center_x - radius,
                    center_y - radius,
                    center_x + radius,
                    center_y + radius,
                )

            if x1 + dx < 0 or x2 + dx > width:
                dx = -dx
            if y1 + dy < 0 or y2 + dy > height:
                dy = -dy

            target["velocity"] = (dx, dy)
            self.canvas.move(target_id, dx, dy)

        self.movement_id = self.root.after(20, self.move_targets)

    def show_pop_effect(self, x, y, radius):
        effect_id = self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            outline=POP_COLORS[0],
            width=5,
        )

        def animate(frame=0):
            if frame >= len(POP_COLORS):
                self.canvas.delete(effect_id)
                return

            if not self.canvas.type(effect_id):
                return

            effect_radius = radius + frame * 9
            self.canvas.coords(
                effect_id,
                x - effect_radius,
                y - effect_radius,
                x + effect_radius,
                y + effect_radius,
            )
            self.canvas.itemconfig(
                effect_id,
                outline=POP_COLORS[frame],
                width=max(1, 5 - frame),
            )
            self.root.after(35, animate, frame + 1)

        animate()

    def handle_click(self, event):
        if not self.playing:
            return

        self.shots += 1
        overlapping_items = self.canvas.find_overlapping(
            event.x, event.y, event.x, event.y
        )
        hit_target = next(
            (target_id for target_id in reversed(overlapping_items)
             if target_id in self.targets),
            None,
        )

        if hit_target is not None:
            x1, y1, x2, y2 = self.canvas.coords(hit_target)
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            radius = self.targets.pop(hit_target)["radius"]
            self.canvas.delete(hit_target)
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.show_pop_effect(center_x, center_y, radius)
            self.spawn_target()

        self.update_accuracy()

    def update_accuracy(self):
        accuracy = round(self.score / self.shots * 100) if self.shots else 0
        self.accuracy_label.config(text=f"Accuracy: {accuracy}%")

    def tick(self):
        self.time_left -= 1
        self.timer_label.config(text=f"Time: {self.time_left}")

        if self.time_left <= 0:
            self.playing = False
            self.targets.clear()
            if self.movement_id is not None:
                self.root.after_cancel(self.movement_id)
                self.movement_id = None
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