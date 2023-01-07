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
from models import db, User, People, Fav_People
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
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

@app.route('/user', methods=['GET'])
def handle_hello():

    all_users = User.query.all()
    new_users = []
    for i in range(len(all_users)):
        print(all_users[i])
        new_users.append(all_users[i].serialize())

    return jsonify(new_users), 200

@app.route("/user/<int:id>", methods= ['GET'])
def one_user(id):
    one = User.query.get(id) 
    if(one is None):
        return "el user no existe"
    else:
        return jsonify(one.serialize())

@app.route("/one/<correo>", methods= ['GET'])
def one_user_mail(correo):
    one = User.query.filter_by(email=correo).first()
    if(one is None):
        return "el user no existe"
    else:
        return jsonify(one.serialize())

@app.route("/user", methods=['POST'])
def new_user():
   
    body = request.get_json()
    print(body)
    if( "email" not in body):
        return "falta email"
    if( "password" not in body):
        return "falta password"

    user = User.query.filter_by(email= body['email']).first()
    if(user):
        return "no puedo registrar  con este mail"

    nuevo = User()
    nuevo.email = body["email"]
    nuevo.password = body["password"]
    nuevo.is_active = True

    db.session.add(nuevo)
    db.session.commit()

    return "ok"

@app.route("/user/<int:id>", methods=['DELETE'])
def delete(id):
    user = User.query.get(id)
    if(user):
        db.session.delete(user)
        db.session.commit()
        return "user eliminado"
    else:
        return "user no existe"










@app.route("/people", methods=["GET"])
def get_all_people():

    return jsonify({
        "mensaje": "aca estaran todos los personajes"
    })

@app.route("/people/<int:id>", methods=["GET"])
def get_one_people(id):

    return jsonify({
        "mensaje": "aca estara la info del personaje con id "+str(id)
    })

@app.route("/favorite/planet/<int:planet_id>", methods=['POST'])
def post_fav_planet(planet_id):
    
    return jsonify({
        "mensaje": "el planeta con id "+ str(planet_id) + " ha sido agregado"
    })

@app.route("/favorite/planet/<int:planet_id>", methods=['DELETE'])
def delete_fav_planet(planet_id):
    
    return jsonify({
        "mensaje": "el planeta con id "+ str(planet_id) + " ha sido eliminado"
    })



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
