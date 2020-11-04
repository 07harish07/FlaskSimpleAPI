from flask import Flask, Response, request
from flask_pymongo import PyMongo
import pymongo
from bson.objectid import ObjectId
import json

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/company"
mongo = PyMongo(app)

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


@app.route("/users", methods=["POST"])
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
