from backend import *
from tkinter import *
import tkinter.font as Font
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox
from tkinter.ttk import Combobox

IMAGESPATH = "images/"

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
		self.deviceWidgets = []

		self.win = Tk()
		self.win.title("Smart Home System")
		self.win.resizable(False, False)

		# make section frames where our widgets will go
		self.headerFrame = Frame(self.win)
		self.headerFrame.grid(row=0, column=0, padx=10, pady=10)

		self.devicesFrame = Frame(self.win)
		self.devicesFrame.grid(row=1, column=0, padx=10, pady=10)

		self.footerFrame = Frame(self.win)
		self.footerFrame.grid(row=2, column=0, padx=10, pady=10)

		# set up fonts and images (must be done after creating the window)
		# this changes the default font for everything
		self.font = Font.nametofont("TkDefaultFont")
		self.font.configure(
			family="Verdana",
			size=11
		)

		# this changes the default monospace font for everything
		self.monoFont = Font.nametofont("TkFixedFont")
		self.monoFont.configure(
			family="Lucida Console",
			size=10
		)

		# here are all of our images for the devices, to be used in the GUI
		self.IMAGEPLUGON = PhotoImage(file=f"{IMAGESPATH}plugon.png")
		self.IMAGEPLUGOFF = PhotoImage(file=f"{IMAGESPATH}plugoff.png")
		self.IMAGEDOORBELLON = PhotoImage(file=f"{IMAGESPATH}doorbellon.png")
		self.IMAGEDOORBELLOFF = PhotoImage(file=f"{IMAGESPATH}doorbelloff.png")
		self.IMAGESLEEP = PhotoImage(file=f"{IMAGESPATH}sleep.png")
		self.IMAGESLEEPOFF = PhotoImage(file=f"{IMAGESPATH}sleepoff.png")
		self.IMAGEIMPORT = PhotoImage(file=f"{IMAGESPATH}import.png")
		self.IMAGEEXPORT = PhotoImage(file=f"{IMAGESPATH}export.png")
		self.IMAGEADD = PhotoImage(file=f"{IMAGESPATH}add.png")
		self.IMAGECLOCK = PhotoImage(file=f"{IMAGESPATH}clock.png")

		# also set up the time and its label here
		self.timeIcon = Label(self.headerFrame, image=self.IMAGECLOCK)
		self.timeIcon.grid(row=0, column=4, padx=5)

		self.time = 0
		self.timeLabel = Label(
			self.headerFrame,
			text=self.getTimeString(),
			font=self.monoFont
		)
		self.timeLabel.grid(row=0, column=5, padx=5, sticky=E)

	def createStaticButtons(self):
		"""Creates the buttons that will always be present in the GUI"""

		# turn on/off all devices in the header
		turnOnIcon = Label(self.headerFrame, image=self.IMAGEPLUGON)
		turnOnIcon.grid(row=0, column=0, padx=5)

		turnOnAllButt = Button(
			self.headerFrame,
			text="Turn on all",
			command=self.turnOnAll
		)
		turnOnAllButt.grid(row=0, column=1, padx=5)

		turnOffIcon = Label(self.headerFrame, image=self.IMAGEPLUGOFF)
		turnOffIcon.grid(row=0, column=2, padx=5)

		turnOffAllButt = Button(
			self.headerFrame,
			text="Turn off all",
			command=self.turnOffAll
		)
		turnOffAllButt.grid(row=0, column=3, padx=5)


		addDeviceIcon = Label(self.footerFrame, image=self.IMAGEADD)
		addDeviceIcon.grid(row=0, column=0, padx=5)

		# add, import, and export devices in the footer
		addDeviceButt = Button(
			self.footerFrame,
			text="Add device",
			command=self.addDevicePrompt
		)
		addDeviceButt.grid(row=0, column=1, padx=5)

		importIcon = Label(self.footerFrame, image=self.IMAGEIMPORT)
		importIcon.grid(row=0, column=2, padx=5)

		importDevicesButt = Button(
			self.footerFrame,
			text="Import",
			command=self.importDevices
		)
		importDevicesButt.grid(row=0, column=3)

		exportIcon = Label(self.footerFrame, image=self.IMAGEEXPORT)
		exportIcon.grid(row=0, column=4, padx=5)

		exportDevicesButt = Button(
			self.footerFrame,
			text="Export",
			command=self.exportDevices
		)
		exportDevicesButt.grid(row=0, column=5, padx=5)

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
			noDevicesLabel.grid(row=0, column=0)
			self.deviceWidgets.append(noDevicesLabel)

	def createDeviceRow(self, widgetList, parentFrame, device, i):
		"""Creates a row of widgets for a device, and draws it to the given frame"""

		if not isinstance(parentFrame, Frame):
			raise ValueError("Widget must be a Frame")
		
		if not isinstance(device, SmartDevice):
			raise ValueError("Device must be a SmartDevice")
				
		deviceType = "Plug" if isinstance(device, SmartPlug) else "Doorbell"

		if deviceType == "Plug":
			deviceImage = self.IMAGEPLUGON if device.getSwitchedOn() else self.IMAGEPLUGOFF
		elif deviceType == "Doorbell":
			deviceImage = self.IMAGEDOORBELLON if device.getSwitchedOn() else self.IMAGEDOORBELLOFF

		deviceTypeImage = Label(parentFrame, image=deviceImage, text=deviceType)
		deviceTypeImage.grid(row=i, column=0, sticky=W, pady=5, padx=2.5)
		widgetList.append(deviceTypeImage) # add it to a list so we can destroy it later on refresh

		deviceTypeLabel = Label(parentFrame, text=deviceType)
		deviceTypeLabel.grid(row=i, column=1, sticky=W, pady=5, padx=2.5)
		widgetList.append(deviceTypeLabel)

		statusText = "ON" if device.getSwitchedOn() else "OFF"
		statusTextVar = StringVar(value=statusText)
		statusLabel = Label(parentFrame, textvariable=statusTextVar)
		statusLabel.grid(row=i, column=2, sticky=W, pady=5, padx=2.5)
		widgetList.append(statusLabel)

		if deviceType == "Plug":
			consumptionText = f"{device.getConsumptionRate()}W"
			consumptionLabel = Label(parentFrame, text=consumptionText, font=self.monoFont)
			consumptionLabel.grid(row=i, column=3, pady=5, padx=2.5)
			widgetList.append(consumptionLabel)
		elif deviceType == "Doorbell":
			if device.getSleep():
				# if sleeping
				sleepImage = self.IMAGESLEEP
				sleepText = "Sleeping"
			else:
				# if awake
				sleepImage = self.IMAGESLEEPOFF
				sleepText = "Not Sleeping"

			sleepLabel = Label(parentFrame, image=sleepImage, text=sleepText, justify=LEFT)
			sleepLabel.grid(row=i, column=3, sticky=W, pady=5, padx=2.5)
			widgetList.append(sleepLabel)

		
		willBe = "off" if device.getSwitchedOn() else "on"
		willBeVar = StringVar(value=f"Turn {willBe}")
		toggleButt = Button(
			parentFrame,
			textvariable=willBeVar,
			padx=5,
			command=lambda: self.toggleDeviceAt(i, statusTextVar, willBeVar)
		)
		
		toggleButt.grid(row=i, column=4, pady=5, padx=2.5)
		widgetList.append(toggleButt)

		editButt = Button(
			parentFrame,
			text="Edit",
			padx=5,
			command=lambda: self.editDevicePrompt(i, statusTextVar, willBeVar)
		)
		editButt.grid(row=i, column=5, pady=5, padx=2.5)
		widgetList.append(editButt)

		scheduleButt = Button(
			parentFrame,
			text="Schedule",
			padx=5,
			command=lambda: self.scheduleDevicePrompt(i)
		)
		scheduleButt.grid(row=i, column=6, pady=5, padx=2.5)
		widgetList.append(scheduleButt)

		removeButt = Button(
			parentFrame,
			text="-",
			padx=5,
			fg="red",
			command=lambda: self.removeDeviceAt(i)
		)
		removeButt.grid(row=i, column=7, pady=5, padx=2.5)
		widgetList.append(removeButt)

	############################################
	# Device manipulation functions
	############################################
	def toggleDeviceAt(self, index, statusTextVar, willBeVar):
		"""Toggles the device at the given index"""
		device = self.home.getDeviceAt(index)	

		device.toggleSwitch()

		if device.getSwitchedOn():
			statusTextVar.set("ON")
			willBeVar.set("Turn off")
		else:
			statusTextVar.set("OFF")
			willBeVar.set("Turn on")

		# no need to refresh since the Tkinter variables are updated in-place
	
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
		deviceType = "plug" if isinstance(self.home.getDeviceAt(index), SmartPlug) else "doorbell"

		# create an "are you sure" messagebox
		sure = MessageBox.askyesno(title="Removing a device", message=f"Are you sure you want to remove this {deviceType}?")
		if not sure:
			return
		
		self.home.removeDevice(index)
		self.refreshDeviceList()

	############################################
	# Add window and its related functions
	############################################
	def addDevicePrompt(self):
		"""Shows a window that allows a user to add a device to the home"""

		addWin = Toplevel(self.win)
		addWin.title("Add a device")
		addWin.resizable(False, False)
		
		consumptionText = Label(addWin, text="Consumption rate, if adding a plug:")
		consumptionText.pack(padx=10, pady=10)

		consumption = IntVar(value=0)
		consumptionEntry = Spinbox(
			addWin,
			from_=0,
			to=150,
			textvariable=consumption,
			wrap=True
		)
		consumptionEntry.pack(padx=10, pady=10)

		addPlugButt = Button(
			addWin,
			text="Add a plug",
			command=lambda: self.addPlug(addWin, consumption.get())
		)
		addPlugButt.pack(side=LEFT, padx=10, pady=20)
		
		addDoorbellButt = Button(
			addWin,
			text="Add a doorbell",
			command=lambda: self.addDoorbell(addWin)
		)
		addDoorbellButt.pack(side=RIGHT, padx=10, pady=20)

		addWin.mainloop()

	def addPlug(self, addWin, consumption):
		"""From the add window, adds a plug to the home, then destroys the window and refreshes the device list"""

		if consumption < 0 or consumption > 150:
			MessageBox.showwarning(title="Check your values!",
			                       message="Consumption rate must be between 0 and 150")
			return

		self.home.addDevice(SmartPlug(consumption))
		addWin.destroy()
		self.refreshDeviceList()

	def addDoorbell(self, addWin):
		"""From the add window, adds a doorbell to the home, then destroys the window and refreshes the device list"""
		self.home.addDevice(SmartDoorbell())
		addWin.destroy()
		self.refreshDeviceList()

	############################################
	# Edit window and its related functions
	############################################
	def editDevicePrompt(self, index, statusTextVar, willBeVar):
		"""Shows a prompt to edit the properties of a device at the given index"""

		device = self.home.getDeviceAt(index)
		deviceType = "plug" if isinstance(device, SmartPlug) else "doorbell"

		editWin = Toplevel(self.win)
		editWin.title(f"Edit {deviceType}")
		editWin.resizable(False, False)

		label = Label(editWin, text=f"Editing {deviceType} at index {index}")
		label.pack(padx=10, pady=10)

		currentStatusLabel = Label(editWin, textvariable=statusTextVar)
		currentStatusLabel.pack(padx=10, pady=10)

		toggleButt = Button(
			editWin,
			textvar=willBeVar,
			command=lambda: self.toggleDeviceAt(index, statusTextVar, willBeVar)
		)
		toggleButt.pack(padx=10, pady=10)


		if deviceType == "plug":
			consumptionText = Label(editWin, text="Consumption rate:")
			consumptionText.pack(padx=10, pady=10)

			consumption = IntVar(value=device.getConsumptionRate())
			consumptionEntry = Spinbox(
				editWin,
				from_=0,
				to=150,
				textvariable=consumption,
				wrap=True
			)
			consumptionEntry.pack(padx=10, pady=10)

			editButt = Button(
				editWin,
				text="Save",
				command=lambda: self.editPlugConsumptionRate(editWin, index, consumption.get())
			)
			editButt.pack(padx=10, pady=10)

		elif deviceType == "doorbell":
			sleepMode = BooleanVar(value=device.getSleep())
			sleepCheck = Checkbutton(
				editWin,
				text="Sleep mode",
				variable=sleepMode
			)
			sleepCheck.pack(padx=10, pady=10)

			editButt = Button(
				editWin,
				text="Save",
				command=lambda: self.editDoorbellSleepMode(editWin, index, sleepMode.get())
			)
			editButt.pack(padx=10, pady=10)

		editWin.mainloop()

	def editPlugConsumptionRate(self, editWin, index, consumption):
		"""
		From the edit window, sets the consumption rate of a plug at the given index,
		then destroys the window and refreshes the device list
		"""
		if consumption < 0 or consumption > 150:
			MessageBox.showwarning(title="Check your values!",
			                       message="Consumption rate must be between 0 and 150")
			return

		self.home.getDeviceAt(index).setConsumptionRate(consumption)
		editWin.destroy()
		self.refreshDeviceList()

	def editDoorbellSleepMode(self, editWin, index, sleepMode):
		"""
		From the edit window, sets the sleep mode of a doorbell at the given index,
		then destroys the window and refreshes the device list
		"""
		self.home.getDeviceAt(index).setSleep(sleepMode)
		editWin.destroy()
		self.refreshDeviceList()

	############################################
	# Schedule window and its related functions, and clock
	############################################
	def getTimeString(self):
		"""Returns the current time as a formatted string (HH:00)"""
		return f"{str(self.time).zfill(2)}:00"
	
	def incrementClock(self):
		"""Increment the clock every 3 seconds, and update the devices accordingly"""

		newTime = self.time + 1 if self.time < 23 else 0
		self.time = newTime

		devicesUpdated = False
		devices = self.home.getDevices()
		for device in devices:
			if device.getSchedule()[newTime] == 0:
				devicesUpdated = True
				device.switchedOn = False
			elif device.getSchedule()[newTime] == 1:
				devicesUpdated = True
				device.switchedOn = True

		if devicesUpdated:
			self.refreshDeviceList()

		self.timeLabel.config(text=self.getTimeString())

		self.win.after(3000, self.incrementClock)

	def scheduleDevicePrompt(self, index):
		"""Shows a window that allows a user to view and edit the schedule for a device"""

		device = self.home.getDeviceAt(index)
		deviceType = "plug" if isinstance(device, SmartPlug) else "doorbell"
		deviceSchedule = device.getSchedule()

		scheduleWin = Toplevel(self.win)
		scheduleWin.title(f"Schedule for {deviceType}")
		scheduleWin.resizable(False, False)

		timesFrame = Frame(scheduleWin)
		timesFrame.grid(row=0, column=0, padx=10, pady=10)

		for i in range(24): # 0 to 23
			timeLabel = Label(timesFrame, text=f"{str(i).zfill(2)}:00")
			timeLabel.grid(row=i, column=0, padx=2, pady=2)

			options = ["Turn Off", "Turn On", "No Change"] # 0, 1, 2
			actionCombo = Combobox(
				timesFrame,
				values=options,
				width=15,
				state="readonly" # user can't type in their own value
			)
			# set the current value to the device's schedule
			actionCombo.current(deviceSchedule[i])

			# when the user changes the value, update the device's schedule
			actionCombo.bind(
				"<<ComboboxSelected>>",
				lambda event, i=i, actionCombo=actionCombo: self.updateDeviceSchedule(index, i, actionCombo.current())
			)

			actionCombo.grid(row=i, column=1, padx=10, pady=10)
	
		scheduleWin.mainloop()

	def updateDeviceSchedule(self, index, hour, action):
		"""Updates the schedule for a device at the given index"""
		self.home.getDeviceAt(index).setActionAtHour(hour, action)
	
	############################################
	# Import and Export functions
	############################################
	def exportDevices(self):
		"""Lets the user export the devices to a CSV file after choosing a location"""
		content = self.home.getCSV()
		file = FileDialog.asksaveasfile(
			mode="w",
			defaultextension=".csv",
			filetypes=[("CSV files", "*.csv")]
		)
		
		try:
			file.write(content)
			file.close()
		except Exception as e:
			MessageBox.showerror(title="Error Writing File", message=f"{e}")
			return

	def importDevices(self):
		"""Prompts the user to import devices from a file"""
		file = FileDialog.askopenfile(
			mode="r",
			filetypes=[("CSV files", "*.csv")]
		)
		
		try:
			content = file.read()
			file.close()
		except Exception as e:
			MessageBox.showerror(title="Error Reading File", message=f"{e}")
			return
		
		self.home.importCSV(content)
		self.refreshDeviceList()

	def run(self):
		"""Runs the GUI and sets up everything"""
		self.createStaticButtons()
		self.refreshDeviceList()
		self.incrementClock()
		self.win.mainloop()

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