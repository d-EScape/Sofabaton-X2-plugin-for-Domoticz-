"""
<plugin key="SofabatonX2mqtt" name="Sofabaton X2 MQTT" author="ESCape" version="1.3">
	<description>
	  <H2>Bidirectional Sofabaton X2 MQTT integration for Domoticz.</H2>
	  The Sofabaton X2 offers two different integrations trough MQTT. Both are used by this plugin.<br/>
	  1. The "Connect to Home Assistant (MQTT broker)" that is found under general settings<br/>
	  2. The "Home Assistant remote" that can be added as a device<br/><br/>
	  
	  (1) Manages the activities. 
	  The plugin creates a Domoticz devices for every activities plus a "No activity" device.
	  Control of the activities works both ways.<br/><br/>
	  (1) also has the ability to send key presses to the Sofabaton. In Domoticz a "Sofabaton key senders" 
	  device is created for this purpose. If you set it to a known key name then that key is activated 
	  on the Sofabaton. The known activity keys (physical buttons) are in mqttkeycodes.py.
	  Although the Sofabaton can also send keys to a specific device i have -for now- limited 
	  this functionality to the current activity.<br/><br/>
	  (2) Lets the Sofabaton send prefabricated messages to MQTT. The plugin receives these messages
	  and translates them into a configurable string that is sent to a Domoticz text device.
	  A script can then act on devicechanges and the new value.
	  The translation must be configured in the mqttkeycodes.py KEY_CODE section to match your
	  device_id and the key_id's you created.
	  The Sofabaton sends a device_id and key_id that are generated when adding a key 
	  to the MQTT device in de Sofabaton app. They can not be changed. You can only add and rename
	  keys in the Sofabaton app.<br/><br/>
	  The Sofabaton ID is the Sofabaton hubs mac-adress without colon symbol (9C:13:E1:23:45:6A > 9C13E123456A)
	  <br/>
	</description>
	<params>
		<param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1"/>
		<param field="Port" label="Port" width="300px" required="true" default="1883"/>
		<param field="Username" label="Username" width="300px"/>
		<param field="Password" label="Password" width="300px" default="" password="true"/>
		<param field="Mode1" label="Sofabaton ID" width="300px" default=""/>
		<param field="Mode6" label="Debug" width="75px">
			<options>
				<option label="Verbose" value="Verbose"/>
				<option label="True" value="Debug"/>
				<option label="False" value="Normal" default="true" />
			</options>
		</param>
	</params>
</plugin>
"""
errmsg = ""
import DomoticzEx
import json
from mqtt import MqttClientSH2
from mqttkeycodes import KEY_CODE, ACTIVITY_KEY
from datetime import datetime

DEVID_ACTIVITY = "Sofabaton activity"
DEVID_MQTTCONTROL = "Sofabaton mqttcontrol"
DEVID_KEYSEND = "Sofabaton keysender"

def prepare_activity_unit(unit, name=None):
	DomoticzEx.Debug(f"Preparing Domoticz unit for activity: {unit} - {name}")
	if DEVID_ACTIVITY not in Devices or unit not in Devices[DEVID_ACTIVITY].Units:
		try:
			DomoticzEx.Unit(Name=name, Unit=unit, DeviceID=DEVID_ACTIVITY, TypeName="Switch", Used=1).Create()
		except Exception as e:
			DomoticzEx.Error(f"Failed to create a domoticz device for sofabaton activity {unit}")
			DomoticzEx.Error(str(e))
			return False
		else:
			DomoticzEx.Log(f"Created a domoticz device for sofabaton activity {unit} named {name}")
	return True
	
def set_unit(device, unit, state="On"):
	nValue = 1 if state=="On" else 0
	if Devices[device].Units[unit].sValue != state:
		Devices[device].Units[unit].nValue = nValue
		Devices[device].Units[unit].sValue = state
		Devices[device].Units[unit].Update(Log=True)
				
def update_active(activity=255, state="on"):
	DomoticzEx.Status(f"Switched activity {Devices[DEVID_ACTIVITY].Units[activity].Name} ({activity}) to {state}")
	if activity == 255 or state == "off":
		set_unit(DEVID_ACTIVITY,255,"On") # "No activity" activity unit
		set_unit(DEVID_KEYSEND,1,"Off") # Media controller/mqtt sender device
		for unit in Devices[DEVID_ACTIVITY].Units:
			if unit != 255:
				set_unit(DEVID_ACTIVITY,unit,"Off")
	else:
		set_unit(DEVID_KEYSEND,1,"On")
		for unit in Devices[DEVID_ACTIVITY].Units:
			if unit == activity:
				set_unit(DEVID_ACTIVITY,unit,"On")
			else:
				set_unit(DEVID_ACTIVITY,unit,"Off")
		
def manage_activities(activities=None):
	existing = {}
	active = None
	for activity in activities:
		prepare_activity_unit(unit=activity["activity_id"], name=activity["activity_name"])
		if activity["state"] == "on":
			active = activity["activity_id"]
		existing[activity["activity_id"]]=activity["activity_name"]
	DomoticzEx.Debug(f"Check if activities still exist: {existing}")
	for unit in Devices[DEVID_ACTIVITY].Units:
		if not unit in existing and not unit == 255:
			DomoticzEx.Error(f"Activity seems to be deleted from sofabaton: {unit} - {Devices[DEVID_ACTIVITY].Units[unit].Name}")
	if active:
		update_active(activity=active, state="on")
	else:
		update_active(activity=255, state="off")
	
def current_activity_id():
	for unit in Devices[DEVID_ACTIVITY].Units:
		if Devices[DEVID_ACTIVITY].Units[unit].sValue == "On" and unit < 255:
			return unit
	return False
					
def handle_mqtt_command(commandcode):
	DomoticzEx.Debug(f"Received MQTT command:{commandcode}")
	dev=commandcode["device_id"]
	key=commandcode["key_id"]
	if dev in KEY_CODE and key in KEY_CODE[dev]:
		command = KEY_CODE[dev][key]
	else:
		command = f"{dev}_{key}"
	DomoticzEx.Debug(f"Executing:{command}")
	Devices[DEVID_MQTTCONTROL].Units[1].sValue = command
	Devices[DEVID_MQTTCONTROL].Units[1].Update(Log=True)
	
class BasePlugin:
	mqttClient = None

	def __init__(self):
		return

	def onStart(self):
		DomoticzEx.Heartbeat(30)
		self.debugging = Parameters["Mode6"]
		if self.debugging == "Verbose":
			DomoticzEx.Debugging(2+4+8+16+64)
		if self.debugging == "Debug":
			DomoticzEx.Debugging(2)
			
		self.hubid=Parameters["Mode1"]
		
		if DEVID_MQTTCONTROL not in Devices:
			DomoticzEx.Unit(Name='Sofabaton MQTT Receiver', Unit=1, DeviceID=DEVID_MQTTCONTROL, Type=243, Subtype=19, Used=1).Create()
		if DEVID_KEYSEND not in Devices:
			DomoticzEx.Unit(Name='Sofabaton key sender', Unit=1, DeviceID=DEVID_KEYSEND, Type=244, Subtype=73, Switchtype=17, Used=1).Create()

		# MQTT topic templates (SOURCE https://github.com/yomonpet/ha-sofabaton-hub/blob/main/custom_components/sofabaton_hub/const.py)
		global TOPIC_ACTIVITY_LIST_REQUEST
		global TOPIC_ACTIVITY_LIST_RESPONSE
		global TOPIC_ACTIVITY_CONTROL_UP
		global TOPIC_ACTIVITY_CONTROL_DOWN
		global TOPIC_ACTIVITY_ASSIGNED_KEY_CONTROL
		global TOPIC_MQTT_CONTROL_UP
		global SUBSCRIPTIONS
		TOPIC_ACTIVITY_LIST_REQUEST = f"activity/{self.hubid}/list_request"
		TOPIC_ACTIVITY_LIST_RESPONSE = f"activity/{self.hubid}/list"
		TOPIC_ACTIVITY_CONTROL_UP = f"activity/{self.hubid}/activity_control_up"
		TOPIC_ACTIVITY_CONTROL_DOWN = f"activity/{self.hubid}/activity_control_down"
		TOPIC_ACTIVITY_ASSIGNED_KEY_CONTROL = f"activity/{self.hubid}/keys_control"	
		TOPIC_MQTT_CONTROL_UP = f"{self.hubid}/up"
		SUBSCRIPTIONS = [TOPIC_ACTIVITY_CONTROL_UP,TOPIC_ACTIVITY_LIST_RESPONSE,TOPIC_MQTT_CONTROL_UP]

		self.mqttserveraddress = Parameters["Address"].strip()
		self.mqttserverport = Parameters["Port"].strip()
		self.mqttClient = MqttClientSH2(self.mqttserveraddress, self.mqttserverport, "Domoticz_Sofabaton", self.onMQTTConnected, self.onMQTTDisconnected, self.onMQTTPublish, self.onMQTTSubscribed)

	def checkDevices(self):
		DomoticzEx.Debug("checkDevices called")

	def onStop(self):
		DomoticzEx.Debug("onStop called")
	
	def onCommand(self, DeviceID, Unit, Command, Level, Color):
		DomoticzEx.Debug("onCommand called")
		DomoticzEx.Debug(f"==> Send to Baton device:{DeviceID}, unit:{Unit} command:{Command}")
		if DeviceID == DEVID_ACTIVITY:
			if Unit == 255 and Command == "On":
				payload = {"data": {"activity_id": 255,"state": "off"}}
				update_active(activity=255, state="off") # opportunistically set the Unit states before confirmation from mqtt 
			elif Command == "On":
				payload = {"data": {"activity_id": Unit,"state": "on"}}
				update_active(activity=Unit, state="on")
			else:
				payload = {"data": {"activity_id": Unit,"state": "off"}}
				update_active(activity=Unit, state="off")
			self.mqttClient.publishjson(TOPIC_ACTIVITY_CONTROL_DOWN, payload)
			
		if DeviceID == DEVID_KEYSEND and Command not in ["On", "Off"]:
			current_id = current_activity_id()
			DomoticzEx.Log(f"Keycommand {Command} for {current_id}")
			if current_id and Command in ACTIVITY_KEY:
				payload = {"data": {"activity_id": current_id, "key_id": ACTIVITY_KEY[Command]}}
				DomoticzEx.Debug(f"==> Send {payload} to Sofabaton")
				self.mqttClient.publishjson(TOPIC_ACTIVITY_ASSIGNED_KEY_CONTROL, payload)
			else:
				DomoticzEx.Error(f"No keymapping for {Command} on current activity={current_id}")
		  
	def onConnect(self, Connection, Status, Description):
		if self.mqttClient is not None:
			self.mqttClient.onConnect(Connection, Status, Description)

	def onDisconnect(self, Connection):
		if self.mqttClient is not None:
			self.mqttClient.onDisconnect(Connection)

	def onMessage(self, Connection, Data):
		if self.mqttClient is not None:
			self.mqttClient.onMessage(Connection, Data)

	def onHeartbeat(self):
		DomoticzEx.Debug("Heartbeating...")
		if self.mqttClient is not None:
			try:
				if (self.mqttClient._connection is None) or (not self.mqttClient.isConnected):
					DomoticzEx.Debug("Reconnecting")
					self.mqttClient._open()
				else:
					self.mqttClient.ping()
			except Exception as e:
				DomoticzEx.Error(str(e))

	def onMQTTConnected(self):
		if self.mqttClient is not None:
			self.mqttClient.subscribe(SUBSCRIPTIONS)
		

	def onMQTTDisconnected(self):
		DomoticzEx.Debug("onMQTTDisconnected")

	def onMQTTSubscribed(self):
		DomoticzEx.Debug("onMQTTSubscribed")
		self.mqttClient.publishjson(TOPIC_ACTIVITY_LIST_REQUEST, {"data": "activity_list"})
		
	def onMQTTPublish(self, topic, message):
		DomoticzEx.Debug("onMQTTPublish called")
		DomoticzEx.Debug(f"<== Baton topic:{topic}")
		DomoticzEx.Debug(f"<== Baton msg:{message}")
		if topic == TOPIC_ACTIVITY_CONTROL_UP and "activity_id" in message:
			update_active(activity=message["activity_id"], state=message["state"])
		elif topic == TOPIC_ACTIVITY_LIST_RESPONSE and "data" in message:
			manage_activities(message["data"])
		elif topic == TOPIC_MQTT_CONTROL_UP:
			handle_mqtt_command(message)
				  
global _plugin
_plugin = BasePlugin()

def onStart():
	global _plugin
	_plugin.onStart()

def onStop():
	global _plugin
	_plugin.onStop()

def onConnect(Connection, Status, Description):
	global _plugin
	_plugin.onConnect(Connection, Status, Description)

def onDisconnect(Connection):
	global _plugin
	_plugin.onDisconnect(Connection)

def onMessage(Connection, Data):
	global _plugin
	_plugin.onMessage(Connection, Data)

def onCommand(DeviceID, Unit, Command, Level, Color):
	global _plugin
	_plugin.onCommand(DeviceID, Unit, Command, Level, Color)

def onHeartbeat():
	global _plugin
	_plugin.onHeartbeat()