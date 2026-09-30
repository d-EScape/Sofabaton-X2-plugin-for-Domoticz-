# Maps Device/Key combinations send by the Sofabaton MQTT virtual device to
# action names in Domoticz, that will be stored in a Domoticz text device.
# Example:
# {
#   "device_id": 8,
#   "key_id": 1
# }
# from Sofabaton MQTT
# is translated to "MediawandAan"

KEY_CODE={
	8:{
		1:"MediawandAan",
		2:"MediawandUit",
		3:"Rolgordijn omhoog",
		4:"Rolgordijn omlaag",
		5:"Lichtaan",
		6:"Lichtuit"
	},
	9:{
		1:"Example_Task1",
		2:"Example_Task2",
		3:"Example_Task3",
		4:"Example_Task4",
		5:"Example_Task5",
		6:"Example_Task6",
		7:"Example_Task7",
		8:"Example_Task8",
		9:"Example_Task9",
		10:"Example_Task10"
	}

}

# Map remote keys te key_id's
# Found at https://community.home-assistant.io/t/sofabaton-x2-trigger-any-command-on-the-x2-hub-from-home-assistant/969617
ACTIVITY_KEY={
    "ok": 176,
    "back": 179,
    "home": 180,
    "menu": 181,
    "volume_up": 182,
    "volume_down": 185,
    "channel_up": 183,
    "channel_down": 186,
    "mute": 184,
    "guide": 157,
    "rewind": 187,
    "play": 156,
    "fast_forward": 189,
    "dvr": 155,
    "pause": 188,
    "exit": 154,
    "red": 190,
    "green": 191,
    "yellow": 192,
    "blue": 193,
    "a": 153,
    "b": 152,
    "c": 151,
    "onzin": 184,
    "met Spatie": 184,
    }