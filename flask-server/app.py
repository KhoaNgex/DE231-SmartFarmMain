from flask import json, json, Flask
from pymongo import MongoClient
from flask import Blueprint, jsonify
from flask_cors import CORS
from configs import MONGO_URI

appClient = MongoClient(MONGO_URI)
appDB = appClient['de_smartfarming']
app = Flask(__name__)
CORS(app, supports_credentials=True)

# model
class FarmNode:
    def __init__(self, node_id, location, latitude, longitude, description=""):
        self.node_id = node_id
        self.location = location
        self.latitude = latitude
        self.longitude = longitude
        self.description = description

    def save(self, db):
        db['FarmNode'].insert_one({
            'node_id': self.node_id,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'description': self.description
        })

    @staticmethod
    def get_all(db):
        return list(db['FarmNode'].find())

class SensorData:
    def __init__(self, humidity, temp, soil, light, node_id, timestamp):
        self.node_id = node_id
        self.humidity = humidity
        self.temp = temp
        self.soil = soil
        self.light = light
        self.timestamp = timestamp

    # def save(self, db):
    #     db['FarmNode'].insert_one({
    #         'node_id': self.node_id,
    #         'location': self.location,
    #         'latitude': self.latitude,
    #         'longitude': self.longitude,
    #         'description': self.description
    #     })

    @staticmethod
    def get_all_from_node(db, node_id):
        return list(db['SensorData'].find({"node_id": node_id}))

class PumpHistoryData:
    def __init__(self, signal, node_id, timestamp):
        self.node_id = node_id
        self.signal = signal
        self.timestamp = timestamp

    # def save(self, db):
    #     db['FarmNode'].insert_one({
    #         'node_id': self.node_id,
    #         'location': self.location,
    #         'latitude': self.latitude,
    #         'longitude': self.longitude,
    #         'description': self.description
    #     })

    @staticmethod
    def get_all_from_node(db, node_id):
        return list(db['PumpHistory'].find({"node_id": node_id}))

# controllers
farmnode_api = Blueprint('farm-node', __name__)
sensor_api = Blueprint('sensor', __name__)
pump_api = Blueprint('pump', __name__)

@farmnode_api.route('/farm-node/get-all', methods=['GET'])
def get_all_farm_node_data():
    farm_node = FarmNode.get_all(appDB)
    for item in farm_node:
        item['_id'] = str(item['_id'])
    return jsonify(farm_node)

@sensor_api.route('/sensor/<string:nodeID>', methods=['GET'])
def get_all_sensor_data_from_node(nodeID):
    data = SensorData.get_all_from_node(appDB, nodeID)
    for item in data:
        item['_id'] = str(item['_id'])
    return jsonify(data)

@pump_api.route('/pump/<string:nodeID>', methods=['GET'])
def get_all_pump_data_from_node(nodeID):
    data = PumpHistoryData.get_all_from_node(appDB, nodeID)
    for item in data:
        item['_id'] = str(item['_id'])
    return jsonify(data)

if __name__ == '__main__':
    app.register_blueprint(farmnode_api)
    app.register_blueprint(sensor_api)
    app.register_blueprint(pump_api)
    app.run(debug=True)
