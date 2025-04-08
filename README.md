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

# Remote Desktop
1. ラズベリーパイとパソコンをEthernetケーブルで接続する
2. パソコンの有線ケーブルに静的IPアドレス`169.254.26.5`, マスクを`255.255.255.0`を割り当てる
3. SSH接続(Tera Term 5を使うと良い)または、RDP接続(windowsならmstscを LinuxならRemminaを使うと良い)を行う
   - ラズベリーパイのIPアドレス`169.254.26.30`
   - Username denki
   - Password password
