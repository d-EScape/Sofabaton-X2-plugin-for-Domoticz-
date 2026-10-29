# KEY_CODE maps the device_id and key_id send by Sofabaton X2 mqtt integration to
# sensible command names in Domoticz. It must be edited to reflect your configuration. The
# X2 creates a device_id for every mqtt integration you add and key_id's for every
# Custom remote button you add to that device. 
# The received commands show up as a value of the "Sofabaton MQTT Receiver" device in Domoticz.
#
# Example:
# {
#   "device_id": 8,
#   "key_id": 2
# }
# from Sofabaton MQTT is translated to "Licht uit" in the example below.
#
# If a name is not configured for the device/key combination then the Domoticz device will 
# receive the keypress as "{device_id}_{key_id}", (e.g. 8_2)
KEY_CODE={
	8:{
		1:"Licht aan",
		2:"Licht uit",
		3:"Licht dimmer",
		4:"Licht feller",
		5:"LichtScene CloudyDay",
		6:"LichtScene Movie",
		7:"Rolgordijn lager",
		8:"Rolgordijn hoger",
		9:"Mediawand aan",
		10:"Mediawand uit",
		11:"Airco aan",
		12:"Airco uit",
		13:"Tuin licht aan",
		14:"Tuin licht uit",
		15:"Eettafel dimmer",
		16:"Eettafel feller",
		17:"Alles uit",
	}
}

# You should NOT need to edit the ACTIVITY_KEY dictionary. These codes seem to be
# the standard codes for the hardware buttons on the remote.
# ACTIVITY_KEY maps sensible command names in Domoticz to the key_id's of the Sofabaton X2
# Found at https://github.com/yomonpet/ha-sofabaton-hub/blob/main/custom_components/sofabaton_hub/const.py
ACTIVITY_KEY={
	"up": 174,
	"down": 178,
	"left": 175,
	"right": 177,
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
    "c": 151
    }