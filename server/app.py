#!/usr/bin/env python3

import os

from flask import Flask, jsonify, make_response, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import Pizza, Restaurant, RestaurantPizza, db

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    # Query all restaurants from the database
    restaurants = Restaurant.query.all()

    # Serialize the restaurant data, excluding 'restaurant_pizzas'
    serialized_restaurants = [
        restaurant.to_dict(rules=("-restaurant_pizzas",)) for restaurant in restaurants
    ]

    # Return a JSON response
    return jsonify(serialized_restaurants), 200


@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    serialized_restaurant = restaurant.to_dict(rules=())
    return jsonify(serialized_restaurant), 200


# Delete a restaurant by ID
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    db.session.delete(restaurant)
    db.session.commit()
    return "", 204


# Retrieve all pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    serialized_pizzas = [
        pizza.to_dict(rules=("-restaurant_pizzas",)) for pizza in pizzas
    ]
    return jsonify(serialized_pizzas), 200


# Create a RestaurantPizza entry
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    # Validate price
    price = data.get("price")
    if not (1 <= price <= 30):
        return jsonify({"errors": ["validation errors"]}), 400

    pizza = Pizza.query.get(data.get("pizza_id"))
    restaurant = Restaurant.query.get(data.get("restaurant_id"))

    if not pizza or not restaurant:
        return jsonify({"errors": ["Invalid pizza_id or restaurant_id"]}), 400

    restaurant_pizza = RestaurantPizza(
        price=price, pizza_id=pizza.id, restaurant_id=restaurant.id
    )

    db.session.add(restaurant_pizza)
    db.session.commit()

    return jsonify(restaurant_pizza.to_dict(rules=())), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
