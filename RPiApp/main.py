import RPi.GPIO as GPIO
import requests
import time

LED_GREEN = 22
LED_RED = 27
LED_BLUE = 23
BUZZER = 12


def requestNFCToch(serialNumber):
    response = requests.post(
            "http://localhost:1234/nfc/touch",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"serialNumber": serialNumber}
    )

    return response.json()["name"]

# print(requestNFCToch("1"))

# initializetion
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_RED, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_GREEN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_BLUE, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(BUZZER, GPIO.OUT, initial=GPIO.LOW)

for i in range(3):
    print("hi")
    GPIO.output(LED_GREEN, 1)
    GPIO.output(LED_RED, 1)
    GPIO.output(LED_BLUE, 1)
    GPIO.output(BUZZER, 1)
    time.sleep(0.5)
    GPIO.output(LED_GREEN,0)
    GPIO.output(LED_RED,0)
    GPIO.output(LED_BLUE,0)
    GPIO.output(BUZZER, 0)
    time.sleep(0.5)

GPIO.cleanup()

           