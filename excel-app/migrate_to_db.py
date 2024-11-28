import openpyxl
from database import VehicleDB
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime

def convert_date(date_value):
    """Convert Excel date to proper datetime format"""
    if isinstance(date_value, datetime):
        return date_value.strftime('%Y-%m-%d')
    elif isinstance(date_value, str):
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(date_value, fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
        except:
            return None
    return None

def migrate_excel_to_db():
    """Migrate Excel data to SQLite database"""
    # Initialize database
    db = VehicleDB()
    
    # Create root window (will be hidden)
    root = tk.Tk()
    root.withdraw()
    
    try:
        # Ask user to select Excel file
        excel_file = filedialog.askopenfilename(
            title="Select Excel File to Migrate",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if not excel_file:
            print("No file selected. Migration cancelled.")
            return
        
        # Load Excel workbook
        print(f"Loading Excel file: {excel_file}")
        wb = openpyxl.load_workbook(excel_file)
        sheet = wb.active
        
        # Get headers
        headers = [cell.value.lower() if cell.value else '' for cell in sheet[1]]
        
        # Find relevant column indices
        date_col = next((i for i, h in enumerate(headers) if 'date' in str(h)), None)
        service_col = next((i for i, h in enumerate(headers) if 'service' in str(h) or 'type' in str(h)), None)
        cost_col = next((i for i, h in enumerate(headers) if 'cost' in str(h) or 'price' in str(h)), None)
        mileage_col = next((i for i, h in enumerate(headers) if 'mile' in str(h) or 'odometer' in str(h)), None)
        provider_col = next((i for i, h in enumerate(headers) if 'provider' in str(h) or 'shop' in str(h)), None)
        notes_col = next((i for i, h in enumerate(headers) if 'note' in str(h) or 'description' in str(h)), None)
        
        # Ask for vehicle information
        vehicle_window = tk.Toplevel()
        vehicle_window.title("Enter Vehicle Information")
        vehicle_window.geometry("300x200")
        
        tk.Label(vehicle_window, text="Make:").pack(pady=5)
        make_entry = tk.Entry(vehicle_window)
        make_entry.pack()
        
        tk.Label(vehicle_window, text="Model:").pack(pady=5)
        model_entry = tk.Entry(vehicle_window)
        model_entry.pack()
        
        tk.Label(vehicle_window, text="Year:").pack(pady=5)
        year_entry = tk.Entry(vehicle_window)
        year_entry.pack()
        
        tk.Label(vehicle_window, text="VIN (optional):").pack(pady=5)
        vin_entry = tk.Entry(vehicle_window)
        vin_entry.pack()
        
        vehicle_info = {}
        
        def save_vehicle_info():
            vehicle_info['make'] = make_entry.get()
            vehicle_info['model'] = model_entry.get()
            vehicle_info['year'] = year_entry.get()
            vehicle_info['vin'] = vin_entry.get()
            vehicle_window.destroy()
        
        tk.Button(vehicle_window, text="Save", command=save_vehicle_info).pack(pady=10)
        
        # Wait for vehicle information
        vehicle_window.wait_window()
        
        if not vehicle_info or not vehicle_info['make'] or not vehicle_info['model'] or not vehicle_info['year']:
            print("Vehicle information incomplete. Migration cancelled.")
            return
        
        # Add vehicle to database
        try:
            year = int(vehicle_info['year'])
        except ValueError:
            print("Invalid year format. Migration cancelled.")
            return
        
        vehicle_id = db.add_vehicle(
            vehicle_info['make'],
            vehicle_info['model'],
            year,
            vehicle_info['vin'] if vehicle_info['vin'] else None
        )
        
        # Migrate maintenance records
        records_migrated = 0
        for row in list(sheet.iter_rows(min_row=2, values_only=True)):
            try:
                # Extract and convert data
                service_date = convert_date(row[date_col]) if date_col is not None else None
                service_type = str(row[service_col]) if service_col is not None and row[service_col] else 'General Service'
                
                # Convert cost to float
                cost = None
                if cost_col is not None and row[cost_col]:
                    try:
                        cost = float(str(row[cost_col]).replace('$', '').replace(',', ''))
                    except:
                        cost = None
                
                # Convert mileage to integer
                mileage = None
                if mileage_col is not None and row[mileage_col]:
                    try:
                        mileage = int(float(str(row[mileage_col]).replace(',', '')))
                    except:
                        mileage = None
                
                provider = str(row[provider_col]) if provider_col is not None and row[provider_col] else None
                notes = str(row[notes_col]) if notes_col is not None and row[notes_col] else None
                
                if service_date:  # Only add records with valid dates
                    db.add_maintenance_record(
                        vehicle_id,
                        service_date,
                        service_type,
                        description=notes,
                        cost=cost,
                        mileage=mileage,
                        service_provider=provider,
                        notes=notes
                    )
                    records_migrated += 1
            
            except Exception as e:
                print(f"Error migrating record: {e}")
                continue
        
        print(f"Migration completed successfully!")
        print(f"Vehicle added: {vehicle_info['year']} {vehicle_info['make']} {vehicle_info['model']}")
        print(f"Total records migrated: {records_migrated}")
        
        messagebox.showinfo(
            "Migration Complete",
            f"Successfully migrated:\n"
            f"Vehicle: {vehicle_info['year']} {vehicle_info['make']} {vehicle_info['model']}\n"
            f"Records: {records_migrated}"
        )
        
    except Exception as e:
        print(f"Error during migration: {e}")
        messagebox.showerror("Error", f"An error occurred during migration:\n{str(e)}")
    
    finally:
        root.destroy()

if __name__ == "__main__":
    migrate_excel_to_db()
