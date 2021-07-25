# borg

Development board network imager service

## Run

Build and run container on host

```bash
export SERVER_ROOT_IP="192.168.86"
export KICKSTART_IP="192.168.86.65"
sudo bash run.sh
```
## Board setup

### RPI4

1. Setup EEPROM of RPI to boot from the network then SD card. Set the BOOT_ORDER value to 0xf12, which means network->SD card->repeat.
2. Use rest API to setup board by using the serial number
3. Power on board with networking connecting
4. After board powers off disable board through API. Now the board will boot from the SD card with Kuiper.
