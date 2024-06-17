# Setup
```shell
# copy systemd file
cd ACPj/systemd/systemd
sudo cp HttpEcho.service NFCTouch.service /lib/systemd/system/

# start demon
sudo systemctl daemon-reload
sudo systemctl enable NFCTouch.service
sudo systemctl enable HttpEcho.service

# reboot
sudo reboot
```
