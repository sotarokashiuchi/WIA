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
