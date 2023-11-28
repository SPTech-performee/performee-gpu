from pyadl import *

device = ADLManager.getInstance().getDevices()
print(device.getCurrentTemperature())
print(device.getCurrentUsage())
