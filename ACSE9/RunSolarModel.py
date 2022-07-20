#!/usr/bin/env python

"""
This module defines a function to run a solar power output
model, defined in a ACSE9.SolarModel.SolarArray class,
over the entire length of the imported solar resource dataset.
"""

import numpy as np
import time


def Run(Solar_Model, solar_resource):
    """
    Run Wind_Model over the length of wind_resource.

    Parameters
    ----------
    Solar_Model: ACSE9.SolarModel.SolarArray
        A solar power output model from the ACSE9 package,
        fully initialised with set-up parameters.
    solar_resource: pandas.DataFrame
        A dataframe containing the resource profile imported
        using ACSE9.import_data(root_dir, model).

    Output
    ------
    Solar_Model: ACSE9.SolarModel.SolarArray
        The same model given in the parameters to this function,
        but simulated over the length of solar_resource.
    solar_P_data: numpy.array
        An array containing the power output, in kW, of the
        solar array defined in Solar_Model for every time-step
        for which data is provided in solar_resource.
    """

    # Run the power output model by looping through entire resource profile
    solar_P_data = np.zeros(len(solar_resource))
    t0 = time.time()
    for i in range(len(solar_resource)):
        '''
        # print message every 1000 iterations for user sanity
        if (i % 1000 == 0):
            print("(SOLAR MODEL) iteration: ", i, "/", len(solar_resource))
        '''
        # day of the year (1-365)
        n = solar_resource["datetime"][i].date().timetuple().tm_yday
        # civil time, in hours
        hour = (solar_resource["datetime"][i].time().hour)
        minute = (solar_resource["datetime"][i].time().minute/60)
        t_c = hour + minute
        # irradiance at current time-step, in kW/m^2
        G = solar_resource["irradiance"][i]
        # Run calculations within Solar_Model object class
        Solar_Model.Calculate_Solar_Declination(n)
        Solar_Model.Calculate_Solar_Time(n, t_c)
        Solar_Model.Calculate_Hour_Angle()
        Solar_Model.Calculate_Extraterrestrial_Normal_Radiation(n)
        Solar_Model.Calculate_Angle_of_Incidence()
        Solar_Model.Calculate_Extraterrestrial_Horizontal_Radiation(n, t_c, G)
        Solar_Model.Calculate_Beam_Ratio()
        Solar_Model.Calculate_Clearness_Index(G)
        Solar_Model.Calculate_Diffuse_Beam_Radiation(G)
        Solar_Model.Calculate_Anistropy_Index()
        Solar_Model.Calculate_Horizon_Factor(G)
        Solar_Model.Calculate_Indcident_Radiation(G)
        Solar_Model.Calculate_Power_Output()
        solar_P_data[i] = Solar_Model.Power_Output

        t1 = time.time()
        t = t1-t0

    # print("(SOLAR MODEL) SIMULATION ENDED. Time elapsed: ", t, " sec\n")

    return Solar_Model, solar_P_data


__author__ = "Teddy Cheung"
__copyright__ = "Copyright 2021, Imperial College London"
__credits__ = ["Teddy Cheung"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Teddy Cheung"
__email__ = "tc20@ic.ac.uk"
__status__ = "Development"
