# _____ _____ _____ __ __ _____ _____
# |	 |   __|	 |  |  |	 |	 |
# |  |  |__   |  |  |_   _|  |  |  |  |
# |_____|_____|_____| |_| |_____|_____|
#
# Project Tutorial Url:http://osoyoo.com/?p=1031
#
import smbus
import time
import unicodedata

# | I2C_ADDR | RS (LCD_CHR or LCD_CMD) | D7 D6 D5 D4 E EN R/W RS
#									  | D3 D2 D1 D0 E EN R/W RS

# Define some device parameters
I2C_ADDR = 0x27  # I2C device address, if any error, change this address to 0x3f
LCD_WIDTH = 16  # Maximum characters per line

# Define some device constants
LCD_CHR = 1  # Mode - Sending data
LCD_CMD = 0  # Mode - Sending command

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94  # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4  # LCD RAM address for the 4th line

LCD_BACKLIGHT = 0x08  # On
# LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100  # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Open I2C interface
# bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1


def lcd_init():
	# Initialise display
	lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
	lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
	lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
	lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
	lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
	lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
	time.sleep(E_DELAY)


def lcd_byte(bits, mode):
	# Send byte to data pins
	# bits = the data
	# mode = 1 for data
	#		0 for command

	# D7 D6 D5 D4 LCD_BACKLIGHT _ _ mode
	bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
	# D3 D2 D1 D0 LCD_BACKLIGHT _ _ mode
	bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

	# High bits
	bus.write_byte(I2C_ADDR, bits_high)
	lcd_toggle_enable(bits_high)

	# Low bits
	bus.write_byte(I2C_ADDR, bits_low)
	lcd_toggle_enable(bits_low)


def lcd_toggle_enable(bits):
	# Toggle enable
	time.sleep(E_DELAY)
	# D7 D6 D5 D4 LCD_BACKLIGHT 1 _ mode
	bus.write_byte(I2C_ADDR, (bits | ENABLE))
	time.sleep(E_PULSE)
	# D7 D6 D5 D4 LCD_BACKLIGHT 0 _ mode
	bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
	time.sleep(E_DELAY)


def lcd_string(message, line):
	lcd_byte(line, LCD_CMD)
	i = 0
	j = 0
	while i < LCD_WIDTH:
		j += 1
		if len(message) < j:
			# 余白を空白文字で埋める
			lcd_byte(ord(" "), LCD_CHR)
			i += 1
			continue

		character = message[j]
		if unicodedata.east_asian_width(character) in "Na":
			lcd_byte(ord(character))
			i += 1
			continue
		
		if character in "パピプペポ":
			if character == "パ":
				lcd_byte(0b11001010, LCD_CHR)
			elif character == "ピ":
				lcd_byte(0b11001011, LCD_CHR)
			elif character == "プ":
				lcd_byte(0b11001100, LCD_CHR)
			elif character == "ペ":
				lcd_byte(0b11001101, LCD_CHR)
			elif character == "ポ":
				lcd_byte(0b11001110, LCD_CHR)
			lcd_byte(0b11011111, LCD_CHR)
			i += 2
			continue
	
		if character in "ガギグゲゴザジズゼゾダヂヅデドバビブベボ":
			if character == "ガ":
					lcd_byte(0b10110110, LCD_CHR)
			elif character == "ギ":
				lcd_byte(0b10110111, LCD_CHR)
			elif character == "グ":
				lcd_byte(0b10111000, LCD_CHR)
			elif character == "ゲ":
				lcd_byte(0b10111001, LCD_CHR)
			elif character == "ゴ":
				lcd_byte(0b10111010, LCD_CHR)
			elif character == "ザ":
				lcd_byte(0b10111011, LCD_CHR)
			elif character == "ジ":
				lcd_byte(0b10111100, LCD_CHR)
			elif character == "ズ":
				lcd_byte(0b10111101, LCD_CHR)
			elif character == "ゼ":
				lcd_byte(0b10111110, LCD_CHR)
			elif character == "ゾ":
				lcd_byte(0b10111111, LCD_CHR)
			elif character == "ダ":
				lcd_byte(0b11000000, LCD_CHR)
			elif character == "ヂ":
				lcd_byte(0b11000001, LCD_CHR)
			elif character == "ヅ":
				lcd_byte(0b11000010, LCD_CHR)
			elif character == "デ":
				lcd_byte(0b11000011, LCD_CHR)
			elif character == "ド":
				lcd_byte(0b11000100, LCD_CHR)
			elif character == "バ":
				lcd_byte(0b11001010, LCD_CHR)
			elif character == "ビ":
				lcd_byte(0b11001011, LCD_CHR)
			elif character == "ブ":
				lcd_byte(0b11001100, LCD_CHR)
			elif character == "ベ":
				lcd_byte(0b11001101, LCD_CHR)
			elif character == "ボ":
				lcd_byte(0b11001110, LCD_CHR)
			lcd_byte(0b11011110, LCD_CHR)
			i += 2
			continue
		
		if character in "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワン":
			if character == "ア":
				lcd_byte(0b10110001, LCD_CHR)
			elif character == "イ":
				lcd_byte(0b10110010, LCD_CHR)
			elif character == "ウ":
				lcd_byte(0b10110011, LCD_CHR)
			elif character == "エ":
				lcd_byte(0b10110100, LCD_CHR)
			elif character == "オ":
				lcd_byte(0b10110101, LCD_CHR)
			elif character == "カ":
				lcd_byte(0b10110110, LCD_CHR)
			elif character == "キ":
				lcd_byte(0b10110111, LCD_CHR)
			elif character == "ク":
				lcd_byte(0b10111000, LCD_CHR)
			elif character == "ケ":
				lcd_byte(0b10111001, LCD_CHR)
			elif character == "コ":
				lcd_byte(0b10111010, LCD_CHR)
			elif character == "サ":
				lcd_byte(0b10111011, LCD_CHR)
			elif character == "シ":
				lcd_byte(0b10111100, LCD_CHR)
			elif character == "ス":
				lcd_byte(0b10111101, LCD_CHR)
			elif character == "セ":
				lcd_byte(0b10111110, LCD_CHR)
			elif character == "ソ":
				lcd_byte(0b10111111, LCD_CHR)
			elif character == "タ":
				lcd_byte(0b11000000, LCD_CHR)
			elif character == "チ":
				lcd_byte(0b11000001, LCD_CHR)
			elif character == "ツ":
				lcd_byte(0b11000010, LCD_CHR)
			elif character == "テ":
				lcd_byte(0b11000011, LCD_CHR)
			elif character == "ト":
				lcd_byte(0b11000100, LCD_CHR)
			elif character == "ナ":
				lcd_byte(0b11000101, LCD_CHR)
			elif character == "ニ":
				lcd_byte(0b11000110, LCD_CHR)
			elif character == "ヌ":
				lcd_byte(0b11000111, LCD_CHR)
			elif character == "ネ":
				lcd_byte(0b11001000, LCD_CHR)
			elif character == "ノ":
				lcd_byte(0b11001001, LCD_CHR)
			elif character == "ハ":
				lcd_byte(0b11001010, LCD_CHR)
			elif character == "ヒ":
				lcd_byte(0b11001011, LCD_CHR)
			elif character == "フ":
				lcd_byte(0b11001100, LCD_CHR)
			elif character == "ヘ":
				lcd_byte(0b11001101, LCD_CHR)
			elif character == "ホ":
				lcd_byte(0b11001110, LCD_CHR)
			elif character == "マ":
				lcd_byte(0b11001111, LCD_CHR)
			elif character == "ミ":
				lcd_byte(0b11010000, LCD_CHR)
			elif character == "ム":
				lcd_byte(0b11010001, LCD_CHR)
			elif character == "メ":
				lcd_byte(0b11010010, LCD_CHR)
			elif character == "モ":
				lcd_byte(0b11010011, LCD_CHR)
			elif character == "ヤ":
				lcd_byte(0b11010100, LCD_CHR)
			elif character == "ユ":
				lcd_byte(0b11010101, LCD_CHR)
			elif character == "ヨ":
				lcd_byte(0b11010110, LCD_CHR)
			elif character == "ラ":
				lcd_byte(0b11010111, LCD_CHR)
			elif character == "リ":
				lcd_byte(0b11011000, LCD_CHR)
			elif character == "ル":
				lcd_byte(0b11011001, LCD_CHR)
			elif character == "レ":
				lcd_byte(0b11011010, LCD_CHR)
			elif character == "ロ":
				lcd_byte(0b11011011, LCD_CHR)
			elif character == "ワ":
				lcd_byte(0b11011100, LCD_CHR)
			elif character == "ン":
				lcd_byte(0b11011101, LCD_CHR)
			i += 1
			continue
		
		if character in "ヲァィゥェォャュョッ・":
			if character == "ヲ":
				lcd_byte(0b10100110, LCD_CHR)
			elif character == "ァ":
				lcd_byte(0b10100111, LCD_CHR)
			elif character == "ィ":
				lcd_byte(0b10101000, LCD_CHR)
			elif character == "ゥ":
				lcd_byte(0b10101001, LCD_CHR)
			elif character == "ェ":
				lcd_byte(0b10101010, LCD_CHR)
			elif character == "ォ":
				lcd_byte(0b10101011, LCD_CHR)
			elif character == "ャ":
				lcd_byte(0b10101100, LCD_CHR)
			elif character == "ュ":
				lcd_byte(0b10101101, LCD_CHR)
			elif character == "ョ":
				lcd_byte(0b10101110, LCD_CHR)
			elif character == "ッ":
				lcd_byte(0b10101111, LCD_CHR)
			elif character == "・":
				lcd_byte(0b10100101, LCD_CHR)
			i += 1
			continue
		
		lcd_byte(ord('*'), LCD_CHR)
		i += 1

def main():
	# Main program block

	# Initialise display
	lcd_init()

	while True:

		# Send some test
		lcd_string("Created by		 <", LCD_LINE_1)
		lcd_string("Osoyoo.com		<", LCD_LINE_2)

		time.sleep(3)

		# Send some more text
		lcd_string("> Tutorial Url:", LCD_LINE_1)
		lcd_string("> http://osoyoo.com", LCD_LINE_2)

		time.sleep(3)


if __name__ == "__main__":

	try:
		main()
	except KeyboardInterrupt:
		pass
	finally:
		lcd_byte(0x01, LCD_CMD)
