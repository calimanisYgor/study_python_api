from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

# Create a Flask application
app = Flask(__name__)

# Configure the SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

# Create a SQLAlchemy instance
db = SQLAlchemy(app)


class Product(db.Model):
    """
    Represents a product in the ecommerce store.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)


@app.route('/')
def hello():
    """
    Simple route that returns a greeting message.

    Returns:
        str: A greeting message.
    """
    return 'Hello, World!'


@app.route('/api/products', methods=['POST'])
def create_product():
    """
    Create a new product.
    """
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data['name'], price=data['price'], description=data.get('description', ''))
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully'}), 201
    return jsonify({'message': 'Invalid product data'}), 400


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Delete a product.

    Args:
        product_id (int): The ID of the product to delete.
    """
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 200
    return jsonify({'message': 'Product not found'}), 404


if __name__ == "__main__":
    app.run(debug=True)

