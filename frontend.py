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
		pass

def main():
	home = setUpHome()
	print(home)

	system = SmartHomeSystem(home)
	print(system)

main()