from backend import *
from tkinter import *
import tkinter.font as Font
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox
from tkinter.ttk import Combobox

IMAGESPATH = "images/"

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
		self.win.resizable(False, False)

		# make sections where our widgets will go
		self.headerFrame = Frame(self.win)
		self.headerFrame.grid(row=0, column=0, padx=10, pady=10)

		self.devicesFrame = Frame(self.win)
		self.devicesFrame.grid(row=1, column=0, padx=10, pady=10)

		self.footerFrame = Frame(self.win)
		self.footerFrame.grid(row=2, column=0, padx=10, pady=10)

		# set up fonts and images (must be done after creating the window)
		self.font = Font.nametofont("TkDefaultFont")
		self.font.configure(
			family="Verdana",
			size=11
		)

		self.monoFont = Font.nametofont("TkFixedFont")
		self.monoFont.configure(
			family="Lucida Console",
			size=10
		)

		self.IMAGEPLUGON = PhotoImage(file=f"{IMAGESPATH}plugon.png")
		self.IMAGEPLUGOFF = PhotoImage(file=f"{IMAGESPATH}plugoff.png")
		self.IMAGEDOORBELLON = PhotoImage(file=f"{IMAGESPATH}doorbellon.png")
		self.IMAGEDOORBELLOFF = PhotoImage(file=f"{IMAGESPATH}doorbelloff.png")
		self.IMAGESLEEP = PhotoImage(file=f"{IMAGESPATH}sleep.png")
		self.IMAGESLEEPOFF = PhotoImage(file=f"{IMAGESPATH}sleepoff.png")

		# time to be used for scheduling
		self.time = 0
		self.timeLabel = Label(
			self.win,
			text=self.getTimeString(),
			font=self.monoFont
		)

	def createStaticButtons(self):
		"""Creates the buttons that will always be present"""
		turnOnAllButt = Button(
			self.headerFrame,
			text="Turn on all",
			command=self.turnOnAll
		)
		turnOnAllButt.grid(row=0, column=0, padx=5)

		turnOffAllButt = Button(
			self.headerFrame,
			text="Turn off all",
			command=self.turnOffAll
		)
		turnOffAllButt.grid(row=0, column=1, padx=5)

		# display the time here
		self.timeLabel.grid(row=0, column=2, padx=5, sticky=E)

		addDeviceButt = Button(
			self.footerFrame,
			text="Add device",
			command=self.addDevicePrompt
		)
		addDeviceButt.grid(row=0, column=0)

		importDevicesButt = Button(
			self.footerFrame,
			text="Import",
			command=self.importDevices
		)
		importDevicesButt.grid(row=0, column=1)

		exportDevicesButt = Button(
			self.footerFrame,
			text="Export",
			command=self.exportDevices
		)
		exportDevicesButt.grid(row=0, column=2)

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

	def createDeviceWidget(self, widgetList, parentFrame, device, i):
		"""Creates a "widget" (row of items) for a device"""
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
		widgetList.append(deviceTypeImage)

		deviceTypeLabel = Label(parentFrame, text=deviceType)
		deviceTypeLabel.grid(row=i, column=1, sticky=W, pady=5, padx=2.5)
		widgetList.append(deviceTypeLabel)

		statusText = "ON" if device.getSwitchedOn() else "OFF"	
		statusLabel = Label(parentFrame, text=statusText)
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
		toggleButt = Button(
			parentFrame,
			text=f"Turn {willBe}",
			padx=5,
			command=lambda: self.toggleDeviceAt(i)
		)
		
		toggleButt.grid(row=i, column=4, pady=5, padx=2.5)
		widgetList.append(toggleButt)

		editButt = Button(
			parentFrame,
			text="Edit",
			padx=5,
			command=lambda: self.editDevicePrompt(i)
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

	def turnOnDeviceAt(self, index):
		"""Turns on the device at the given index"""
		device = self.home.getDeviceAt(index)
		device.switchedOn = True
		self.refreshDeviceList()

	def turnOffDeviceAt(self, index):
		"""Turns off the device at the given index"""
		device = self.home.getDeviceAt(index)
		device.switchedOn = False
		self.refreshDeviceList()

	def toggleDeviceAt(self, index):
		"""Toggles the device at the given index"""
		device = self.home.getDeviceAt(index)
		device.toggleSwitch()
		self.refreshDeviceList()

	def removeDeviceAt(self, index):
		"""Removes the device at the given index"""
		deviceType = "plug" if isinstance(self.home.getDeviceAt(index), SmartPlug) else "doorbell"

		# create an "are you sure" messagebox
		sure = MessageBox.askyesno(title="Removing a device", message=f"Are you sure you want to remove this {deviceType}?")
		if not sure:
			return
		
		self.home.removeDevice(index)
		self.refreshDeviceList()
	
	def addPlug(self, addWin, consumption):
		"""Adds a plug to the home"""
		if consumption < 0 or consumption > 150:
			MessageBox.showwarning(title="Check your values!", text="Consumption rate must be between 0 and 150")
			return

		self.home.addDevice(SmartPlug(consumption))
		addWin.destroy()
		self.refreshDeviceList()

	def editPlug(self, editWin, index, consumption):
		"""Edits a plug at the given index"""
		if consumption < 0 or consumption > 150:
			MessageBox.showwarning(title="Check your values!", text="Consumption rate must be between 0 and 150")
			return

		self.home.getDeviceAt(index).setConsumptionRate(consumption)
		editWin.destroy()
		self.refreshDeviceList()

	def editDoorbell(self, editWin, index, sleepMode):
		"""Edits a doorbell at the given index"""
		self.home.getDeviceAt(index).setSleep(sleepMode)
		editWin.destroy()
		self.refreshDeviceList()

	def addDoorbell(self, addWin):
		"""Adds a doorbell to the home"""
		self.home.addDevice(SmartDoorbell())
		addWin.destroy()
		self.refreshDeviceList()

	def addDevicePrompt(self):
		"""Adds a device to the home, based on user selection"""
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

	def editDevicePrompt(self, index):
		"""Edits a device at the given index"""
		device = self.home.getDeviceAt(index)
		deviceType = "plug" if isinstance(device, SmartPlug) else "doorbell"

		editWin = Toplevel(self.win)
		editWin.title(f"Edit {deviceType}")
		editWin.resizable(False, False)

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
				text="Edit",
				command=lambda: self.editPlug(editWin, index, consumption.get())
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
				text="Edit",
				command=lambda: self.editDoorbell(editWin, index, sleepMode.get())
			)
			editButt.pack(padx=10, pady=10)

		editWin.mainloop()

	def scheduleDevicePrompt(self, index):
		"""Schedules a device at the given index"""
		device = self.home.getDeviceAt(index)
		deviceType = "plug" if isinstance(device, SmartPlug) else "doorbell"
		deviceSchedule = device.getSchedule()

		scheduleWin = Toplevel(self.win)
		scheduleWin.title(f"Schedule for {deviceType}")
		scheduleWin.resizable(False, False)

		timesFrame = Frame(scheduleWin)
		timesFrame.grid(row=0, column=1, padx=10, pady=10)

		for i in range(24): # 0 to 23
			timeLabel = Label(timesFrame, text=f"{str(i).zfill(2)}:00")
			timeLabel.grid(row=i, column=0, padx=2, pady=2)

			options = ["Turn Off", "Turn On", "No Change"] # 0, 1, 2

			actionCombo = Combobox(
				timesFrame,
				values=options,
				width=10,
				state="readonly"
			)
			actionCombo.current(deviceSchedule[i])

			actionCombo.bind(
				"<<ComboboxSelected>>",
				lambda event, i=i, actionCombo=actionCombo: self.updateDeviceSchedule(index, i, actionCombo.current())
			)

			actionCombo.grid(row=i, column=1, padx=10, pady=10)
	

		scheduleWin.mainloop()


	def turnOnAll(self):
		"""Turns on all devices"""
		self.home.turnOnAll()
		self.refreshDeviceList()

	def turnOffAll(self):
		"""Turns off all devices"""
		self.home.turnOffAll()
		self.refreshDeviceList()

	def updateDeviceSchedule(self, index, hour, action):
		"""Updates the schedule for a device at the given index"""
		self.home.getDeviceAt(index).setActionAtHour(hour, action)
		print(self.home.getDeviceAt(index).getSchedule())
	

	def exportDevices(self):
		"""Exports the devices to a file"""
		content = self.home.getCSV()
		file = FileDialog.asksaveasfile(
			mode="w",
			defaultextension=".csv",
			filetypes=[("CSV files", "*.csv")]
		)
		if file is None:
			return
		file.write(content)
		file.close()

	def importDevices(self):
		"""Imports devices from a file"""
		file = FileDialog.askopenfile(
			mode="r",
			filetypes=[("CSV files", "*.csv")]
		)
		if file is None:
			return
		content = file.read()
		file.close()
		self.home.importCSV(content)
		self.refreshDeviceList()

	def tickTimer(self):
		# update devices based on schedule
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
	
		self.win.after(3000, self.tickTimer)

	def getTimeString(self):
		return f"{str(self.time).zfill(2)}:00"

	def run(self):
		self.createStaticButtons()
		self.refreshDeviceList()
		self.tickTimer()
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