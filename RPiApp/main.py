import RPi.GPIO as GPIO
import requests
import time
import i2clcda as lcd

HIGH = 1
LOW = 0
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
    # test program
    lcd.lcd_string("Created by         <",lcd.LCD_LINE_1)
    lcd.lcd_string("Osoyoo.com        <",lcd.LCD_LINE_2)
    time.sleep(3)

    lcd.lcd_string("> Tutorial Url:",lcd.LCD_LINE_1)
    lcd.lcd_string("> http://osoyoo.com",lcd.LCD_LINE_2)
    time.sleep(3)

    lcd.lcd_string("> ワタシノナマエハ",lcd.LCD_LINE_1)
    lcd.lcd_string("> バビブペピョ",lcd.LCD_LINE_2)
    time.sleep(3)
    return

    serialNumber = ""
    name = ""
    while True:
        # NFC読み取り処理
        if serialNumber == "1":
            if serialNumber != "学生証のデータ形式ではない":
                # 学生証ではない
                lcd.lcd_string("Error", lcd.LCD_LINE_1)
                lcd.lcd_string("Failed to Read", lcd.LCD_LINE_2)
                GPIO.output(BUZZER, HIGH)
                GPIO.output(LED_RED, LOW)
            else:
                name = requestNFCToch(serialNumber)
                if name == "":
                    # 名前の未登録
                    lcd.lcd_string("Warning", lcd.LCD_LINE_1)
                    lcd.lcd_string("Not Registered", lcd.LCD_LINE_2)
                    GPIO.output(BUZZER, HIGH)
                    GPIO.output(LED_BLUE, HIGH)
                else:
                    # 正常処理
                    lcd.lcd_string("Completed!", lcd.LCD_LINE_1)
                    lcd.lcd_string(name, lcd.LCD_LINE_2)
                    GPIO.output(BUZZER, HIGH)
                    GPIO.output(LED_GREEN, HIGH)
            
            time.sleep(0.5)
            GPIO.output(LED_GREEN, LOW)
            GPIO.output(LED_BLUE, LOW)
            GPIO.output(LED_RED, LOW)
            GPIO.output(BUZZER, LOW)
            lcd.lcd_init()
    return

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        finalize()

