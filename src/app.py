"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Favorites_People, Favorites_Planets
from sqlalchemy import select, insert, delete
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


@app.route('/people', methods=['GET'])
def get_all_people():
    # Obtenemos la lista de objetos People desde la base de datos
    people_list = db.session.execute(select(People)).scalars().all()
    # Convertimos la lista de objetos a una lista de diccionarios usando map
    return jsonify(list(map(lambda p: p.serialize(), people_list))), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    # .get() busca directamente por el ID (Primary Key)
    person = db.session.get(People, people_id)
    if person is None:
        return jsonify({"msg": "Personaje no encontrado"}), 404
    return jsonify(person.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets_list = db.session.execute(select(Planets)).scalars().all()
    return jsonify(list(map(lambda p: p.serialize(), planets_list))), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = db.session.get(Planets, planet_id)
    if planet is None:
        return jsonify({"msg": "Planeta no encontrado"}), 404
    return jsonify(planet.serialize()), 200


@app.route('/users', methods=['GET'])
def get_users():
    users = db.session.execute(select(User)).scalars().all()
    return jsonify(list(map(lambda p: p.serialize(), users))), 200


@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_all_user_favorites(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    # Usamos map y lambda para procesar ambas listas de favoritos
    return jsonify({
        "planets": list(map(lambda f: f.serialize(), user.fav_planet)),
        "people": list(map(lambda f: f.serialize(), user.fav_people))
    }), 200


@app.route('/users', methods=['POST'])
def create_user():
    # 1. Obtenemos los datos del Body
    data = request.get_json()
    # 2. Instanciamos el modelo directamente con los datos recibidos
    new_user = User(
        email=data["email"],
        username=data["username"],
        password=data["password"],
        firstname=data.get("firstname"),
        lastname=data.get("lastname")
    )
    # 3. Añadimos y guardamos sin comprobación manual
    db.session.add(new_user)
    db.session.commit()
    # 4. Retornamos el resultado serializado
    return jsonify(new_user.serialize()), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_fav_people(user_id, people_id):
    new_favorite = Favorites_People(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"msg": "Personaje favorito añadido"}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_fav_planet(user_id, planet_id):
    new_favorite = Favorites_Planets(user_id=user_id, people_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"msg": "Planeta favorito añadido"}), 201


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_fav_people(favorite_id):
    favorite = db.session.get(Favorites_People, favorite_id)
    if favorite is None:
        return jsonify({"msg": "Favorito no encontrado"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Personaje favorito eliminado"}), 200


@app.route('/favorite/planet/<int:favorite_id>', methods=['DELETE'])
def delete_fav_planet(favorite_id):
    favorite = db.session.get(Favorites_Planets, favorite_id)
    if favorite is None:
        return jsonify({"msg": "Favorito no encontrado"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Planeta favorito eliminado"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
