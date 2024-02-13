from tkinter import *
from backend import *

def setUpHome():
	newHome = SmartHome()

	# allow the user to populate it with 5 devices
	while len(newHome.getDevices()) < 5:
		print(f"🏡 Adding device {len(newHome.getDevices()) + 1}/5")
		choice = input("Enter 1 for SmartPlug, 2 for SmartDoorbell: ")

		if not choice.isdigit():
			print("⚠️ You must enter a number!")
			continue

		if int(choice) == 1:
			print("🔌 Adding a SmartPlug")
			
			consumptionRate = input("Enter the consumption rate of the plug: ")
			while not consumptionRate.isdigit():
				print("⚠️ Consumption rate must be a number")
				consumptionRate = input("Enter the consumption rate of the plug: ")
			
			consumptionRate = int(consumptionRate)

			if consumptionRate < 0 or consumptionRate > 150:
				print("⚠️ Consumption rate must be between 0 and 150")
				continue

			newHome.addDevice(SmartPlug(consumptionRate))
			print(f"🔌 Added a SmartPlug, with consumption rate of {consumptionRate}")

		elif int(choice) == 2:
			newHome.addDevice(SmartDoorbell())
			print("🔔 Added a SmartDoorbell")
		else:
			print("⚠️ You must enter 1 or 2!")

	return newHome

class SmartHomeSystem:
	def __init__(self, home): 
		if not isinstance(home, SmartHome):
			raise ValueError("Home must be a SmartHome")

		self.home = home
		self.deviceWidgets = []

		self.win = Tk()
		self.win.title("Smart Home System")
		self.win.geometry("500x200")

		self.headerFrame = Frame(self.win)
		self.headerFrame.grid(row=0, column=0, padx=10, pady=10)

		self.devicesFrame = Frame(self.win)
		self.devicesFrame.grid(row=1, column=0, padx=10, pady=10)

		self.footerFrame = Frame(self.win)
		self.footerFrame.grid(row=2, column=0, padx=10, pady=10)


	def createStaticButtons(self):
		"""Creates the buttons that will always be present"""
		self.turnOnAllButt = Button(
			self.headerFrame,
			text="Turn on all",
			command=self.turnOnAll
		)
		self.turnOnAllButt.grid(row=0, column=0, padx=5)

		self.turnOffAllButt = Button(
			self.headerFrame,
			text="Turn off all",
			command=self.turnOffAll
		)
		self.turnOffAllButt.grid(row=0, column=1, padx=5)

		
		self.addDeviceButt = Button(
			self.footerFrame,
			text="Add device",
			command=nI
		)
		self.addDeviceButt.grid(row=0, column=0, padx=5)

	def refreshDeviceList(self):
		"""
		Removes all widgets from the devicesFrame and re-creates
		them with current devices/statuses
		"""

		for widget in self.deviceWidgets:
			widget.destroy()

		devices = self.home.getDevices()
		numDevices = len(devices)

		for i in range(numDevices):
			device = devices[i]
			self.createDeviceWidget(self.deviceWidgets, self.devicesFrame, device, i)

		if numDevices == 0:
			noDevicesLabel = Label(self.devicesFrame, text="No devices")
			noDevicesLabel.grid(row=0, column=0)
			self.deviceWidgets.append(noDevicesLabel)

	def createDeviceWidget(self, widgetArray, widget, device, i):
		"""Creates a widget for a device"""
		if not isinstance(widget, Frame):
			raise ValueError("Widget must be a Frame")
		
		if not isinstance(device, SmartDevice):
			raise ValueError("Device must be a SmartDevice")
		
		deviceType = "Plug" if isinstance(device, SmartPlug) else "Doorbell"
		deviceTypeLabel = Label(widget, text=deviceType, justify=LEFT, padx=5)
		deviceTypeLabel.grid(row=i, column=0, sticky=W)
		widgetArray.append(deviceTypeLabel)

		statusText = "ON" if device.getSwitchedOn() else "OFF"	
		statusLabel = Label(widget, text=statusText, justify=LEFT, padx=5)
		statusLabel.grid(row=i, column=1, sticky=W)
		widgetArray.append(statusLabel)

		if deviceType == "SmartPlug":
			consumptionText = f"Consumption: {device.getConsumptionRate()}"
			consumptionLabel = Label(widget, text=consumptionText, justify=LEFT, padx=5)
			consumptionLabel.grid(row=i, column=2)
			widgetArray.append(consumptionLabel)
		elif deviceType == "SmartDoorbell":
			sleepStatus = "Sleeping" if device.getSleep() else "Awake"
			sleepText = f"Sleep mode: {sleepStatus}"
			sleepLabel = Label(widget, text=sleepText, justify=LEFT, padx=5)
			sleepLabel.grid(row=i, column=3)
			widgetArray.append(sleepLabel)

		toggleButt = Button(
			widget,
			text="T",
			padx=5,
			command=lambda: self.toggleDeviceAt(i)
		)
		toggleButt.grid(row=i, column=4)
		widgetArray.append(toggleButt)

		editButt = Button(
			widget,
			text="E",
			padx=5,
			command=nI
		)
		editButt.grid(row=i, column=5)
		widgetArray.append(editButt)

		removeButt = Button(
			widget,
			text="-",
			padx=5,
			command=lambda: self.removeDeviceAt(i)
		)
		removeButt.grid(row=i, column=6)
		widgetArray.append(removeButt)

	def toggleDeviceAt(self, index):
		"""Toggles the device at the given index"""
		device = self.home.getDeviceAt(index)
		device.toggleSwitch()
		self.refreshDeviceList()

	def removeDeviceAt(self, index):
		"""Removes the device at the given index"""
		self.home.removeDevice(index)
		self.refreshDeviceList()

	def turnOnAll(self):
		"""Turns on all devices"""
		self.home.turnOnAll()
		self.refreshDeviceList()

	def turnOffAll(self):
		"""Turns off all devices"""
		self.home.turnOffAll()
		self.refreshDeviceList()

	def run(self):
		self.createStaticButtons()
		self.refreshDeviceList()
		self.win.mainloop()

def nI():
	print("Not implemented")

def main():
	# home = setUpHome()
	# print(home)

	home = SmartHome()
	home.addDevice(SmartPlug(50))
	home.addDevice(SmartDoorbell())
	home.addDevice(SmartPlug(100))
	home.addDevice(SmartDoorbell())
	home.addDevice(SmartPlug(150))
	home.addDevice(SmartPlug(123))

	system = SmartHomeSystem(home)
	# print(system)



	system.run()

main()