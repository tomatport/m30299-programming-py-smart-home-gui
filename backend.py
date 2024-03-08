class SmartDevice:
	"""
		Super class for all smart devices
	"""
	def __init__(self):
		self.switchedOn = False

	def toggleSwitch(self):
		self.switchedOn = not self.switchedOn

	def getSwitchedOn(self):
		return self.switchedOn

class SmartPlug():
	def __init__(self, consumptionRate=0):
		self.switchedOn = False

		if consumptionRate < 0 or consumptionRate > 150:
			raise ValueError("Consumption rate must be between 0 and 150")
		
		self.consumptionRate = consumptionRate

	def toggleSwitch(self):
		self.switchedOn = not self.switchedOn

	def getSwitchedOn(self):
		return self.switchedOn

	def getConsumptionRate(self):
		return self.consumptionRate

	def setConsumptionRate(self, consumptionRate):
		if consumptionRate < 0 or consumptionRate > 150:
			raise ValueError("Consumption rate must be between 0 and 150")
		else:
			self.consumptionRate = consumptionRate

	def __str__(self):
		out = "SmartPlug:"
		out += f" switched on: {self.getSwitchedOn()}"
		out += f", comp. rate: {self.getConsumptionRate()}"
		return out
	

class SmartDoorbell():
	def __init__(self):
		self.switchedOn = False
		self.sleepMode = False

	def toggleSwitch(self):
		self.switchedOn = not self.switchedOn

	def getSwitchedOn(self):
		return self.switchedOn

	def getSleep(self):
		return self.sleepMode
	
	def setSleep(self, sleepMode):
		if sleepMode == True or sleepMode == False:
			self.sleepMode = sleepMode
		else:
			raise ValueError("Sleep mode must be True or False")

	def __str__(self):
		out = "SmartDoorbell:"
		out += f" switched on: {self.getSwitchedOn()}"
		out += f", sleep mode: {self.getSleep()}"
		return out
	
class SmartHome():
	def __init__(self):
		self.devices = []

	def getDevices(self):
		return self.devices
	
	def getDeviceAt(self, index):
		return self.devices[index]
	
	def addDevice(self, device):
		if not isinstance(device, SmartDevice):
			raise ValueError("Device must be a SmartDevice")

		self.devices.append(device)

	def removeDeviceAt(self, index):
		if index < 0 or index >= len(self.devices):
			raise ValueError("Index out of range")

		self.devices.pop(index)

	def toggleSwitch(self, index):
		if index < 0 or index >= len(self.devices):
			raise ValueError("Index out of range")

		self.devices[index].toggleSwitch()

	def turnOffAll(self):
		for device in self.devices:
			device.switchedOn = False

	def turnOnAll(self):
		for device in self.devices:
			device.switchedOn = True
			
	def __str__(self):
		out = "SmartHome"

		i = 0
		for device in self.devices:
			out += f"\n{i}: {device}"
			i += 1
		return out

def testSmartPlug():
	print("Testing SmartPlug")
	# Create an instance of the SmartPlug class with a consumption rate of 45.
	p = SmartPlug(45)
	# Toggle the status of this plug by calling its toggleSwitch method.
	p.toggleSwitch()
	# Print the value of switchedOn using the appropriate accessor method.
	print(p.getSwitchedOn())
	# Print the value of consumptionRate,
	print(p.getConsumptionRate())
	# set it to a new valid value (of your choice),
	p.setConsumptionRate(42)
	# and then print it again.
	print(p.getConsumptionRate())
	# Print the SmartPlug object.
	print(p)

def testSmartDoorbell():
	print("Testing SmartDoorbell")
	# Create an instance of your CustomDevice class.
	d = SmartDoorbell()
	# Toggle the status of this device using the toggleSwitch method.
	d.toggleSwitch()
	# Print the switchedOn instance variable using the appropriate accessor method.
	print(d.getSwitchedOn())
	# Print the current value of the option instance variable (from table 1).
	print(d.getSleep())
	# Then set it to a new value (of your choice).
	d.setSleep(True)
	# Next, print it again.
	print(d.getSleep())
	# Print the CustomDevice object.
	print(d)

def testSmartHome():
	# Create an instance of the SmartHome class and two instances of the SmartPlug class
	# with consumption rates of 45.
	home = SmartHome() 
	p1 = SmartPlug(45)
	p2 = SmartPlug(45)
	# Additionally, create an instance of your custom device.
	d = SmartDoorbell()
	# Toggle the first plug, hence turning it on. Then set its consumption rate to 150.
	p1.toggleSwitch()
	p1.setConsumptionRate(150)
	# Then, set the consumptionRate of the second plug to 25.
	p2.setConsumptionRate(25)
	# Lastly, set the option of the custom device to a value of your choice.
	d.setSleep(True)
	# Add both plugs and the custom device to the smart home object.
	home.addDevice(p1)
	home.addDevice(p2)
	home.addDevice(d)
	# Toggle the status of the second plug using the appropriate method of the smart home object.
	home.toggleSwitch(1)
	# Print the smart home object.
	print(home)
	# Turn on all devices in the smart home and print the smart home object again.
	home.turnOnAll()
	print(home)
	# Remove the first device and print the smart home.
	home.removeDeviceAt(0)
	print(home)


testSmartPlug()
testSmartDoorbell()
testSmartHome()