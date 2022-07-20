#!/usr/bin/env python

"""
This module defines a function to run a storage power output
model, defined in a ACSE9.StorageModel.StorageArray class,
over the entire length of the imported load dataset.
"""

import numpy as np
import time


def Run(Storage_Model, load, solar_P_data, wind_P_data):
    """
    Run Wind_Model over the length of wind_resource.

    Parameters
    ----------
    Storage_Model: ACSE9.StorageModel.StorageArray
        A storage power output model from the ACSE9 package,
        fully initialised with set-up parameters.
    load: pandas.DataFrame
        A dataframe containing the load profile imported
        using ACSE9.import_data(root_dir, model).
    solar_P_data: numpy.array
        An array containing the power output, in kW, of the
        solar array defined in Solar_Model for every time-step
        for which data is provided in solar_resource.
        (see ACSE9.RunSolarModel.Run).
    wind_P_data: numpy.array
        An array containing the power output, in kW, of the
        wind array defined in Wind_Model for every time-step
        for which data is provided in wind_resource.
        (see ACSE9.RunWindModel.Run).

    Output
    ------
    Storage_Model: ACSE9.StorageModel.StorageArray
        The same model given in the parameters to this function,
        but simulated over the length of solar_resource.
    storage_P_data: numpy.array
        An array containing the power output, in kW, of the
        storage array defined in Storage_Model for every time-step
        for which data is provided in load.
    storage_SoC_data: numpy.array
        An array containing the state-of-charge, in %, of the
        storage array defined in Storage_Model for every time-step
        for which data is provided in load.
    """

    # Run the power output model by looping through entire resource profile
    storage_P_data = np.zeros(len(load))
    storage_SoC_data = np.zeros(len(load))
    t0 = time.time()
    for i in range(len(load)):
        '''
        # print message every 1000 iterations for user sanity
        if (i % 1000 == 0):
            print("(STORAGE MODEL) iteration: ", i, "/", len(load))
        '''
        P_solar = solar_P_data[i]
        P_wind = wind_P_data[i]
        P_load = load["load"][i]

        Storage_Model.Calculate_Charge_Discharge(P_solar, P_wind, P_load)
        storage_P_data[i] = Storage_Model.Power_Output
        storage_SoC_data[i] = Storage_Model.SoC

    t1 = time.time()
    t = t1-t0

    # print("(STORAGE MODEL) SIMULATION ENDED. Time elapsed: ", t, " sec\n")

    return Storage_Model, storage_P_data, storage_SoC_data


__author__ = "Teddy Cheung"
__copyright__ = "Copyright 2021, Imperial College London"
__credits__ = ["Teddy Cheung"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Teddy Cheung"
__email__ = "tc20@ic.ac.uk"
__status__ = "Development"
