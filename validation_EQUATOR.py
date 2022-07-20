#!/usr/bin/env python

"""
This file sets up and runs a full wind-solar PV-storage power output model
using the ACSE9 package and its associated modules.

For help running this file, see the readme at:
<https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20.git>
"""

import ACSE9.import_data as import_data
import ACSE9.WindModel as WindModel
import ACSE9.RunWindModel as RunWindModel
import ACSE9.SolarModel as SolarModel
import ACSE9.RunSolarModel as RunSolarModel
import ACSE9.StorageModel as StorageModel
import ACSE9.RunStorageModel as RunStorageModel
import ACSE9.plot_colour_map as plot_colour_map
import numpy as np
import matplotlib.pyplot as plt


# ------------------------- WIND MODEL -------------------------------
# import wind resource
root_dir = './01 Validation/Inputs/Equator/wind_data.csv'
wind_resource = import_data.import_resource(root_dir, 'WindModel')

# import WTG power curve
root_dir = './01 Validation/Inputs/example_power_curve.csv'
Power_Curve = import_data.import_resource(root_dir, 'Power_Curve')

# set fixed variables
z_hub = 17.0  # wind turbine hub height, in  meters
z_anem = 10.0  # height of the anemometer, in  meters
z_0 = 0.01  # surface roughness, in  meters
WTG_Count = 25  # turbine count
altitude = 0.0  # altitude above sea level, in meters

# initialise wind model in a WindArray class
Wind_Model = WindModel.WindArray(z_hub, z_anem, z_0, Power_Curve,
                                 altitude, WTG_Count)

# Run the power output model by looping through entire resource profile
wind_Output = RunWindModel.Run(Wind_Model, wind_resource)
Wind_Model = wind_Output[0]
wind_P_data = wind_Output[1]

# plot results
root_dir = './01 Validation/Results/Equator/'
plot_colour_map.plot(wind_P_data, 'WindModel', root_dir)

# ------------------------- SOLAR MODEL -------------------------------
# import irradiance resource
root_dir = './01 Validation/Inputs/Equator/irradiance_data.csv'
solar_resource = import_data.import_resource(root_dir, 'SolarModel')

# set fixed variables
time_zone = 2.0  # The time zone in hours east of GMT.
lat = 3.319  # The latitude of the Solar PV facility, in degrees.
long = 36.234  # The longitude of the Solar PV facility, in degrees.
slope = 3.53  # Angle between the ground and the panel surface, degrees.
azimuth = 0.0  # The pole direction in which the panel faces, in degrees.
dt = 1.0  # The time-step size, in hours.
Module_Capacity = 1.0  # The rated capacity, in kW.
Module_Count = 25  # The number of solar photovoltaic modules in the array.
albedo = 0.2  # The ground reflectance, a percentage expressed in decimal.
Derating_Factor = 0.8  # Scale factor to account for reduced real-life output.

# initialise solar model in a SolarArray class
Solar_Model = SolarModel.SolarArray(time_zone, long, lat, slope, azimuth, dt,
                                    Module_Capacity, Module_Count, albedo,
                                    Derating_Factor)

# Run the power output model by looping through entire resource profile
solar_Output = RunSolarModel.Run(Solar_Model, solar_resource)
Solar_Model = solar_Output[0]
solar_P_data = solar_Output[1]

# plot results
root_dir = './01 Validation/Results/Equator/'
plot_colour_map.plot(solar_P_data, 'SolarModel', root_dir)

# ------------------------- STORAGE MODEL -------------------------------
# Import load data
root_dir = './01 Validation/Inputs/Equator/load_data.csv'
load = import_data.import_resource(root_dir, 'StorageModel')

# set fixed variables
dt = 1.0  # The time-step size, in hours.
count = 100  # number of li-ion cells
v_nominal = 6.0  # nominal voltage of li-ion cells, in V
SoC = 100.0  # initial state-of-charge, %
SoC_min = 20.0  # minimum state-of-charge of li-ion cells, %
i_charge = 167.0  # maximum charging current (abs) of each li-ion cell, in A
i_discharge = 500.0  # maximum discharge current of each li-ion cell, in A
q_nominal = 167.0  # nominal capacity of each li-ion cell, in Ah
eff_round = 0.95  # roundtrip efficiency of each li-ion cell

# initialise solar model in a SolarArray class
Storage_Model = StorageModel.StorageArray(dt, count, v_nominal, SoC,
                                          SoC_min, i_charge,
                                          i_discharge, q_nominal,
                                          eff_round)

root_dir = './01 Validation/HOMER results/Equator/HOMER_validation_data.csv'

# Run the power output model by looping through entire resource profile
storage_Output = RunStorageModel.Run(Storage_Model, load,
                                     solar_P_data, wind_P_data)
Storage_Model = storage_Output[0]
storage_P_data = storage_Output[1]
storage_SoC_data = storage_Output[2]

# plot results
root_dir = './01 Validation/Results/Equator/'
plot_colour_map.plot(storage_P_data, 'StorageModel', root_dir)

# ------------------------ UNMET LOAD -----------------------------
generation = wind_P_data + solar_P_data + storage_P_data  # total generation
# Calculate unmet load for every time-step
ACSE9_unmet_load = load["load"].to_numpy() - generation
for i in range(len(ACSE9_unmet_load)):
    # set load surplus to zero with regards to unmet load
    if (ACSE9_unmet_load[i] < 0):
        ACSE9_unmet_load[i] = 0
# Calculate capacity shortage fraction
total_unmet_load = np.sum(ACSE9_unmet_load)  # in kWh
total_load = np.sum(load["load"].to_numpy())  # in kWh
capacity_shortage_fraction = total_unmet_load / total_load
print("\nCapacity shortage fraction of system: ", capacity_shortage_fraction)

# ------------------- HOMER RESULTS (VALIDATION) -------------------------
root_dir = './01 Validation/HOMER results/Equator/HOMER_validation_data.csv'
# import expected results from HOMER and split into individual numpy arrays
HOMER_P_data = import_data.import_resource(root_dir, 'HOMER')
HOMER_wind_P_data = HOMER_P_data["power wind"].to_numpy()
HOMER_solar_P_data = HOMER_P_data["power solar"].to_numpy()
HOMER_storage_P_data = HOMER_P_data["power storage"].to_numpy()
HOMER_SoC_data = HOMER_P_data["SoC"].to_numpy()
HOMER_unmet_load = HOMER_P_data["unmet load"].to_numpy()
# calculate difference between ACSE9 model and HOMER
wind_delta = HOMER_wind_P_data - wind_P_data
solar_delta = HOMER_solar_P_data - solar_P_data
storage_delta = HOMER_storage_P_data - storage_P_data
SoC_delta = HOMER_SoC_data - storage_SoC_data
# plot colour maps for HOMER results
root = './01 Validation/Results/Equator/'
plot_colour_map.plot(HOMER_wind_P_data, 'WindModel', root, HOMER=True)
plot_colour_map.plot(HOMER_solar_P_data, 'SolarModel', root, HOMER=True)
plot_colour_map.plot(HOMER_storage_P_data, 'StorageModel', root, HOMER=True)

# plot power deltas for wind, solar and storage
n = np.linspace(0, len(wind_delta)-1, len(wind_delta))
fig, axs = plt.subplots(1, figsize=(10, 5))
axs.set_title("Difference in HOMER Model and ACSE9 Power Output")
axs.set_xlabel("datetime (n = 0 to 8759; 24 hours, 365 days)")
Delta = r'$\Delta$'  # LaTeX Delta is acting strange when called in function
axs.set_ylabel(Delta + "Power Output (kW)")
axs.plot(n, wind_delta, label='wind', color='b')
axs.plot(n, solar_delta, label='solar', color='r')
axs.plot(n, storage_delta, label='storage', color='g')
axs.legend()
foo = './01 Validation/Results/Equator/HomerModel_vs_ACSE9Model Power Output'
fig.savefig(foo)

# plot unmet load for HOMER and for ACSE9 model
fig, axs = plt.subplots(1, figsize=(10, 5))
note = '\nNote: HOMER values are not negative in reality, '
note = note + 'and are plotted as such for readability.'
axs.set_title("Unmet Load Calculated in HOMER Model and ACSE9 Model" + note, y=1.005)
axs.set_xlabel("datetime (n = 0 to 8759; 24 hours, 365 days)")
axs.set_ylabel("Unmet load (kW)")
axs.plot(n, ACSE9_unmet_load, label='ACSE9', color='r')
axs.plot(n, -HOMER_unmet_load, label='HOMER', color='g')
axs.legend()
fig.savefig('./01 Validation/Results/Equator/HomerModel_vs_ACSE9Model Unmet Load')

# print results
print('\nWIND VALIDATION RESULTS:')
print('Minimum Power Output (kW):\t HOMER Pro =',
      min(HOMER_wind_P_data), '\tACSE9 =', min(wind_P_data))
print('Maximum Power Output (kW):\t HOMER Pro =',
      max(HOMER_wind_P_data), '\tACSE9 =', max(wind_P_data))
print('Average Power Output (kW):\t HOMER Pro =',
      np.average(HOMER_wind_P_data), '\tACSE9 =', np.average(wind_P_data))
error = (np.average(HOMER_wind_P_data) - np.average(wind_P_data))
error = (error / np.average(HOMER_wind_P_data)) * 100
print('\taverage error (%):\t',np.round(error, 3))

print('\nSOLAR VALIDATION RESULTS:')
print('Minimum Power Output (kW):\t HOMER Pro =',
      min(HOMER_solar_P_data), '\tACSE9 =', min(solar_P_data))
print('Maximum Power Output (kW):\t HOMER Pro =',
      max(HOMER_solar_P_data), '\tACSE9 =', max(solar_P_data))
print('Average Power Output (kW):\t HOMER Pro =',
      np.average(HOMER_solar_P_data), '\tACSE9 =', np.average(solar_P_data))
error = (np.average(HOMER_solar_P_data) - np.average(solar_P_data))
error = (error / np.average(HOMER_solar_P_data)) * 100
print('\taverage error (%):\t',np.round(error, 3))

print('\nSTORAGE VALIDATION RESULTS:')
print('Minimum Power Output (kW):\t HOMER Pro =',
      min(HOMER_storage_P_data), '\tACSE9 =', min(storage_P_data))
print('Maximum Power Output (kW):\t HOMER Pro =',
      max(HOMER_storage_P_data), '\tACSE9 =', max(storage_P_data))
print('Average Power Output (kW):\t HOMER Pro =',
      np.average(HOMER_storage_P_data), '\tACSE9 =', np.average(storage_P_data))
error = (np.average(HOMER_storage_P_data) - np.average(storage_P_data))
error = (error / np.average(HOMER_storage_P_data)) * 100
print('\taverage error (%):\t',np.round(error, 3))


__author__ = "Teddy Cheung"
__copyright__ = "Copyright 2021, Imperial College London"
__credits__ = ["Teddy Cheung"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Teddy Cheung"
__email__ = "tc20@ic.ac.uk"
__status__ = "Development"

