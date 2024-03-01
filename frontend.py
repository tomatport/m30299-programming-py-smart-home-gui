from backendChallenge import *
from tkinter import *
from tkinter import messagebox

def setUpHome():
	"""Sets up a home with 5 devices via shell input, returns the home"""

	newHome = SmartHome()
	print("🏡 Setting up your Smart Home")

	# allow the user to populate home with 5 devices
	while len(newHome.getDevices()) < 5:
		print(f"\n➕ Adding device {len(newHome.getDevices()) + 1}/5")
		choice = input("Enter 'plug' for SmartPlug, 'doorbell' for SmartDoorbell: ")
		choice = choice.lower().replace(" ", "")

		if choice == "plug":
			print("🔌 Adding a SmartPlug")
			
			while True: # keep asking until valid
				consumptionRate = input("Enter the consumption rate of the plug: ")
				
				if consumptionRate.isdigit() and int(consumptionRate) >= 0 and int(consumptionRate) <= 150:
					consumptionRate = int(consumptionRate)
					break

				print("⚠️ Consumption rate must be a number between 0 and 150!")
			

			newHome.addDevice(SmartPlug(consumptionRate))
			print(f"🔌 Added a SmartPlug, with consumption rate of {consumptionRate}")

		elif choice == "doorbell":
			# no questions to ask for a doorbell
			newHome.addDevice(SmartDoorbell())
			print("🔔 Added a SmartDoorbell")

		else:
			print("⚠️ You must enter 'plug' or 'doorbell'!")

	return newHome

class SmartHomeSystem:
	"""Represents the smart home system as whole, with a GUI frontend"""

	def __init__(self, home):
		if not isinstance(home, SmartHome):
			raise ValueError("Home must be a SmartHome")

		self.home = home
		self.deviceWidgets = [] # list of widgets to be destroyed on refresh

		self.win = Tk()
		self.win.title("Smart Home System")
		self.win.minsize(400, 0) # stops the window getting smaller when widgets are destroyed or changed
		self.win.resizable(False, False)

		# make section frames where our widgets will go
		self.headerFrame = Frame(self.win)
		self.headerFrame.grid(row=0, column=0, padx=10, pady=10)

		self.devicesFrame = Frame(self.win)
		self.devicesFrame.grid(row=1, column=0, padx=10, pady=10)

		self.footerFrame = Frame(self.win)
		self.footerFrame.grid(row=2, column=0, padx=10, pady=10)

	def createStaticButtons(self):
		"""Creates the buttons that will always be present in the GUI"""

		# turn on/off all devices in the header
		turnOnAllButt = Button(
			self.headerFrame,
			text="Turn on all",
			command=self.turnOnAll,
			padx=5,
			pady=5
		)
		turnOnAllButt.grid(row=0, column=0, padx=10)

		turnOffAllButt = Button(
			self.headerFrame,
			text="Turn off all",
			command=self.turnOffAll,
			padx=5,
			pady=5
		)
		turnOffAllButt.grid(row=0, column=1, padx=10)

		# add, import, and export devices in the footer
		addButt = Button(
			self.footerFrame,
			text="Add",
			command=self.addDeviceWindow,
			padx=5,
			pady=5
		)
		addButt.grid(row=0, column=0, padx=10)

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
			self.createDeviceRow(self.deviceWidgets, self.devicesFrame, device, i)

		if numDevices == 0:
			noDevicesLabel = Label(self.devicesFrame, text="No devices")
			noDevicesLabel.grid(row=0, column=0, columnspan=4)
			self.deviceWidgets.append(noDevicesLabel)

	def createDeviceRow(self, widgetList, parentFrame, device, i):
		"""Creates a row of widgets for a device, and draws it to the given frame"""

		if not isinstance(parentFrame, Frame):
			raise ValueError("Widget must be a Frame")
		
		if not isinstance(device, SmartDevice):
			raise ValueError("Device must be a SmartDevice")
		
		deviceStatus = "on" if device.getSwitchedOn() else "off"
		
		if isinstance(device, SmartPlug):
			consumptionRate = device.getConsumptionRate()
			textLabel = f"Plug: {deviceStatus}, Consumption: {consumptionRate}"
		elif isinstance(device, SmartDoorbell):
			sleepMode = "enabled" if device.getSleep() else "disabled"
			textLabel = f"Doorbell: {deviceStatus}, Sleep mode: {sleepMode}"
		else:
			textLabel = "Unknown device"

		deviceLabel = Label(parentFrame, text=textLabel, width=28)
		deviceLabel.grid(row=i, column=0, padx=10, pady=5)
		widgetList.append(deviceLabel) # add to list to be destroyed later

		
		toggleButt = Button(
			parentFrame,
			text="Toggle",
			padx=5,
			command=lambda i=i: self.toggleDeviceAt(i)
		)
		
		toggleButt.grid(row=i, column=1, pady=5, padx=2.5)
		widgetList.append(toggleButt)

		editButt = Button(
			parentFrame,
			text="Edit",
			padx=5,
			command=lambda i=i: self.editDeviceWindow(i)
		)
		editButt.grid(row=i, column=2, pady=5, padx=2.5)
		widgetList.append(editButt)

		removeButt = Button(
			parentFrame,
			text="Delete",
			padx=5,
			fg="red",
			command=lambda i=i: self.removeDeviceAt(i)
		)
		removeButt.grid(row=i, column=3, pady=5, padx=2.5)
		widgetList.append(removeButt)

	############################################
	# Device manipulation functions
	############################################
	def toggleDeviceAt(self, index):
		"""Toggles the device at the given index"""
		device = self.home.getDeviceAt(index)
		device.toggleSwitch()
		self.refreshDeviceList()
	
	def turnOnAll(self):
		"""Turns on all devices"""
		self.home.turnOnAll()
		self.refreshDeviceList()

	def turnOffAll(self):
		"""Turns off all devices"""
		self.home.turnOffAll()
		self.refreshDeviceList()

	def removeDeviceAt(self, index):
		"""Removes the device at the given index, after confirmation"""		
		self.home.removeDeviceAt(index)
		self.refreshDeviceList()

	############################################
	# Add window and its related functions
	############################################
	def addDeviceWindow(self):
		"""Shows a window that allows a user to add a device to the home"""

		addWin = Toplevel(self.win)
		addWin.title("Add a device")
		addWin.resizable(False, False)

		consumptionText = Label(addWin, text="Plug consumption rate (0-150):")
		consumptionText.grid(row=0, column=0, padx=10, pady=10)

		consumptionVar = IntVar(value=0)
		consumptionEntry = Spinbox(
			addWin,
			from_=0,
			to=150,
			width=4,
			textvariable=consumptionVar,
			wrap=True
		)
		consumptionEntry.grid(row=0, column=1, padx=10, pady=10)

		addPlugButt = Button(
			addWin,
			text="Add a plug",
			command=lambda addWin=addWin, consumptionVar=consumptionVar:
					self.addPlug(addWin, consumptionVar)
		)
		addPlugButt.grid(row=1, column=0, columnspan=2,
		                 padx=10, pady=10, sticky=EW)

		orText = Label(addWin, text="or")
		orText.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=EW)

		addDoorbellButt = Button(
			addWin,
			text="Add a doorbell",
			command=lambda addWin=addWin: self.addDoorbell(addWin)
		)
		addDoorbellButt.grid(row=3, column=0, columnspan=2,
		                     padx=10, pady=10, sticky=EW)

		addWin.mainloop()

	def addPlug(self, addWin, consumptionVar):
		"""
		From the add window, adds a plug to the home,
		then destroys the window and refreshes the device list
		"""
		try:
			consumption = consumptionVar.get()
		except:
			messagebox.showwarning(
				title="Check your values!",
				message="Consumption rate must be a number, and cannot be blank"
			)
			return

		if consumption < 0 or consumption > 150:
			messagebox.showwarning(
				title="Check your values!",
				message="Consumption rate must be between 0 and 150"
			)
			return

		self.home.addDevice(SmartPlug(consumption))
		addWin.destroy()
		self.refreshDeviceList()

	def addDoorbell(self, addWin):
		"""
		From the add window, adds a doorbell to the home,
		then destroys the window and refreshes the device list
		"""
		self.home.addDevice(SmartDoorbell())
		addWin.destroy()
		self.refreshDeviceList()

	############################################
	# Edit window and its related functions
	############################################
	def editDeviceWindow(self, i):
		"""
		Shows a prompt to edit the properties of a device at the given index
		"""

		device = self.home.getDeviceAt(i)
		deviceType = "plug" if isinstance(device, SmartPlug) else "doorbell"

		editWin = Toplevel(self.win)
		editWin.title(f"{deviceType.title()} at index {i}")
		editWin.resizable(False, False)

		label = Label(editWin, text=f"{deviceType.title()} at index {i}")
		label.grid(row=0, column=0, padx=10, columnspan=2, pady=10)

		if deviceType == "plug":
			consumptionText = Label(editWin, text="Consumption rate:")
			consumptionText.grid(row=1, column=0, padx=10)

			consumption = IntVar(value=device.getConsumptionRate())
			consumptionEntry = Spinbox(
				editWin,
				from_=0,
				to=150,
				textvariable=consumption,
				wrap=True
			)
			consumptionEntry.grid(row=2, column=0, padx=10, pady=10)

			editButt = Button(
				editWin,
				text="Save",
				command=lambda editWin=editWin, i=i:
						self.editPlugConsumptionRate(editWin, i, consumption.get())
			)
			editButt.grid(row=2, column=1, padx=10, pady=10)

		elif deviceType == "doorbell":
			sleepMode = BooleanVar(value=device.getSleep())
			sleepCheck = Checkbutton(
				editWin,
				text="Enable sleep mode",
				variable=sleepMode
			)
			sleepCheck.grid(row=2, column=0, padx=10, pady=10)

			editButt = Button(
				editWin,
				text="Save",
				command=lambda editWin=editWin, i=i:
						self.setDoorbellSleepMode(editWin, i, sleepMode.get())
			)
			editButt.grid(row=2, column=1, padx=10, pady=10)

		editWin.mainloop()

	def editPlugConsumptionRate(self, editWin, index, consumption):
		"""
		From the edit window, sets the consumption rate of a plug at the given index,
		then destroys the window and refreshes the device list
		"""
		if consumption < 0 or consumption > 150:
			messagebox.showwarning(
				title="Check your values!",
				message="Consumption rate must be between 0 and 150"
			)
			return

		self.home.getDeviceAt(index).setConsumptionRate(consumption)
		editWin.destroy()
		self.refreshDeviceList()

	def setDoorbellSleepMode(self, editWin, index, sleepMode):
		"""
		From the edit window, sets the sleep mode of a doorbell at the given index,
		then destroys the window and refreshes the device list
		"""
		self.home.getDeviceAt(index).setSleep(sleepMode)
		editWin.destroy()
		self.refreshDeviceList()

	############################################
	# Run the GUI
	############################################
	def run(self):
		"""Runs the GUI and sets up everything"""
		self.createStaticButtons()
		self.refreshDeviceList()
		self.win.mainloop()

def main():
	home = setUpHome()
	# print(home)

	system = SmartHomeSystem(home)
	# print(system)
	system.run()

main()