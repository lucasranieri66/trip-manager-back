import pymongo
import json
from flask import Flask, Response, request
from flask_cors import CORS, cross_origin
# from pymongo.common import SERVER_SELECTION_TIMEOUT

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

try:
    mongo = pymongo.MongoClient(
        host='localhost', 
        port=27017, 
        serverSelectionTimeoutMS=1000
    )
    db = mongo.trip_manager
    mongo.server_info() #ativa exceção se não conectar
except:
    print('error: cannont connect to the db.')


###################################
@app.route('/agent', methods=['POST'])
@cross_origin()
def create_agent():
    try:
        data = json.loads(request.data)
        agent = {
            "username": data["username"], 
            "firstname": data["firstname"],
            "lastName": data["lastname"],
            "password": data["password"],
            "email": data["email"],
            "company": data["company"],
        }
        dbResponse = db.agent.insert_one(agent)
        return Response(
            response = json.dumps({"message": "user created", "id": f'{dbResponse.inserted_id}'}),
            status = 200,
            mimetype = "application/json",
        )
    except Exception as ex:
        print(ex)

@app.route('/traveller', methods=['POST'])
@cross_origin()
def create_agent():
    try:
        data = json.loads(request.data)
        traveller = {
            "username": data["username"], 
            "firstname": data["firstname"],
            "lastName": data["lastname"],
            "password": data["password"],
            "email": data["email"]
        }
        dbResponse = db.traveller.insert_one(traveller)
        return Response(
            response = json.dumps({"message": "user created", "id": f'{dbResponse.inserted_id}'}),
            status = 200,
            mimetype = "application/json",
        )
    except Exception as ex:
        print(ex)

###################################
if __name__ == '__main__':
    app.run(port=3333, debug=True)
