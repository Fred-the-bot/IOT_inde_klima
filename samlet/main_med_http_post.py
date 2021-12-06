from umqtt.simple import MQTTClient
from machine import ADC, Pin
import time
import math 
import dht
import network
import urequests
import ujson
import secret


adc = ADC(Pin(36)) #A4 på esp32
adc.read()
d = dht.DHT11(Pin(4))
time.sleep(2) #der sættes en lille sleep på fra vi initialisere DHT sensoren da det gør systemet mere robust.

i=0
value=0
j=0
x=0

#https://stackoverflow.com/questions/2272149/round-to-5-or-other-number-in-python
def myround(x, base=5):
    return base*round(x/base)

def tabel(j):
    switcher={
        0:'problem med aparat',
        40:'stille visken',
        60:'stille samtale',
        65:'normal samtale',
        70:'støvsuger',
        75:'larmende samtale !OBS! risiko for tinitus ved udsættelse i lang tid',
        80:'høj sang, !OBS! risiko for tinitus ved udsættelse i længere tid',
        85:'bil, !OBS! risiko for tinitus, ved usættelse i 8 timer SKAL der bruges høreværn',
        90:'motorcykel, !OBS! risiko for tinitus, ved usættelse i 2 timer SKAL der bruges høreværn',
        95:'blender, !OBS! risiko for tinitus, ved usættelse i 1 time SKAL der bruges høreværn',
        100:'tog, !OBS! risiko for tinitus, ved udsættelse i 15 minutter SKAL der bruges høreværn',
        }
    return switcher.get(j,'fejl')

#forbinder sig til netværket med vores "hemmelige" wifi navn og "hemmelige" kode
station = network.WLAN(network.STA_IF)
station.active(True)
if not station.isconnected():
    station.connect(secret.ssid, secret.passwd)

SERVER = secret.IP  #  Server Address 



#bruges ikke, men kan tilføjes for at sætte flere enheder på
# apiKeyValue = str("tPmAT5Ab3j7F9")
# sensorName = str("ESP32")
# sensorLocation = str("rum_1")

temp = d.temperature()
hum = d.humidity()

while (i<5):
     value=adc.read()+value
     i=i+1
     time.sleep(0.5)
     if (i==5):
         d.measure()
         temp = d.temperature()
         hum = d.humidity()
         print(temp, "C")
         print(hum, "% Fugt")
         calibration=(0.0596*(value/5)+116.57)/66+65 #kalibreret via 120+ målinger ved ca. 66dB.
         calibration=math.ceil(calibration) #Runder resultatet til nærmeste integer
         volume=myround(calibration) # runder resultatet til nærmeste brugbare værdig til tabellen
         if (volume<50 and volume!=0):
             volume=40
         elif (volume>50 and volume<64):
             volume=60
 
         print(tabel(int(volume))) #print hvad værdien svarer til via vores tabel.
loud=tabel(int(volume))

upload = ujson.dumps({ 'Temp': temp, 'fugt': hum, 'lyd': loud }) #Tager og "omformatere" micropython tekster til brugbar JSON format

#https://techtutorialsx.com/2017/06/18/esp32-esp8266-micropython-http-post-requests/
if station.isconnected():
    print("network config:",station.ifconfig())
    test = urequests.post("https://e36f7ff8-a58d-4076-b0aa-f7ffdc8efaf6.mock.pstmn.io", headers = {'content-type': 'application/json'}, data=upload) #poster vores tekst i formatet (IP,HEADER,DATA)
else:
    print("error, could not connect to the wifi")

