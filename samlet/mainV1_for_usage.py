#programmet laver en måling hvert 5 minut.
#programmet måler støj i en selvlavet tabel
#det måler varme og fugt
#og laver en HTTP.POST til en server der ligger lokalt i børnehaven
#for at stoppe programmet skal man bare holde knappen der sidder i boksen inde i ca 6 sekunder


from machine import ADC, Pin, reset
import time
import math 
import dht
import network
import urequests
import ujson
import secret
import sys
import ntptime

reset_button = Pin(13)
adc = ADC(Pin(36)) #A4 på esp32
adc.read()
d = dht.DHT11(Pin(4))
red_led = Pin(12, Pin.OUT)
green_led = Pin(27, Pin.OUT)
blue_led = Pin(33, Pin.OUT)
red_led.off()
green_led.off()
blue_led.off()

time.sleep(2) #der sættes en lille sleep på fra vi initialisere DHT sensoren da det gør systemet mere robust.

i=0
value=0
j=0
x=0

red_led.off()
green_led.off()
blue_led.off()

ntptime.host = "1.europe.pool.ntp.org"

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
    time.sleep(5)

SERVER = secret.IP  #  Server Address 



#bruges ikke, men kan tilføjes for at sætte flere enheder på
apiKeyValue = secret.api
sensorName = str("ESP32")
sensorLocation = str("Lokale1")

temp = d.temperature()
hum = d.humidity()

while (i<5):
     if time.localtime()[3]+1>18 or time.localtime()[3]+1<5:
         time.sleep(3600)
         reset()
         
     blue_led.on()
     if (reset_button.value() == 1):
         blue_led.off()
         red_led.on()
         time.sleep(1)
         red_led.off()
         sys.exit()
     value=adc.read()+value
     i=i+1
     time.sleep(0.5)
     if (i==5):
         if not station.isconnected():
             station.connect(secret.ssid, secret.passwd)
             time.sleep(5)
         blue_led.off()
         d.measure()
         temp = d.temperature()
         hum = d.humidity()
         calibration=(0.0596*(value/5)+116.57)/66+65 #kalibreret via 120+ målinger ved ca. 66dB.
         calibration=math.ceil(calibration) #Runder resultatet til nærmeste integer
         volume=myround(calibration) # runder resultatet til nærmeste brugbare værdig til tabellen
         if (volume<50 and volume!=0):
             volume=40
         elif (volume>50 and volume<64):
             volume=60
         loud=tabel(int(volume))
         
         apiKeyValue=str(apiKeyValue)
         sensorName=str(sensorName)
         sensorLocation=str(sensorLocation)
         temp=str(temp)
         hum=str(hum)
         lyd=str(loud)
       
         if station.isconnected():
             green_led.on()
             test = urequests.post(SERVER, headers = {'content-type': 'application/x-www-form-urlencoded'}, data="api_key=" + apiKeyValue + "&sensor=" + sensorName + "&location=" + sensorLocation + "&value1=" + temp + "&value2=" + hum + "&value3=" + loud).json #poster vores tekst i formatet (IP,HEADER,DATA)
             #time.sleep(5)#giver programmet 5 sekunder til at udføre sin POST før forbindelsen lukkes
             ntptime.settime()
             green_led.off()
         else:
             print("ikke forbundet")
             station.connect(secret.ssid, secret.passwd)
         i=0
         while(i<2):
             i=i+1
             if (reset_button.value() == 1):
                  blue_led.off()
                  red_led.on()
                  time.sleep(1)
                  red_led.off()
                  sys.exit()
             time.sleep(6)
         
         
