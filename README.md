# WIA (Who Is Absent)
WIAは、学生証を用いて出席確認を自動化し、手間やミスを削減するための出席管理システムです。パソコンやスマートフォンなど、すべての端末から操作可能で、オフラインで完結するのが特徴です。

## 特徴
- 学生証を利用した出席確認
- 高速かつ正確な一括出席管理
- オフラインで完結（電源さえあれば動作可能）
- Webブラウザから操作可能（端末を問わず）

## 主な機能
- 学生証の登録
- 出席簿の作成と管理
- 出席確認
- 手動入力対応
- CSV形式での出力
- 時刻同期機能
- デーモン化による自動起動
- シャットダウン機能

## システム構成
![](./system_configuration.drawio.svg)

## Setup
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
