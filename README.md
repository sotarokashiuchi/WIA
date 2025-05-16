# Setup
```shell
# copy systemd file
cd ACPj/systemd/systemd
sudo cp HttpEcho.service NFCTouch.service /lib/systemd/system/

# start demon
sudo systemctl daemon-reload
sudo systemctl enable NFCTouch.service
sudo systemctl enable HttpEcho.service

# setting shutdown pin
sudo vi /boot/config.txt
# add to /boot/config.txt
dtoverlay=gpio-shutdown,gpio_pin=4,debounce=2000

# reboot
sudo reboot
```

# 部品
| 名称                  | 数量   |
| --------------------- | ------ |
| Raspberry Pi 2B       | 1      |
| M2*5~7                | 8      |
| M2スペーサ            | 4      |
| ピンヘッダ20*2        | 1      |
| RFID-RC522            | 1      |
| M3*9~12               | 4      |
| I2C transport LCD     | 1      |
| M3*12~15              | 4      |
| M3ボルト              | 8      |
| RTC                   | 1      |
| M2*8~11               | 3      |
| M2ボルト              | 3      |
| RotaryEncoder_Switch  | 1      |
| 抵抗 130Ω             | 3      |
| スイッチ              | 5 or 6 |
| LED(RED, BLUE, GREEN) | 3      |
| ブザー                | 1      |
