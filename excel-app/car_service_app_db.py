import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
from database import VehicleDB

class CarServiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vehicle Maintenance Manager")
        self.db = VehicleDB()
        
        # Initialize variables
        self.current_vehicle_id = None
        self.setup_gui()
        self.load_theme()
        self.refresh_vehicle_list()

    def setup_gui(self):
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Vehicle selection
        vehicle_frame = ttk.LabelFrame(self.main_frame, text="Vehicle", padding="5")
        vehicle_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)

        self.vehicle_var = tk.StringVar()
        self.vehicle_combo = ttk.Combobox(vehicle_frame, textvariable=self.vehicle_var)
        self.vehicle_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        self.vehicle_combo.bind('<<ComboboxSelected>>', self.on_vehicle_selected)

        ttk.Button(vehicle_frame, text="Add Vehicle", command=self.add_vehicle_dialog).grid(row=0, column=1, padx=5)
        
        # Treeview for maintenance records
        self.tree = ttk.Treeview(self.main_frame, columns=("Date", "Service", "Cost", "Mileage", "Provider", "Notes"),
                                show='headings', height=15)
        
        # Setup columns
        self.tree.heading("Date", text="Date")
        self.tree.heading("Service", text="Service Type")
        self.tree.heading("Cost", text="Cost")
        self.tree.heading("Mileage", text="Mileage")
        self.tree.heading("Provider", text="Service Provider")
        self.tree.heading("Notes", text="Notes")
        
        # Column widths
        self.tree.column("Date", width=100)
        self.tree.column("Service", width=150)
        self.tree.column("Cost", width=80)
        self.tree.column("Mileage", width=80)
        self.tree.column("Provider", width=120)
        self.tree.column("Notes", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid the treeview and scrollbar
        self.tree.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        scrollbar.grid(row=1, column=3, sticky=(tk.N, tk.S), pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=5)
        
        ttk.Button(button_frame, text="Add Record", command=self.add_record_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit Record", command=self.edit_record_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Record", command=self.delete_record).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame, relief=tk.SUNKEN)
        self.status_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        self.status_left = ttk.Label(self.status_frame, text="Records: 0")
        self.status_left.pack(side=tk.LEFT, padx=5)
        
        self.status_middle = ttk.Label(self.status_frame, text="Total Cost: $0.00")
        self.status_middle.pack(side=tk.LEFT, padx=5)
        
        self.status_right = ttk.Label(self.status_frame, text="")
        self.status_right.pack(side=tk.RIGHT, padx=5)

    def load_theme(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))

    def refresh_vehicle_list(self):
        vehicles = self.db.get_all_vehicles()
        vehicle_list = [f"{v[2]} {v[1]} {v[2]}" for v in vehicles]  # year make model
        self.vehicle_combo['values'] = vehicle_list
        if vehicle_list:
            self.vehicle_combo.set(vehicle_list[0])
            self.current_vehicle_id = vehicles[0][0]
            self.refresh_records()

    def refresh_records(self):
        if not self.current_vehicle_id:
            return

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get records from database
        records = self.db.get_vehicle_records(self.current_vehicle_id)
        
        total_cost = 0
        record_count = 0
        
        for record in records:
            # Convert record tuple to proper display format
            date = record[2]  # service_date
            service_type = record[3]  # service_type
            cost = f"${record[5]:.2f}" if record[5] else ""  # cost
            mileage = record[6] if record[6] else ""  # mileage
            provider = record[7] if record[7] else ""  # service_provider
            notes = record[8] if record[8] else ""  # notes
            
            # Add to treeview
            self.tree.insert("", "end", values=(date, service_type, cost, mileage, provider, notes))
            
            # Update totals
            if record[5]:  # if cost exists
                total_cost += record[5]
            record_count += 1
            
            # Color coding based on date
            try:
                service_date = datetime.strptime(date, '%Y-%m-%d')
                months_old = (datetime.now() - service_date).days / 30
                
                if months_old <= 3:
                    tag = 'recent'
                elif months_old <= 6:
                    tag = 'attention'
                else:
                    tag = 'overdue'
                    
                self.tree.tag_configure('recent', foreground='green')
                self.tree.tag_configure('attention', foreground='orange')
                self.tree.tag_configure('overdue', foreground='red')
                
            except ValueError:
                pass  # Skip coloring if date is invalid
        
        # Update status bar
        self.status_left.config(text=f"Records: {record_count}")
        self.status_middle.config(text=f"Total Cost: ${total_cost:.2f}")
        
        # Update color legend
        self.status_right.config(text="■ Recent  ■ Attention  ■ Overdue")

    def add_vehicle_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Vehicle")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text="Make:").pack(pady=5)
        make_entry = ttk.Entry(dialog)
        make_entry.pack()
        
        ttk.Label(dialog, text="Model:").pack(pady=5)
        model_entry = ttk.Entry(dialog)
        model_entry.pack()
        
        ttk.Label(dialog, text="Year:").pack(pady=5)
        year_entry = ttk.Entry(dialog)
        year_entry.pack()
        
        ttk.Label(dialog, text="VIN (optional):").pack(pady=5)
        vin_entry = ttk.Entry(dialog)
        vin_entry.pack()
        
        def save_vehicle():
            try:
                year = int(year_entry.get())
                self.db.add_vehicle(
                    make_entry.get(),
                    model_entry.get(),
                    year,
                    vin_entry.get() if vin_entry.get() else None
                )
                self.refresh_vehicle_list()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid year format")
        
        ttk.Button(dialog, text="Save", command=save_vehicle).pack(pady=10)

    def add_record_dialog(self):
        if not self.current_vehicle_id:
            messagebox.showerror("Error", "Please select a vehicle first")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Maintenance Record")
        dialog.geometry("400x400")
        
        # Date
        ttk.Label(dialog, text="Date (YYYY-MM-DD):").pack(pady=5)
        date_entry = ttk.Entry(dialog)
        date_entry.pack()
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Service Type
        ttk.Label(dialog, text="Service Type:").pack(pady=5)
        service_types = [mt[1] for mt in self.db.get_maintenance_types()]  # Get names from maintenance_types
        service_var = tk.StringVar()
        service_combo = ttk.Combobox(dialog, textvariable=service_var, values=service_types)
        service_combo.pack()
        
        # Cost
        ttk.Label(dialog, text="Cost:").pack(pady=5)
        cost_entry = ttk.Entry(dialog)
        cost_entry.pack()
        
        # Mileage
        ttk.Label(dialog, text="Mileage:").pack(pady=5)
        mileage_entry = ttk.Entry(dialog)
        mileage_entry.pack()
        
        # Service Provider
        ttk.Label(dialog, text="Service Provider:").pack(pady=5)
        provider_entry = ttk.Entry(dialog)
        provider_entry.pack()
        
        # Notes
        ttk.Label(dialog, text="Notes:").pack(pady=5)
        notes_text = tk.Text(dialog, height=4, width=40)
        notes_text.pack()
        
        def save_record():
            try:
                # Validate date
                service_date = datetime.strptime(date_entry.get(), '%Y-%m-%d').strftime('%Y-%m-%d')
                
                # Convert cost to float
                cost = float(cost_entry.get()) if cost_entry.get() else None
                
                # Convert mileage to int
                mileage = int(mileage_entry.get()) if mileage_entry.get() else None
                
                self.db.add_maintenance_record(
                    self.current_vehicle_id,
                    service_date,
                    service_var.get(),
                    description=notes_text.get("1.0", tk.END).strip(),
                    cost=cost,
                    mileage=mileage,
                    service_provider=provider_entry.get(),
                    notes=notes_text.get("1.0", tk.END).strip()
                )
                
                self.refresh_records()
                dialog.destroy()
                
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Save", command=save_record).pack(pady=10)

    def edit_record_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to edit")
            return
            
        # TODO: Implement edit functionality
        messagebox.showinfo("Info", "Edit functionality coming soon!")

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            # TODO: Implement delete functionality
            messagebox.showinfo("Info", "Delete functionality coming soon!")

    def on_vehicle_selected(self, event):
        vehicles = self.db.get_all_vehicles()
        selected_index = self.vehicle_combo.current()
        if selected_index >= 0:
            self.current_vehicle_id = vehicles[selected_index][0]
            self.refresh_records()

if __name__ == "__main__":
    root = tk.Tk()
    app = CarServiceApp(root)
    root.mainloop()
