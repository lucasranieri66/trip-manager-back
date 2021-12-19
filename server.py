import pymongo
import json
from flask import Flask, Response, request
from flask_cors import CORS, cross_origin
from bson.objectid import ObjectId
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


################################### SIGNIN/SIGNUP
@app.route('/agent', methods=['POST'])
@cross_origin()
def create_agent():
    try:
        data = json.loads(request.data)
        agent = {
            "username": data["username"], 
            "firstname": data["firstname"],
            "lastname": data["lastname"],
            "password": data["password"],
            "email": data["email"],
            "company": data["company"],
        }

        #antes de inserir: veriricar se já tem no banco.
        already_exists = db.agent.find_one({"username": agent["username"]}) #username deve ser único
        if already_exists:
            return Response(
                response = json.dumps({"message": "agent already exists."}),
                status = 403,
                mimetype = "application/json"
            )
        dbResponse = db.agent.insert_one(agent)
        
        return Response(
            response = json.dumps({"message": "agent created", "id": f'{dbResponse.inserted_id}'}),
            status = 200,
            mimetype = "application/json",
        )
    except Exception as ex:
        print(ex)
        return Response(
            response = json.dumps({"message": "Erro ao cadastrar agente."}),
            status = 500,
            mimetype = "application/json",
        )

@app.route('/agent-signin', methods=['POST'])
@cross_origin()
def login_agent():
    try:
        data = json.loads(request.data)
        
        #validacao (verificar se existem campos "username" ou passwod)
        agent = {
            "username": data["username"], 
            "password": data["password"]
        }
        dbResponse = list(db.agent.find({"username": agent["username"]}))

        for user in dbResponse:
            user['_id'] = str(user['_id'])

        #validacao (verificar se senhas batem)
        if not dbResponse or dbResponse[0]["password"] != agent["password"]:
            return Response(
                response = json.dumps({"message": 'credenciais invalidas.'}),
                status = 401,
                mimetype = "application/json",
            )

        return Response(
            response = json.dumps({"id": f'{dbResponse[0]["_id"]}'}),
            status = 200,
            mimetype = "application/json",
        )
    except Exception as ex:
        print(ex)
        return Response( response = json.dumps({"message": "cannot find the user."}), status = 500, mimetype = "application/json")

@app.route('/traveller', methods=['POST'])
@cross_origin()
def create_traveller():
    try:
        data = json.loads(request.data)
        traveller = {
            "username": data["username"], 
            "firstname": data["firstname"],
            "lastname": data["lastname"],
            "password": data["password"],
            "email": data["email"]
        }

        #validacao (verificar se usuario ja esta no banco)
        dbResponse = list(db.traveller.find({"username": traveller["username"]}))
        for user in dbResponse:
            user['_id'] = str(user['_id'])
        if dbResponse:
            return Response(
                response = json.dumps({"message": 'usuario ja existe.'}),
                status = 409,
                mimetype = "application/json",
            )

        dbResponse = db.traveller.insert_one(traveller)
        return Response(
            response = json.dumps({"message": "traveller created", "id": f'{dbResponse.inserted_id}'}),
            status = 200,
            mimetype = "application/json",
        )
    except Exception as ex:
        print(ex)
        return Response(
            response = json.dumps({"message": "Erro ao cadastrar viajante."}),
            status = 500,
            mimetype = "application/json",
        )

@app.route('/traveller-signin', methods=['POST'])
@cross_origin()
def login_traveller():
    try:
        data = json.loads(request.data)
        
        #validacao (verificar se existem campos "username" ou passwod)
        traveller = {
            "username": data["username"], 
            "password": data["password"]
        }
        dbResponse = list(db.traveller.find({"username": traveller["username"]}))

        for user in dbResponse:
            user['_id'] = str(user['_id'])

        #validacao (verificar se senhas batem)
        if not dbResponse or dbResponse[0]["password"] != traveller["password"]:
            return Response(
                response = json.dumps({"message": 'credenciais invalidas.'}),
                status = 401,
                mimetype = "application/json",
            )

        return Response(
            response = json.dumps({"id": f'{dbResponse[0]["_id"]}'}),
            status = 200,
            mimetype = "application/json",
        )
    except Exception as ex:
        print(ex)
        return Response( response = json.dumps({"message": "cannot find the user."}), status = 500, mimetype = "application/json")

################################### SERVICES

@app.route('/agent-create-package', methods=['POST'])
@cross_origin()
def create_package():
    try:
        data = json.loads(request.data)
        #validacao (verificar se existem campos "username" ou passwod) - se estiver errado, gera status 400
        package = data["trip"]
        city = package["country"]["city"]

        #validacao (verificar se usuario ja esta no banco)
        dbResponseAgent = list(db.agent.find({"username": package["agent"]}))
        dbResponseTraveller = list(db.traveller.find({"username": package["traveller"]}))
        if not (bool(dbResponseAgent) and bool(dbResponseTraveller)):
            return Response(
                response = json.dumps({"message": 'agente ou viajante nao existe.'}),
                status = 409,
                mimetype = "application/json",
            )

        country = [
            {
                "name": package["country"]["name"],
                "city": [
                    {
                        "name": city["name"],
                        "restaurant": city["restaurant"],
                        "hotel": city["hotel"],
                        "tourism": city["tourism"],
                        "leisure": city["leisure"]
                    }
                ]
            }
        ]
        trip = {
            "trip":
            {
                "agent": package["agent"], 
                "traveller": package["traveller"],
                "country": country,
                "status": "ongoing" #ongoing/finished 
            }
        }

        dbResponse = db.trip_package.insert_one(trip)
        return Response(
            response = json.dumps({"message": "trip created", "id": f'{dbResponse.inserted_id}'}),
            status = 200,
            mimetype = "application/json",
        )
    except Exception as ex:
        print(ex)
        return Response( response = json.dumps({"message": "requisicao de pacote invalida."}), status = 400, mimetype = "application/json")

@app.route('/agent-trips/<string:id>', methods=['GET'])
@cross_origin()
def agent_trips(id):
    try:
        dbResponseAgent = list(db.agent.find({"_id": ObjectId(str(id))}))
        if not dbResponseAgent:
            return Response(
                response = json.dumps({"message": 'agente nao existe.'}),
                status = 409,
                mimetype = "application/json",
            )
        username = dbResponseAgent[0]["username"]
        trips = get_trips(username, agent=True)

        return Response(
            response = json.dumps(trips),
            status = 200,
            mimetype = "application/json",
        )
    except Exception as ex:
        print(ex)
        return Response( response = json.dumps({"message": "erro ao recuperar viajens do agente."}), status = 500, mimetype = "application/json")

@app.route('/traveller-trips/<string:id>', methods=['GET'])
@cross_origin()
def traveller_trips(id):
    try:
        dbResponseTraveller = list(db.traveller.find({"_id": ObjectId(str(id))}))
        if not dbResponseTraveller:
            return Response(
                response = json.dumps({"message": 'viajante nao existe.'}),
                status = 409,
                mimetype = "application/json",
            )
        
        username = dbResponseTraveller[0]["username"]
        trips = get_trips(username, agent=False)

        return Response(
            response = json.dumps(trips),
            status = 200,
            mimetype = "application/json",
        )
    except Exception as ex:
        print(ex)
        return Response( response = json.dumps({"message": "erro ao recuperar viajens do viajante."}), status = 500, mimetype = "application/json")

@app.route('/user-type/<string:id>', methods=['GET'])
@cross_origin()
def user_type(id):
    try:
        dbResponseTraveller = list(db.traveller.find({"_id": ObjectId(str(id))}))
        if dbResponseTraveller:
            return Response(
                response = json.dumps({"id": "traveller"}),
                status = 200,
                mimetype = "application/json",
            )
        
        dbResponseAgent = list(db.agent.find({"_id": ObjectId(str(id))}))
        if dbResponseAgent:
            return Response(
                response = json.dumps({"id": "agent"}),
                status = 200,
                mimetype = "application/json",
            )

        return Response(
            response = json.dumps({"message": "not found"}),
            status = 409,
            mimetype = "application/json",
        )
    except Exception as ex:
        print(ex)
        return Response( response = json.dumps({"message": "erro ao recuperar usuario."}), status = 500, mimetype = "application/json")


def get_trips(username, agent):

    if agent: trips = list(db.trip_package.find({"trip.agent": username}))
    else: trips = list(db.trip_package.find({"trip.traveller": username}))

    for trip in trips:
        trip['_id'] = str(trip['_id'])
  
    return trips

# @app.route('/agent-username/<string:id>', methods=['GET'])
# @cross_origin()
# def agent_username(id):
#     try:
#         dbResponseAgent = list(db.agent.find({"_id": ObjectId(str(id))}))
#         if not dbResponseAgent:
#             return Response(
#                 response = json.dumps({"message": 'agente nao encontrado.'}),
#                 status = 409,
#                 mimetype = "application/json",
#             )
#         for user in dbResponseAgent:
#             user['_id'] = str(user['_id'])

#         return Response(
#             response = json.dumps({"username": f'{dbResponseAgent[0]["username"]}'}),
#             status = 200,
#             mimetype = "application/json",
#         )

#     except Exception as ex:
#         return Response( response = json.dumps({"message": "erro ao recuperar viajens do agente."}), status = 500, mimetype = "application/json")


###################################
if __name__ == '__main__':
    app.run(port=3333, debug=True)
