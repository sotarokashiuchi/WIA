import RPi.GPIO as GPIO
import time

class Encoder:
    def __init__(self, encoder_a, encoder_b):
        self.counter = 0
        self.AstateOld = 1
        self.BstateOld = 1
        self.RotaryEncoderA = encoder_a
        self.RotaryEncoderB = encoder_b

    def read(self, sleep_time=0.001):
        Astate = GPIO.input(self.RotaryEncoderA)
        Bstate = GPIO.input(self.RotaryEncoderB)

        if Astate == 1 and self.AstateOld == 0:
            self.BstateOld = Bstate

            if self.AstateOld == 0 and self.BstateOld == 0:
                self.counter += 1
            elif self.AstateOld == 0 and self.BstateOld == 1:
                self.counter -= 1

            print("counter  = " + str(self.counter))

        self.AstateOld = Astate
        self.BstateOld = Bstate

        time.sleep(sleep_time)
        return self.counter

    def set(self, value=0):
        self.counter = value