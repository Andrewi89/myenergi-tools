import tkinter as tk


class LEDDisplay(tk.Canvas):
    def __init__(self, parent, lines=9, status="OFF", width_percentage=33, bg="black", *args, **kwargs):
        super().__init__(parent, *args, **kwargs, bg=bg)
        self.lines = lines
        self.status = status
        self.line_height = int(self.winfo_reqheight() / lines)
        self.text_ids = [self.create_text(5, (i+0.5)*self.line_height, text="",
                                          anchor="w", fill="red", font=("Helvetica", 12)) for i in range(lines)]
        self.set_status(status)

    def set_status(self, status):
        self.status = status
        for i in range(self.lines):
            self.itemconfig(
                self.text_ids[i], text=status if i == 0 else "", fill="red" if i == 0 else "white")


def on_button_click(button_id):
    # Put your heating control logic here
    # Update the LED display accordingly
    button_texts = ["Button 1", "Button 2", "Button 3", "Button 4"]
    led_display.set_status(button_texts[button_id - 1])


# Create the main window
window = tk.Tk()
window.title("Heating Control Simulator")

# Calculate the desired LED display width and height
window_width = window.winfo_screenwidth()
led_display_width = int(window_width * 0.33)
led_display_lines = 9
line_height = 20  # Adjust as needed

# Create the LED display
led_display = LEDDisplay(window, lines=led_display_lines, status="OFF",
                         width=led_display_width, height=led_display_lines*line_height, bg="black")
led_display.pack()

# Create buttons as circular shapes
button_radius = 20
button_style = {"width": button_radius * 2, "height": button_radius *
                2, "bg": "lightgray", "activebackground": "gray"}

button1 = tk.Button(
    window, text="1", command=lambda: on_button_click(1), **button_style)
button2 = tk.Button(
    window, text="2", command=lambda: on_button_click(2), **button_style)
button3 = tk.Button(
    window, text="3", command=lambda: on_button_click(3), **button_style)
button4 = tk.Button(
    window, text="4", command=lambda: on_button_click(4), **button_style)

# Pack buttons in a row
button1.pack(side=tk.LEFT, padx=5)
button2.pack(side=tk.LEFT, padx=5)
button3.pack(side=tk.LEFT, padx=5)
button4.pack(side=tk.LEFT, padx=5)

# Run the GUI main loop
window.mainloop()
