import sqlite3
from datetime import datetime
import os

class VehicleDB:
    def __init__(self, db_file='vehicle_maintenance.db'):
        """Initialize database connection"""
        self.db_file = db_file
        self.initialize_db()

    def initialize_db(self):
        """Create database and tables if they don't exist"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()

            # Create vehicles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    make TEXT NOT NULL,
                    model TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    vin TEXT UNIQUE
                )
            ''')

            # Create maintenance_records table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS maintenance_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id INTEGER NOT NULL,
                    service_date DATE NOT NULL,
                    service_type TEXT NOT NULL,
                    description TEXT,
                    cost DECIMAL(10,2),
                    mileage INTEGER,
                    service_provider TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
                )
            ''')

            # Create maintenance_types table for standardized service types
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS maintenance_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    recommended_interval_months INTEGER,
                    recommended_interval_miles INTEGER
                )
            ''')

            # Insert some default maintenance types
            default_types = [
                ('Oil Change', 'Regular oil and filter change', 6, 5000),
                ('Tire Rotation', 'Rotate tires for even wear', 6, 6000),
                ('Brake Service', 'Inspect and service brakes', 12, 12000),
                ('Air Filter', 'Replace engine air filter', 12, 15000),
                ('Transmission Service', 'Transmission fluid change', 24, 30000)
            ]

            cursor.executemany('''
                INSERT OR IGNORE INTO maintenance_types (name, description, recommended_interval_months, recommended_interval_miles)
                VALUES (?, ?, ?, ?)
            ''', default_types)

            conn.commit()

    def add_vehicle(self, make, model, year, vin=None):
        """Add a new vehicle to the database"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO vehicles (make, model, year, vin)
                VALUES (?, ?, ?, ?)
            ''', (make, model, year, vin))
            return cursor.lastrowid

    def add_maintenance_record(self, vehicle_id, service_date, service_type, description=None, 
                             cost=None, mileage=None, service_provider=None, notes=None):
        """Add a new maintenance record"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO maintenance_records 
                (vehicle_id, service_date, service_type, description, cost, mileage, service_provider, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (vehicle_id, service_date, service_type, description, cost, mileage, service_provider, notes))
            return cursor.lastrowid

    def get_all_vehicles(self):
        """Get all vehicles from the database"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM vehicles')
            return cursor.fetchall()

    def get_vehicle_records(self, vehicle_id):
        """Get all maintenance records for a specific vehicle"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM maintenance_records 
                WHERE vehicle_id = ? 
                ORDER BY service_date DESC
            ''', (vehicle_id,))
            return cursor.fetchall()

    def get_maintenance_types(self):
        """Get all maintenance types"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM maintenance_types')
            return cursor.fetchall()

    def import_from_excel(self, excel_data, vehicle_id):
        """Import maintenance records from Excel data"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            for row in excel_data:
                # Assuming Excel data matches the maintenance_records table structure
                cursor.execute('''
                    INSERT INTO maintenance_records 
                    (vehicle_id, service_date, service_type, description, cost, mileage, service_provider, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (vehicle_id, *row))
            conn.commit()

    def export_to_excel(self, vehicle_id=None):
        """Export maintenance records to Excel format"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            if vehicle_id:
                cursor.execute('''
                    SELECT * FROM maintenance_records 
                    WHERE vehicle_id = ? 
                    ORDER BY service_date DESC
                ''', (vehicle_id,))
            else:
                cursor.execute('SELECT * FROM maintenance_records ORDER BY service_date DESC')
            return cursor.fetchall()

    def get_upcoming_maintenance(self, vehicle_id):
        """Get upcoming maintenance based on intervals"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    mt.name,
                    mt.recommended_interval_months,
                    mt.recommended_interval_miles,
                    MAX(mr.service_date) as last_service_date,
                    MAX(mr.mileage) as last_mileage
                FROM maintenance_types mt
                LEFT JOIN maintenance_records mr 
                    ON mr.service_type = mt.name 
                    AND mr.vehicle_id = ?
                GROUP BY mt.name
            ''', (vehicle_id,))
            return cursor.fetchall()

if __name__ == "__main__":
    # Test the database
    db = VehicleDB()
    print("Database initialized successfully!")
