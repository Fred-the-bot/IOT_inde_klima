import dht
import machine
import time
d = dht.DHT11(machine.Pin(14))
time.sleep(2)

while True:
    d.measure()
    temp = d.temperature()
    hum = d.humidity()
    print(temp, "C")
    print(hum, "%")
    time.sleep(5)
    print("Måler igen")
