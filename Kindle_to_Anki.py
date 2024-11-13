import sqlite3
import csv
import os
import json
import tkinter as tk
from tkinter import filedialog

def export_to_list(db_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    conn.text_factory = lambda b: b.decode(errors='ignore')
    cursor = conn.cursor()

    # Execute the SQL query to extract the desired data
    cursor.execute("""
    SELECT w.word, l.usage, b.title
    FROM WORDS w
    JOIN LOOKUPS l ON l.word_key = w.id
    JOIN BOOK_INFO b ON l.book_key = b.id
    """)

    # Convert the data to a list of lists
    data = [['Word', 'Usage', 'Book', 'Definition']]
    for row in cursor:
        data.append([col.encode('utf-8-sig').decode('utf-8-sig') for col in row])

    # Close the database connection
    conn.close()
    return data

def load_dictionary(dictionary_file):
    try:
        with open(dictionary_file, 'r', encoding='utf-8') as file:
            dictionary = json.load(file)
            return dictionary
    except Exception as e:
        print(f"Error loading dictionary: {e}")
        return {}

def sanitize_definition(definition):
    sanitized = definition.replace('\n', ' ').replace('\r', '')
    sanitized = ' '.join(sanitized.split())  # Remove multiple spaces
    return sanitized

def get_definition(word, dictionary):
    word = word.lower()  # Normalize to lowercase for consistent matching
    definition = dictionary.get(word, "No definition found.")
    return sanitize_definition(definition)

def add_definitions_to_list(data, dictionary):
    for row in data[1:]:  # Skip the header row
        word = row[0]  # Assuming the word is in the first column
        definition = get_definition(word, dictionary)  # Get the definition
        row.append(definition)  # Append the definition to the row
    return data

def remove_rows_with_no_definition(data):
    return [row for row in data if row[-1] != "No definition found."]

def save_to_csv(data, csv_file):
    # Create the output directory if it doesn't exist
    csv_dir = os.path.dirname(csv_file)
    os.makedirs(csv_dir, exist_ok=True)

    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

    print(f"Output saved to {csv_file}")

def main():
    # Create the GUI
    root = tk.Tk()
    root.title("Vocabulary Tool")

    # Functions for the GUI
    def select_db_file():
        db_file = filedialog.askopenfilename(filetypes=[("SQLite Database", "*.db")])
        db_file_entry.delete(0, tk.END)
        db_file_entry.insert(0, db_file)

    def select_csv_file():
        csv_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        csv_file_entry.delete(0, tk.END)
        csv_file_entry.insert(0, csv_file)

    def select_dictionary_file():
        dictionary_file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        dictionary_file_entry.delete(0, tk.END)
        dictionary_file_entry.insert(0, dictionary_file)

    def run_process():
        db_file = db_file_entry.get()
        csv_file = csv_file_entry.get()
        dictionary_file = dictionary_file_entry.get()

        # Step 1: Export vocabulary data to a list from SQLite database
        data = export_to_list(db_file)

        # Step 2: Load the dictionary from the specified file
        dictionary = load_dictionary(dictionary_file)
        if not dictionary:
            print("Failed to load the dictionary. Exiting.")
            return

        # Step 3: Add definitions to the data list
        data = add_definitions_to_list(data, dictionary)

        # Step 4: Remove rows with "No definition found."
        data = remove_rows_with_no_definition(data)

        # Step 5: Save the data with definitions to the CSV file
        save_to_csv(data, csv_file)

    # GUI elements
    db_label = tk.Label(root, text="SQLite Database:")
    db_label.grid(row=0, column=0, padx=10, pady=10)
    db_file_entry = tk.Entry(root, width=50)
    db_file_entry.grid(row=0, column=1, padx=10, pady=10)
    db_button = tk.Button(root, text="Browse", command=select_db_file)
    db_button.grid(row=0, column=2, padx=10, pady=10)

    csv_label = tk.Label(root, text="Output CSV File:")
    csv_label.grid(row=1, column=0, padx=10, pady=10)
    csv_file_entry = tk.Entry(root, width=50)
    csv_file_entry.grid(row=1, column=1, padx=10, pady=10)
    csv_button = tk.Button(root, text="Browse", command=select_csv_file)
    csv_button.grid(row=1, column=2, padx=10, pady=10)

    dictionary_label = tk.Label(root, text="Dictionary File:")
    dictionary_label.grid(row=2, column=0, padx=10, pady=10)
    dictionary_file_entry = tk.Entry(root, width=50)
    dictionary_file_entry.grid(row=2, column=1, padx=10, pady=10)
    dictionary_button = tk.Button(root, text="Browse", command=select_dictionary_file)
    dictionary_button.grid(row=2, column=2, padx=10, pady=10)

    run_button = tk.Button(root, text="Run", command=run_process)
    run_button.grid(row=3, column=1, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()