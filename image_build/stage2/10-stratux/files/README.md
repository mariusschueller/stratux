# SkyHound

This project is a Python-based system designed to display ADS-B (Automatic Dependent Surveillance-Broadcast) and GPS data on an LCD and OLED displays using a Raspberry Pi. It integrates with a Stratux ADS-B receiver to provide real-time aircraft tracking, GPS location, and attitude information. The system supports multiple display modes, including radar plots, closest aircraft lists, and an attitude indicator.

# Materials

| Part | Notes | Link |
|------|-------|------|
| Raspberry Pi Zero 2 W | With header soldered on | |
| X307 V1.0 | Custom power and USB board from SubTronics | Custom 10 piece prototype run |
| Vilros USB RTL-SDR & ASD-B Receiver | SDR Operating at 1090MHz | [Link](https://vilros.com/products/vilros-usb-rtl-sdr-asd-b-receiver) |
| Vilros USB RTL-SDR & ASD-B Receiver | SDR Operating at 978MHz | [Link](https://vilros.com/products/vilros-usb-rtl-sdr-asd-b-receiver) |
| WaveShare OLED/LCD HAT (A) | Tri-Display with 4 GPIOs | [Link](https://www.waveshare.com/wiki/OLED/LCD_HAT_(A)) |
| M10 USB GPS | Any decent GPS chip will work | [Link](https://www.aliexpress.us/item/2251832795465775.html?spm=a2g0o.productlist.main.11.6e9cVTVFVTVF7Q&algo_pvid=b42262ed-e870-4986-8ef7-cabf1811a23f&algo_exp_id=b42262ed-e870-4986-8ef7-cabf1811a23f-5&pdp_npi=4%40dis%21USD%2116.88%218.44%21%21%2116.88%218.44%21%402103010b17375794570863588e13b2%2112000033493101997%21sea%21US%21934459528%21X&curPageLogUid=fqtEyWCjfE90&utparam-url=scene%3Asearch%7Cquery_from%3A) |
| 16GB Industrial MicroSD card | Using an overlay filesystem to avoid writes | [Link](https://www.amazon.com/dp/B085GL8XBJ?ref=fed_asin_title) |
| Adafruit TDK InvenSense ICM-20948 9-DoF IMU (MPU-9250 Upgrade) - STEMMA QT / Qwiic | Inertial Measurement Unit | [Link](https://www.adafruit.com/product/4554) |
| Adafruit BMP280 I2C or SPI Barometric Pressure & Altitude Sensor - STEMMA QT | Barometric Pressure Sensor | [Link](https://www.adafruit.com/product/2651) |
| SparkFun Qwiic SHIM for Raspberry Pi | I2C bus shim (fits under display hat ribbon cable) | [Link](https://www.sparkfun.com/sparkfun-qwiic-shim-for-raspberry-pi.html) |
| Flexible Qwiic Cable - 50mm | I2C Qwiic cables x 2 | [Link](https://www.sparkfun.com/flexible-qwiic-cable-50mm.html) |
| 40 Pins IDE Extension Flexible Flat Cable for 3.5 Inch IDE Hard | Ribbon cable for display | [Link](https://www.aliexpress.us/item/3256806913387009.html?spm=a2g0o.order_list.order_list_main.5.57491802HvL78J&gatewayAdapt=glo2usa) |
| NooElec ADS-B Discovery 5dBi (High Gain) Antenna Bundle - 1090MHz & 978MHz Antenna Bundle for SMA and MCX-Connected Software Defined Radios (SDRs) | Antenna set for SDRs | [Link](https://www.amazon.com/dp/B01J9DH9U2?ref=fed_asin_title) |


# Set Up

1. **Install Git**:
    ```bash
   sudo apt update
   sudo apt install git
   ```

2. **Set Up Git**:

   Hit enter through prompts
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

   <br>

   Then
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

   <br>

   Copy and paste following output and give any title into [GitHub New SSH](https://github.com/settings/ssh/new)
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

   <br>

   Back on the pi
   ```bash
   ssh -T git@github.com
   ```

   <br>

   Clone Repository
   ```bash
   sudo GIT_SSH_COMMAND="ssh -i $HOME/.ssh/id_ed25519" git clone git@github.com:sellenberg/Skyhound.git
   ```

   <br>

   Set git global config
   ```bash
   sudo git config --global user.name "NAME"
   sudo git config --global user.email "your_email@example.com"   
   ```

   Key root configuration
   ```bash
   sudo mkdir -p /root/.ssh
   sudo cp ~/.ssh/id_ed25519 /root/.ssh/
   sudo cp ~/.ssh/id_ed25519.pub /root/.ssh/
   sudo chmod 600 /root/.ssh/id_ed25519
   ```

4. **Skyhound File Set Up**:

   Copy .service files to /etc/systemd/system/
   ```bash
   sudo cp /boot/firmware/Skyhound/*.service /etc/systemd/system/
   ```

   <br>

   Libraries to import
   ```bash
   sudo apt update
   sudo apt install python3-websocket
   sudo apt install python3-websockets
   sudo apt install python3-luma.lcd
   ```

   Enable Systems
   ```bash
   sudo systemctl enable stratux_2LCD-ADSB.service
   sudo systemctl enable stratux_wswrite.service
   sudo systemctl enable auto_update.service
   ```

   Reboot to automatically launch
   ```bash
   sudo reboot
   ```

3. **General Workflow**:
   ```bash
   cd /boot/firmware/Skyhound
   sudo git pull
   sudo git add
   sudo git status
   sudo git commit -m "comment"
   sudo git push
   ```


The program should now be running automatically
