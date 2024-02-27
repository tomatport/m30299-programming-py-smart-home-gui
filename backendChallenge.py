class SmartDevice:
	"""
		Super class for all smart devices
	"""
	def __init__(self):
		self.switchedOn = False
		self.schedule = []

		for _ in range(24): # 0 - 23
			self.schedule.append(None)

	def toggleSwitch(self):
		self.switchedOn = not self.switchedOn

	def getSwitchedOn(self):
		return self.switchedOn
	
	def getSchedule(self):
		return self.schedule
	
	def getScheduleText(self):
		out = ""
		for i in range(24):
			out += f"{self.schedule[i]};"
		return out

	def setActionAtHour(self, hour, action):
		if hour < 0 or hour > 23:
			raise ValueError("Hour must be between 0 and 23")
		
		if action == None or action == True or action == False:
			self.schedule[hour] = action
		else:
			raise ValueError("Action must be None (no change), True (on), or False (off)")

class SmartPlug(SmartDevice):
	def __init__(self, consumptionRate=0):
		super().__init__()
		if consumptionRate < 0 or consumptionRate > 150:
			raise ValueError("Consumption rate must be between 0 and 150")
		
		self.consumptionRate = consumptionRate

	def getConsumptionRate(self):
		return self.consumptionRate

	def setConsumptionRate(self, consumptionRate):
		# must be between 0 and 150
		if consumptionRate < 0 or consumptionRate > 150:
			raise ValueError("Consumption rate must be between 0 and 150")
		else:
			self.consumptionRate = consumptionRate

	def getCSVRow(self):
		return f"SmartPlug, {self.getSwitchedOn()}, {self.getScheduleText()}, {self.getConsumptionRate()}"

	def __str__(self):
		out = "SmartPlug"
		out += f"\n   switched on: {self.getSwitchedOn()}"
		out += f"\n   comp. rate: {self.getConsumptionRate()}"
		return out
	

class SmartDoorbell(SmartDevice):
	def __init__(self):
		super().__init__()
		self.sleepMode = False

	def getSleep(self):
		return self.sleepMode
	
	def setSleep(self, sleepMode):
		if sleepMode == True or sleepMode == False:
			self.sleepMode = sleepMode
		else:
			raise ValueError("Sleep mode must be True or False")

	def getCSVRow(self):
		return f"SmartDoorbell, {self.getSwitchedOn()}, {self.getScheduleText()}, {self.getSleep()}"

	def __str__(self):
		out = "SmartDoorbell"
		out += f"\n   switched on: {self.getSwitchedOn()}"
		out += f"\n   sleep mode: {self.getSleep()}"
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

	def getCSV(self):
		out = "DeviceType, Switched On, Schedule, Consumption Rate or Sleep State\n"
		for device in self.devices:
			out += f"{device.getCSVRow()}\n"
		return out
	
	def importCSV(self, csv):
		self.devices = []

		# remove first line
		csv = csv.split("\n")[1:]
		for line in csv:
			if not line:
				continue

			device = line.split(", ")
			deviceType = device[0]
			switchedOn = device[1]
			schedule = device[2]
			option = device[3]

			if deviceType == "SmartPlug":
				newDevice = SmartPlug(int(option))
			elif deviceType == "SmartDoorbell":
				newDevice = SmartDoorbell()
				if option == "True":
					newDevice.setSleep(True)
				else:
					newDevice.setSleep(False)
			else:
				raise ValueError("Invalid device type")

			if switchedOn == "True":
				newDevice.toggleSwitch()
			
			schedule = schedule.split(";")
			for i in range(24):
				newDevice.setActionAtHour(i, eval(schedule[i])) # eval is used to convert string to boolean

			self.addDevice(newDevice)
			
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