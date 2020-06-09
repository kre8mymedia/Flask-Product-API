from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
import os
import json
import requests

web_hook_url = os.getenv('SLACK_WEBHOOK')

#Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# Product Class/Model
class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), unique=True)
  description = db.Column(db.String(200))
  price = db.Column(db.Float)
  qty = db.Column(db.Integer)

  def __init__(self, name, description, price, qty):
    self.name = name
    self.description = description
    self.price = price
    self.qty = qty

# Product Schema
class ProductSchema(ma.Schema):
  class Meta:
    fields = ('id', 'name', 'description', 'price', 'qty')

# Init Schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Home Route
@app.route('/', methods=['GET'])
def get():
  ### SLACK MESSAGE ###
  message = {'text': "Home Page Visitor!!"}
  requests.post(web_hook_url, data=json.dumps(message))
  ### SLACK MESSAGE ###
  return "<h3>Welcome to the Product API</h3><ul><li>Create Product [POST]: '/product'</li><li>Get Product [GET]: '/product/[id]'</li><li>All Products [GET]: '/product'</li><li>Update Product [PUT]: '/product/[id]'</li><li>Delete Product [DELETE]: '/product/[id]'</li></ul>"

#Create a product
@app.route('/product', methods=['POST'])
def add_product():
  name = request.json['name']
  description = request.json['description']
  price = request.json['price']
  qty = request.json['qty']

  new_product = Product(name, description, price, qty)

  db.session.add(new_product)
  db.session.commit()
  # Slack Message
  if new_product:
    message = {'text': "New Product Added!"}
    requests.post(web_hook_url, data=json.dumps(message))

  return product_schema.jsonify(new_product)

# Get All Product
@app.route('/product', methods=['GET'])
def get_products():
  message = {'text': "User requesting all products!"}
  requests.post(web_hook_url, data=json.dumps(message))
  # query db for all products
  all_products = Product.query.all()
  # return array of all products
  result = products_schema.dump(all_products)
  return jsonify(result)

# Get Single Product
@app.route('/product/<id>', methods=['GET'])
def get_product(id):
  message = {'text': f"User requested Product {id}"}
  requests.post(web_hook_url, data=json.dumps(message))
  # query db for all products
  product = Product.query.get(id)
  return product_schema.jsonify(product)

#Create a product
@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
  # find item we'd like to change
  product = Product.query.get(id)
  # init request variables
  name = request.json['name']
  description = request.json['description']
  price = request.json['price']
  qty = request.json['qty']
  # save new model params
  product.name = name
  product.description = description
  product.price = price
  product.qty = qty
  # commit the change
  db.session.commit()

  # Output slack channel message
  if product.name:
    message = {'text': "Updated Product!"}
    requests.post(web_hook_url, data=json.dumps(message))

  return product_schema.jsonify(product)

# Get Single Product
@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
  # slack message
  message = {'text': f"User deleted Product {id}"}
  requests.post(web_hook_url, data=json.dumps(message))
  # find product to delete
  product = Product.query.get(id)
  db.session.delete(product)
  db.session.commit()

  # return the deleted object
  return product_schema.jsonify(product)

#Run Sever
if __name__ == '__main__':
  app.run(debug=True)