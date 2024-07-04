import tkinter as tk
from tkinter import font

# Custom button class to create rounded buttons
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width, height, radius=25, bg='white', fg='black', font=('Helvetica', 12)):
        tk.Canvas.__init__(self, parent, width=width, height=height, bg=bg, highlightthickness=0)
        self.command = command
        self.radius = radius
        self.text = text
        self.bg = bg
        self.fg = fg
        self.font = font
        self.width = width
        self.height = height
        self.create_rounded_rectangle(0, 0, width, height, radius=self.radius, fill=self.bg, outline="")
        self.text_id = self.create_text(width // 2, height // 2, text=self.text, fill=self.fg, font=self.font)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1]
        self.create_polygon(points, **kwargs, smooth=True)

    def on_press(self, event):
        self.configure(relief="sunken")
        self.command()

    def on_release(self, event):
        self.configure(relief="raised")

# Function to add gradient background
def create_gradient(canvas, color1, color2):
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    limit = height
    for i in range(limit):
        color = "#%02x%02x%02x" % (color1[0] + (color2[0] - color1[0]) * i // limit,
                                   color1[1] + (color2[1] - color1[1]) * i // limit,
                                   color1[2] + (color2[2] - color1[2]) * i // limit)
        canvas.create_line(0, i, width, i, fill=color)

# Define placeholder functionality

# Initialize the main window

def start_menu(root, com):
    for widget in root.winfo_children():
        widget.destroy()
    def on_entry_click(event):
        if name_entry.get("1.0", "end-1c") == 'Enter your name':
            name_entry.delete(0, "end")
            name_entry.insert(0, '')
            name_entry.config(fg='black')

    def get_entry_text():
        brain = name_entry.get("1.0", "end-1c")
        print(brain)
        return com(brain)

    def on_focusout(event):
        if name_entry.get("1.0", "end-1c") == '':
            name_entry.insert(0, 'Enter your name')
            name_entry.config(fg='grey')

    # Create a canvas for the gradient background
    canvas = tk.Canvas(root, width=600, height=400, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.bind("<Configure>",
                lambda e: create_gradient(canvas, (255, 255, 255), (0, 51, 102)))  # White to Dark Blue gradient

    # Set a custom font for the title
    title_font = font.Font(family='Helvetica', size=36, weight='bold')
    subtitle_font = font.Font(family='Helvetica', size=16)

    # Create and place the title label
    title_label = tk.Label(root, text="Prompt GPT Chess", font=title_font, bg="#b4c5e4", fg="#090c9b")
    title_label_window = canvas.create_window(300, 80, window=title_label)

    # Create and place the subtitle label
    subtitle_label = tk.Label(root, text="Gpt Logic", font=subtitle_font, bg="#3c3744", fg="#b4c5e4")
    subtitle_label_window = canvas.create_window(300, 160, window=subtitle_label)

    # Create and place the entry field with placeholder text
    name_entry = tk.Text(root, font=subtitle_font, height=2, width=40, bg="#b4c5e4", fg='#3c3744')
    name_entry.insert('1.0', 'Check which pieces white has. Chose one then consider how it moves. Think of all possible moves. Respond with one of them.')
    name_entry.bind('<FocusIn>', on_entry_click)
    name_entry.bind('<FocusOut>', on_focusout)
    name_entry_window = canvas.create_window(300, 200, window=name_entry)

    # Create and place the rounded start button
    start_button = RoundedButton(root, text="Start Game", command=get_entry_text, fg="white",
                                 width=200, height=50, bg="#090c9b", radius=25, font=subtitle_font)
    start_button_window = canvas.create_window(300, 280, window=start_button)

