from flask import Flask, Response, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from passlib.hash import sha256_crypt
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
import bcrypt
from bson.objectid import ObjectId
import json

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/company"
mongo = PyMongo(app)

jwt = JWTManager(app)

app.config["JWT_SECRET_KEY"] = "Dev-Harish-secret-key"

# try:
#     mongo = pymongo.MongoClient(
#         host="localhost",
#         port="27017",
#         # serverSelectionTimeoutMS = 1000
#     )
#     db = mongo.company 
#     mongo.server_info()
# except:
#     print("ERROR - Cannot connect to db")

@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    # test = User.query.filter_by(email=email).first()
    test = mongo.db.authuser.find_one({"email": email})
    if test:
        return jsonify(message="User Already Exist"), 409
    else:
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        # password = request.form["password"]
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        user_info = dict(first_name=first_name, last_name=last_name, email=email, password=password)
        # user_info = dict(first_name=first_name, last_name=last_name, email=email, password=generate_password_hash(password))
        mongo.db.authuser.insert_one(user_info)
        return jsonify(message="User added sucessfully"), 201

@app.route("/login", methods=["POST"])
def login():
    if request.is_json:
        email = request.json["email"]
        password = request.json['password'].encode('utf-8')
    else:
        email = request.form["email"]
        password = request.form['password'].encode('utf-8')

    login_user = mongo.db.authuser.find_one({"email": email})
    if login_user:
        if bcrypt.hashpw(password, login_user['password']) == login_user['password']:
            access_token = create_access_token(identity=email)
            return jsonify(message="Login Succeeded!", access_token=access_token), 201
    else:
        return jsonify(message="Bad Email or Password"), 401

@app.route("/users/create", methods=["POST"])
@jwt_required
def create_user():
    try:
        if request.method == "POST":
            user = {"name":request.form['name'], "lastname":request.form['lastname']}
            dbResponse = mongo.db.users.insert_one(user)
            return Response(
                response= json.dumps(
                    {"message":"User created", 
                    "id":f"{dbResponse.inserted_id}",
                    "name":user['name'],
                    "lastname":user['lastname']
                    }),
                status=200,
                mimetype="application/json"
            )
    except Exception as ex:
        return 'ex'


@app.route("/users/list", methods=["GET"])
@jwt_required
def users_list():
    try:
        data = list(mongo.db.users.find())
        for user in data:
            user['_id'] = str(user['_id'])
        return Response(
            response= json.dumps(data),
            status=200,
            mimetype="application/json"
        )
    except Exception as ex:
        return Response(
            response= json.dumps(
                {"message":"cannot read users"}),
            status=500,
            mimetype="application/json"
        )


@app.route("/users/<id>", methods=["GET"])
@jwt_required
def user(id):
    try:
        data = list(mongo.db.users.find({"_id":ObjectId(id)}))
        for user in data:
            user['_id'] = str(user['_id'])
        return Response(
            response= json.dumps(data),
            status=200,
            mimetype="application/json"
        )
    except Exception as ex:
        return Response(
            response= json.dumps(
                {"message":"cannot read user"}),
            status=500,
            mimetype="application/json"
        )



@app.route("/users/update/<id>", methods=["PUT"])
@jwt_required
def user_update(id):
    try:
        if request.method == "PUT":
            dbResponse = mongo.db.users.update_one(
                {"_id":ObjectId(id)},
                {"$set":{"name":request.form["name"],
                        "lastname":request.form["lastname"]}}
                )
            if dbResponse.modified_count == 1:
                return Response(
                    response= json.dumps(
                        {"message":"user updated successfully"}),
                    status=200,
                    mimetype="application/json"
                )
            else:            
                return Response(
                    response= json.dumps(
                        {"message":"Nothing to update"}),
                    status=200,
                    mimetype="application/json"
                )
    except Exception as ex:
        return Response(
            response= json.dumps(
                {"message":"Sorry cannot update user"}),
            status=500,
            mimetype="application/json"
        )


@app.route("/users/delete/<id>", methods=["DELETE"])
@jwt_required
def user_delete(id):
    try:
        if request.method == "DELETE":
            dbResponse = mongo.db.users.delete_one({"_id":ObjectId(id)})
            return Response(
                response= json.dumps({"message":"user deleted successfully", "id":f"{id}"}),
                status=200,
                mimetype="application/json"
            )
        
    except Exception as ex:
        return Response(
            response= json.dumps(
                {"message":"Sorry cannot delete user"}),
            status=500,
            mimetype="application/json"
        )


if __name__ == "__main__":
    app.run(debug=True)
