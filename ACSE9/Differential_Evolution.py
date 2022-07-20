#!/usr/bin/env python


import ACSE9.import_data as import_data
import ACSE9.WindModel as WindModel
import ACSE9.RunWindModel as RunWindModel
import ACSE9.SolarModel as SolarModel
import ACSE9.RunSolarModel as RunSolarModel
import ACSE9.StorageModel as StorageModel
import ACSE9.RunStorageModel as RunStorageModel
import ACSE9.FinancialModel as FinancialModel
import numpy as np


def objective(x):
    # Economic data:
    project_lifetime = 25  # years
    inflation_rate = 0.02  # percentage in decimal
    nominal_discount_rate = 0.08  # percentage in decimal

    # Storage component data:
    Cell_Count = x[0]
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
    Cell_NPC = Cell_finance[1]

    # WTG component data:
    WTG_Count = x[1]
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
    WTG_NPC = WTG_finance[1]

    # Module component data:
    Module_Count = x[2]
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
    Module_NPC = Module_finance[1]

    Plant_NPC = Cell_NPC + WTG_NPC + Module_NPC

    return Plant_NPC


def constraint1(x):
    # ------------------------- WIND MODEL -------------------------------
    # import wind resource
    root_dir = './01 Validation/Inputs/Equator/wind_data.csv'
    wind_resource = import_data.import_resource(root_dir, 'WindModel')

    # import WTG power curve
    root_dir = './01 Validation/Inputs/example_power_curve.csv'
    Power_Curve = import_data.import_resource(root_dir, 'Power_Curve')

    # set fixed variables
    WTG_Count = x[1]
    z_hub = 17.0  # wind turbine hub height, in  meters
    z_anem = 10.0  # height of the anemometer, in  meters
    z_0 = 0.01  # surface roughness, in  meters
    altitude = 0.0  # altitude above sea level, in meters

    # initialise wind model in a WindArray class
    Wind_Model = WindModel.WindArray(z_hub, z_anem, z_0, Power_Curve,
                                     altitude, WTG_Count)

    # Run the power output model by looping through entire resource profile
    wind_Output = RunWindModel.Run(Wind_Model, wind_resource)
    wind_P_data = wind_Output[1]

    # ------------------------- SOLAR MODEL -------------------------------
    # import irradiance resource
    root_dir = './01 Validation/Inputs/Equator/irradiance_data.csv'
    solar_resource = import_data.import_resource(root_dir, 'SolarModel')

    # set fixed variables
    Module_Count = x[2]
    time_zone = 2.0  # The time zone in hours east of GMT.
    lat = 3.319  # The latitude of the Solar PV facility, in degrees.
    long = 36.234  # The longitude of the Solar PV facility, in degrees.
    slope = 3.53  # Angle between the ground and the panel surface, degrees.
    azimuth = 0.0  # The pole direction in which the panel faces, in degrees.
    dt = 1.0  # The time-step size, in hours.
    Module_Capacity = 1.0  # The rated capacity, in kW.
    albedo = 0.2  # The ground reflectance, a percentage expressed in decimal.
    Derating_Factor = 0.8  # Factor to account for reduced real-life output.

    # initialise solar model in a SolarArray class
    Solar_Model = SolarModel.SolarArray(time_zone, long, lat, slope, azimuth,
                                        dt, Module_Capacity, Module_Count,
                                        albedo, Derating_Factor)

    # Run the power output model by looping through entire resource profile
    solar_Output = RunSolarModel.Run(Solar_Model, solar_resource)
    solar_P_data = solar_Output[1]

    # ------------------------- STORAGE MODEL -------------------------------
    # Import load data
    root_dir = './01 Validation/Inputs/Equator/load_data.csv'
    load = import_data.import_resource(root_dir, 'StorageModel')

    # set fixed variables
    Cell_Count = x[0]
    dt = 1.0  # The time-step size, in hours.
    v_nominal = 6.0  # nominal voltage of li-ion cells, in V
    SoC = 100.0  # initial state-of-charge, %
    SoC_min = 20.0  # minimum state-of-charge of li-ion cells, %
    i_charge = 167.0  # maximum charging current (abs) of each li-ion cell,in A
    i_discharge = 500.0  # maximum discharge current of each li-ion cell, in A
    q_nominal = 167.0  # nominal capacity of each li-ion cell, in Ah
    eff_round = 0.95  # roundtrip efficiency of each li-ion cell

    # initialise solar model in a SolarArray class
    Storage_Model = StorageModel.StorageArray(dt, Cell_Count, v_nominal, SoC,
                                              SoC_min, i_charge,
                                              i_discharge, q_nominal,
                                              eff_round)

    # Run the power output model by looping through entire resource profile
    storage_Output = RunStorageModel.Run(Storage_Model, load,
                                         solar_P_data, wind_P_data)
    storage_P_data = storage_Output[1]

    # ----------------------- SYSTEM FEASIBILITY -----------------------------
    generation = wind_P_data + solar_P_data + storage_P_data  # total gen
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

    return capacity_shortage_fraction
