# Dirt Rally 2.0
## Notes
The game does not report the track and car info in the UDP structure. It is possible to infer those from other fields *(see the implementations of [ErlerPhilipp](https://github.com/ErlerPhilipp/dr2_logger) and [soong-construction](https://github.com/soong-construction/dirt-rally-time-recorder)*), however at least currently this functionality is not present in **sim-stats**.

This all means that **you need to manully select the track and car either at the start or at the end of a run**.

## Setup
- Open `C:\\Users\\USERNAME\\Documents\\My Games\\DiRT Rally 2.0\\hardwaresettings\\hardware_settings_config.xml`
- Find the UDP settings, under motion platform
- Set enabled to "True", and extradata to "3" 
```xml
<udp enabled="true" extradata="3" ip="127.0.0.1" port="20777" delay="1" />
```
- You can change the port number to anything you like, but be sure to change the settings for sim-stats as well
  - Open `sim-stats\\settings.json`
  - Set `game_settings.DirtRally2.udp_port` to the same value
```json
{"game_settings": {"DirtRally2": {"udp_port": 20777, "udp_buffer_size": 1024}}}
```

# References
## Tech Stack
https://buddy.works/tutorials/building-a-desktop-app-with-electron-and-angular

https://medium.com/red-buffer/integrating-python-flask-backend-with-electron-nodejs-frontend-8ac621d13f72

## Dirt Rally 2 Data Strcture
https://github.com/ErlerPhilipp/dr2_logger

https://github.com/soong-construction/dirt-rally-time-recorder