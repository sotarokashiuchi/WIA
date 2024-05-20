import RPi.GPIO as GPIO
import requests
import time
import i2clcda as lcd

LED_GREEN = 22
LED_RED = 27
LED_BLUE = 23
BUZZER = 12

def initialize():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_RED, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(LED_GREEN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(LED_BLUE, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(BUZZER, GPIO.OUT, initial=GPIO.LOW)
    lcd.lcd_init()

def finalize():
    GPIO.cleanup()
    lcd.lcd_byte(0x01, lcd.LCD_CMD)
    return

def requestNFCToch(serialNumber):
    response = requests.post(
            "http://localhost:1234/nfc/touch",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"serialNumber": serialNumber}
    )

    return response.json()["name"]


def main():
    # print(requestNFCToch("1"))
    while True:
        # Send some test
        lcd.lcd_string("Created by         <",lcd.LCD_LINE_1)
        lcd.lcd_string("Osoyoo.com        <",lcd.LCD_LINE_2)

        time.sleep(3)

        # Send some more text
        lcd.lcd_string("> Tutorial Url:",lcd.LCD_LINE_1)
        lcd.lcd_string("> http://osoyoo.com",lcd.LCD_LINE_2)

        time.sleep(3)

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
    return

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        finalize()

