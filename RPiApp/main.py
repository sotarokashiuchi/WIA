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
ROTARY_ENCODER_A = 20
ROTARY_ENCODER_B = 21
HOME_BUTTON = 5
MENU_BUTTON = 6
PREVIOUS_BUTTON = 13
DONE_BUTTON = 19
NEXT_BUTTON = 26

SW_ON = 0
SW_OFF = 1

rdr = RFID(pin_rst=25, pin_irq=24, pin_mode=GPIO.BCM)
buzzerPWM = tone.Tone(BUZZER)

def initialize():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LED_RED, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(LED_GREEN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(LED_BLUE, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(ROTARY_ENCODER_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ROTARY_ENCODER_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(MENU_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(NEXT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PREVIOUS_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(DONE_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(HOME_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
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
    rdr.wait_for_tag(1)
    (error, tag_type) = rdr.request()
    if not error:
        (error, uid) = rdr.anticoll()
        if not error:
            return str(uid)

def wait_sw_off(SW):
    while GPIO.input(SW)==SW_ON:
        pass
    return

def menu():
    lcd_menu = [
                    [
                        ">Attendance",
                        " Time  WiFi"
                    ],[
                        " Attendance",
                        ">Time  WiFi"
                    ],[
                        " Attendance",
                        " Time >WiFi"
                    ]
                ]
    lcd_menu_index=0
    while GPIO.input(DONE_BUTTON)!=SW_ON:
        lcd.lcd_string(lcd_menu[lcd_menu_index][0], lcd.LCD_LINE_1)
        lcd.lcd_string(lcd_menu[lcd_menu_index][1], lcd.LCD_LINE_2)
        lcd.lcd_display_on()
        if GPIO.input(HOME_BUTTON)==SW_ON:
            wait_sw_off(HOME_BUTTON)
            return
        if GPIO.input(NEXT_BUTTON)==SW_ON:
            lcd_menu_index=lcd_menu_index+1
            if lcd_menu_index >= 3:
                lcd_menu_index=2
            wait_sw_off(NEXT_BUTTON)
        if GPIO.input(PREVIOUS_BUTTON)==SW_ON:
            lcd_menu_index=lcd_menu_index-1
            if lcd_menu_index < 0:
                lcd_menu_index=0
            wait_sw_off(PREVIOUS_BUTTON)
    
    if lcd_menu_index==0:
        set_attendance()
    elif lcd_menu_index==1:
        set_time()
    elif lcd_menu_index==2:
        get_wifi()

def set_attendance():
    pass

def set_time():
    pass

def get_wifi():
    pass

def main():
    serialNumber = ""
    name = ""
    oldSerialNumber = ""
    oldTimeStanp = 0
    while True:
        if GPIO.input(MENU_BUTTON)==SW_ON:
            menu()

        # NFC読み取り処理
        oldSerialNumber = serialNumber
        oldTimeStanp = time.time()
        serialNumber = readTagUID()
        if oldSerialNumber == serialNumber and time.time()-oldTimeStanp < 0.01:
            time.sleep(0.1)
            continue
        
        name = requestNFCToch(serialNumber)
        lcd.lcd_display_off()
        if name == "":
            # 名前の未登録
            buzzerPWM.beep(440)
            lcd.lcd_string("Warning", lcd.LCD_LINE_1)
            lcd.lcd_string("Not Registered", lcd.LCD_LINE_2)
            lcd.lcd_display_on()
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
            lcd.lcd_display_on()
            GPIO.output(BUZZER, HIGH)
            GPIO.output(LED_BLUE, HIGH)
            time.sleep(0.05)
            buzzerPWM.none()
        
        time.sleep(0.75)
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

