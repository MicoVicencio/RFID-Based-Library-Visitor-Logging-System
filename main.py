import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime, timedelta
from tkinter import ttk
import keyboard
import threading
from database import LibraryDatabase 
from crud_library import RFID_App
from pdf_generator import generate_logs_pdf
import time
from tkcalendar import DateEntry
 


class LibraryLoggingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("RFID Library Logging System")
        self.root.state('zoomed')
        self.cooldown_seconds = 60  # 1 minute cooldown

        
        self.credentials = {
            "admin": "123",
            "staff": "password123"
        }

        # 🔒 Disable window controls (minimize, maximize, close)
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)  # Disable close (X)
        self.root.resizable(False, False)  # Disable resize
        self.root.attributes("-toolwindow", True)  # Removes minimize/maximize buttons (Windows only)

        # 🚫 Lock current size after zoom
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        self.root.minsize(width, height)
        self.root.maxsize(width, height)

        # 🚫 Prevent dragging the window
        self.fixed_x = self.root.winfo_x()
        self.fixed_y = self.root.winfo_y()
        self.root.bind("<Configure>", self.prevent_move)

        # Initialize database and CRUD
        self.db = LibraryDatabase(self)
        self.crud = RFID_App(root, self)
        self.rfid_enabled = True

        # Initialize menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Load and display background image
        self.bg_label = None
        self.bg_image = None
        self.load_background("pic.png")

        # Create menus
        self.create_menus()

        # Bind resize event to update background size
        self.root.bind("<Configure>", self.resize_background)

        # RFID monitoring thread
        threading.Thread(target=self.monitor_rfid, daemon=True).start()
    
    def security(self, step):
        self.pause_rfid()
        """
        Creates a modal login window to secure administrative actions.
        """
        login_window = tk.Toplevel(self.root)
        login_window.title("User Login")
        login_window.geometry("300x250")
        login_window.resizable(False, False)

        # Center window
        x = self.root.winfo_x() + (self.root.winfo_width() // 2 - 150)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2 - 125)
        login_window.geometry(f"300x250+{x}+{y}")

        # Prevent interaction with the main window until login is complete
        login_window.transient(self.root)
        login_window.grab_set()

        login_frame = tk.Frame(login_window, padx=20, pady=20)
        login_frame.pack(expand=True, fill="both")

        tk.Label(login_frame, text="User Login", font=("Arial", 16, "bold")).pack(pady=(0, 15))

        tk.Label(login_frame, text="Username:", font=("Arial", 12)).pack(anchor='w')
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12))
        self.username_entry.pack(fill='x', pady=5)

        tk.Label(login_frame, text="Password:", font=("Arial", 12)).pack(anchor='w')
        self.password_entry = tk.Entry(login_frame, show="*", font=("Arial", 12))
        self.password_entry.pack(fill='x', pady=5)

        tk.Button(login_frame, text="Login", font=("Arial", 12, "bold"),
                  command=lambda: self.check_credentials(login_window, step)).pack(fill='x', pady=8)

        tk.Button(login_frame, text="Cancel", font=("Arial", 12),
                  command=login_window.destroy).pack(fill='x', pady=5)

        # Allow pressing Enter to submit
        login_window.bind("<Return>", lambda event: self.check_credentials(login_window, step))

    def check_credentials(self, login_window, step):
        """
        Checks for valid credentials and proceeds with the correct action.
        """
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username in self.credentials and self.credentials[username] == password:
            login_window.destroy()
            if step == "show_logs":   # ✅ fixed typo
                self.show_logs()
            elif step == "print_logs":
                self.print_logs()
            elif step == "import_bulk":
                self.import_students()
            elif step == "add_student":
                self.add_student()
            elif step == "update_student":
                self.update_student()
            elif step == "delete_student":
                self.delete_student()
            elif step == "view_student":
                self.show_students()
            elif step == "quit_program":  # ✅ match menu
                self.close_program()
            elif step == "manage_purpose":
                self.manage_purpose_list()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            self.password_entry.delete(0, tk.END)
        
        self.resume_rfid()

            
            

    def disable_event(self):
        # 🚫 Prevent window close
        pass  

    def prevent_move(self, event):
        # 🚫 Reset position if user tries to drag window
        if self.root.winfo_x() != self.fixed_x or self.root.winfo_y() != self.fixed_y:
            self.root.geometry(f"+{self.fixed_x}+{self.fixed_y}")


    def load_background(self, img_path):
        img = Image.open(img_path)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        img = img.resize((screen_width, screen_height), Image.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(img)

        if self.bg_label is None:
            self.bg_label = tk.Label(self.root, image=self.bg_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.bg_label.config(image=self.bg_image)
            self.bg_label.image = self.bg_image

    def resize_background(self, event):
        if self.bg_label:
            self.load_background("pic.png")

    def create_menus(self):
        # --- File Menu ---
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="System", menu=file_menu)
        file_menu.add_command(label="Exit", command=lambda: self.security("quit_program"))

        # --- Transactions Menu ---
        transactions_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Transactions", menu=transactions_menu)
        transactions_menu.add_command(label="Show Logs", command=lambda: self.security("show_logs"))
        transactions_menu.add_command(label="Generate PDF Reports", command=lambda: self.security("print_logs"))

        # --- Database Menu ---
        database_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Database", menu=database_menu)

        # Student Sub-menu
        student_menu = tk.Menu(database_menu, tearoff=0)
        database_menu.add_cascade(label="Students", menu=student_menu)
        student_menu.add_command(label="Import Bulk Student List", command=lambda: self.security("import_bulk"))
        student_menu.add_command(label="Add New Student", command=lambda: self.security("add_student"))
        student_menu.add_command(label="Update Student", command=lambda: self.security("update_student"))
        student_menu.add_command(label="Delete Student", command=lambda: self.security("delete_student"))
        student_menu.add_command(label="View Students", command=lambda: self.security("view_student"))
        # --- Settings Menu ---
        settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Manage Options in Purpose", command=lambda: self.security("manage_purpose"))

        # --- Help Menu ---
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    # === Command functions ===
    def show_students(self):
        self.crud.view_users()
        
    def show_logs(self):
        self.show_students()
        
 
    def print_logs(self):
        """Open a Toplevel window to select date range and optional student name for PDF generation."""
        top = tk.Toplevel(self.root)
        top.title("Generate Logs PDF")
        top.geometry("450x350")
        top.resizable(False, False)
        top.transient(self.root)

        tk.Label(
            top,
            text="Generate Library Logs PDF",
            font=("Arial", 16, "bold"),
            pady=10
        ).pack()

        form_frame = tk.Frame(top, padx=20, pady=10)
        form_frame.pack(fill="both", expand=True)

        # --- Name filter ---
        tk.Label(form_frame, text="Student Name (optional):", font=("Arial", 14)).grid(row=0, column=0, sticky="w", pady=10)
        name_var = tk.StringVar()
        name_entry = tk.Entry(form_frame, textvariable=name_var, font=("Arial", 14))
        name_entry.grid(row=0, column=1, pady=10, sticky="ew")

        # --- Start date ---
        tk.Label(form_frame, text="Start Date:", font=("Arial", 14)).grid(row=1, column=0, sticky="w", pady=10)
        start_date = DateEntry(
            form_frame, width=18, background="darkblue",
            foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd", font=("Arial", 12)
        )
        start_date.grid(row=1, column=1, pady=10, sticky="ew")

        # --- End date ---
        tk.Label(form_frame, text="End Date:", font=("Arial", 14)).grid(row=2, column=0, sticky="w", pady=10)
        end_date = DateEntry(
            form_frame, width=18, background="darkblue",
            foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd", font=("Arial", 12)
        )
        end_date.grid(row=2, column=1, pady=10, sticky="ew")

        # --- Generate button ---
        def generate():
            name_filter = name_var.get().strip() or None
            start = start_date.get_date().strftime("%Y-%m-%d")
            end = end_date.get_date().strftime("%Y-%m-%d")

            if start > end:
                messagebox.showerror("Invalid Range", "Start date cannot be after end date.")
                return

            top.destroy()
            generate_logs_pdf(name_filter=name_filter, start_date=start, end_date=end)

        tk.Button(
            form_frame,
            text="Generate PDF",
            font=("Arial", 14, "bold"),
            bg="#27ae60",
            fg="white",
            command=generate
        ).grid(row=3, column=0, columnspan=2, pady=20)

        form_frame.columnconfigure(1, weight=1)



    def close_program(self):
        self.root.destroy()
    
    def import_students(self):
        self.crud.import_bulk_data()

    def add_student(self):
        self.crud.add_user()

    def update_student(self):
        self.crud.update_user()

    def delete_student(self):
       self.crud.delete_user()

    def change_image(self):
        messagebox.showinfo("Settings", "This would change the icon/image of a menu item.")

    def show_about(self):
        # --- Create Toplevel window ---
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("500x350")
        about_window.resizable(False, False)
        about_window.transient(self.root)

        tk.Label(
            about_window,
            text="About This Project",
            font=("Arial", 18, "bold"),
            pady=10
        ).pack()

        # --- Frame for Text + Scrollbar ---
        frame = tk.Frame(about_window, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        about_text_widget = tk.Text(
            frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            font=("Arial", 14),
            bg="#f9f9f9",
            bd=0,
            relief="flat"
        )
        about_text_widget.pack(fill="both", expand=True)

        about_content = (
            "📚 Project Title:\n"
            "    CONNECT: RFID-Based Library Logging System\n\n"
            "👨‍💻 Project Proponent:\n"
            "    SchoolTech Solutions\n\n"
            "⚙️ Version:\n"
            "    1.0 (2025)\n\n"
            "© 2025 SchoolTech Solutions. All rights reserved."
        )

        about_text_widget.insert("1.0", about_content)
        about_text_widget.config(state="disabled")  # Make read-only
        scrollbar.config(command=about_text_widget.yview)

        # --- Close button ---
        tk.Button(
            about_window,
            text="Close",
            font=("Arial", 14, "bold"),
            bg="#2980b9",
            fg="white",
            command=about_window.destroy
        ).pack(pady=10)


    def monitor_rfid(self):
        buffer = ""
        while True:
            if not self.rfid_enabled:  # Skip reading if disabled
                time.sleep(0.05)
                continue

            event = keyboard.read_event(suppress=False)
            
            if event.event_type == "down":
                if event.name == "enter":
                    rfid_code = buffer.strip()
                    buffer = ""
                    if rfid_code:
                        self.root.after(0, lambda code=rfid_code: self.handle_rfid_scan(code))
                else:
                    buffer += event.name if len(event.name) == 1 else ""
                    
    def pause_rfid(self):
        self.rfid_enabled = False

    def resume_rfid(self):
        self.rfid_enabled = True
        
    def _parse_time(self, t):
        """Robustly parse a stored time value into a datetime or return None."""
        if t is None:
            return None
        if isinstance(t, datetime):
            return t

        # Try common formats (add more if your DB has other formats)
        formats = [
            "%B %d, %Y %I:%M %p",      # e.g. "October 9, 2025 06:29 PM"
            "%Y-%m-%d %H:%M:%S",       # e.g. "2025-10-09 18:29:08"
            "%Y-%m-%d %H:%M:%S.%f",    # e.g. with microseconds
            "%Y-%m-%dT%H:%M:%S",       # e.g. ISO-ish "2025-10-09T18:29:08"
            "%m/%d/%Y %H:%M:%S",       # e.g. "10/09/2025 18:29:08"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(t, fmt)
            except Exception:
                continue

        # Try fromisoformat (can handle many ISO variants)
        try:
            return datetime.fromisoformat(t)
        except Exception:
            pass

        # Try numeric epoch string
        try:
            return datetime.fromtimestamp(float(t))
        except Exception:
            pass

        # Could not parse
        return None

    def handle_rfid_scan(self, rfid_code):
        """Handle RFID scan for time-in/time-out logic with 1-minute cooldown."""
        # Query student by RFID
        student = self.db.get_student_by_rfid(rfid_code)

        if not student:
            popup = tk.Toplevel(self.root)
            popup.title("Unknown RFID")
            popup.geometry("400x150")
            popup.attributes("-topmost", True)
            tk.Label(
                popup,
                text=f"RFID '{rfid_code}' not found in database.",
                font=("Helvetica", 14),
                justify="center"
            ).pack(expand=True)
            popup.after(1500, popup.destroy)
            return

        # Extract student info
        name = student[1]
        grade = student[2]
        section = student[3]

        # Check for existing log with empty timeout
        existing_logs = self.db.get_logs()
        active_log = None
        for log in reversed(existing_logs):
            if log[1] == name and (log[3] == "" or log[3] is None):
                active_log = log
                break

        now = datetime.now()

        if active_log:
            # Parse time-in into datetime
            time_in_raw = active_log[2]  # assuming log[2] is time-in column
            time_in = self._parse_time(time_in_raw)

            if time_in is None:
                # Could not parse existing time-in — inform admin/helpful popup
                popup = tk.Toplevel(self.root)
                popup.title("Time-in Parse Error")
                popup.geometry("520x180")
                popup.attributes("-topmost", True)
                tk.Label(
                    popup,
                    text=(f"Could not read the stored Time-in for {name}.\n"
                          f"Stored value: {time_in_raw}\n"
                          "Please contact the administrator to correct this entry."),
                    font=("Helvetica", 12),
                    justify="center",
                    wraplength=480
                ).pack(expand=True)
                popup.after(3000, popup.destroy)
                return

            # Check cooldown (1 minute by default)
            elapsed = (now - time_in).total_seconds()
            if elapsed < self.cooldown_seconds:
                remaining = int(self.cooldown_seconds - elapsed)
                popup = tk.Toplevel(self.root)
                popup.title("Too Soon to Time Out")
                popup.geometry("480x160")
                popup.attributes("-topmost", True)
                tk.Label(
                    popup,
                    text=f"{name} ({grade}-{section})\nPlease wait {remaining} second(s) before timing out.",
                    font=("Helvetica", 14),
                    justify="center"
                ).pack(expand=True)
                popup.after(2000, popup.destroy)
                return

            # Allowed to time out — update db using a consistent format
            timeout_str = now.strftime("%Y-%m-%d %H:%M:%S")
            self.db.update_timeout(active_log[0], timeout_str)

            popup = tk.Toplevel(self.root)
            popup.title("Time Out Recorded")
            popup.geometry("600x250")
            popup.attributes("-topmost", True)
            tk.Label(
                popup,
                text=f"{name} ({grade}-{section})\nTime Out recorded",
                font=("Helvetica", 16),
                justify="center"
            ).pack(expand=True)
            popup.after(2000, popup.destroy)

        else:
            # No active log, record new time-in
            # Prefer to store in consistent format: YYYY-MM-DD HH:MM:SS
            time_in_str = now.strftime("%Y-%m-%d %H:%M:%S")
            # If your DB has a method to insert time-in directly, call it:
            # self.db.insert_log(name, time_in_str, ...)
            # If you still use the GUI form, make sure when it writes it uses the same format.
            self.show_rfid_window(prefill_rfid=rfid_code)



    def show_rfid_window(self, prefill_rfid=""):
        rfid_toplevel = tk.Toplevel(self.root)
        rfid_toplevel.title("📌 RFID Logging")
        rfid_toplevel.geometry("500x350")
        rfid_toplevel.resizable(False, False)
        
        # Center window
        rfid_toplevel.update_idletasks()
        x = (rfid_toplevel.winfo_screenwidth() // 2) - (600 // 2)
        y = (rfid_toplevel.winfo_screenheight() // 2) - (400 // 2)
        rfid_toplevel.geometry(f"500x350+{x}+{y}")

        details_frame = tk.Frame(rfid_toplevel, padx=20, pady=20, bg="#f9f9f9")
        details_frame.pack(fill="both", expand=True)

        rfid_var = tk.StringVar(value=prefill_rfid)
        name_var = tk.StringVar()
        time_var = tk.StringVar(value=datetime.now().strftime("%B %d, %Y %I:%M %p"))
        purpose_var = tk.StringVar()

        # Auto-fill name if RFID exists
        if prefill_rfid:
            student = self.db.get_student_by_rfid(prefill_rfid)
            if student:
                name_var.set(student[1])

        def create_field(label, var, readonly=False, row=0):
            tk.Label(details_frame, text=label, font=("Arial", 14), bg="#f9f9f9").grid(row=row, column=0, sticky="w", pady=10)
            state = "readonly" if readonly else "normal"
            entry = tk.Entry(details_frame, textvariable=var, font=("Arial", 14), state=state)
            entry.grid(row=row, column=1, sticky="ew", pady=10)
            return entry

        rfid_entry = create_field("RFID:", rfid_var, readonly=True, row=0)
        name_entry = create_field("Name:", name_var, readonly=True, row=1)
        time_entry = create_field("Time In:", time_var, readonly=True, row=2)

        tk.Label(details_frame, text="Purpose:", font=("Arial", 14), bg="#f9f9f9").grid(row=3, column=0, sticky="w", pady=10)
        purpose_dropdown = ttk.Combobox(details_frame, textvariable=purpose_var, values=self.db.get_purposes(), font=("Arial", 14), state="readonly")
        purpose_dropdown.grid(row=3, column=1, sticky="ew", pady=10)
        purpose_dropdown.set("Select Purpose")

        submit_button = tk.Button(details_frame, text="✅ Submit Log", font=("Arial", 14, "bold"), bg="#27ae60", fg="white",
                                  command=lambda: self.submit_log(rfid_var.get(), name_var.get(), time_var.get(), purpose_var.get(), rfid_toplevel))
        submit_button.grid(row=4, column=0, columnspan=2, pady=20)

        details_frame.columnconfigure(1, weight=1)
        
    def submit_log(self, rfid, name, time_in, purpose, window):
        if purpose == "Select Purpose":
            messagebox.showwarning("Incomplete Information", "Please select a purpose for the visit.")
            return

        now = datetime.now()
        # Check for existing log with empty timeout
        existing_logs = self.db.get_logs()  # fetch all logs
        last_log = None
        for log in reversed(existing_logs):  # assuming logs are in order of insertion
            if log[1] == name and log[3] == "":  # log[1]=name, log[3]=timeout
                last_log = log
                break

        if last_log:
            # Parse the timein string into datetime using numeric format
            timein_dt = datetime.strptime(last_log[2], "%Y-%m-%d %H:%M:%S")  # log[2]=timein
            if now - timein_dt < timedelta(hours=8):
                # Update timeout in the existing record using numeric format
                self.db.update_timeout(last_log[0], now.strftime("%Y-%m-%d %H:%M:%S"))  # log[0]=id
                log_message = f"RFID: {rfid}\nName: {name}\nTime Out: {now.strftime('%Y-%m-%d %H:%M:%S')}\nPurpose: {purpose}"
                messagebox.showinfo("Time Out Recorded", log_message)
            else:
                # More than 8 hours, new log
                self.db.add_log(name=name, timein=now.strftime("%Y-%m-%d %H:%M:%S"), timeout="", purpose=purpose)
                messagebox.showinfo("Log Submitted", f"New Time In recorded for {name}")
        else:
            # No previous empty timeout, new log
            self.db.add_log(name=name, timein=now.strftime("%Y-%m-%d %H:%M:%S"), timeout="", purpose=purpose)
            messagebox.showinfo("Log Submitted", f"New Time In recorded for {name}")

        window.destroy()

    def show_logs(self):
        """Display all logs with search functionality."""
        self.pause_rfid()

        view_window = tk.Toplevel(self.root)
        view_window.title("📋 Library Logs")
        view_window.geometry("1000x500")
        view_window.config(bg="#f5f6fa")

        # --- Search Frame ---
        search_frame = tk.Frame(view_window, bg="#f5f6fa", pady=10, padx=10)
        search_frame.pack(fill="x")
        tk.Label(search_frame, text="Search by Name:", font=("Arial", 12, "bold"), bg="#f5f6fa").pack(side="left", padx=(0,5))
        search_entry = tk.Entry(search_frame, font=("Arial", 12))
        search_entry.pack(side="left", fill="x", expand=True)

        # --- Treeview Frame ---
        tree_frame = tk.Frame(view_window, bg="#f5f6fa", padx=10, pady=10)
        tree_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#2d3436",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Arial", 12))
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), foreground="#0984e3")
        style.map("Treeview", background=[("selected", "#74b9ff")], foreground=[("selected", "#2d3436")])

        columns = ("Name", "Time In", "Time Out", "Purpose")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        tree.pack(fill="both", expand=True, side="left")

        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)

        # --- Zebra Striping ---
        def tag_rows():
            for i, row_id in enumerate(tree.get_children()):
                if i % 2 == 0:
                    tree.item(row_id, tags=("evenrow",))
                else:
                    tree.item(row_id, tags=("oddrow",))
            tree.tag_configure("evenrow", background="#fefefe")  # bright white
            tree.tag_configure("oddrow", background="#f0f0f0")   # soft gray

        # --- Filtering Function ---
        def filter_logs(event=None):
            query = search_entry.get().strip()
            for item in tree.get_children():
                tree.delete(item)
            pattern = f"%{query}%"
            rows = self.db.cursor.execute(
                "SELECT name, timein, timeout, purpose FROM logs WHERE name LIKE ? ORDER BY timein DESC",
                (pattern,)
            ).fetchall()
            for row in rows:
                tree.insert("", "end", values=row)
            tag_rows()  # Apply zebra effect

        search_entry.bind("<KeyRelease>", filter_logs)
        filter_logs()

        # --- Handle window close ---
        view_window.protocol("WM_DELETE_WINDOW", lambda: (self.resume_rfid(), view_window.destroy()))


    def manage_purpose_list(self):
        """Admin UI to add/remove purposes in DB."""
        win = tk.Toplevel(self.root)
        win.title("⚙️ Manage Purpose List")
        win.geometry("400x400")
        win.transient(self.root)
        win.grab_set()
        win.config(bg="#f9f9f9")

        tk.Label(win, text="Manage Purposes", font=("Arial", 14, "bold"), bg="#f9f9f9").pack(pady=10)

        purpose_list = tk.Listbox(win, font=("Arial", 12))
        purpose_list.pack(fill="both", expand=True, padx=20, pady=10)

        def refresh_list():
            purpose_list.delete(0, tk.END)
            for p in self.db.get_purposes():
                purpose_list.insert(tk.END, p)
        refresh_list()

        new_purpose_var = tk.StringVar()
        entry = tk.Entry(win, textvariable=new_purpose_var, font=("Arial", 12))
        entry.pack(fill="x", padx=20, pady=5)

        def add_purpose():
            val = new_purpose_var.get().strip()
            if val:
                if self.db.add_purpose(val):
                    refresh_list()
                    new_purpose_var.set("")
                else:
                    messagebox.showerror("Error", f"'{val}' already exists.")

        def delete_purpose():
            selected = purpose_list.curselection()
            if selected:
                purpose = purpose_list.get(selected[0])
                self.db.delete_purpose(purpose)
                refresh_list()

        btn_frame = tk.Frame(win, bg="#f9f9f9")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="➕ Add Purpose", font=("Arial", 12, "bold"), bg="#27ae60", fg="white", command=add_purpose).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="🗑️ Delete Selected", font=("Arial", 12, "bold"), bg="#c0392b", fg="white", command=delete_purpose).grid(row=0, column=1, padx=10)





if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryLoggingSystem(root)
    root.mainloop()
