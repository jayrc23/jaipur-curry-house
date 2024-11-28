from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import qrcode
import io
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Use environment variable in production
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

# Database Configuration
def get_database_url():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # Local development - use SQLite
        return 'sqlite:///instance/restaurant.db'
    
    if database_url.startswith('postgres://'):
        # Render PostgreSQL URL needs to be modified for SQLAlchemy
        return database_url.replace('postgres://', 'postgresql://', 1)
    
    return database_url

app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create instance directory for SQLite (local development)
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:'):
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

# Enable HTTPS redirect in production
if os.environ.get('FLASK_ENV') == 'production':
    from flask_talisman import Talisman
    Talisman(app, force_https=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'Appetizer', 'Main Course', 'Dessert', 'Beverage'
    image_url = db.Column(db.String(200))
    available = db.Column(db.Boolean, default=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # nullable for guest orders
    table_number = db.Column(db.Integer)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Float, nullable=False)
    special_instructions = db.Column(db.Text)
    menu_item = db.relationship('MenuItem')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    try:
        with app.app_context():
            db.create_all()
            
            # Add sample menu items if they don't exist
            if MenuItem.query.count() == 0:
                sample_items = [
                    # Appetizers
                    MenuItem(
                        name='Samosa',
                        description='Crispy pastry filled with spiced potatoes and peas',
                        price=6.99,
                        category='Appetizer',
                        available=True
                    ),
                    MenuItem(
                        name='Onion Bhaji',
                        description='Crispy onion fritters with Indian spices',
                        price=5.99,
                        category='Appetizer',
                        available=True
                    ),
                    
                    # Main Courses
                    MenuItem(
                        name='Butter Chicken',
                        description='Tender chicken in a rich, creamy tomato sauce',
                        price=16.99,
                        category='Main Course',
                        available=True
                    ),
                    MenuItem(
                        name='Paneer Tikka Masala',
                        description='Grilled cottage cheese in spiced tomato gravy',
                        price=15.99,
                        category='Main Course',
                        available=True
                    ),
                    
                    # Breads
                    MenuItem(
                        name='Garlic Naan',
                        description='Fresh bread with garlic and butter',
                        price=3.99,
                        category='Bread',
                        available=True
                    ),
                    MenuItem(
                        name='Roti',
                        description='Whole wheat flatbread',
                        price=2.99,
                        category='Bread',
                        available=True
                    ),
                    
                    # Beverages
                    MenuItem(
                        name='Mango Lassi',
                        description='Sweet yogurt drink with mango',
                        price=4.99,
                        category='Beverage',
                        available=True
                    ),
                    MenuItem(
                        name='Masala Chai',
                        description='Indian spiced tea with milk',
                        price=3.99,
                        category='Beverage',
                        available=True
                    )
                ]
                
                for item in sample_items:
                    db.session.add(item)
                
                db.session.commit()
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        db.session.rollback()

# Routes
@app.route('/')
def index():
    return redirect(url_for('menu'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    if 'cart' not in session:
        session['cart'] = []
    
    menu_item = MenuItem.query.get_or_404(item_id)
    cart_item = {
        'id': menu_item.id,
        'name': menu_item.name,
        'price': menu_item.price,
        'quantity': int(request.form.get('quantity', 1))
    }
    session['cart'].append(cart_item)
    session.modified = True
    
    flash(f'{menu_item.name} added to cart!')
    return redirect(url_for('menu'))

@app.route('/cart')
def cart():
    if 'cart' not in session:
        session['cart'] = []
    
    total_amount = sum(item['price'] * item['quantity'] for item in session['cart'])
    return render_template('cart.html', cart=session['cart'], total_amount=total_amount)

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != item_id]
        session.modified = True
        flash('Item removed from cart')
    return redirect(url_for('cart'))

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty')
        return redirect(url_for('cart'))

    try:
        total_amount = sum(item['price'] * item['quantity'] for item in session['cart'])
        
        # Create the order
        order = Order(
            user_id=current_user.id if current_user.is_authenticated else None,
            total_amount=total_amount,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Add order items
        for item in session['cart']:
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item['id'],
                quantity=item['quantity'],
                price_at_time=item['price']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # Clear the cart
        session['cart'] = []
        session.modified = True
        
        flash('Order placed successfully!')
        return redirect(url_for('menu'))
        
    except Exception as e:
        db.session.rollback()
        flash('Error placing order. Please try again.')
        return redirect(url_for('cart'))

@app.route('/menu')
def menu():
    menu_items = MenuItem.query.filter_by(available=True).all()
    menu_by_category = {}
    categories = sorted(set(item.category for item in menu_items))
    
    for category in categories:
        menu_by_category[category] = [item for item in menu_items if item.category == category]
    
    return render_template('menu.html', menu_items=menu_by_category, categories=categories)

@app.route('/qr/<int:table_number>')
def qr_menu(table_number):
    categories = ['Appetizer', 'Main Course', 'Dessert', 'Beverage']
    menu_items = {}
    for category in categories:
        menu_items[category] = MenuItem.query.filter_by(category=category, available=True).all()
    return render_template('qr_menu.html', menu_items=menu_items, categories=categories, table_number=table_number)

@app.route('/api/place_order', methods=['POST'])
def place_order_api():
    data = request.get_json()
    table_number = data.get('table_number')
    items = data.get('items', [])
    
    if not items:
        return jsonify({'error': 'No items in order'}), 400
    
    # Create new order
    order = Order(table_number=table_number)
    total_amount = 0
    
    # Add items to order
    for item in items:
        menu_item = MenuItem.query.get(item['id'])
        if not menu_item:
            continue
        
        order_item = OrderItem(
            menu_item_id=menu_item.id,
            quantity=item['quantity'],
            price_at_time=menu_item.price,
            special_instructions=item.get('special_instructions', '')
        )
        total_amount += menu_item.price * item['quantity']
        order.items.append(order_item)
    
    order.total_amount = total_amount
    db.session.add(order)
    db.session.commit()
    
    return jsonify({
        'message': 'Order placed successfully',
        'order_id': order.id
    }), 201

@app.route('/api/order_status/<int:order_id>')
def order_status(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify({
        'status': order.status,
        'created_at': order.created_at,
        'total_amount': order.total_amount
    })

@app.route('/generate_qr/<int:table_number>')
def generate_qr(table_number):
    # Generate QR code for the table's menu URL
    menu_url = url_for('qr_menu', table_number=table_number, _external=True)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(menu_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to bytes buffer
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return send_file(img_buffer, mimetype='image/png')

@app.route('/admin')
@login_required
def admin():
    # In a production environment, you should check if the user is an admin
    return render_template('admin.html')

@app.route('/api/active_orders')
@login_required
def active_orders():
    # Get all non-completed orders
    orders = Order.query.filter(Order.status.in_(['pending', 'confirmed'])).all()
    return jsonify([{
        'id': order.id,
        'table_number': order.table_number,
        'status': order.status,
        'total_amount': order.total_amount,
        'items': [{
            'name': item.menu_item.name,
            'quantity': item.quantity,
            'price': item.price_at_time
        } for item in order.items]
    } for order in orders])

@app.route('/api/update_order_status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['pending', 'confirmed', 'completed', 'cancelled']:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400
    
    order = Order.query.get_or_404(order_id)
    order.status = new_status
    db.session.commit()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(host='0.0.0.0', port=port)
    else:
        app.run(debug=True, port=port)
