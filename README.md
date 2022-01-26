# sim-stats

This tool was created to log laptimes for various driving sims, and then to show various graphs about the gathered data.

## Contents

## Supported games

**Currently**
- Dirt Rally 2.0

**Planned in the near future**
- Project Cars 2
- Assetto Corsa Competizione

**Planned for later**
- Assetto Corsa
- F1 202X

## Tech-stack


<!-- ---------------------------------------------------------------- -->
# Dirt Rally 2.0

## Notes

As of now the **Rallycross mode is not supported.** It will be added in a future version.

Since the game does not provide the car & track data directly, they need to be inferred from other parts of the UDP data (thanks to https://github.com/ErlerPhilipp/dr2_logger for that ! ).
However in the case of a couple of cars they can't be indentified uniquely based on those data.
**This means that if you set the car to "AUTO-DETECT" it can result in a bad configuration.** You can correct it at the end of the run.

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

<!-- ---------------------------------------------------------------- -->
# Special thanks

- **[ErlerPhilipp](https://github.com/ErlerPhilipp)** & **[soong-construction](https://github.com/soong-construction)**, for helping me understand the data structure of Dirt Rally 2.0

# References

## Tech Stack

https://buddy.works/tutorials/building-a-desktop-app-with-electron-and-angular

https://medium.com/red-buffer/integrating-python-flask-backend-with-electron-nodejs-frontend-8ac621d13f72

## Dirt Rally 2 Data Strcture

https://github.com/ErlerPhilipp/dr2_logger

https://github.com/soong-construction/dirt-rally-time-recorder