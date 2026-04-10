import time
import network
import ubinascii
from machine import unique_id, Pin
from umqtt.simple import MQTTClient
import dht
import ssl 

from machine import ADC
air_sensor = ADC(Pin(34))
air_sensor.atten(ADC.ATTN_11DB)
air_sensor.width(ADC.WIDTH_12BIT)

light_sensor = ADC(Pin(35))
light_sensor.atten(ADC.ATTN_11DB)
light_sensor.width(ADC.WIDTH_12BIT)




WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

MQTT_BROKER = "your-broker"
MQTT_PORT = 8883
KEEPALIVE = 60
MQTT_USER = "your user name"
MQTT_PASS = "your pwd"
SSL_PARAMS = {"server_hostname": MQTT_BROKER} #bach i3rf tls chmen server 

TOPIC_TEMP = b"hospital/operatingroom1/temperature"
TOPIC_HUM  = b"hospital/operatingroom1/humidity"
TOPIC_AIR  = b"hospital/operatingroom1/airquality"
TOPIC_MOTION = b"hospital/operatingroom1/motion"
TOPIC_LIGHT = b"hospital/operatingroom1/light" 

CLIENT_ID = b"esp32-" + ubinascii.hexlify(unique_id())

sensor = dht.DHT22(Pin(15))  

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(0.2)
    print("WiFi OK:", wlan.ifconfig()[0])

def mqtt_connect():
    print("Connecting to MQTT...")
    c = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT,user = MQTT_USER , password = MQTT_PASS, keepalive=KEEPALIVE , ssl = True,ssl_params =SSL_PARAMS)
    c.connect()
    print("MQTT OK")
    return c

wifi_connect()
client = mqtt_connect()

pir = Pin(13, Pin.IN)

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()        
        motion = pir.value()
        air_ADC_VALUE = air_sensor.read()
        light_raw = light_sensor.read()
        client.publish(TOPIC_LIGHT,str(light_raw).encode(),qos=1)
        client.publish(TOPIC_MOTION,str(motion).encode(),qos=1)
        client.publish(TOPIC_AIR,str(air_ADC_VALUE).encode(), qos=1)
        client.publish(TOPIC_TEMP, str(temp).encode(), qos=1)
        client.publish(TOPIC_HUM,  str(hum).encode(), qos=1)

        print("Temp:", temp, "Hum:", hum , "Air(raw):", air_ADC_VALUE,"Motion:", motion , "Light(raw):", light_raw)
    except Exception as e:
        print("Sensor read failed:", e)


    time.sleep(5)
