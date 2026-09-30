# Sofabaton X2 plugin for Domoticz
Integrates the Sofabaton X2 MQTT functionality into Domoticz

The Sofabaton X2 offers two different integrations trough MQTT. Both are used by this plugin.
1. The "Connect to Home Assistant (MQTT broker)" that is found under general settings.
2. The "Home Assistant remote" that can be added as a device.

(1) Manages the activities. 
The plugin creates a Domoticz devices for every activities plus a "No activity" device.
Control of the activities works both ways.

(1) also has the ability to send key presses to the Sofabaton. In Domoticz a "Sofabaton key senders" 
device is created for this purpose. If you set it to a known key name then that key is activated on the Sofabaton. The known activity keys (physical buttons) are in mqttkeycodes.py.
Although the Sofabaton can also send keys to a specific device i have -for now- limited this functionality to the current activity.

(2) Lets the Sofabaton send prefabricated messages to MQTT. The plugin receives these messages and translates them into a configurable string that is send to a Domoticz text device.
A script can then act upon devicechanges and the new value.
The translation must be configured in the mqttkeycodes.py KEY_CODE section to match your device_id and the key_id's you created.

The Sofabaton sends a device_id and key_id that are generated when adding a key to the MQTT device in de Sofabaton app. They can not be changed. You can only add and rename keys in the Sofabaton app.

The Sofabaton ID is the Sofabaton hubs mac-adress without colon symbol (9C:13:E1:23:45:6A > 9C13E123456A)
