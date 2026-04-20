from flask import Blueprint, render_template, url_for, flash, redirect, request
from app.forms import RegistrationForm, LoginForm, CommentForm, AddToCartForm, CheckoutForm, UpdateProfileForm
from app.models import User, Product, Comment, Order, OrderItem
from app import db
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
from flask import send_from_directory

main = Blueprint('main', __name__)

# ---------- Landing Page (ให้เปลี่ยนมาเป็นหน้าแรกสุด) ----------
@main.route('/')
def landing_page():
    return render_template('landing.html')

# ---------- Home Page / Products (เปลี่ยนชื่อ Route เป็นอย่างอื่น เช่น /products) ----------
@main.route('/products')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

# ---------- Product Detail ----------
@main.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    form = CommentForm()
    cart_form = AddToCartForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(content=form.content.data, author=current_user, product=product)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added!', 'success')
        return redirect(url_for('main.product_detail', product_id=product.id))
    return render_template('product_detail.html', product=product, form=form, cart_form=cart_form)

# ---------- Add to Cart ----------
@main.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = request.form.get('quantity', 1, type=int)
    # ค้นหา Order pending ของผู้ใช้
    order = Order.query.filter_by(user_id=current_user.id, status='Pending').first()
    if not order:
        order = Order(user_id=current_user.id, status='Pending', name=current_user.username, address=current_user.address, phone='')
        db.session.add(order)
        db.session.commit()
    # เพิ่มสินค้าลง OrderItem
    item = OrderItem.query.filter_by(order_id=order.id, product_id=product.id).first()
    if item:
        item.quantity += quantity
    else:
        item = OrderItem(order_id=order.id, product_id=product.id, quantity=quantity)
        db.session.add(item)
    db.session.commit()
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('main.product_detail', product_id=product.id))

# ---------- Cart ----------
@main.route('/cart')
@login_required
def cart():
    order = Order.query.options(joinedload(Order.items).joinedload(OrderItem.product))\
                       .filter_by(user_id=current_user.id, status='Pending').first()
    
    total = 0
    if order:
        total = sum(item.quantity * item.product.price for item in order.items)
    
    return render_template('cart.html', order=order, total=total)

# ---------- Checkout ----------
@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    order = Order.query.options(joinedload(Order.items).joinedload(OrderItem.product))\
                       .filter_by(user_id=current_user.id, status='Pending').first()
    if not order:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('main.index'))

    # คำนวณ total
    total = sum(item.quantity * item.product.price for item in order.items) if order.items else 0

    form = CheckoutForm()
    if form.validate_on_submit():
        order.name = form.name.data
        order.address = form.address.data
        order.phone = form.phone.data
        order.status = 'Placed'
        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('main.my_orders'))

    return render_template('checkout.html', form=form, order=order, total=total)

# ---------- My Orders ----------
@main.route('/my_orders')
@login_required
def my_orders():
    # โหลด order + items + product แบบ eager
    orders = Order.query.options(joinedload(Order.items).joinedload(OrderItem.product))\
                        .filter_by(user_id=current_user.id)\
                        .order_by(Order.date_ordered.desc())\
                        .all()

    # คำนวณ total สำหรับแต่ละ order
    for order in orders:
        order.total = sum(item.quantity * item.product.price for item in order.items)

    return render_template('my_orders.html', orders=orders)

# ---------- User Profile ----------
@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.address = form.address.data
        if form.profile_image.data:
            # Save profile image
            image_file = f"profile_{current_user.id}.jpg"
            form.profile_image.data.save(f"app/static/images/{image_file}")
            current_user.profile_image = image_file
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.address.data = current_user.address
    return render_template('profile.html', form=form)

# ---------- Login ----------
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    return render_template('login.html', form=form)

# ---------- Logout ----------
@main.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

# ---------- Register ----------
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

from functools import wraps

# ---------- Admin Required Decorator ----------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# ---------- Admin Dashboard ----------
@main.route('/admin')
@admin_required
def admin_dashboard():
    users = User.query.all()
    products = Product.query.all()
    orders = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.product),
        joinedload(Order.customer)
    ).order_by(Order.date_ordered.desc()).all()

    # คำนวณ total ของแต่ละ order
    for order in orders:
        order.total = sum(item.quantity * item.product.price for item in order.items)

    return render_template('admin_dashboard.html', users=users, products=products, orders=orders)


# ---------- Toggle Admin ----------
@main.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Cannot change your own admin status.", 'danger')
        return redirect(url_for('main.admin_dashboard'))
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f"{user.username}'s admin status updated.", 'success')
    return redirect(url_for('main.admin_dashboard'))

# ---------- Delete User ----------
@main.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Cannot delete your own account.", 'danger')
        return redirect(url_for('main.admin_dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} deleted.", 'success')
    return redirect(url_for('main.admin_dashboard'))

# ---------- Add Product ----------
@main.route('/admin/add_product', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price'))
        description = request.form.get('description')
        image_file = request.files.get('image')
        filename = 'default_product.jpg'
        if image_file:
            filename = f"product_{name}.jpg"
            image_file.save(f"app/static/images/{filename}")
        product = Product(name=name, price=price, description=description, image_file=filename)
        db.session.add(product)
        db.session.commit()
        flash(f"Product '{name}' added.", 'success')
        return redirect(url_for('main.admin_dashboard'))
    return render_template('add_product.html')

# ---------- Delete Product ----------
@main.route('/admin/delete_product/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash(f"Product '{product.name}' deleted.", 'success')
    return redirect(url_for('main.admin_dashboard'))

# ---------- Update Order Status ----------
@main.route('/admin/update_order/<int:order_id>/<string:status>', methods=['POST'])
@admin_required
def update_order(order_id, status):
    order = Order.query.get_or_404(order_id)
    if status in ['Shipped', 'Cancelled']:
        order.status = status
        db.session.commit()
        flash(f"Order #{order.id} marked as {status}.", 'success')
    return redirect(url_for('main.admin_dashboard'))

# ---------- Remove Item from Cart ----------
@main.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = OrderItem.query.get_or_404(item_id)
    order = Order.query.filter_by(user_id=current_user.id, status='Pending').first()
    
    if not order or item.order_id != order.id:
        flash("Item not found in your cart.", "danger")
        return redirect(url_for('main.cart'))
    
    # เก็บชื่อสินค้าไว้ก่อนลบ
    product_name = item.product.name
    
    db.session.delete(item)
    db.session.commit()
    
    flash(f"{product_name} removed from cart.", "success")
    return redirect(url_for('main.cart'))

# Remove Order สำหรับลบออเดอร์ในหน้าแดชบอร์ด
@main.route('/admin/remove_order/<int:order_id>', methods=['POST'])
@admin_required
def remove_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    # ลบ OrderItem ทั้งหมดก่อน
    for item in order.items:
        db.session.delete(item)
    
    db.session.delete(order)
    db.session.commit()
    
    flash(f"Order #{order.id} has been removed.", "success")
    return redirect(url_for('main.admin_dashboard'))

# ลบโค้ดชุดเดิมที่ประกาศ route ซ้ำออกให้หมด แล้วใส่โค้ดนี้ลงไปแทนครับ
@main.route('/google182eb51858f50114.html')
def google_verification():
    # ใช้ send_from_directory เพื่ออ่านไฟล์จากโฟลเดอร์ static
    return send_from_directory('static', 'google182eb51858f50114.html')