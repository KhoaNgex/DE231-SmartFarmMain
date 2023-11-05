import paho.mqtt.client as paho
import datetime
from pymongo import MongoClient
import json

USERNAME = 'khoandahp'
PASSWORD = '10042002'
appClient = MongoClient(mongo_cluster_uri)
appDB = appClient['de_smartfarming']

def on_connect(client, userdata, flags, rc):
    print('CONNACK received with code %d.' % (rc))
    
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    topic = msg.topic
    sensor_data = msg.payload
    try:
        nodeID = "node"+topic.split("-")[-1]
        new_data = parse_data(sensor_data)
        new_data["node_id"] = nodeID
        new_data["timestamp"] = datetime.datetime.now()
        connect_and_insert_data("SensorData", new_data)
        print("Inserted.")
    except Exception as error:
        print('Caught this error: ' + repr(error))

def parse_data(byte_data):
    json_string = byte_data.decode('utf-8')
    parsed_data = json.loads(json_string)
    return parsed_data

def connect_and_insert_data(collection_name, data_to_insert):
    collection = appDB[collection_name]
    try:
        # Insert data into the collection
        result = collection.insert_one(data_to_insert)
        print(f"Data inserted with ObjectId: {result.inserted_id}")
    except Exception as e:
        print(f"Error inserting data: {str(e)}")

client = paho.Client()
client.on_subscribe = on_subscribe
client.on_message = on_message
client.username_pw_set(USERNAME, PASSWORD)
client.connect('broker.mqttdashboard.com')
client.subscribe('weather-node-1', qos=2)
client.loop_forever()