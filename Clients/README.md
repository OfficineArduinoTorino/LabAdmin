# Labadmin clients
This repo contains example code to interface labadmin with different hardware clients:
- [Arduino MKR1000](https://www.arduino.cc/en/Main/ArduinoMKR1000)
- [Olimex ESP8266-EVB](https://www.olimex.com/Products/IoT/ESP8266-EVB/open-source-hardware)
- [Arduino YUN](https://www.arduino.cc/en/Main/ArduinoBoardYun)
- [Raspberry Pi 3 Model B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)

All clients are basically sending, in different languages and hardwares, the very same POST/GET calls:

As stated in [```views.py```](https://github.com/OfficineArduinoTorino/LabAdmin/blob/master/labadmin/views.py)

## API

### Get user name

Post:
```
<Server>/labadmin/labadmin/nfc/users/
```
Body:
```
{"nfc_id":"*****"}
```

### Start a device

POST:
```
<Server>/labadmin/labadmin/device/use/start/
```
Body:
```
{"nfc_id":"*****"}
```
Headers:
```
Authorization   Token Your_Device_Token
Content-Type    application/json
```

### Stop a device

POST:
```
<Server>/labadmin/labadmin/device/use/stop/
```
Body:
```
{"nfc_id":"*****"}
```
Headers:
```
Authorization   Token Your_Device_Token
Content-Type    application/json
```

### Consume user credits

POST:
```
<Server>/labadmin/labadmin/card/credits/
```
Body:
```
{"nfc_id":"*****" , "amount": -3}
```


### Get user credits

GET:
```
<Server>/labadmin/labadmin/card/credits/?nfc_id=YOUR_NFC_ID
```
