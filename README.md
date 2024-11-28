# Jaipur Curry House @ Taman TTDI - Digital Menu System

A comprehensive digital restaurant menu platform with QR code functionality for table-based ordering.

## Features

- Digital menu display with categories
- Real-time order management
- Shopping cart functionality
- QR code generation for tables
- Admin dashboard
- Mobile-responsive design
- Toast notifications
- Interactive UI elements

## Tech Stack

- Backend: Flask (Python)
- Database: SQLAlchemy with SQLite
- Frontend: HTML, Tailwind CSS
- Authentication: Flask-Login
- QR Code: qrcode library

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd personal-website
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python app.py
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Visit http://localhost:5000 in your web browser

## Project Structure

```
personal-website/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── static/
│   ├── images/        # Image assets
│   ├── css/          # CSS files
│   └── js/           # JavaScript files
└── templates/
    ├── base.html     # Base template
    ├── menu.html     # Menu page
    ├── admin.html    # Admin dashboard
    └── register.html # Registration page
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

## Database Models

- MenuItem: Menu items with details
- Order: Customer orders
- OrderItem: Individual items in orders
- User: Admin user accounts

## Security

- HTTPS recommended for production
- Password hashing for admin accounts
- Input validation
- CSRF protection

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any inquiries, please reach out to [contact information].
