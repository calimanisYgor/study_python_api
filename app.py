# imports
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

# app
app = Flask(__name__)

# config base de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

# instanciar base de dados
db = SQLAlchemy(app)

# Modelagem
# Produto (id, name, price, description)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)



# rotas
# Definir uma rota raiz e a função que será executado ao requisitar
@app.route('/')
def hello_world():
    return 'Hello, World!'
    
@app.route('/api/products/add', methods=['POST'])
def add_products():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data.get('name'), price=data.get('price'), description=data.get('description', ''))
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product added sucessfully'}), 200
    return jsonify({'message': 'Invalid product data'}), 400

@app.route('/api/products/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted sucessfully'}), 200
    return jsonify({'message': 'Product not found'}), 404


if __name__== "__main__":
    app.run(debug=True)