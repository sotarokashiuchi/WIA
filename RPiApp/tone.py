import RPi.GPIO as GPIO
import time

class Tone:
    # Initialize an instance by specifying PWM pin number
    def __init__(self, pwm_pin):
        GPIO.setup(pwm_pin, GPIO.OUT, initial=GPIO.LOW)
        self.pwm = GPIO.PWM(pwm_pin, 1)
 
    # Beep a tone by specifying frequency and duty
    def beep(self, freq, duty=0.5):
        self.pwm.ChangeFrequency(freq)
        self.pwm.start(duty*100)
    
    # Beep a tone by specifying frequency and duty until duration time
    def beepUntilTime(self, freq, duration, duty=0.5):
        self.beep(freq, duty)
        time.sleep(duration)
        self.none()
 
    def none(self):
        self.pwm.ChangeDutyCycle(0)
                                 
    # Destroy instance by cleaning up pins
    def destroy(self):
        self.none()
        GPIO.cleanup()
