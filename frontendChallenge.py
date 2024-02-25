from backendChallenge import *
from tkinter import *
from tkinter import messagebox, filedialog, font
from tkinter.ttk import Combobox, Separator

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

		# set up fonts and images (must be done after creating the window)
		# this changes the default font for everything
		self.font = font.nametofont("TkDefaultFont")
		self.font.configure(
			family="Verdana",
			size=11
		)

		# this changes the default monospace font for everything
		self.monoFont = font.nametofont("TkFixedFont")
		self.monoFont.configure(
			family="Lucida Console",
			size=11
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
		self.IMAGEEDIT = PhotoImage(file=f"{IMAGESPATH}edit.png")
		self.IMAGEDELETE = PhotoImage(file=f"{IMAGESPATH}delete.png")
		self.TOGGLEON = PhotoImage(file=f"{IMAGESPATH}toggleon.png")
		self.TOGGLEOFF = PhotoImage(file=f"{IMAGESPATH}toggleoff.png")

		# also set up the time here
		self.time = 0
		self.timeString = StringVar(value=self.getTimeString())

	def createStaticButtons(self):
		"""Creates the buttons that will always be present in the GUI"""

		# turn on/off all devices in the header
		turnOnAllButt = Button(
			self.headerFrame,
			text="Turn on all",
			image=self.IMAGEPLUGON,
			compound=LEFT,
			command=self.turnOnAll,
			padx=5,
			pady=5
		)
		turnOnAllButt.grid(row=0, column=0, padx=10)


		turnOffAllButt = Button(
			self.headerFrame,
			text="Turn off all",
			image=self.IMAGEPLUGOFF,
			compound=LEFT,
			command=self.turnOffAll,
			padx=5,
			pady=5
		)
		turnOffAllButt.grid(row=0, column=1, padx=10)

		headerSeparator = Separator(self.headerFrame, orient=VERTICAL)
		headerSeparator.grid(row=0, column=2, padx=20, sticky="ns")

		# clock, also in the header
		self.timeLabel = Label(
			self.headerFrame,
			textvariable=self.timeString,
			image=self.IMAGECLOCK,
			compound=LEFT,
			font=self.monoFont,
			padx=5,
			pady=5
		)
		self.timeLabel.grid(row=0, column=3, padx=10)

		# add, import, and export devices in the footer
		addButt = Button(
			self.footerFrame,
			text="Add device",
			image=self.IMAGEADD,
			compound=LEFT,
			command=self.addDeviceWindow,
			padx=5,
			pady=5
		)
		addButt.grid(row=0, column=0, padx=10)

		footerSeparator = Separator(self.footerFrame, orient=VERTICAL)
		footerSeparator.grid(row=0, column=1, padx=20, sticky="ns")

		importButt = Button(
			self.footerFrame,
			text="Import",
			image=self.IMAGEIMPORT,
			compound=LEFT,
			command=self.importDevices,
			padx=5,
			pady=5
		)
		importButt.grid(row=0, column=2, padx=10)

		exportButt = Button(
			self.footerFrame,
			text="Export",
			image=self.IMAGEEXPORT,
			compound=LEFT,
			command=self.exportDevices,
			padx=5,
			pady=5
		)
		exportButt.grid(row=0, column=3, padx=10)

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

		indexLabel = Label(parentFrame, text=str(i))
		indexLabel.grid(row=i, column=0, sticky=W, pady=5, padx=2.5)
		widgetList.append(indexLabel)

		if deviceType == "Plug":
			deviceImage = self.IMAGEPLUGON
		elif deviceType == "Doorbell":
			deviceImage = self.IMAGEDOORBELLON

		deviceTypeLabel = Label(parentFrame, text=deviceType, image=deviceImage, compound=LEFT)
		deviceTypeLabel.grid(row=i, column=1, sticky=W, pady=5, padx=2.5)
		widgetList.append(deviceTypeLabel) # add it to a list so we can destroy it later on refresh

		statusText = "ON" if device.getSwitchedOn() else "OFF"
		statusTextVar = StringVar(value=statusText)
		statusLabel = Label(parentFrame, textvariable=statusTextVar)
		statusLabel.grid(row=i, column=2, sticky=W, pady=5, padx=2.5)
		widgetList.append(statusLabel)

		if deviceType == "Plug":
			consumptionVar = IntVar(value=device.getConsumptionRate())
			consumptionEntry = Spinbox(
				parentFrame,
				from_=0,
				to=150,
				width=5,
				textvariable=consumptionVar,
				wrap=True
			)
			consumptionEntry.grid(row=i, column=3, sticky=W, pady=5, padx=2.5)
			widgetList.append(consumptionEntry)

			consumptionEntry.bind(
				"<FocusOut>",
				lambda event, i=i, consumptionVar=consumptionVar:
					self.editPlugConsumptionRate(i, consumptionVar)
			)

		elif deviceType == "Doorbell":
			sleepImage = self.IMAGESLEEP if device.getSleep() else self.IMAGESLEEPOFF
			# sleepText = "Sleeping" if device.getSleep() else "Awake"

			sleepButton = Button(
				parentFrame,
				# text=sleepText,
				image=sleepImage,
				compound=LEFT,
				padx=5,
				command=lambda i=i: self.editDoorbellSleepMode(i, not device.getSleep())
			)
			sleepButton.grid(row=i, column=3, pady=5, padx=2.5)
			widgetList.append(sleepButton)
		
		statusImage = self.TOGGLEON if device.getSwitchedOn() else self.TOGGLEOFF
		toggleButt = Button(
			parentFrame,
			text="Toggle",
			image=statusImage,
			padx=5,
			command=lambda i=i: self.toggleDeviceAt(i)
		)
		
		toggleButt.grid(row=i, column=4, pady=5, padx=2.5)
		widgetList.append(toggleButt)

		scheduleButt = Button(
			parentFrame,
			text="Schedule",
			image=self.IMAGECLOCK,
			padx=5,
			command=lambda i=i: self.scheduleDeviceWindow(i)
		)
		scheduleButt.grid(row=i, column=5, pady=5, padx=2.5)
		widgetList.append(scheduleButt)

		removeButt = Button(
			parentFrame,
			text="Remove",
			image=self.IMAGEDELETE,
			padx=5,
			fg="red",
			command=lambda i=i: self.removeDeviceAt(i)
		)
		removeButt.grid(row=i, column=6, pady=5, padx=2.5)
		widgetList.append(removeButt)

	############################################
	# Device manipulation functions
	############################################
	def toggleDeviceAt(self, index, statusVar=None):
		"""Toggles the device at the given index"""
		device = self.home.getDeviceAt(index)
		device.toggleSwitch()

		if statusVar:
			statusVar.set("ON" if device.getSwitchedOn() else "OFF")

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
		deviceType = "plug" if isinstance(self.home.getDeviceAt(index), SmartPlug) else "doorbell"

		# create an "are you sure" messagebox
		sure = messagebox.askyesno(
			title="Removing a device",
			message=f"Are you sure you want to remove this {deviceType}?"
		)
		if not sure:
			return
		
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
		
		consumptionText = Label(addWin, text="Consumption rate, if adding a plug:")
		consumptionText.pack(padx=10, pady=10)

		consumptionVar = IntVar(value=0)
		consumptionEntry = Spinbox(
			addWin,
			from_=0,
			to=150,
			textvariable=consumptionVar,
			wrap=True
		)
		consumptionEntry.pack(padx=10, pady=10)

		addPlugButt = Button(
			addWin,
			text="Add a plug",
			command=lambda addWin=addWin: self.addPlug(addWin, consumptionVar)
		)
		addPlugButt.pack(side=LEFT, padx=10, pady=20)
		
		addDoorbellButt = Button(
			addWin,
			text="Add a doorbell",
			command=lambda addWin=addWin: self.addDoorbell(addWin)
		)
		addDoorbellButt.pack(side=RIGHT, padx=10, pady=20)

		addWin.mainloop()

	def addPlug(self, addWin, consumptionVar):
		"""From the add window, adds a plug to the home, then destroys the window and refreshes the device list"""
		try:
			consumption = consumptionVar.get()
		except:
			# if a non-int is entered, or the box is left blank:
			messagebox.showwarning(
				title="Check your values!",
				message="Consumption rate must be a number and cannot be blank"
			)
			return

		if consumption < 0 or consumption > 150:
			messagebox.showwarning(
				title="Check your values!",
				message="Consumption rate must be a number between 0 and 150"
			)
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
	# Device editing functions
	############################################
	def editPlugConsumptionRate(self, index, consumptionVar):
		"""Sets the consumption rate of a plug, then refreshes the device list"""

		try:
			consumption = consumptionVar.get()
		except:
			# if a non-int is entered, or the box is left blank:
			messagebox.showwarning(
				title="Check your values!",
				message="Consumption rate must be a number and cannot be blank"
			)
			return

		if consumption < 0 or consumption > 150:
			messagebox.showwarning(
				title="Check your values!",
				message="Consumption rate must be between 0 and 150"
			)
			return

		self.home.getDeviceAt(index).setConsumptionRate(consumption)
		self.refreshDeviceList()

	def editDoorbellSleepMode(self, index, sleepMode):
		"""Sets the sleep mode of a doorbell, then refreshes the device list"""
		self.home.getDeviceAt(index).setSleep(sleepMode)
		self.refreshDeviceList()

	############################################
	# Schedule window and its related functions, and accompanying clock things
	############################################
	def getTimeString(self):
		"""Returns the current time as a formatted string (HH:00)"""
		return f"{str(self.time).zfill(2)}:00"
	
	def incrementClock(self):
		"""Increment the clock every 3 seconds, and update the devices accordingly"""

		newTime = self.time + 1 if self.time < 23 else 0
		self.time = newTime
		self.timeString.set(self.getTimeString())

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

	def scheduleDeviceWindow(self, index):
		"""Shows a window that allows a user to view and edit the schedule for a device"""

		device = self.home.getDeviceAt(index)
		deviceType = "plug" if isinstance(device, SmartPlug) else "doorbell"
		deviceSchedule = device.getSchedule()

		scheduleWin = Toplevel(self.win)
		scheduleWin.title(f"Schedule for {deviceType} at index {index}")
		scheduleWin.resizable(False, False)

		deviceLabel = Label(scheduleWin, text=f"Schedule for {deviceType} at index {index}")
		deviceLabel.grid(row=0, column=0, padx=10, pady=10)

		timesFrame = Frame(scheduleWin)
		timesFrame.grid(row=1, column=0, padx=10, pady=10)

		for hr in range(24): # 0 to 23
			timeLabel = Label(timesFrame, text=f"{str(hr).zfill(2)}:00")
			timeLabel.grid(row=hr, column=0, padx=2, pady=2)

			optionsTexts = ["Turn Off", "Turn On", "No Change"]
			optionsValues = [False, True, None]

			# get current text value for the device's schedule
			optionVar = StringVar()
			optionVar.set(optionsTexts[optionsValues.index(deviceSchedule[hr])])

			optionMenu = OptionMenu(
				timesFrame,
				optionVar,
				*optionsTexts
			)

			# when the user changes the value, update the device's schedule
			optionMenu.bind(
				"<Configure>",
				lambda event, i=hr, optionVar=optionVar:
					self.updateDeviceSchedule(index, i, optionsValues[optionsTexts.index(optionVar.get())])
			)

			optionMenu.grid(row=hr, column=1, padx=10, pady=10)
	
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
		file = filedialog.asksaveasfile(
			mode="w",
			defaultextension=".csv",
			filetypes=[("CSV files", "*.csv")]
		)
		
		try:
			file.write(content)
			file.close()
		except Exception as e:
			messagebox.showerror(title="Error Writing File", message=f"{e}")
			return

	def importDevices(self):
		"""Prompts the user to import devices from a file"""
		# warn that this will overwrite the current devices
		sure = messagebox.askyesno(
			title="Importing devices",
			message="Importing  will overwrite the current devices. Are you sure?"
		)
		if not sure:
			return

		file = filedialog.askopenfile(
			mode="r",
			filetypes=[("CSV files", "*.csv")]
		)
		
		try:
			content = file.read()
			file.close()
		except Exception as e:
			messagebox.showerror(title="Error Reading File", message=f"{e}")
			return
		
		self.home.importCSV(content)
		self.refreshDeviceList()

	############################################
	# Run the GUI
	############################################
	def run(self):
		"""Runs the GUI and sets up everything"""
		self.createStaticButtons()
		self.refreshDeviceList()
		self.incrementClock()
		self.win.mainloop()

def main():
	home = setUpHome()
	# print(home)

	system = SmartHomeSystem(home)
	# print(system)
	system.run()

main()