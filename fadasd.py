import tkinter as tk
from tkcalendar import Calendar

root = tk.Tk()
root.title("Calendar Example")
root.geometry("400x400")

# Create Calendar
cal = Calendar(root, selectmode="day", year=2025, month=9, day=21)
cal.pack(pady=20)

# Function to get selected date
def grab_date():
    selected_date = cal.get_date()
    tk.Label(root, text=f"Selected Date: {selected_date}").pack(pady=5)

# Button to confirm selection
btn = tk.Button(root, text="Get Date", command=grab_date)
btn.pack(pady=10)

root.mainloop()
