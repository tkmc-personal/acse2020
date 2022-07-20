#!/usr/bin/env python

"""
This module defines a function to run a wind power output
model, defined in a ACSE9.WindModel.WindArray class,
over the entire length of the imported wind resource dataset.
"""

import numpy as np
import time


def Run(Wind_Model, wind_resource):
    """
    Run Wind_Model over the length of wind_resource.

    Parameters
    ----------
    Wind_Model: ACSE9.WindModel.WindArray
        A wind power output model from the ACSE9 package,
        fully initialised with set-up parameters.
    wind_resource: pandas.DataFrame
        A dataframe containing the resource profile imported
        using ACSE9.import_data(root_dir, model).

    Output
    ------
    Wind_Model: ACSE9.WindModel.WindArray
        The same model given in the parameters to this function,
        but simulated over the length of wind_resource.
    wind_P_data: numpy.array
        An array containing the power output, in kW, of the
        wind array defined in Wind_Model for every time-step
        for which data is provided in wind_resource.
    """

    # Run the power output model by looping through entire resource profile
    wind_P_data = np.zeros(len(wind_resource))
    t0 = time.time()
    for i in range(len(wind_resource)):
        '''
        # print message every 1000 iterations for user sanity
        if (i % 1000 == 0):
            print("(WIND MODEL) iteration: ", i, "/", len(wind_resource))
        '''
        # find wind speed (in m/s) at anenometer height at current time-step
        u_anem = wind_resource["wind speed"][i]
        # Calculate wind speed at hub height of the wind turbine, in m/s
        Wind_Model.Calculate_Hub_Wind_Speed(u_anem)
        # Calculate the power output of the wind turbine, in kW
        Wind_Model.Calculate_Power_Output()
        wind_P_data[i] = Wind_Model.Power_Output
    t1 = time.time()
    t = t1-t0

    # print("(WIND MODEL) SIMULATION ENDED. Time elapsed: ", t, " sec\n")

    return Wind_Model, wind_P_data


__author__ = "Teddy Cheung"
__copyright__ = "Copyright 2021, Imperial College London"
__credits__ = ["Teddy Cheung"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Teddy Cheung"
__email__ = "tc20@ic.ac.uk"
__status__ = "Development"
