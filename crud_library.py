import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
from tkinter import simpledialog
import pandas as pd
from tkinter import filedialog, messagebox

class RFID_App:
    """
    A Tkinter application for managing RFID data, specifically for students.
    It includes a simple database using SQLite3 for CRUD operations.
    """
    def __init__(self, root, app):
        """Initializes the main application window and database connection."""
        self.root = root
        self.app = app
        self.root.title("RFID Data Management")
        self.root.geometry("800x600")
        self.root.configure(bg="#f2f2f2")

        # Connect to the SQLite database
        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()

        # Create the necessary database tables if they don't exist
        self._create_tables()

        # Build the main user interface
        self._create_widgets()
        self.conn.commit()

    def _create_tables(self):
        """Creates the 'students' and 'logs' tables in the database."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                rfid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                grade TEXT,
                section TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rfid TEXT,
                name TEXT,
                timestamp TEXT
            )
        ''')
        self.conn.commit()

    def _create_widgets(self):
        """Configures the UI elements, including buttons and styling."""
        # Main title
        title = tk.Label(self.root, text="RFID DATA MANAGEMENT", font=("Arial", 28, "bold"), bg="#f2f2f2")
        title.pack(pady=20)

        # Button frame for organization
        button_frame = tk.Frame(self.root, bg="#f2f2f2")
        button_frame.pack(pady=50)

        # CRUD buttons
        add_btn = tk.Button(button_frame, text="Add User", width=20, height=2, bg="#4CAF50", fg="white",
                             font=("Arial", 14, "bold"), command=self.add_user)
        add_btn.grid(row=0, column=0, padx=20, pady=10)

        view_btn = tk.Button(button_frame, text="View Users", width=20, height=2, bg="#2196F3", fg="white",
                             font=("Arial", 14, "bold"), command=self.view_users)
        view_btn.grid(row=0, column=1, padx=20, pady=10)

        update_btn = tk.Button(button_frame, text="Update User", width=20, height=2, bg="#FFC107", fg="black",
                               font=("Arial", 14, "bold"), command=self.update_user)
        update_btn.grid(row=1, column=0, padx=20, pady=10)

        delete_btn = tk.Button(button_frame, text="Delete User", width=20, height=2, bg="#F44336", fg="white",
                               font=("Arial", 14, "bold"), command=self.delete_user)
        delete_btn.grid(row=1, column=1, padx=20, pady=10)

        # Bulk import and logs buttons
        import_btn = tk.Button(button_frame, text="Import Bulk Students Data", width=25, height=2, bg="#9C27B0", fg="white",
                               font=("Arial", 14, "bold"), command=self.import_bulk_data)
        import_btn.grid(row=2, column=0, columnspan=2, padx=20, pady=10)

        # Apply styling to Treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        style.configure("Treeview", font=("Arial", 11))

    # --- CRUD FUNCTIONALITY ---

    def add_user(self):
        self.app.pause_rfid()
        """Opens a new window to add a single user."""

        add_window = tk.Toplevel(self.root)
        add_window.title("Add New User")
        add_window.geometry("500x400")
        add_window.transient(self.root)
        add_window.config(bg="#f9f9f9")

        # --- Header ---
        tk.Label(
            add_window,
            text="➕ Add a New Student",
            font=("Arial", 18, "bold"),
            bg="#f9f9f9",
            fg="#2c3e50"
        ).pack(pady=15)

        # --- Form Frame ---
        form_frame = tk.Frame(add_window, bg="#f9f9f9")
        form_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Labels & Entry Fields
        def create_field(label, row):
            tk.Label(
                form_frame,
                text=label,
                font=("Arial", 14),
                bg="#f9f9f9",
                anchor="w"
            ).grid(row=row, column=0, sticky="w", pady=8, padx=5)

            entry = tk.Entry(
                form_frame,
                font=("Arial", 14),
                width=25,
                relief="solid",
                bd=1
            )
            entry.grid(row=row, column=1, pady=8, padx=5)
            return entry

        rfid_entry = create_field("Scan RFID:", 0)
        name_entry = create_field("Full Name:", 1)
        grade_entry = create_field("Grade:", 2)
        section_entry = create_field("Section:", 3)
        def on_close():
            self.app.resume_rfid()
            add_window.destroy()

        add_window.protocol("WM_DELETE_WINDOW", on_close)

        # --- Save User Function ---
        def save_user():
            rfid = rfid_entry.get().strip()
            name = name_entry.get().strip()
            grade = grade_entry.get().strip()
            section = section_entry.get().strip()

            if not rfid or not name:
                messagebox.showerror("Error", "RFID and Name are required.", parent=add_window)
                return

            # Check if RFID already exists
            self.cursor.execute("SELECT rfid FROM students WHERE rfid = ?", (rfid,))
            if self.cursor.fetchone():
                messagebox.showerror("Error", f"RFID '{rfid}' already exists.", parent=add_window)
                return

            try:
                self.cursor.execute(
                    "INSERT INTO students (rfid, name, grade, section) VALUES (?, ?, ?, ?)",
                    (rfid, name, grade, section)
                )
                self.conn.commit()
                messagebox.showinfo("Success", "✅ User added successfully!", parent=add_window)
                self.app.resume_rfid()
                add_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add user: {e}", parent=add_window)

        # --- Buttons ---
        btn_frame = tk.Frame(add_window, bg="#f9f9f9")
        btn_frame.pack(pady=20)

        save_btn = tk.Button(
            btn_frame,
            text="💾 Save User",
            command=save_user,
            font=("Arial", 14, "bold"),
            bg="#27ae60",
            fg="white",
            padx=15,
            pady=5,
            relief="flat"
        )
        save_btn.grid(row=0, column=0, padx=10)

        cancel_btn = tk.Button(
            btn_frame,
            text="❌ Cancel",
            command=lambda: (self.app.resume_rfid(), add_window.destroy()),
            font=("Arial", 14, "bold"),
            bg="#c0392b",
            fg="white",
            padx=15,
            pady=5,
            relief="flat"
        )
        cancel_btn.grid(row=0, column=1, padx=10)
        


    def view_users(self):
        """Opens a new window to display all registered students with a search bar."""
        self.app.pause_rfid()
        view_window = tk.Toplevel(self.root)
        view_window.title("View All Users")
        view_window.geometry("1000x600")
        view_window.configure(bg="#f5f6fa")  # very light background
        view_window.transient(self.root)

        # --- Search Frame ---
        search_frame = tk.Frame(view_window, bg="#f5f6fa", pady=10)
        search_frame.pack(fill="x")

        tk.Label(search_frame, text="Search RFID or Name:", font=("Arial", 12, "bold"), bg="#f5f6fa").pack(side=tk.LEFT, padx=(10,5))
        search_entry = tk.Entry(search_frame, font=("Arial", 12), width=30)
        search_entry.pack(side=tk.LEFT, padx=(0,10))

        # --- Treeview Frame ---
        tree_frame = tk.Frame(view_window, bg="#f5f6fa")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

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

        tree = ttk.Treeview(tree_frame, columns=("RFID", "Name", "Grade", "Section"), show="headings")
        tree.heading("RFID", text="RFID")
        tree.heading("Name", text="Name")
        tree.heading("Grade", text="Grade")
        tree.heading("Section", text="Section")
        tree.pack(fill="both", expand=True, side="left")

        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)

        # --- Zebra Striping with soft colors ---
        def tag_rows():
            for i, row_id in enumerate(tree.get_children()):
                if i % 2 == 0:
                    tree.item(row_id, tags=("evenrow",))
                else:
                    tree.item(row_id, tags=("oddrow",))
            tree.tag_configure("evenrow", background="#fefefe")  # bright white
            tree.tag_configure("oddrow", background="#f0f0f0")   # soft gray

        # --- Filter function ---
        def filter_users(event=None):
            """Filters the treeview based on the search query."""
            query = search_entry.get().strip()

            # Clear existing data
            for item in tree.get_children():
                tree.delete(item)

            # Fetch filtered data from the database
            search_pattern = f"%{query}%"
            self.cursor.execute("SELECT * FROM students WHERE rfid LIKE ? OR name LIKE ? ORDER BY name",
                                (search_pattern, search_pattern))
            rows = self.cursor.fetchall()

            # Insert the new data
            for row in rows:
                tree.insert("", tk.END, values=row)

            tag_rows()  # Apply zebra striping

        search_entry.bind("<KeyRelease>", filter_users)
        filter_users()  # Initial load

        # --- Handle window close ---
        def on_close():
            self.app.resume_rfid()
            view_window.destroy()

        view_window.protocol("WM_DELETE_WINDOW", on_close)

    


    def update_user(self):
        """
        Opens a window to update an existing user's details.
        User scans an RFID to automatically populate the form.
        """
        self.app.pause_rfid()
        update_window = tk.Toplevel(self.root)
        update_window.title("✏️ Update User")
        update_window.geometry("600x400")
        update_window.resizable(False, False)
        update_window.transient(self.root)

        tk.Label(update_window, text="Update Student by RFID", font=("Arial", 20, "bold")).pack(pady=15)

        form_frame = tk.Frame(update_window, padx=20, pady=20, bg="#f9f9f9")
        form_frame.pack(fill="both", expand=True)

        rfid_var = tk.StringVar()
        name_var = tk.StringVar()
        grade_var = tk.StringVar()
        section_var = tk.StringVar()

        # Helper to create labeled entry
        def create_field(label, var, row, focus=False):
            tk.Label(form_frame, text=label, font=("Arial", 16, "bold"), bg="#f9f9f9").grid(row=row, column=0, sticky="w", pady=8)
            entry = tk.Entry(form_frame, textvariable=var, font=("Arial", 16))
            entry.grid(row=row, column=1, sticky="ew", pady=8)
            if focus:
                entry.focus_set()
            return entry

        rfid_entry = create_field("Scan RFID:", rfid_var, row=0, focus=True)
        name_entry = create_field("Name:", name_var, row=1)
        grade_entry = create_field("Grade:", grade_var, row=2)
        section_entry = create_field("Section:", section_var, row=3)

        form_frame.columnconfigure(1, weight=1)

        # --- Function to fetch user info by RFID ---
        def find_user(event=None):
            rfid = rfid_var.get().strip()
            if not rfid:
                return
            self.cursor.execute("SELECT name, grade, section FROM students WHERE rfid=?", (rfid,))
            result = self.cursor.fetchone()

            # Clear previous values
            name_var.set("")
            grade_var.set("")
            section_var.set("")

            if result:
                name_var.set(result[0])
                grade_var.set(result[1])
                section_var.set(result[2])
            else:
                messagebox.showerror("Error", "No student found with this RFID.", parent=update_window)
                self.app.resume_rfid()

        rfid_entry.bind("<Return>", find_user)

        # --- Function to update record ---
        def update_record():
            rfid = rfid_var.get().strip()
            name = name_var.get().strip()
            grade = grade_var.get().strip()
            section = section_var.get().strip()

            if not rfid:
                messagebox.showerror("Error", "RFID is required to update.", parent=update_window)
                self.app.resume_rfid()
                return

            # Check if RFID exists
            self.cursor.execute("SELECT 1 FROM students WHERE rfid=?", (rfid,))
            if self.cursor.fetchone() is None:
                messagebox.showerror("Error", "No user found with that RFID.", parent=update_window)
                self.app.resume_rfid()
                return

            self.cursor.execute("UPDATE students SET name=?, grade=?, section=? WHERE rfid=?",
                                (name, grade, section, rfid))
            self.conn.commit()

            messagebox.showinfo("✅ Success", "User updated successfully!", parent=update_window)
            self.app.resume_rfid()
            update_window.destroy()

        update_btn = tk.Button(update_window, text="Update", font=("Arial", 14, "bold"), bg="#2980b9", fg="white",
                               command=update_record)
        update_btn.pack(pady=20)
        
        def on_close():
            self.app.resume_rfid()
            update_window.destroy()

        update_window.protocol("WM_DELETE_WINDOW", on_close)
    

        
        
    def delete_user(self):
        """Opens a window to delete a user by RFID or all records."""
        self.app.pause_rfid()  # Pause RFID scanning while this window is open

        delete_window = tk.Toplevel(self.root)
        delete_window.title("🗑️ Delete User")
        delete_window.geometry("500x350")
        delete_window.transient(self.root)
        delete_window.config(bg="#f9f9f9")

        # --- Header ---
        tk.Label(
            delete_window,
            text="Delete Student Record",
            font=("Arial", 18, "bold"),
            bg="#f9f9f9",
            fg="#c0392b"
        ).pack(pady=15)

        # --- Form Frame ---
        form_frame = tk.Frame(delete_window, bg="#f9f9f9")
        form_frame.pack(pady=5, padx=20, fill="both", expand=True)

        def create_field(label_text, var=None, readonly=False, row=0):
            tk.Label(
                form_frame,
                text=label_text,
                font=("Arial", 14),
                bg="#f9f9f9",
                anchor="w"
            ).grid(row=row, column=0, sticky="w", pady=8)

            state = "readonly" if readonly else "normal"
            entry = tk.Entry(
                form_frame,
                textvariable=var,
                font=("Arial", 14),
                width=25,
                relief="solid",
                bd=1,
                state=state
            )
            entry.grid(row=row, column=1, pady=8, padx=5)
            return entry

        name_var = tk.StringVar()
        grade_section_var = tk.StringVar()

        rfid_entry = create_field("RFID to Delete:", row=0)
        name_entry = create_field("Name:", var=name_var, readonly=True, row=1)
        grade_section_entry = create_field("Grade + Section:", var=grade_section_var, readonly=True, row=2)

        # --- Fetch student info ---
        def fetch_student_info(event=None):
            rfid = rfid_entry.get().strip()
            if rfid:
                self.cursor.execute("SELECT name, grade, section FROM students WHERE rfid=?", (rfid,))
                student = self.cursor.fetchone()
                if student:
                    name_var.set(student[0])
                    grade_section_var.set(f"{student[1]} - {student[2]}")
                else:
                    name_var.set("")
                    grade_section_var.set("")

        rfid_entry.bind("<KeyRelease>", fetch_student_info)

        # --- Delete single user ---
        def confirm_delete():
            rfid = rfid_entry.get().strip()
            if not rfid:
                messagebox.showerror("Error", "Please enter an RFID.", parent=delete_window)
                return

            self.cursor.execute("SELECT name FROM students WHERE rfid=?", (rfid,))
            user = self.cursor.fetchone()
            if not user:
                messagebox.showerror("Error", "No user found with that RFID.", parent=delete_window)
                return

            confirm = messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete {user[0]} (RFID: {rfid})?",
                parent=delete_window
            )
            if confirm:
                self.cursor.execute("DELETE FROM students WHERE rfid=?", (rfid,))
                self.conn.commit()
                messagebox.showinfo("Success", "✅ User deleted successfully!", parent=delete_window)
                self.app.resume_rfid()
                delete_window.destroy()

        # --- Buttons Frame ---
        btn_frame = tk.Frame(delete_window, bg="#f9f9f9")
        btn_frame.pack(pady=20)

        delete_btn = tk.Button(
            btn_frame,
            text="🗑️ Delete User",
            command=confirm_delete,
            font=("Arial", 14, "bold"),
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=5,
            relief="flat"
        )
        delete_btn.grid(row=0, column=0, padx=10)

        # --- Delete all records ---
        def delete_all_records():
            self.cursor.execute("SELECT COUNT(*) FROM students")
            count = self.cursor.fetchone()[0]
            confirm = messagebox.askyesno(
                "Confirm Delete All",
                f"There are {count} student records. Are you sure you want to delete ALL?",
                parent=delete_window
            )
            if confirm:
                self.cursor.execute("DELETE FROM students")
                self.conn.commit()
                messagebox.showinfo("Success", "✅ All student records deleted!", parent=delete_window)
                delete_window.destroy()
                self.app.resume_rfid()

        delete_all_btn = tk.Button(
            btn_frame,
            text="🗑️ Delete All Records",
            command=delete_all_records,
            font=("Arial", 12, "bold"),
            bg="#c0392b",
            fg="white",
            padx=10,
            pady=5,
            relief="flat"
        )
        delete_all_btn.grid(row=0, column=1, padx=10)
        def on_close():
            self.app.resume_rfid()
            delete_window.destroy()

        delete_window.protocol("WM_DELETE_WINDOW", on_close)



    def import_bulk_data(self):
        """Opens a Toplevel form to upload an Excel file, map columns, and import student data"""

        def browse_file():
            file_path = filedialog.askopenfilename(
                title="Select Excel File",
                filetypes=[("Excel files", "*.xlsx *.xls")]
            )
            if file_path:
                file_entry.delete(0, tk.END)
                file_entry.insert(0, file_path)

                try:
                    df = pd.read_excel(file_path)
                    df.columns = df.columns.str.strip()  # clean spaces
                    excel_columns[:] = list(df.columns)  # store column names

                    # Update dropdown values
                    for field, cb in dropdowns.items():
                        cb["values"] = excel_columns
                        if field in excel_columns:  # auto-match if same name
                            cb.set(field)
                        else:
                            cb.set("")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read Excel: {e}", parent=top)

        def process_import():
            file_path = file_entry.get().strip()
            if not file_path:
                messagebox.showwarning("No File", "Please select an Excel file.", parent=top)
                return

            try:
                df = pd.read_excel(file_path)
                df.columns = df.columns.str.strip()

                # Build mapping dictionary
                mapping = {}
                for field, cb in dropdowns.items():
                    selected_col = cb.get()
                    if not selected_col:
                        messagebox.showerror("Mapping Error", f"Please select a column for '{field}'", parent=top)
                        return
                    mapping[field] = selected_col

                # Rename columns according to mapping
                df = df.rename(columns={v: k for k, v in mapping.items()})

                # Ensure required fields exist
                required_fields = ["rfid", "name", "grade", "section"]
                for field in required_fields:
                    if field not in df.columns:
                        messagebox.showerror("Mapping Error", f"Missing required field: {field}", parent=top)
                        return

                # --- Validation checks ---
                errors = []

                # Missing RFID
                missing_rfid = df[df["rfid"].isna() | (df["rfid"].astype(str).str.strip() == "")]
                if not missing_rfid.empty:
                    errors.append(f"Missing RFID in rows: {list(missing_rfid.index + 2)}")

                # Missing Name
                missing_name = df[df["name"].isna() | (df["name"].astype(str).str.strip() == "")]
                if not missing_name.empty:
                    errors.append(f"Missing Name in rows: {list(missing_name.index + 2)}")

                # Duplicate inside Excel
                duplicate_rfid = df[df["rfid"].duplicated(keep=False)]
                if not duplicate_rfid.empty:
                    errors.append(f"Duplicate RFID in Excel: {duplicate_rfid['rfid'].tolist()}")

                duplicate_name = df[df["name"].duplicated(keep=False)]
                if not duplicate_name.empty:
                    errors.append(f"Duplicate Name in Excel: {duplicate_name['name'].tolist()}")

                # --- Check against DB ---
                conn = sqlite3.connect("library.db")
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS students (
                        rfid TEXT PRIMARY KEY, 
                        name TEXT NOT NULL, 
                        grade TEXT, 
                        section TEXT
                    )
                """)

                cursor.execute("SELECT rfid, name FROM students")
                existing_students = cursor.fetchall()
                existing_rfids = {row[0] for row in existing_students}
                existing_names = {row[1] for row in existing_students}

                new_rfids = set(df["rfid"].astype(str).str.strip())
                new_names = set(df["name"].astype(str).str.strip())

                duplicates_rfids_db = new_rfids & existing_rfids
                duplicates_names_db = new_names & existing_names

                if duplicates_rfids_db:
                    errors.append(f"RFID(s) already exist in DB: {list(duplicates_rfids_db)}")

                if duplicates_names_db:
                    errors.append(f"Name(s) already exist in DB: {list(duplicates_names_db)}")

                if errors:
                    conn.close()
                    messagebox.showerror("Validation Error", "\n".join(errors), parent=top)
                    return

                # --- Import into DB ---
                for _, row in df.iterrows():
                    cursor.execute("""
                        INSERT OR REPLACE INTO students (rfid, name, grade, section)
                        VALUES (?, ?, ?, ?)
                    """, (
                        str(row["rfid"]).strip(),
                        str(row["name"]).strip(),
                        str(row["grade"]).strip(),
                        str(row["section"]).strip()
                    ))

                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "✅ Student data imported successfully!", parent=top)
                top.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {e}", parent=top)

        # --- Toplevel Window ---
        top = tk.Toplevel(self.root)
        top.title("📥 Import Bulk Student Data")
        top.geometry("650x400")
        top.transient(self.root)
        top.config(bg="#f9f9f9")

        # --- Header ---
        tk.Label(
            top, 
            text="Import Students from Excel", 
            font=("Arial", 18, "bold"),
            bg="#f9f9f9",
            fg="#2c3e50"
        ).pack(pady=15)

        # --- File Browse ---
        frame = tk.Frame(top, bg="#f9f9f9")
        frame.pack(pady=10)

        file_entry = tk.Entry(frame, width=40, font=("Arial", 14))
        file_entry.pack(side=tk.LEFT, padx=5)

        browse_btn = tk.Button(frame, text="📂 Browse", font=("Arial", 14, "bold"), command=browse_file, bg="#3498db", fg="white", relief="flat")
        browse_btn.pack(side=tk.LEFT)

        # --- Dropdown Mapping ---
        excel_columns = []
        dropdowns = {}
        fields = ["rfid", "name", "grade", "section"]

        mapping_frame = tk.Frame(top, bg="#f9f9f9")
        mapping_frame.pack(pady=20)

        for field in fields:
            row = tk.Frame(mapping_frame, bg="#f9f9f9")
            row.pack(fill="x", pady=5)

            tk.Label(
                row, 
                text=f"{field.upper()} →", 
                width=12, 
                anchor="e",
                font=("Arial", 14, "bold"),
                bg="#f9f9f9"
            ).pack(side=tk.LEFT, padx=5)

            cb = ttk.Combobox(row, width=25, state="readonly", font=("Arial", 12))
            cb.pack(side=tk.LEFT)
            dropdowns[field] = cb

        # --- Import Button ---
        import_btn = tk.Button(
            top, 
            text="⬇️ Import Data", 
            command=process_import,
            bg="#27ae60", fg="white",
            font=("Arial", 14, "bold"),
            relief="flat",
            padx=10, pady=5
        )
        import_btn.pack(pady=15)
        def on_close():
            self.app.resume_rfid()
            top.destroy()

        top.protocol("WM_DELETE_WINDOW", on_close)


    
        

if __name__ == "__main__":
    root = tk.Tk()
    app = RFID_App(root)
    root.mainloop()
