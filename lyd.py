from machine import ADC, Pin
import time
import math

adc = ADC(Pin(36)) #A4 på esp32
adc.read()

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



while (i<5):
    value=adc.read()+value
    print(value)
    i=i+1
    time.sleep(0.5)
    if (i==5):
        calibration=(0.0596*(value/5)+116.57)/66+65 #kalibreret via 120+ målinger ved ca. 66dB.
        calibration=math.ceil(calibration) #Runder resultatet til nærmeste integer
        volume=myround(calibration) # runder resultatet til nærmeste brugbare værdig til tabellen
        if (volume<50 and volume!=0):
            volume=40
        elif (volume>50 and volume<64):
            volume=60

        print(tabel(int(volume))) #print hvad værdien svarer til via vores tabel.
    


    
