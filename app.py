from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import qrcode
import io
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Use environment variable in production
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///hardware_store.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200))

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
    with app.app_context():
        db.create_all()
        # Add sample products if none exist
        if not Product.query.first():
            sample_products = [
                Product(name='Hammer', description='Standard claw hammer', price=19.99, 
                       stock_quantity=50, category='Tools', 
                       image_url='/static/images/hammer.jpg'),
                Product(name='Screwdriver Set', description='Set of 6 screwdrivers', 
                       price=24.99, stock_quantity=30, category='Tools',
                       image_url='/static/images/screwdriver.jpg'),
                Product(name='Paint Brush', description='High-quality paint brush', 
                       price=9.99, stock_quantity=100, category='Painting',
                       image_url='/static/images/paintbrush.jpg'),
                Product(name='Wood Screws', description='Box of 100 wood screws', 
                       price=8.99, stock_quantity=200, category='Hardware',
                       image_url='/static/images/screws.jpg'),
                Product(name='Power Drill', description='Cordless power drill', 
                       price=129.99, stock_quantity=20, category='Power Tools',
                       image_url='/static/images/drill.jpg')
            ]
            for product in sample_products:
                db.session.add(product)
            db.session.commit()
        
        # Add sample menu items if they don't exist
        if MenuItem.query.count() == 0:
            sample_items = [
                # Appetizers
                MenuItem(
                    name='Crispy Calamari',
                    description='Tender calamari rings, lightly breaded and fried, served with marinara sauce',
                    price=12.99,
                    category='Appetizer',
                    available=True
                ),
                MenuItem(
                    name='Bruschetta',
                    description='Grilled bread rubbed with garlic and topped with diced tomatoes, fresh basil, and olive oil',
                    price=9.99,
                    category='Appetizer',
                    available=True
                ),
                
                # Main Courses
                MenuItem(
                    name='Grilled Salmon',
                    description='Fresh Atlantic salmon fillet, grilled to perfection with lemon herb butter',
                    price=24.99,
                    category='Main Course',
                    available=True
                ),
                MenuItem(
                    name='Beef Tenderloin',
                    description='8oz beef tenderloin, served with roasted vegetables and red wine reduction',
                    price=32.99,
                    category='Main Course',
                    available=True
                ),
                
                # Desserts
                MenuItem(
                    name='Tiramisu',
                    description='Classic Italian dessert with layers of coffee-soaked ladyfingers and mascarpone cream',
                    price=8.99,
                    category='Dessert',
                    available=True
                ),
                MenuItem(
                    name='Chocolate Lava Cake',
                    description='Warm chocolate cake with a molten center, served with vanilla ice cream',
                    price=9.99,
                    category='Dessert',
                    available=True
                ),
                
                # Beverages
                MenuItem(
                    name='Fresh Lemonade',
                    description='Homemade lemonade with fresh mint',
                    price=4.99,
                    category='Beverage',
                    available=True
                ),
                MenuItem(
                    name='Italian Soda',
                    description='Sparkling water with your choice of flavored syrup',
                    price=3.99,
                    category='Beverage',
                    available=True
                )
            ]
            
            for item in sample_items:
                db.session.add(item)
            
            db.session.commit()

# Routes
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

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

@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html')

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    if quantity > product.stock_quantity:
        return jsonify({'error': 'Not enough stock'}), 400
    
    cart_data = request.cookies.get('cart', '{}')
    cart = eval(cart_data)
    cart[product_id] = cart.get(product_id, 0) + quantity
    
    response = jsonify({'message': 'Added to cart'})
    response.set_cookie('cart', str(cart))
    return response

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_data = request.cookies.get('cart', '{}')
    cart = eval(cart_data)
    
    if not cart:
        flash('Your cart is empty')
        return redirect(url_for('cart'))
    
    total_amount = 0
    order_items = []
    
    for product_id, quantity in cart.items():
        product = Product.query.get(product_id)
        if product.stock_quantity < quantity:
            flash(f'Not enough stock for {product.name}')
            return redirect(url_for('cart'))
        
        total_amount += product.price * quantity
        order_items.append({
            'product': product,
            'quantity': quantity,
            'price': product.price
        })
        
        product.stock_quantity -= quantity
    
    order = Order(user_id=current_user.id, total_amount=total_amount)
    db.session.add(order)
    db.session.flush()
    
    for item in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product'].id,
            quantity=item['quantity'],
            price_at_time=item['price']
        )
        db.session.add(order_item)
    
    db.session.commit()
    response = redirect(url_for('orders'))
    response.delete_cookie('cart')
    flash('Order placed successfully')
    return response

@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)

@app.route('/product/<int:product_id>')
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock_quantity': product.stock_quantity,
        'category': product.category,
        'image_url': '/static/images/placeholder.jpg'  # Default to placeholder image
    })

@app.route('/menu')
def menu():
    categories = ['Appetizer', 'Main Course', 'Dessert', 'Beverage']
    menu_items = {}
    for category in categories:
        menu_items[category] = MenuItem.query.filter_by(category=category, available=True).all()
    return render_template('menu.html', menu_items=menu_items, categories=categories)

@app.route('/qr/<int:table_number>')
def qr_menu(table_number):
    categories = ['Appetizer', 'Main Course', 'Dessert', 'Beverage']
    menu_items = {}
    for category in categories:
        menu_items[category] = MenuItem.query.filter_by(category=category, available=True).all()
    return render_template('qr_menu.html', menu_items=menu_items, categories=categories, table_number=table_number)

@app.route('/api/place_order', methods=['POST'])
def place_order():
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
