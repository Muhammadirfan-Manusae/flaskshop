from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    profile_image = db.Column(db.String(20), nullable=True, default='default.jpg')
    orders = db.relationship('Order', backref='customer', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(20), nullable=True, default='default_product.jpg')
    comments = db.relationship('Comment', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_ordered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Pending, Shipped, Cancelled
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
