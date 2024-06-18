import RPi.GPIO as GPIO
import requests
import time
import i2clcda as lcd
from pirc522 import RFID
import tone

HIGH = 1
LOW = 0
LED_GREEN = 22
LED_RED = 27
LED_BLUE = 23
BUZZER = 12

rdr = RFID(pin_rst=25, pin_irq=24, pin_mode=GPIO.BCM)
buzzerPWM = tone.Tone(BUZZER)

def initialize():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LED_RED, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(LED_GREEN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(LED_BLUE, GPIO.OUT, initial=GPIO.LOW)
    lcd.lcd_init()
    lcd.lcd_string("> Completed", lcd.LCD_LINE_1)
    lcd.lcd_string("> Initialize!!", lcd.LCD_LINE_2)

def finalize():
    GPIO.cleanup()
    rdr.cleanup()
    lcd.lcd_byte(0x01, lcd.LCD_CMD)
    buzzerPWM.destroy()
    return

def requestNFCToch(serialNumber):
    response = requests.post(
            "http://localhost:1234/nfc/touch",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"serialNumber": serialNumber}
    )

    return response.json()["name"]

def readTagUID():
    while(True):
        rdr.wait_for_tag()
        (error, tag_type) = rdr.request()
        if not error:
            #print("Tag detected")
            (error, uid) = rdr.anticoll()
            if not error:
                #print("UID: " + str(uid))
                return str(uid)

def main():
    serialNumber = ""
    name = ""
    oldSerialNumber = ""
    oldTimeStanp = 0
    while True:
        # NFC読み取り処理
        oldSerialNumber = serialNumber
        oldTimeStanp = time.time()
        serialNumber = readTagUID()
        if oldSerialNumber == serialNumber and time.time()-oldTimeStanp < 0.01:
            time.sleep(0.1)
            continue
        
        print(serialNumber)
        name = requestNFCToch(serialNumber)
        if name == "":
            # 名前の未登録
            buzzerPWM.beep(440)
            lcd.lcd_string("Warning", lcd.LCD_LINE_1)
            lcd.lcd_string("Not Registered", lcd.LCD_LINE_2)
            GPIO.output(BUZZER, HIGH)
            GPIO.output(LED_RED, HIGH)
            time.sleep(0.05)
            buzzerPWM.none()
        else:
            # 正常処理
            requestNFCToch(serialNumber)
            buzzerPWM.beep(2000)
            lcd.lcd_string("Completed!", lcd.LCD_LINE_1)
            lcd.lcd_string(name, lcd.LCD_LINE_2)
            GPIO.output(BUZZER, HIGH)
            GPIO.output(LED_BLUE, HIGH)
            time.sleep(0.05)
            buzzerPWM.none()
        
        time.sleep(0.35)
        GPIO.output(LED_GREEN, LOW)
        GPIO.output(LED_BLUE, LOW)
        GPIO.output(LED_RED, LOW)
        lcd.lcd_init()
    return

if __name__ == '__main__':
    try:
        initialize()
        main()
    except KeyboardInterrupt:
        pass
    finally:
        finalize()

