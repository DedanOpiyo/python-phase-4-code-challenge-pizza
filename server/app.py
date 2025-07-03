#!/usr/bin/env python3
from sqlalchemy.exc import IntegrityError # sqlalchemy.exc for db level exceptions
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Resaurces
class RestaurantResource(Resource):

    def get(self):

        restaurants = [restaurant.to_dict(only=('address', 'id', 'name',)) for restaurant in Restaurant.query.all()]

        if not restaurants:
            return jsonify({'error': 'Error retrieving restaurants Or No restaurants available'}), 500

        return make_response(restaurants, 200)
    
# class RestaurantById(Resource):

#     def get(self, id):

#         if not id:
#             return {'error': 'Restaurant not found'}, 404

#         restaurant = Restaurant.query.get(id)

#         if not restaurant:
#             return jsonify({'error': 'Restaurant not found'}), 404

#         return make_response(restaurant.to_dict(), 200)
    
#     def delete(self, id):

#         if not id:
#             return {'error': 'Restaurant not found'}, 404
        
#         restaurant = Restaurant.query.get(id)

#         if not restaurant:
#             return jsonify({'error': 'Restaurant not found'}), 404
        
#         db.session.delete(restaurant)
#         db.session.commit()

#         return {}, 204
class RestaurantID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)

        if not restaurant:
                return {"error": "Restaurant not found"}, 404

        return restaurant.to_dict(rules=('restaurant_pizzas', 'restaurant_pizzas.pizza')), 200

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Reastaurant not found"}, 404

        db.session.delete(restaurant)
        db.session.commit()
        return '',204

api.add_resource(RestaurantID, '/restaurants/<int:id>')
    
# class Pizzas(Resource):

#     def get(self):

#         pizzas = [pizza.to_dict(only=('id', 'ingredients', 'name',)) for pizza in Pizza.query.all()]

#         if not pizzas:
#             return jsonify({'error': 'Error retrieving pizzas Or No pizzas available'}), 500

#         return make_response(pizzas, 200)
class PizzaResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [p.to_dict() for p in pizzas], 200

api.add_resource(PizzaResource, '/pizzas')

# class PizzaById(Resource):

#     def get(self, id):

#         if not id:
#             return {'error': 'Pizza ID Missing'}, 400

#         pizza = Pizza.query.get(id)

#         if not pizza:
#             return jsonify({'error': 'Pizza not found'}), 400

#         return make_response(pizza.to_dict(), 200)

class ReastaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()

        try:
            price = data.get('price')
            pizza_id = data.get('pizza_id')
            restaurant_id = data.get('restaurant_id')

            if price is None or pizza_id is None or restaurant_id is None:
                return {"errors": ["Missing required fields"]}, 400

            new_rp = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )
            db.session.add(new_rp)
            db.session.commit()

            return new_rp.to_dict(rules=('pizza',)), 201
        except Exception as e:
            return {"errors": ["validation errors"]}, 400 

api.add_resource(ReastaurantPizzaResource, '/restaurant_pizzas')
    
# class RestaurantPizzas(Resource):

#     def get(self):

#         restaurant_pizzas = [restaurant_pizza.to_dict() for restaurant_pizza in RestaurantPizza.query.all()]

#         if not restaurant_pizzas:
#             return {'error': 'Error retrieving restaurant_pizzas Or No restaurant_pizzas available'}, 500

#         return make_response(restaurant_pizzas, 200)
    
#     def post(self):

#         data = request.get_json()

#         if not data:
#             return {"missing_fields": {"price": None, "pizza_id": None, "restaurant_id": None}}, 400

#         price = data.get('price')
#         pizza_id = data.get('pizza_id')
#         restaurant_id = data.get('restaurant_id')

#         errors = []
#         if not price:
#             errors.append('validation errors') # 'validation errors' to pass the test i.e if price is 0
#         if not pizza_id:
#             errors.append('Pizza_id is required')
#         if not restaurant_id:
#             errors.append('Restaurant_id is required')
#         if errors:
#             return {"errors": errors}, 400 # 422 # **No jsonify! returning a Response object (jsonify(...)) isn't serializable in flask_restful.
        
#         try:
#             new_restaurant_pizza = RestaurantPizza( 
#                 price=price,
#                 pizza_id=pizza_id,
#                 restaurant_id=restaurant_id
#             )

#             db.session.add(new_restaurant_pizza)
#             db.session.commit()

#         except ValueError:
#             return {"errors": ["validation errors"]}, 400 # 422
#         except (IntegrityError, KeyError) as e:
#             return {"error": str(e)}, 400 # No jsonified responses in Flask-RESTful # Works in plain Flask, but not in Flask-RESTful
#         except:
#             return {"errors": ["validation errors"]}, 400 # 422 # {"errors": "422: Unprocessable Entity"}
        
#         return make_response(new_restaurant_pizza.to_dict(), 201)

api.add_resource(RestaurantResource, '/restaurants', endpoint='/restaurants')
# api.add_resource(RestaurantById, '/restaurants/<int:id>', endpoint='/restaurantsbyid')
# api.add_resource(Pizzas, '/pizzas', endpoint='/pizzas')
# api.add_resource(PizzaById, '/pizzas/<int:id>', endpoint='/pizzasbyid')
# api.add_resource(RestaurantPizzas, '/restaurant_pizzas', endpoint='/restaurant_pizzas')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
