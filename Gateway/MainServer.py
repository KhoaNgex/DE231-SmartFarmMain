import paho.mqtt.client as paho
import pymongo
from datetime import datetime
import json
import threading
import pickle
import logging
import time

def parse_data(byte_data):
    json_string = byte_data.decode('utf-8')
    parsed_data = json.loads(json_string)
    return parsed_data

MONGO_URI = "mongodb+srv://khoawithexceptional:10042002@cluster0.x3hoemg.mongodb.net/?retryWrites=true&w=majority"
MAX_BUFFER_SIZE = 10

# Configure the logger
logging.basicConfig(filename='error_log.txt', level=logging.ERROR)

class SensorDataHandler:
    def __init__(self, mqtt_broker, mqtt_username, mqtt_password, mongo_host, mongo_db):
        self.MQTT_BROKER = mqtt_broker
        self.MQTT_USERNAME = mqtt_username
        self.MQTT_PASSWORD = mqtt_password
        self.MONGO_HOST = mongo_host
        self.MONGO_DB = mongo_db
        self.topics = ['weather-node-1', 'weather-node-2']
        self.nodes = ['node1', 'node2']
        self.collection_name = ['SensorData', 'PumpHistory']
        self.should_exit = False
        with open('model.pkl', 'rb') as model_file:
            self.model = pickle.load(model_file)

        # SET UP CONNECTION TO MQTT BROKER
        self.client = paho.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.MQTT_USERNAME, self.MQTT_PASSWORD)
        self.client.connect(self.MQTT_BROKER)

        # SET UP CONNECTION TO MONGODB
        self.mongo_client = pymongo.MongoClient(self.MONGO_HOST)
        self.mongo_db = self.mongo_client[self.MONGO_DB]

        self.sensor_data_buffers = {node_id:list() for node_id in self.nodes}
        self.pump_data_buffers = {node_id:list() for node_id in self.nodes}
        self.thread_lock = threading.Lock()

    def on_connect(self, client, userdata, flags, rc):
        print('CONNACK received with code %d.' % rc)
    
        # Subscribe to all topics of ESP Nodes
        for topic in self.topics:
            client.subscribe(topic, qos=2)

    def on_message(self, client, userdata, msg):
        pass
    
    def is_valid_data(self, data):
        if 'temp' in data and 'humidity' in data and 'soil' in data and 'light' in data:
            if -50 <= data['temp'] <= 100 \
                and 0 <= data['humidity'] <= 100 \
                and 0 <= data['soil'] <= 100 \
                and 0 <= data['light'] <= 10000:
                return True
        print("Invalid data range.")
        return False

    def check_valid_and_transform_data(self, topic, sensor_data):
        nodeID = "node"+topic.split("-")[-1]
        new_data = parse_data(sensor_data)
        if self.is_valid_data(new_data):
            new_data["node_id"] = nodeID
            new_data["timestamp"] = datetime.now()
            return nodeID, new_data
        return -1, None

    def predict_pump_action(self, data):
        prediction = self.model.predict([[
            data['temp'],
            data['humidity'],
            data['soil'],
            data['light']
        ]])
        return prediction[0]

class BatchProcessingSensorDataHandler(SensorDataHandler):
    def __init__(self, mqtt_broker, mqtt_username, mqtt_password, mongo_host, mongo_db):
        super().__init__(mqtt_broker, mqtt_username, mqtt_password, mongo_host, mongo_db)

    def on_message(self, client, userdata, msg):
        print(f"Received message on topic {msg.topic}")
        topic = msg.topic
        sensor_data = msg.payload
        try:
            esp_node_id, new_data = self.check_valid_and_transform_data(topic, sensor_data)
            if esp_node_id != -1:     
                with self.thread_lock:
                    if esp_node_id in self.sensor_data_buffers:
                        self.sensor_data_buffers[esp_node_id].append(new_data)
                    else:
                        self.sensor_data_buffers[esp_node_id] = [new_data]
                    print(f"Save sensor data to buffer {esp_node_id}.")
                
                # check pump
                try:
                    pump_action = self.predict_pump_action(new_data)
                    pump_topic = 'pump-signal'
                    client.publish(pump_topic, json.dumps({'signal':int(pump_action)}))
                    pump_history_data = {
                        'signal': int(pump_action),
                        'node_id': esp_node_id,
                        "timestamp": datetime.now(),
                    }
                    print(f"Send pump signal to {esp_node_id} successfully.")
                    with self.thread_lock:
                        if esp_node_id in self.pump_data_buffers:
                            self.pump_data_buffers[esp_node_id].append(pump_history_data)
                        else:
                            self.pump_data_buffers[esp_node_id] = [pump_history_data]
                        print(f"Save pump data to buffer {esp_node_id}.")
                except:
                    print(f"Send pump signal to {esp_node_id} failed.")
                
            else:
                error_message = "Invalid data received and discarded."
                print(error_message)
                logging.error(f"{datetime.now()} - {error_message}")
        except Exception as e:
            error_message = f"Failed to process data: {e}"
            print(error_message)
            logging.error(f"{datetime.now()} - {error_message}")
            
    def insert_sensor_data_to_mongodb(self, esp_node_id, auto):
        with self.thread_lock:
            sensor_data_buffer = self.sensor_data_buffers.get(esp_node_id, [])
            pump_data_buffer = self.pump_data_buffers.get(esp_node_id, [])
        
        # if node buffer is empty, not insert and vice versa
        # reduce overload and bottleneck
        if auto == True:
            condition = sensor_data_buffer
            insert_case = "AUTO"
        else:
            condition = sensor_data_buffer and len(sensor_data_buffer) == MAX_BUFFER_SIZE
            insert_case = "BUFFER LIMIT EXCESS"
        if condition:
            try:
                sensor_collection = self.mongo_db[self.collection_name[0]]
                sensor_collection.insert_many(sensor_data_buffer)
                pump_collection = self.mongo_db[self.collection_name[1]]
                pump_collection.insert_many(pump_data_buffer)
                print(f"{insert_case}: Inserted {len(sensor_data_buffer)}x2 records from ESP Node {esp_node_id} into MongoDB.")
                with self.thread_lock:
                    del self.sensor_data_buffers[esp_node_id]
                    del self.pump_data_buffers[esp_node_id]
            except Exception as e:
                error_message = f"Failed to insert data from ESP Node {esp_node_id} into MongoDB: {e}"
                print(error_message)
                logging.error(f"{datetime.now()} - {error_message}")
        else:
            print(f"{insert_case}: No data in buffer of ESP Node {esp_node_id}.")

    def worker_thread(self, esp_node_id):
        while not self.should_exit:
            time.sleep(5)
            self.insert_sensor_data_to_mongodb(esp_node_id, auto=False)
        else:
            print(f"Stop worker for {esp_node_id}")
    
    def auto_insert_worker(self, esp_node_id):
        while not self.should_exit:
            time.sleep(60)  # Wait for 60 seconds
            self.insert_sensor_data_to_mongodb(esp_node_id, auto=True)
        else:
            print(f"Stop auto worker for {esp_node_id}")

    def start(self):
        worker_threads = []  # Create a list to keep track of worker threads
        auto_insert_threads = []  # Create a list for auto insert threads

        for esp_node_id in self.sensor_data_buffers:
            worker_thread = threading.Thread(target=self.worker_thread, args=(esp_node_id,))
            auto_insert_thread = threading.Thread(target=self.auto_insert_worker, args=(esp_node_id,))
            
            worker_threads.append(worker_thread)  # Add worker threads to the list
            auto_insert_threads.append(auto_insert_thread)  # Add auto insert threads to the list

            worker_thread.start()
            auto_insert_thread.start()
        
        try:
            while not self.should_exit:  # Use a flag to control the loop
                self.client.loop()
        except KeyboardInterrupt:
            print("Received keyboard interrupt. Exiting...")
            self.should_exit = True  # Set the flag to exit the loop

        # Join all the worker threads and auto insert threads
        for worker_thread in worker_threads:
            worker_thread.join()

        for auto_insert_thread in auto_insert_threads:
            auto_insert_thread.join()

        # Cleanup: Insert any remaining data in the buffers before exiting
        for esp_node_id in self.sensor_data_buffers:
            self.insert_sensor_data_to_mongodb(esp_node_id, auto=True)

if __name__ == "__main__":
    batch_processing_handler = BatchProcessingSensorDataHandler(
        mqtt_broker='broker.mqttdashboard.com',
        mqtt_username='khoandahp',
        mqtt_password='10042002',
        mongo_host=MONGO_URI,
        mongo_db='de_smartfarming'
    )

    batch_processing_handler.start()
