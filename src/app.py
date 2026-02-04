"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, abort, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import Character, Planet, db, User, Vehicle, Favorite
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)

# ==========================
#     ENDPOINTS DE USER
# ==========================


@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    users_to_json = jsonify([user.serialize() for user in users])
    return users_to_json, 200


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404, description="User not found")
    user_to_json = jsonify(user.serialize())
    return user_to_json, 200


@app.route('/users-by-email/<string:email>', methods=['GET'])
def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    if user is None:
        abort(404, description="User not found")
    user_to_json = jsonify(user.serialize())
    return user_to_json, 200


@app.route('/users', methods=['POST'])
def create_user():
    body = request.get_json()
    if not body:
        abort(400, description="Request body must be JSON")
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in body or not body[field]:
            abort(422, description=f"'{field}' is required")
    existing_email = User.query.filter_by(email=body['email']).first()
    if existing_email:
        abort(409, description="Email already exists")
    try:
        new_user = User(email=body["email"],
                        password=body["password"],
                        first_name=body.get("first_name"),
                        last_name=body.get("last_name"))
        db.session.add(new_user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Internal Server Error")
    return jsonify(new_user.serialize()), 201


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404, description=f"User with ID {user_id} not found")
    body = request.get_json()
    if not body:
        abort(400, description="Request body must be JSON")
    if 'email' in body and body['email'] != user.email:
        existing_email = User.query.filter_by(email=body['email']).first()
        if existing_email:
            abort(409, description="Email already exists")
    try:
        user.email = body['email']
        user.password = body['password']
        user.first_name = body.get("first_name")
        user.last_name = body.get("last_name")
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Internal Server Error")
    return jsonify(user.serialize()), 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404, description=f"User with ID {user_id} not found")
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Internal Server Error")
    return jsonify({"message": f"User with ID {user_id} has been deleted"}), 200



# ==========================
#     ENDPOINTS DE CHARACTER
# ==========================
@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters = Character.query.all()
    characters_to_json = jsonify([character.serialize() for character in characters])
    return characters_to_json, 200


@app.route('/characters/<int:id>', methods=['GET'])
def get_character_by_id(id):
    character = Character.query.get(id)
    if character is None:
        abort(404, description="Character not found")
    character_to_json = jsonify(character.serialize())
    return character_to_json, 200


@app.route('/characters/<string:name>', methods=['GET'])
def get_character_by_name(name):
    character = Character.query.filter_by(name=name).first()
    if character is None:
        abort(404, description="Character not found")
    character_to_json = jsonify(character.serialize())
    return character_to_json, 200


@app.route('/characters', methods=['POST'])
def create_character():
    body = request.get_json()
    if not body:
        abort(400, description="Request body must be JSON")
    required_fields = ['name']
    for field in required_fields:
        if field not in body or not body[field]:
            abort(422, description=f"'{field}' is required")
    existing_name = Character.query.filter_by(name=body['name']).first()
    if existing_name:
        abort(409, description="Name already exists")
    try:
        new_character = Character(name=body["name"],
                        gender=body.get("gender"),
                        height=body.get("height"),
                        mass=body.get("mass"))
        db.session.add(new_character)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Internal Server Error")
    return jsonify(new_character.serialize()), 201


@app.route('/characters/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    character = Character.query.get(character_id)
    if character is None:
        abort(404, description=f"Character with ID {character_id} not found")
    body = request.get_json()
    if not body:
        abort(400, description="Request body must be JSON")
    if 'name' in body and body['name'] != character.name:
        existing_name = Character.query.filter_by(name=body['name']).first()
        if existing_name:
            abort(409, description="Name already exists")
    try:
        character.name = body['name']
        character.gender = body.get('gender')
        character.height = body.get("height")
        character.mass = body.get("mass")
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Internal Server Error")
    return jsonify(character.serialize()), 200


@app.route('/characters/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = Character.query.get(character_id)
    if character is None:
        abort(404, description=f"Character with ID {character_id} not found")
    try:
        db.session.delete(character)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Internal Server Error")
    return jsonify({"message": f"Character with ID {character_id} has been deleted"}), 200



# ==========================
#     ENDPOINTS DE PLANET
# ==========================
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    planets_to_json = jsonify([planet.serialize() for planet in planets])
    return planets_to_json, 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        abort(404, description="Planet not found")
    planet_to_json = jsonify(planet.serialize())
    return planet_to_json, 200


@app.route('/planets/<string:name>', methods=['GET'])
def get_planet_by_name(name):
    planet = Planet.query.filter_by(name=name).first()
    if planet is None:
        abort(404, description="Planet not found")
    planet_to_json = jsonify(planet.serialize())
    return planet_to_json, 200


@app.route('/planets', methods=['POST'])
def create_planet():
    body = request.get_json()
    if not body:
        abort(400, description="Request body must be JSON")
    required_fields = ['name']
    for field in required_fields:
        if field not in body or not body[field]:
            abort(422, description=f"'{field}' is required")
    existing_name = Planet.query.filter_by(name=body['name']).first()
    if existing_name:
        abort(409, description="Name already exists")
    try:
        new_planet = Planet(name=body["name"],
                        climate=body.get("climate"),
                        population=body.get("population"),
                        terrain=body.get("terrain"))
        db.session.add(new_planet)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Internal Server Error")
    return jsonify(new_planet.serialize()), 201


@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        abort(404, description=f"Planet with ID {planet_id} not found")
    body = request.get_json()
    if not body:
        abort(400, description="Request body must be JSON")
    if 'name' in body and body['name'] != planet.name:
        existing_name = Planet.query.filter_by(name=body['name']).first()
        if existing_name:
            abort(409, description="Name already exists")
    try:
        planet.name = body['name']
        planet.climate = body.get("climate")
        planet.population = body.get("population")
        planet.terrain = body.get("terrain")
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Internal Server Error")
    return jsonify(planet.serialize()), 200


@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        abort(404, description=f"Planet with ID {planet_id} not found")
    try:
        db.session.delete(planet)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Internal Server Error")
    return jsonify({"message": f"Planet with ID {planet_id} has been deleted"}), 200



# ==========================
#     ENDPOINTS DE VEHICLE
# ==========================
@app.route('/vehicles', methods=['GET'])
def get_all_vehicles():
    vehicles = Vehicle.query.all()
    vehicles_to_json = jsonify([vehicle.serialize() for vehicle in vehicles])
    return vehicles_to_json, 200


@app.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle_by_id(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle is None:
        abort(404, description="Vehicle not found")
    vehicle_to_json = jsonify(vehicle.serialize())
    return vehicle_to_json, 200


@app.route('/vehicles/<string:name>', methods=['GET'])
def get_vehicle_by_name(name):
    vehicle = Vehicle.query.filter_by(name=name).first()
    if vehicle is None:
        abort(404, description="Vehicle not found")
    vehicle_to_json = jsonify(vehicle.serialize())
    return vehicle_to_json, 200


@app.route('/vehicles', methods=['POST'])
def create_vehicle():
    body = request.get_json()
    if not body:
        abort(400, description="Request body must be JSON")
    required_fields = ['name']
    for field in required_fields:
        if field not in body or not body[field]:
            abort(422, description=f"'{field}' is required")
    existing_name = Vehicle.query.filter_by(name=body['name']).first()
    if existing_name:
        abort(409, description="Name already exists")
    try:
        new_vehicle = Vehicle(name=body["name"],
                        cargo_capacity=body.get("cargo_capacity"),
                        length=body.get("length"),
                        model=body.get("model"))
        db.session.add(new_vehicle)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Internal Server Error :)")
    return jsonify(new_vehicle.serialize()), 201


@app.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle is None:
        abort(404, description=f"Vehicle with ID {vehicle_id} not found")
    body = request.get_json()
    if not body:
        abort(400, description="Request body must be JSON")
    if 'name' in body and body['name'] != vehicle.name:
        existing_name = Vehicle.query.filter_by(name=body['name']).first()
        if existing_name:
            abort(409, description="Name already exists")
    try:
        vehicle.name = body['name']
        vehicle.cargo_capacity = body.get("cargo_capacity")
        vehicle.length = body.get("length")
        vehicle.model = body.get("model")
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Internal Server Error")
    return jsonify(vehicle.serialize()), 200


@app.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle is None:
        abort(404, description=f"Vehicle with ID {vehicle_id} not found")
    try:
        db.session.delete(vehicle)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Internal Server Error")
    return jsonify({"message": f"Vehicle with ID {vehicle_id} has been deleted"}), 200



# ==========================
#     ENDPOINTS DE FAVORITE
# ==========================
@app.route('/favorites', methods=['GET'])
def get_all_favorites():
    favorites = Favorite.query.all()
    favorites_to_json = jsonify([favorite.serialize() for favorite in favorites])
    return favorites_to_json, 200


@app.route('/favorites/<int:favorite_id>', methods=['GET'])
def get_favorite_by_id(favorite_id):
    favorite = Favorite.query.get(favorite_id)
    if favorite is None:
        abort(404, description="Favorite not found")
    favorite_to_json = jsonify(favorite.serialize())
    return favorite_to_json, 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
