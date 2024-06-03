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
    while True:
        # NFC読み取り処理
        serialNumber = readTagUID()
        print(serialNumber)

        #if serialNumber != "":
        #    if serialNumber != "学生証のデータ形式ではない":
        #        # 学生証ではない
        #        buzzerPWM.beep(440)
        #        lcd.lcd_string("Error", lcd.LCD_LINE_1)
        #        lcd.lcd_string("Failed to Read", lcd.LCD_LINE_2)
        #        GPIO.output(BUZZER, HIGH)
        #        GPIO.output(LED_RED, LOW)

        name = requestNFCToch(serialNumber)
        if name == "":
            # 名前の未登録
            buzzerPWM.beep(440)
            lcd.lcd_string("Warning", lcd.LCD_LINE_1)
            lcd.lcd_string("Not Registered", lcd.LCD_LINE_2)
            GPIO.output(BUZZER, HIGH)
            GPIO.output(LED_BLUE, HIGH)
        else:
            # 正常処理
            requestNFCToch(serialNumber)
            buzzerPWM.beep(770)
            lcd.lcd_string("Completed!", lcd.LCD_LINE_1)
            lcd.lcd_string(name, lcd.LCD_LINE_2)
            GPIO.output(BUZZER, HIGH)
            GPIO.output(LED_GREEN, HIGH)
        
        time.sleep(0.5)
        GPIO.output(LED_GREEN, LOW)
        GPIO.output(LED_BLUE, LOW)
        GPIO.output(LED_RED, LOW)
        buzzerPWM.none()
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

