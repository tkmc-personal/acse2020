#!/usr/bin/env python

"""
This module defines a wind power output model, inside a python class.

The modelling methods used in this module are based upon
Hybrid Optimisation of Multiple Energy Resources (HOMER) software,
developed by HOMER Energy LLC.

Descriptions of the modelling choices can be found at either:
- https://www.homerenergy.com/products/pro/docs/latest/homers_calculations.html
"""

import sys
import numpy as np
import pandas as pd


class WindArray:
    """
    A class defining a Wind Turbine Generator (WTG) array power output model.

    Fixed attributes
    ----------------
    self.z_hub: float
        The hub height of the WTGs, in m.
    self.z_anem: float
        The height of anemometer, in m.
    self.z_0: float
        The surface roughness, in  m.
    self.Power_Curve: pd.DataFrame
        A pandas dataframe containing the power curve of the WTG model used
        in the array. Power_Curve must include a column named "wind speed",
        which contains the hub height wind speeds (in m/s) at which the power
        curve is defined; and a column named "power", which contains the
        power output (in kW) predicted by the power curve at the
        corresponding wind speed. All data in Power_Curve should be defined
        at standard air density of 1.225 kg/m^3.
    self.altitude: float
            The average altitude above sea level of the WTG array, in m.
    self.WTG_Count: int
            The number of WTG in the array.

    Variable attributes
    -------------------
    self.u_anem: float
        The wind speed at anemometer height, in m/s.
        u_anem corresponds to the wind speed in the provided wind resource
        profile, at the given time-step.
    self.Hub_Wind_Speed: float
        The wind speed at the hub height of the WTG, in m/s.
    self.Power_Output: float
        The power output, adjusted for air density, of the WTG array, in kW.

    """
    # Note: WTG = Wind Turbine Generator
    def __init__(self, z_hub, z_anem, z_0, Power_Curve, altitude, WTG_Count):
        # Initialise class attributes
        # ----- fixed class attributes: -----
        # hub height of the WTG, in m.
        if isinstance(z_hub, float):
            self.z_hub = z_hub
        elif not isinstance(z_hub, float):
            sys.exit("Error: z_hub must be of type <float>")
        # height of anemometer, in m.
        if isinstance(z_anem, float):
            self.z_anem = z_anem
        elif not isinstance(z_anem, float):
            sys.exit("Error: z_anem must be of type <float>")
        # The surface roughness, in  m.
        if isinstance(z_0, float):
            self.z_0 = z_0
        elif not isinstance(z_0, float):
            sys.exit("Error: z_0 must be of type <float>")
        # The power curve of the WTG model used in the array, pandas dataframe.
        if isinstance(Power_Curve, pd.DataFrame):
            self.Power_Curve = Power_Curve
        elif not isinstance(Power_Curve, pd.DataFrame):
            sys.exit("Error: Power_Curve must be of type <pd.DataFrame>")
        # The average altitude above sea level of the WTG array, in m.
        if isinstance(altitude, float):
            self.altitude = altitude
        elif not isinstance(altitude, float):
            sys.exit("Error: altitude must be of type <float>")
        # The number of WTG in the array.
        self.WTG_Count = WTG_Count

        # ----- variable class attributes: -----
        # wind speed at anemometer height, in m/s.
        self.u_anem = None
        # The wind speed at the hub height of the WTG, in m/s.
        self.Hub_Wind_Speed = None
        # The power output, adjusted for air density, of the WTG array, in kW.
        self.Power_Output = None

    # ------ Class methods: ------
    def Calculate_Hub_Wind_Speed(self, u_anem):
        """
        A function to calculate the wind speed at the hub height of the WTG.

        Parameters
        ----------
        u_anem: float
            The wind speed at anemometer height, in m/s.
            u_anem corresponds to the wind speed in the provided wind resource
            profile, at the given time-step.
        self.z_hub: float
            The hub height of the WTGs, in m.
        self.z_anem: float
            The height of anemometer, in m.
        self.z_0: float
            The surface roughness, in  m.
        Output
        ------
        self.Hub_Wind_Speed: float
            The wind speed at the hub height of the WTG, in m/s.
        Example
        -------
            # Define WTG array power output model, where ... = fixed attributes
            >> Example_Model = Wind_Array(...)
            # Calculate the wind speed at the hub height of the WTG and
            # set it as the variable class attribute, self.Hub_Wind_Speed.
            >> Example_Model.Calculate_Hub_Wind_Speed()
        """

        self.u_anem = u_anem
        self.Hub_Wind_Speed = self.u_anem * (np.log(self.z_hub/self.z_0) /
                                             np.log(self.z_anem/self.z_0))

        return None

    def Calculate_Power_Output(self):
        """
        A function to calculate the power output, adjusted for air density,
        of the WTG array.

        Parameters
        ----------
        self.Power_Curve: pd.DataFrame
            A pandas dataframe containing the power curve of the WTG model used
            in the array. Power_Curve must include a column named "wind speed",
            which contains the hub height wind speeds (in m/s) at which the
            power curve is defined; and a column named "power", which contains
            the power output (in kW) predicted by the power curve at the
            corresponding wind speed. All data in Power_Curve should be defined
            at standard air density of 1.225 kg/m^3.
        self.Hub_Wind_Speed: float
            The wind speed at the hub height of the WTG, in m/s.
        self.altitude: float
            The average altitude above sea level of the WTG array, in m.
        self.WTG_Count: int
            The number of WTG in the array.
        Output
        ------
        self.Power_Output: float
            The power output, adjusted for air density, of the WTG array at
            the current time-step, in kW.
        Example
        -------
            # Define WTG array power output model, where ... = fixed attributes
            >> Example_Model = Wind_Array(...)
            # Calculate the power output (kW) of the array, adjusted for air
            # density, and set it as the variable class attribute,
            # self.Power_Output.
            >> Example_Model.Calculate_Power_Output()
        """
        # set cut-off wind speed
        cut_off = max(self.Power_Curve["wind speed"])
        if (self.Hub_Wind_Speed > cut_off):
            self.Power_Output = 0
        else:
            # find upper and lower data points for linear interpolation
            # convert power curve wind speed data to np array for processing
            foo = np.array(self.Power_Curve["wind speed"])
            # find two closest data points to hub wind speed
            # create array of input verus power curve wind speed delta
            delta = np.abs(foo - self.Hub_Wind_Speed)
            # find index of the closest power curve wind speed to
            # the input wind speed
            index_1 = np.where(delta == np.min(delta))[0][0]
            # if index_1 is the last index in the power curve array,
            # the wind speed must be calculated from the index below
            if (index_1 == len(delta) - 1):
                index_2 = index_1 - 1
            # if index_1 is at the first index in the power curve array,
            # the wind speed must be calculated from the index above
            if (index_1 == 0):
                index_2 = 1
            # otherwise, we must find whether the next-closest value is above
            # or below the value at index_1.
            if (index_1 > 0) & (index_1 < len(delta) - 1):
                foo = min(delta[index_1 - 1], delta[index_1 + 1])
                index_2 = np.where(delta == foo)[0][0]

            # set upper and lower indices
            upper_index = max(index_1, index_2)
            lower_index = min(index_1, index_2)
            # set upper and lower power curve wind speeds and power outputs
            u0 = self.Power_Curve["wind speed"][lower_index]
            u1 = self.Power_Curve["wind speed"][upper_index]
            p0 = self.Power_Curve["power"][lower_index]
            p1 = self.Power_Curve["power"][upper_index]
            # perform linear interpolation
            gradient = (p1-p0)/(u1-u0)
            self.Power_Output = (p0 + (gradient)*(self.Hub_Wind_Speed - u0))
            self.Power_Output = self.Power_Output * self.WTG_Count

            # Apply density correction for changes in air density due to
            # changes in altitude above sea level:
            # standard temperature, in K.
            T_0 = 288.16
            # gas constant, in j/kg.K
            R = 287
            # lapse rate, in K/m
            B = 0.0065
            # gravitational acceleration in m/s^2
            g = 9.81
            # air density ratio (air density:air density at STP)
            term1 = 1 - ((B*self.altitude)/T_0)
            term2 = T_0 / (T_0 - (B*self.altitude))
            air_density_ratio = (term1**(g/(R*B)))*term2
            # air density correction to power output
            self.Power_Output = air_density_ratio * self.Power_Output

        if (self.Power_Output < 0):
            self.Power_Output = 0

        return None


__author__ = "Teddy Cheung"
__copyright__ = "Copyright 2021, Imperial College London"
__credits__ = ["Teddy Cheung"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Teddy Cheung"
__email__ = "tc20@ic.ac.uk"
__status__ = "Development"
