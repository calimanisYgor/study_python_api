from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

CORS(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=True)
    cart = db.relationship('CartItem', backref='user', lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    cart = db.relationship('CartItem', backref='product', lazy=True)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['POST'])
def user_login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and data.get('password') == user.password:
        login_user(user)
        return jsonify({'message': 'Logged in successfully'}), 200
    return jsonify({'message': 'Unauthorized. Invalid credentials'}), 401


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout in successfully'}), 200


@app.route('/api/products/add', methods=['POST'])
@login_required
def create_product():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data['name'], price=data['price'],
                          description=data.get('description', ''))
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully'}), 201
    return jsonify({'message': 'Invalid product data'}), 400


@app.route('/api/products/delete/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 200
    return jsonify({'message': 'Product not found'}), 404


@app.route('/api/products/getAll', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    product_list = [{'id': product.id,
                     'name': product.name,
                     'price': product.price} for product in products]
    return jsonify(product_list)


@app.route('/api/products/getById/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'description': product.description})
    return jsonify({'message': 'Product not found'}), 404


@app.route('/api/products/update/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if product:
        data = request.json
        for key, value in data.items():
            setattr(product, key, value)
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'}), 200
    return jsonify({'message': 'Product not found'}), 404


# checkout
@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    user = User.query.get(current_user.id)

    if product and user:
        cart_item = CartItem(user_id=user.id, product_id=product.id)
        db.session.add(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item added to the cart successfully'}), 200
    return jsonify({'message': 'Failed to add item to the cart'}), 400


@app.route('/api/cart/remove/<int:product_id>', methods=['DELETE'])
@login_required
def delete_from_cart(product_id):
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item removed from the cart successfully'}), 200
    return jsonify({'message': 'Failed to remove item from the cart'}), 400


@app.route('/api/cart/', methods=['GET'])
@login_required
def view_cart():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    cart_content = []
    for cart_item in cart_items:
        product = Product.query.get(cart_item.product_id)
        cart_content.append({
            'id': cart_item.product.id,
            'user_id': cart_item.user_id,
            'product_id': cart_item.product_id,
            'product_name': product.name,
            'product_price': product.price,
        })
    if cart_content == []:
        return jsonify({'message': 'Cart is empty'}), 200
    return jsonify(cart_content)

@app.route('/api/cart/checkout', methods=['POST'])
@login_required
def checkout():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    if cart_items:
        for cart_item in cart_items:
            db.session.delete(cart_item)
            db.session.commit()
        return jsonify({'message': 'Checkout successfully. Cart has been cleared'}), 200
    return jsonify({'message': 'Checkout failed. Cart is empty'}), 400
if __name__ == "__main__":
    app.run(debug=True)
