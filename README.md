# 📚 RFID-Based Library Visitor Logging System

> **System #03 · Library Management**
> Capstone Project — Bachelor of Science in Computer Science
> Cainta Catholic College

---

## 📖 Overview

The **RFID-Based Library Visitor Logging System** is a desktop application that replaces traditional manual logbooks with an automated RFID-based visitor tracking system for school libraries. Students register their RFID cards linked to their personal information; every scan automatically records entry and exit timestamps, and administrators can generate detailed, filterable PDF reports — making library management faster, more accurate, and entirely paperless.

---

## ✨ Features

- **RFID Auto-Logging** — Scans automatically record library entry/exit with date and time — no manual sign-in needed.
- **Student Record Management** — Full CRUD operations: add, update, delete, and search student profiles with name, grade, and section.
- **Bulk Excel Import** — Administrators can import large batches of student records from Excel files for fast onboarding.
- **Filterable PDF Reports** — Auto-generated PDF visitor reports can be filtered by student name or date range for easy analysis.

---

## 🛠️ Technologies Used

| Category      | Technologies                                     |
|---------------|--------------------------------------------------|
| **Language**  | Python                                           |
| **Database**  | SQLite                                           |
| **Libraries** | Tkinter (GUI), ReportLab (PDF), openpyxl (Excel) |
| **Hardware**  | RFID Reader, RFID Cards                          |

---

## 🏗️ System Architecture

```
[Student RFID Card Scan]
         │
         ▼
[RFID Reader (USB/Serial)]
         │
         ▼
[Python Desktop App (Tkinter)]
    ┌────┴─────────┐
    ▼              ▼
[SQLite DB]   [Admin Panel]
 (Visitor      ┌───┴───────────────┐
  Logs &        ▼                  ▼
  Students)  [PDF Report      [Excel Import
              Generator]       (openpyxl)]
                │
           [ReportLab]
                │
           [Filtered PDF Output]
```

---

## ⚙️ How It Works

1. Students register their RFID cards with their personal details (name, grade, section) in the admin panel.
2. When a student arrives at the library, they tap their RFID card on the reader.
3. The system fetches their record from SQLite and logs their **entry timestamp** automatically.
4. On departure, a second tap logs their **exit timestamp**.
5. Administrators can search, edit, or delete student records anytime through the GUI.
6. New student batches can be imported in bulk from a formatted Excel file using openpyxl.
7. Reports can be generated as PDFs (via ReportLab), filterable by student name or date range.

---

## 🗂️ Database Schema

### `students` Table
| Column     | Type    | Description                    |
|------------|---------|--------------------------------|
| id         | INTEGER | Primary key (auto-increment)   |
| rfid_uid   | TEXT    | Unique RFID card identifier    |
| name       | TEXT    | Full student name              |
| grade      | TEXT    | Grade level                    |
| section    | TEXT    | Section / class                |

### `visit_logs` Table
| Column      | Type     | Description                     |
|-------------|----------|---------------------------------|
| log_id      | INTEGER  | Primary key (auto-increment)    |
| rfid_uid    | TEXT     | Foreign key → students.rfid_uid |
| entry_time  | DATETIME | Timestamp of library entry      |
| exit_time   | DATETIME | Timestamp of library exit       |

---

## 📋 Prerequisites

- Python 3.x
- RFID reader module (e.g., RC522 or USB HID reader)
- RFID cards / key fobs

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/library-visitor-logger.git
cd library-visitor-logger
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
```
reportlab
openpyxl
pyserial   # for RFID reader communication
```
> **Note:** `tkinter` and `sqlite3` are included in the Python standard library.

### 3. Connect the RFID Reader
- Plug in the RFID reader via USB.
- Update the serial port in `config.py`:
```python
RFID_PORT = "COM3"      # Windows
# RFID_PORT = "/dev/ttyUSB0"  # Linux/Mac
BAUD_RATE = 9600
```

### 4. Run the Application
```bash
python main.py
```

---

## 📄 Generating Reports

1. Open the **Reports** tab in the admin panel.
2. Set filters:
   - **By Student Name** — type the name in the search field.
   - **By Date Range** — select start and end dates.
3. Click **Generate PDF** — the report will be saved to the `/reports` directory.

---

## 📥 Bulk Excel Import

Prepare an Excel file with the following column headers (row 1):

| rfid_uid | name | grade | section |
|----------|------|-------|---------|

Then in the admin panel, navigate to **Students → Import from Excel** and select your file.

---

## 👥 Team

| Name | Role |
|------|------|
| Alvarado, John Zymond D. | BSCS Student |
| Arado, Nemuel Adrian | BSCS Student |
| Bañas, JhonPaul B. | BSCS Student |
| Gabilo, Carl Allen R. | BSCS Student |
| Vicencio, Mico D. | Group Leader / Main Programmer |

---

## 🏫 Institution

**Cainta Catholic College**
Bachelor of Science in Computer Science — BSCS Tech Expo

---

*Built with ❤️ by BSCS Students of Cainta Catholic College*
