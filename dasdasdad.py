# generate_student_data.py

import openpyxl

def generate_dummy_data_excel():
    """
    Creates an Excel file with a 'Students' worksheet, 
    4 columns, and 20 rows of dummy data.
    """
    # Create a new workbook and select the active worksheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Students"

    # Define the column headers
    headers = ['RFID', 'Name', 'Grade', 'Section']
    sheet.append(headers)

    # Generate and append 20 rows of dummy data
    for i in range(1, 2100):
        rfid = f"{1000 + i}"
        name = f"Student {i}"
        grade = f"Grade {((i - 1) // 5) + 9}"  # Assigns grades 9-12
        section = ["A", "B", "C", "D"][i % 4]
        
        row_data = [rfid, name, grade, section]
        sheet.append(row_data)

    # Save the workbook to a file
    file_name = 'student_info.xlsx'
    workbook.save(file_name)
    print(f"Successfully created '{file_name}' with 20 rows of dummy data.")

if __name__ == "__main__":
    generate_dummy_data_excel()