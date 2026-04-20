from app import create_app, db
from app.models import User, Product, Comment, Order, OrderItem
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash

app = create_app()
migrate = Migrate(app, db)

# ---------- สร้างแอดมินหลักอัตโนมัติ ----------
with app.app_context():
    if not User.query.filter_by(is_admin=True).first():
        admin = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin@example.com / admin123")

# ---------- Shell context ----------
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Product': Product, 'Comment': Comment, 'Order': Order, 'OrderItem': OrderItem}

if __name__ == '__main__':
    app.run(debug=True)
