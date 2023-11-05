import network
import time
from machine import Pin, ADC
import dht
import ujson
import math
from umqtt.simple import MQTTClient

# MQTT Server Parameters
MQTT_CLIENT_ID = "micropython-weather-demo"
MQTT_BROKER    = "broker.mqttdashboard.com"
MQTT_USER      = "khoandahp"
MQTT_PASSWORD  = "10042002"
MQTT_TOPIC     = "weather-node-1"
MQTT_SUBSCRIBE_TOPIC = "pump-signal"

dht22_sensor = dht.DHT22(Pin(15))
soil_adc = ADC(Pin(34))
soil_adc.atten(ADC.ATTN_11DB)  

light_adc = ADC(Pin(35))  
light_adc.atten(ADC.ATTN_11DB)  
rl10 = 50e3     #LDR resistance at 10lux
gamma = 0.7     #log(Ra/Rb) / log(La/Lb) 

#R2 =  R1 * Vout / (Vin - Vout)
def calculate_resistance(adc):
  value = adc.read()  
  voltage_ratio = value / (4095 - value)
  return 10e3 * voltage_ratio

#R = R_10 * (lux / 10) ^ -γ => R10/​R​=(10/lux​)^−γ => R/R10​​=(10/lux​)^γ => (R10​​/R)^(1/γ​)=10/lux​ => lux=10*(R10/R​​)^(1/γ)​
def calculate_lux(resistance):
  return 10 * math.pow(rl10/resistance, 1/gamma)

led = Pin(33, Pin.OUT)

print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Connected!")

print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)

def on_message(topic, msg):
    print("Received message on topic {}: {}".format(topic, msg))
    message_dict = ujson.loads(msg)
    signal_value = int(message_dict["signal"])
    print("Pump signal: " + str(signal_value))
    if signal_value == 1:
      led.on()
    else:
      led.off()


client.set_callback(on_message)

# init
h = -1
t = -1
l = -1
s = -1
prev_weather = ""

while True:
  print("Measuring weather conditions... ", end="")
  dht22_sensor.measure() 
  resistance = calculate_resistance(light_adc)
  light = round(calculate_lux(resistance),1)
  soil = round(soil_adc.read()*100/4095,1)

  # packaging
  message = ujson.dumps({
    "temp": dht22_sensor.temperature(),
    "humidity": dht22_sensor.humidity(),
    "light": light,
    "soil": soil,
  })

  if h != dht22_sensor.humidity() or t != dht22_sensor.temperature() or l != light or s != soil:
    # update
    
    t = dht22_sensor.temperature()
    h = dht22_sensor.humidity()
    l = light
    s = soil
    # update to MQTT topic
    print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC, message))
    client.connect()
    print("Connected!")
    client.subscribe(MQTT_SUBSCRIBE_TOPIC)
    client.publish(MQTT_TOPIC, message)
    time.sleep(1)
    client.check_msg()
    client.disconnect() 
    print("Disconnected!")
    prev_weather = message
  else:
    print("No change")
  time.sleep(1)
