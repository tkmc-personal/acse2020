#!/usr/bin/env python

"""
This file sets up and runs a full wind-solar PV-storage
exhaustive search sizing optimisation using the ACSE9 package
and its associated modules.
"""

import ACSE9.import_data as import_data
import ACSE9.WindModel as WindModel
import ACSE9.RunWindModel as RunWindModel
import ACSE9.SolarModel as SolarModel
import ACSE9.RunSolarModel as RunSolarModel
import ACSE9.StorageModel as StorageModel
import ACSE9.RunStorageModel as RunStorageModel
import ACSE9.FinancialModel as FinancialModel
import ACSE9.plot_colour_map as plot_colour_map
import numpy as np
import time


# ------------------------- SEARCH SPACE -------------------------------
# Search space
SS = np.linspace(0, 100, 11).tolist()

# WIND MODEL search space
WTG_Count_SS = SS
wind_P_data_SS = []
Wind_Model_SS = []
WTG_Count_Analysis = []  # list for saving feasible designs
# SOLAR MODEL search space
Module_Count_SS = SS
solar_P_data_SS = []
Solar_Model_SS = []
Module_Count_Analysis = []  # list for saving feasible designs
# STORAGE MODEL search space
Cell_Count_SS = SS
storage_P_data_SS = []
storage_SoC_data_SS = []
Storage_Model_SS = []
Cell_Count_Analysis = []  # list for saving feasible designs
# Constraint on capacity shortage fraction for feasible/infeasible
capacity_shortage_max = 0.01  # percentage in decimal
capacity_shortage_analysis = []  # list for saving data of designs

t0 = time.time()
# ------------------------- WIND MODEL -------------------------------
# import wind resource
root_dir = './01 Validation/Inputs/Equator/wind_data.csv'
wind_resource = import_data.import_resource(root_dir, 'WindModel')
# import WTG power curve
root_dir = './01 Validation/Inputs/example_power_curve.csv'
Power_Curve = import_data.import_resource(root_dir, 'Power_Curve')

# run wind model over search space
for WTG_Count in WTG_Count_SS:
    # print for user sanity
    print('Evaluating [WTGs]: ', [WTG_Count])

    if (WTG_Count == 0):
        Wind_Model = 0
        wind_P_data = np.zeros(len(wind_resource["datetime"]))
    else:
        # set fixed variables
        z_hub = 17.0  # wind turbine hub height, in  meters
        z_anem = 10.0  # height of the anemometer, in  meters
        z_0 = 0.01  # surface roughness, in  meters
        altitude = 0.0  # altitude above sea level, in meters

        # initialise wind model in a WindArray class
        Wind_Model = WindModel.WindArray(z_hub, z_anem, z_0, Power_Curve,
                                         altitude, WTG_Count)

        # Run the power output model by looping through entire resource profile
        wind_Output = RunWindModel.Run(Wind_Model, wind_resource)
        Wind_Model = wind_Output[0]
        wind_P_data = wind_Output[1]

    # Save results for future search space analysis
    wind_P_data_SS.append(wind_P_data)
    Wind_Model_SS.append(Wind_Model)

# ------------------------- SOLAR MODEL -------------------------------
# import irradiance resource
root_dir = './01 Validation/Inputs/Equator/irradiance_data.csv'
solar_resource = import_data.import_resource(root_dir, 'SolarModel')

# run solar model over search space
for Module_Count in Module_Count_SS:
    # print for user sanity
    print('Evaluating [Modules]: ', [Module_Count])

    if (Module_Count == 0):
        Solar_Model = 0
        solar_P_data = np.zeros(len(solar_resource["datetime"]))
    else:
        # set fixed variables
        time_zone = 2.0  # The time zone in hours east of GMT.
        lat = 3.319  # The latitude of the Solar PV facility, in degrees.
        long = 36.234  # The longitude of the Solar PV facility, in degrees.
        slope = 3.53  # Angle between ground and panel surface, degrees.
        azimuth = 0.0  # Pole direction in which the panel faces, in degrees.
        dt = 1.0  # The time-step size, in hours.
        Module_Capacity = 1.0  # The rated capacity, in kW.
        albedo = 0.2  # Ground reflectance, percentage expressed in decimal.
        Derating_Factor = 0.8  # Factor to account for reduced reallife output.

        # initialise solar model in a SolarArray class
        Solar_Model = SolarModel.SolarArray(time_zone, long, lat, slope,
                                            azimuth, dt, Module_Capacity,
                                            Module_Count, albedo,
                                            Derating_Factor)

        # Run the power output model by looping through entire resource profile
        solar_Output = RunSolarModel.Run(Solar_Model, solar_resource)
        Solar_Model = solar_Output[0]
        solar_P_data = np.array(solar_Output[1])

    # Save results for future search space analysis
    solar_P_data_SS.append(solar_P_data)
    Solar_Model_SS.append(Solar_Model)

# ------------------------- STORAGE MODEL -------------------------------
# Import load data
root_dir = './01 Validation/Inputs/Equator/load_data.csv'
load = import_data.import_resource(root_dir, 'StorageModel')
# see below comments on system feasibility
Cell_Count_previous = -1
WTG_Count_previous = -1
Module_Count_previous = -1
feasible = False
total_load = np.sum(load["load"].to_numpy())  # in kWh
# run storage model over search space
# Note: this is a 'naive' approach in which every single possible
# combination is calculated.
for Cell_Count in Cell_Count_SS:
    for wind_P_data in wind_P_data_SS:
        for solar_P_data in solar_P_data_SS:
            # get number of WTG in the current config
            for i in range(len(wind_P_data_SS)):
                if (np.allclose(wind_P_data_SS[i], wind_P_data)):
                    WTG_Count = WTG_Count_SS[i]
            # get number of Solar PV modules in the current config
            for i in range(len(solar_P_data_SS)):
                if (np.allclose(solar_P_data_SS[i], solar_P_data)):
                    Module_Count = Module_Count_SS[i]

            # print for user sanity
            foo = [Cell_Count, WTG_Count, Module_Count]
            print('Evaluating [Cells, WTGs, Module]: ', foo)

            if (Cell_Count == 0):
                Storage_Model = 0
                storage_P_data = np.zeros(len(load["datetime"]))
                storage_SoC_data = np.zeros(len(load["datetime"]))
            else:
                # set fixed variables
                dt = 1.0  # The time-step size, in hours.
                v_nominal = 6.0  # nominal voltage of li-ion cells, in V
                SoC = 100.0  # initial state-of-charge, %
                SoC_min = 20.0  # min state-of-charge of li-ion cells, %
                i_charge = 167.0  # max charge current (abs) of each cell,A
                i_discharge = 500.0  # max discharge current of each cell,A
                q_nominal = 167.0  # nominal capacity of each cell, Ah
                eff_round = 0.95  # roundtrip efficiency of each cell

                # initialise solar model in a SolarArray class
                Storage_Model = StorageModel.StorageArray(dt, Cell_Count,
                                                          v_nominal,
                                                          SoC, SoC_min,
                                                          i_charge,
                                                          i_discharge,
                                                          q_nominal,
                                                          eff_round)

                # Run power model by looping through resource profile
                storage_Output = RunStorageModel.Run(Storage_Model, load,
                                                     solar_P_data,
                                                     wind_P_data)
                Storage_Model = storage_Output[0]
                storage_P_data = storage_Output[1]
                storage_SoC_data = storage_Output[2]

                # calculate overall generation of wind + solar + storage
                generation = wind_P_data + solar_P_data + storage_P_data
                # Calculate unmet load for every time-step
                unmet_load = load["load"].to_numpy() - generation
                for foo in range(len(unmet_load)):
                    # set load surplus to zero with regards to unmet load
                    if (unmet_load[foo] < 0):
                        unmet_load[foo] = 0
                total_unmet_load = np.sum(unmet_load)  # in kWh
                # Calculate capacity shortage fraction
                capacity_shortage_fraction = total_unmet_load / total_load
                # check system feasibility
                foo = capacity_shortage_fraction <= capacity_shortage_max
                feasible = foo  # pep8 made me split this up
                if (feasible):
                    # save the configuration and its data
                    storage_P_data_SS.append(storage_P_data)
                    storage_SoC_data_SS.append(storage_SoC_data)
                    Storage_Model_SS.append(Storage_Model)
                    Cell_Count_Analysis.append(Cell_Count)
                    WTG_Count_Analysis.append(WTG_Count)
                    Module_Count_Analysis.append(Module_Count)
                    CSF = capacity_shortage_fraction  # shortened for pep8
                    capacity_shortage_analysis.append(CSF)
                if not (feasible):
                    # don't save configuration
                    None

"""
The variables `Cell_Count_Analysis`, `WTG_Count_Analysis`, and
`Module_Count_Analysis` now contain the count of each component
at indexes where the combination of cells, WTGs and modules constitute
a feasible design (a design which reaches the constraint on maximum
capacity shortage fraction). For example, if:
- `Cell_Count_Analysis` = [25, 100]
- `WTG_Count_Analysis` = [25, 75]
- `Module_Count_Analysis` = [25, 0]
then, there are two feasible hybrid power plant designs:
- 25-cells + 25-WTGs + 25-PV Modules
- 100-cells + 75-WTGs + 0-PV Modules
"""

# ------------------------- FINANCIAL MODEL -------------------------------
Cell_DCF_Analysis = []  # list for discounted cashflow
WTG_DCF_Analysis = []
Module_DCF_Analysis = []
Plant_NPC_Analysis = []  # list for NPC of each feasible plant design
# Run the financial model on the feasible designs
for i in range(len(capacity_shortage_analysis)):
    # Economic data:
    project_lifetime = 25  # years
    inflation_rate = 0.02  # percentage in decimal
    nominal_discount_rate = 0.08  # percentage in decimal

    # Storage component data:
    Cell_Count = Cell_Count_Analysis[i]
    Cell_lifetime = 15  # years
    Cell_capital_cost = 550  # USD per component
    Cell_replacement_cost = 550  # USD per component
    Cell_OM_cost = 10  # USD per year
    Cell_Data = [Cell_lifetime,
                 project_lifetime,
                 inflation_rate,
                 nominal_discount_rate,
                 Cell_capital_cost,
                 Cell_replacement_cost,
                 Cell_OM_cost,
                 Cell_Count]

    Cell_finance = FinancialModel.Calculate_NPC(Cell_Data[0],
                                                Cell_Data[1],
                                                Cell_Data[2],
                                                Cell_Data[3],
                                                Cell_Data[4],
                                                Cell_Data[5],
                                                Cell_Data[6],
                                                Cell_Data[7])
    Cell_cashflow = Cell_finance[0]
    Cell_NPC = Cell_finance[1]

    # WTG component data:
    WTG_Count = WTG_Count_Analysis[i]
    WTG_lifetime = 20  # years
    WTG_capital_cost = 18000  # USD per component
    WTG_replacement_cost = 18000  # USD per component
    WTG_OM_cost = 180  # USD per year
    WTG_Data = [WTG_lifetime,
                project_lifetime,
                inflation_rate,
                nominal_discount_rate,
                WTG_capital_cost,
                WTG_replacement_cost,
                WTG_OM_cost,
                WTG_Count]
    WTG_finance = FinancialModel.Calculate_NPC(WTG_Data[0],
                                               WTG_Data[1],
                                               WTG_Data[2],
                                               WTG_Data[3],
                                               WTG_Data[4],
                                               WTG_Data[5],
                                               WTG_Data[6],
                                               WTG_Data[7])
    WTG_cashflow = WTG_finance[0]
    WTG_NPC = WTG_finance[1]

    # Module component data:
    Module_Count = Module_Count_Analysis[i]
    Module_lifetime = 20  # years
    Module_capital_cost = 2500  # USD per component
    Module_replacement_cost = 2500  # USD per component
    Module_OM_cost = 10  # USD per year
    Module_Data = [Module_lifetime,
                   project_lifetime,
                   inflation_rate,
                   nominal_discount_rate,
                   Module_capital_cost,
                   Module_replacement_cost,
                   Module_OM_cost,
                   Module_Count]
    Module_finance = FinancialModel.Calculate_NPC(Module_Data[0],
                                                  Module_Data[1],
                                                  Module_Data[2],
                                                  Module_Data[3],
                                                  Module_Data[4],
                                                  Module_Data[5],
                                                  Module_Data[6],
                                                  Module_Data[7])
    Module_cashflow = Module_finance[0]
    Module_NPC = Module_finance[1]

    Cell_DCF_Analysis.append(Cell_cashflow)
    WTG_DCF_Analysis.append(WTG_cashflow)
    Module_DCF_Analysis.append(Module_cashflow)

    Plant_NPC = Cell_NPC + WTG_NPC + Module_NPC
    Plant_NPC_Analysis.append(Plant_NPC)

# ------------------------- OPTIMAL SOLUTION -------------------------------
# The optimal solution the the feasible design with the lowest NPC
index = Plant_NPC_Analysis.index(min(Plant_NPC_Analysis))
Cell_Count = Cell_Count_Analysis[index]
WTG_Count = WTG_Count_Analysis[index]
Module_Count = Module_Count_Analysis[index]
capacity_shortage_fraction = capacity_shortage_analysis[index]
# Save colour maps of the optimal solution
wind_P_data = wind_P_data_SS[WTG_Count_SS.index(WTG_Count)]
solar_P_data = solar_P_data_SS[Module_Count_SS.index(Module_Count)]
storage_P_data = storage_P_data_SS[index]
root = './02 Results/'
plot_colour_map.plot(wind_P_data, 'WindModel', root)
plot_colour_map.plot(solar_P_data, 'SolarModel', root)
plot_colour_map.plot(storage_P_data, 'StorageModel', root)
# Save cash flow analysis of optimal plant design as csv
root = root + 'storage-discounted-cash-flow.csv'
Cell_DCF_Analysis[index].to_csv(root, index=False)
root = root + 'wind-discounted-cash-flow.csv'
WTG_DCF_Analysis[index].to_csv(root, index=False)
root = root + 'solar-discounted-cash-flow.csv'
Module_DCF_Analysis[index].to_csv(root, index=False)
# print result
print('Optimal solution:')
print(Cell_Count, '-Cells + ', WTG_Count, '-WTGs + ', Module_Count, '-Modules')
print('NPC = ', Plant_NPC_Analysis[index])

t1 = time.time()
t = t1 - t0
print('Total time elapsed: ', t/60, ' minutes')

result = [Cell_Count, WTG_Count, Module_Count]
np.savetxt('result.csv', result)


__author__ = "Teddy Cheung"
__copyright__ = "Copyright 2021, Imperial College London"
__credits__ = ["Teddy Cheung"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Teddy Cheung"
__email__ = "tc20@ic.ac.uk"
__status__ = "Development"
