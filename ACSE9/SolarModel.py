#!/usr/bin/env python

"""
This module defines a solar PV array power output model, inside a python class.

The modelling methods used in this module are based upon
Hybrid Optimisation of Multiple Energy Resources (HOMER) software,
developed by HOMER Energy LLC.

Descriptions of the modelling choices can be found at either:
- https://www.homerenergy.com/products/pro/docs/latest/homers_calculations.html
"""

import sys
import numpy as np


class SolarArray:
    """
    A class defining a solar PV array power output model.

    Fixed attributes
    ----------------
    time_zone: int
        The time zone in hours east of GMT.
        Example: Central European Time (CET) is one hour
        ahead of GMT, thus time_zone = 1.
        Example: Pacific Standard Time (PST) is eight hours
        behind GMT, thus time_zone = -8.
    self.long: float
        The longitude of the Solar PV facility, in degrees.
    self.lat: float
        The latitude of the Solar PV facility, in degrees.
    self.slope: float
        The angle between the ground and the surface of the panel,
        in degrees.
    self.azimuth: float
        The pole direction in which the panel faces, in degrees -
        due south is zero azimuth, and the azimuth is positive in
        the clockwise direction.
    self.dt: float
        The time-step from t_c to the next simulation time, in hours.
    self.Module_Capacity: float
        The rated capacity, in kW of each PV module under
        Standard Test Conditions.
    self.Module_Count: float
        The number of solar photovoltaic modules in the array.
    self.Array_Capacity: float
        The rated capacity, in kW, of the solar photovoltaic
        array under Standard Test Conditions.
    self.albedo: float
        The ground reflectance, as a percentage.
    self.Derating_Factor: float
        The derating factor, a scaling factor to account for reduced
        PV output in real-life conditions such as electrical losses,
        soiling and aging. Expressed as a decimal; for example,
        if these losses are modelling at 10% of the PV array power
        output, Derating_Factor = 0.9.

    Variable attributes
    -------------------
    self.n: int
        The day of the year (1 to 365)
    self.Solar_Declination: float
        The solar declination, in degrees, of the sun.
    self.Civil_Time: float
        The civil time, in hours.
        Example: The civil time is 0.00 at midnight,
        12.00 at midday and 17.75 at a quarter to six in the evening.
    self.Solar_Time: float
        The solar time, in hours.
    self.Hour_Angle: float
        The hour angle in degrees.
    self.Extraterrestrial_Normal_Radiation: float
        The extraterrestrial normal radiation, in kW/m^2,
        incident on the earth's atmosphere.
    self.Angle_of_Incidence: float
        The angle of incidence between the surface of the PV panel
        and the irradiance, in degrees.
    self.zenith: float
        The angle between the axis normal to the earth's surface
        and the irradiance, in degrees.
    self.Extraterrestrial_Horizontal_Radiation: float
        An average of the extraterrestrial horizontal radiation, in kW/m^2,
        incident on the earth's atmosphere, over the time-step.
    self.Beam_Ratio: float
        The beam ratio, the ratio of beam radiation on the
        tilted surface to beam radiation on the horizontal surface.
    self.Clearness_Index: float
        The clearness index, unitless.
    self.Diffuse_Radiation: float
        The diffuse component of the global horizontal radiation, in kW/m^2
    self.Beam_Radiation: float
        The beam component of the global horizontal radiation, in kW/m^2.
    self.Anistropy_Index: float
        The anistropy index, unitless.
    self.Horizon_Factor: float
        The horizon brightening factor, unitless.
    self.Incident_Radiation: float
        The global radiation incident on the surface of the PV panel, in kW.
    self.Power_Output: float
        The power output of the solar PV array at the current time-step,
        in kW.
    """
    # Note: SoC = State-of-Charge
    def __init__(self, time_zone, long, lat, slope, azimuth, dt,
                 Module_Capacity, Module_Count, albedo, Derating_Factor):
        # Initialise class attributes
        # ----- fixed class attributes: -----
        # The time zone in hours east of GMT.
        if isinstance(time_zone, float):
            self.time_zone = time_zone
        elif not (isinstance(time_zone, float)):
            sys.exit("Error: time_zone must be of type <float>")
        # The longitude of the Solar PV facility, in degrees.
        if isinstance(long, float):
            self.long = long
        elif not (isinstance(long, float)):
            sys.exit("Error: long must be of type <float>")
        # The latitude of the Solar PV facility, in degrees.
        if isinstance(lat, float):
            self.lat = lat
        elif not (isinstance(lat, float)):
            sys.exit("Error: lat must be of type <float>")
        # The angle between the ground and the surface of the panel,
        # in degrees.
        if isinstance(slope, float):
            self.slope = slope
        elif not (isinstance(slope, float)):
            sys.exit("Error: slope must be of type <float>")
        # The pole direction in which the panel faces, in degrees -
        # due south is zero azimuth, and the azimuth is positive in
        # the clockwise direction.
        if isinstance(azimuth, float):
            self.azimuth = azimuth
        elif not (isinstance(azimuth, float)):
            sys.exit("Error: azimuth must be of type <float>")
        # The time-step from civil_time to the next simulation time, in hours.
        if isinstance(dt, float):
            self.dt = dt
        elif not (isinstance(dt, float)):
            sys.exit("Error: dt must be of type <float>")
        # The rated capacity, in kW of each PV module under STC.
        if isinstance(Module_Capacity, float):
            self.Module_Capacity = Module_Capacity
        elif not (isinstance(Module_Capacity, float)):
            sys.exit("Error: Module_Capacity must be of type <float>")
        # The number of solar photovoltaic modules in the array.
        self.Module_Count = Module_Count
        # The ground reflectance, as a percentage.
        if isinstance(albedo, float):
            self.albedo = albedo
        elif not (isinstance(albedo, float)):
            sys.exit("Error: albedo must be of type <float>")
        # The rated capacity, in kW, of the solar photovoltaic
        # array under Standard Test Conditions.
        self.Array_Capacity = self.Module_Count * self.Module_Capacity
        # The derating factor, a scaling factor to account for reduced
        # PV output in real-life conditions such as electrical losses,
        # soiling and aging. Expressed as a decimal; for example,
        # if these losses are modelling at 10% of the PV array power
        # output, Derating_Factor = 0.9.
        if isinstance(Derating_Factor, float):
            self.Derating_Factor = Derating_Factor
        elif not (isinstance(Derating_Factor, float)):
            sys.exit("Error: Derating_Factor must be of type <float>")

        # ----- variable class attributes: -----
        # The day of the year (1 to 365);
        # This attribute is not used in any calculations,
        # it is required that the user input 'n' whenever
        # it is needed. This avoids potential error.
        # The class attribute defined below is set
        # whenever a function uses 'n', and is present for
        # informational purposes only.
        self.n = None
        # The civil time, in hours.
        # Please see above comment with regards to the use
        # of 'n' in calculations. The same process applies to
        # 't_c'.
        self.Civil_Time = None
        # The solar declination, in degrees, of the sun.
        self.Solar_Declination = None
        # The solar time, in hours.
        self.Solar_Time = None
        # The hour angle in degrees
        self.Hour_Angle = None
        # The extraterrestrial normal radiation, in kW/m^2,
        # incident on the earth's atmosphere.
        self.Extraterrestrial_Normal_Radiation = None
        # The angle of incidence between the surface of the PV panel
        # and the irradiance, in degrees.
        self.Angle_of_Incidence = None
        # The angle between the axis normal to the earth's surface
        # and the irradiance, in degrees.
        self.zenith = None
        # An average of the extraterrestrial horizontal radiation, in kW/m^2,
        # incident on the earth's atmosphere, over the time-step.
        self.Extraterrestrial_Horizontal_Radiation = None
        # The beam ratio, the ratio of beam radiation on the
        # tilted surface to beam radiation on the horizontal surface.
        self.Beam_Ratio = None
        # The clearness index, unitless.
        self.Clearness_Index = None
        # The diffuse component of the global horizontal radiation, in kW/m^2
        self.Diffuse_Radiation = None
        # The beam component of the global horizontal radiation, in kW/m^2.
        self.Beam_Radiation = None
        # The anistropy index, unitless.
        self.Anistropy_Index = None
        # The horizon brightening factor, unitless.
        self.Horizon_Factor = None
        # The global radiation incident on the surface of the PV panel, in kW.
        self.Incident_Radiation = None
        # The power output of the solar PV array at the current time-step, kW.
        self.Power_Output = None

    # ------ Class methods: ------
    def Calculate_Solar_Declination(self, n):
        """
        Calculate the solar declination of the sun given a day of the year
        Parameters
        ----------
        n: int
            The day of the year (1 to 365)
        Output
        ------
        self.Solar_Declination: float
            The solar declination, in degrees, of the sun.
        """
        # check the datatype of n.
        if isinstance(n, int):
            self.n = n
        elif not (isinstance(n, int)):
            sys.exit("Error: n must be of type <int>")

        self.Solar_Declination = 23.45 * np.sin(((2*np.pi)/365)*(284 + n))

        return None

    def Calculate_Solar_Time(self, n, t_c):
        """
        Calculate the solar time, in hours, given the civil time.

        Parameters
        ----------
        n: int
            The day of the year (1 to 365)
        t_c: float
            The civil time, in hours.
            Example: The civil time is 0.00 at midnight,
            12.00 at midday and 17.75 at a quarter to six in the evening.
        self.time_zone: int
            The time zone in hours east of GMT.
            Example: Central European Time (CET) is one hour
            ahead of GMT, thus time_zone = 1.
            Example: Pacific Standard Time (PST) is eight hours
            behind GMT, thus time_zone = -8.
        self.long: float
            The longitude of the Solar PV facility, in degrees.
        Output
        ------
        self.Solar_Time: float
            The solar time, in hours.
        """

        # check the datatype of n.
        if isinstance(n, int):
            self.n = n
        elif not (isinstance(n, int)):
            sys.exit("Error: n must be of type <int>")
        # check the datatype of t_c.
        if isinstance(t_c, float):
            self.Civil_Time = t_c
        elif not (isinstance(t_c, float)):
            sys.exit("Error: t_c must be of type <float>")

        # B, an angle required for the equation of time
        B = (2*np.pi)*((n-1)/365)
        # Calculate the equation of time
        term1 = 0.000075 + 0.001868*np.cos(B)
        term2 = 0.032077*np.sin(B)
        term3 = 0.014615*np.cos(2*B)
        term4 = 0.04089*np.sin(2*B)
        E = 3.82 * (term1 - term2 - term3 - term4)
        # Calculate the solar time
        self.Solar_Time = t_c + (self.long / 15) - self.time_zone + E

        return None

    def Calculate_Hour_Angle(self):
        """
        Calculate the hour angle of the sun's location in the sky

        Parameters
        ----------
        self.Solar_Time: float
            The solar time, in hours.
            The function `Calculate_Solar_Time(n, t_c)`
            should be used to calculate t_s.
        Output
        ------
        self.Hour_Angle: float
            The hour angle in degrees.
        """
        # The hour angle in degrees
        self.Hour_Angle = (self.Solar_Time - 12) * 15

        return None

    def Calculate_Extraterrestrial_Normal_Radiation(self, n):
        """
        Parameters
        ----------
        n: int
            The day of the year (1 to 365)
        Output
        ------
        self.Extraterrestrial_Normal_Radiation: float
            The extraterrestrial normal radiation, in kW/m^2,
            incident on the earth's atmosphere.
        """
        # check the datatype of n.
        if isinstance(n, int):
            self.n = n
        elif not (isinstance(n, int)):
            sys.exit("Error: n must be of type <int>")

        # The solar constant, in kW/m^2
        G_sc = 1.367

        term1 = 1 + 0.033*np.cos((2*np.pi*n)/365)

        # The Extraterrestrial normal radiation
        self.Extraterrestrial_Normal_Radiation = G_sc * term1

        return None

    def Calculate_Angle_of_Incidence(self):
        """
        Calculate the angle of incidence between the surface
        of the PV panel and the irradiance.

        Parameters
        ----------
        self.lat: float
            The latitude of the Solar PV facility, in degrees.
        self.slope: float
            The angle between the ground and the surface of the panel,
            in degrees.
        self.azimuth: float
            The pole direction in which the panel faces, in degrees -
            due south is zero azimuth, and the azimuth is positive in
            the clockwise direction.
        self.Solar_Declination: float
            The solar declination, in degrees.
            The function `Calculate_Solar_Declination(n)` should be
            used to calculate self.Solar_Declination.
        self.Hour_Angle: float
            The hour angle of the sun's location in the sky, in degrees.
            The function `Calculate_Hour_Angle()` should be used to
            calculate self.Hour_Angle.
        Output
        ------
        self.Angle_of_Incidence: float
            The angle of incidence between the surface of the PV panel
            and the irradiance, in degrees.
        self.zenith: float
            The angle between the axis normal to the earth's surface
            and the irradiance, in degrees.
        """

        # convert all degrees to radians for use in calculations
        lat = np.radians(self.lat)
        slope = np.radians(self.slope)
        azimuth = np.radians(self.azimuth)
        dec = np.radians(self.Solar_Declination)
        hour_angle = np.radians(self.Hour_Angle)

        # Calculate the angle of incidence
        term1 = np.sin(dec)*np.sin(lat)*np.cos(slope)
        term2 = np.sin(dec)*np.cos(lat)*np.sin(slope)*np.cos(azimuth)
        term3 = np.cos(dec)*np.cos(lat)*np.cos(slope)*np.cos(hour_angle)
        term4 = np.cos(dec)*np.sin(lat)*np.sin(slope)*np.cos(azimuth)
        term4 = term4*np.cos(hour_angle)  # on new line for pep8 compliance
        term5 = np.cos(dec)*np.sin(slope)*np.sin(azimuth)*np.sin(hour_angle)
        # RHS of the angle of incidence equation
        RHS = term1 - term2 + term3 + term4 + term5
        # Angle of incidence in degrees
        self.Angle_of_Incidence = np.degrees(np.arccos(RHS))

        # Calculate the zenith angle by artificially setting slope = 0.
        term1 = np.sin(dec)*np.sin(lat)
        term2 = np.cos(dec)*np.cos(lat)*np.cos(hour_angle)
        # RHS of the zenith angle equation
        RHS = term1 + term2
        # zenith angle in degrees
        self.zenith = np.degrees(np.arccos(RHS))

        return None

    def Calculate_Extraterrestrial_Horizontal_Radiation(self, n, t_c, G):
        """
        Calculate extraterrestrial normal radiation.

        Parameters
        ----------
        self.dt: float
            The time-step from t_c to the next simulation time, in hours.
        t_c: float
            The civil time, in hours.
            Example: The civil time is 0.00 at midnight,
            12.00 at midday and 17.75 at a quarter to six in the evening.
        n: int
            The day of the year (1 to 365)
        self.time_zone: int
            The time zone in hours east of GMT.
            Example: Central European Time (CET) is
            one hour ahead of GMT, thus time_zone = 1.
            Example: Pacific Standard Time (PST) is
            eight hours behind GMT, thus time_zone = -8.
        self.lat: float
            The latitude of the Solar PV facility, in degrees.
        self.long: float
            The longitude of the Solar PV facility, in degrees.
        self.Solar_Declination: float
            The solar declination, in degrees.
            The function `Calculate_Solar_Declination(n)`
            should be used to calculate dec.
        self.Extraterrestrial_Normal_Radiation: float
            The extraterrestrial normal radiation, in kW/m^2,
            incident on the earth's atmosphere. The function
            Calculate_Extraterrestrial_Normal_Radiation(n)
            should be used to calculate self.Extraterrestrial_Normal_Radiation.
        Output
        ------
        self.Extraterrestrial_Horizontal_Radiation: float
            An average of the extraterrestrial horizontal radiation, in kW/m^2,
            incident on the earth's atmosphere, over the time-step.
        """
        # check the datatype of n.
        if isinstance(n, int):
            self.n = n
        elif not (isinstance(n, int)):
            sys.exit("Error: n must be of type <int>")
        # check the datatype of t_c.
        if isinstance(t_c, float):
            self.Civil_Time = t_c
        elif not (isinstance(t_c, float)):
            sys.exit("Error: t_c must be of type <float>")

        # convert all degrees to radians for use in calculations
        lat = np.radians(self.lat)
        dec = np.radians(self.Solar_Declination)

        # empty list to store integral data points
        output = []

        # to avoid convoluted self referencing and creation of a class
        # within this class, the calculations used in the funciton
        # Calculate_Solar_Time(n, t_c) are repeated here.
        # B, an angle required for the equation of time
        B = (2*np.pi)*((n-1)/365)
        # Calculate the equation of time
        term1 = 0.000075 + 0.001868*np.cos(B)
        term2 = 0.032077*np.sin(B)
        term3 = 0.014615*np.cos(2*B)
        term4 = 0.04089*np.sin(2*B)
        E = 3.82 * (term1 - term2 - term3 - term4)

        i = t_c
        while (i < (t_c + self.dt)):
            t_c_end = i+(self.dt/10)
            # Solar time at the beginning of the secondary time-step
            t_s1 = i + (self.long / 15) - self.time_zone + E
            # Solar time at end of secondary time-step
            t_s2 = t_c_end + (self.long / 15) - self.time_zone + E
            # associated hour angles, in radians
            hour_angle_ts1 = np.radians((t_s1 - 12) * 15)
            hour_angle_ts2 = np.radians((t_s2 - 12) * 15)

            #  Calculate extraterrestrial horizontal radiation (G_o), in kW/m^2
            term1 = np.cos(lat)*np.cos(dec)
            term1 = term1*(np.sin(hour_angle_ts2) - np.sin(hour_angle_ts1))
            term2 = (hour_angle_ts2 - hour_angle_ts1)*np.sin(lat)*np.sin(dec)

            foo = self.Extraterrestrial_Normal_Radiation*(term1 + term2)
            G_o = (12/np.pi)*foo

            # The above calculations can sometimes incorrectly produce
            # negative power outputs due to the action of the trigonometric
            # functions, in this case the output should be set to zero.
            if (G_o < 0):
                G_o = 0

            output.append(G_o)

            i += (self.dt/10)

        self.Extraterrestrial_Horizontal_Radiation = np.mean(output)

        # PLEASE READ:
        """
        The above calculation of extraterrestrial normal radiation (G_o)
        has can cause issues when it is calculated at or near sunset:
        At or near sunset, G_o may reach a value of zero faster than
        the imported irradiance resource data. In reality, when G_o is zero,
        the global horizontal irradiance (G) (which is incident below the
        earth's atmosphere, i.e. is not extraterrestrial) should also
        equal zero. The discrepency between G_o and G when modelling is
        likely to occur as G is usually data taken from solar radiation
        sensors, which are sensitive enough to continue measuring
        irradiance within many decimal places from zero. For example,
        a negligible value of G such as 0.001 kW/m^2 will still be read
        as non-zero. Since it is not physically possible for G to be
        larger than G_o, this model implements a 'sunset exception';
        such that if G > G_o, and the hour angle indicates the plant is
        outside of daylight, G_o is artifically set higher than G.
        """

        # calculate sunrise/sunset hour angle (ADD REFERENCE)
        a = np.radians(-0.83)
        hour_angle_rise = np.arccos(np.sin(a) - (np.tan(lat)*np.tan(dec)))
        hour_angle_set = -hour_angle_rise
        hour_angle = np.radians(self.Hour_Angle)
        # If the array is still in daylight, artificially set
        # self.Extraterrestrial_Horizontal_Radiation larger than G.
        if (hour_angle > hour_angle_set) | (hour_angle < hour_angle_rise):
            if (G > self.Extraterrestrial_Horizontal_Radiation):
                # Sunset exception
                self.Extraterrestrial_Horizontal_Radiation = G*10

        return None

    def Calculate_Beam_Ratio(self):
        """
        Calculate the ratio of beam radiation on the tilted surface to
        beam radiation on the horizontal surface.

        Parameters
        ----------
        self.Angle_of_Incidence: float
            The angle of incidence between the normal axis to the
            surface of the panel and the irradiance, in degrees.
            The function Calculate_Angle_of_Incidence()
            should be used to calculate self.Angle_of_Incidence.
        self.zenith: float
            The angle between the axis normal to the earth's
            surface and the irradiance, in degrees. The function
            Calculate_Angle_of_Incidence()
            should be used to calculate self.zenith.
        Output
        ------
        self.Beam_Ratio: float
            The beam ratio, the ratio of beam radiation on the
            tilted surface to beam radiation on the horizontal surface.
        """

        # When the solar zenith angle hits 90 degrees, beam radiation
        # is parallel to the horizontal surface, thus the beam ratio
        # is equal to 1 (i.e. all beam radiation is hitting the
        # tilted surface).
        if (np.ceil(self.zenith) == 90) | (np.floor(self.zenith) == 90):
            self.Beam_Ratio = 1
        if (np.ceil(self.zenith) != 90) & (np.floor(self.zenith) != 90):
            # convert all degrees to radians calculations
            incidence = np.radians(self.Angle_of_Incidence)
            zenith = np.radians(self.zenith)

            self.Beam_Ratio = np.abs(np.cos(incidence)/np.cos(zenith))

        return None

    def Calculate_Clearness_Index(self, G):
        """
        A function to calculate the clearness index,

        Parameters
        ----------
        G: float
            The global horizontal radiation on the earth's surface
            averaged over the time-step, in kW/m^2.
        self.Extraterrestrial_Horizontal_Radiation: float
            An average of the extraterrestrial horizontal radiation,
            in kW/m^2, incident on the earth's atmosphere,
            over the time-step.
        Output
        ------
        self.Clearness_Index: float
            The clearness index, unitless.
        """

        # If G_o is zero (such as in the night-time),
        # output a perfect clearness index
        if (self.Extraterrestrial_Horizontal_Radiation == 0):
            self.Clearness_Index = 1

        else:
            self.Clearness_Index = G/self.Extraterrestrial_Horizontal_Radiation

        return None

    def Calculate_Diffuse_Beam_Radiation(self, G):
        """
        Calculate the diffuse component of the global horizontal radiation.

        Parameters
        ----------
        G: float
            The global horizontal radiation on the earth's surface
            averaged over the time-step, in kW/m^2.
        self.Clearness_Index: float
            The clearness index, unitless.
        Output
        ------
        self.Diffuse_Radiation: float
            The diffuse component of the global horizontal radiation, in kW/m^2
        self.Beam_Radiation: float
            The beam component of the global horizontal radiation, in kW/m^2.
        """
        # k_t = self.Clearness_Index to make pep8 line length compliance easier
        k_t = self.Clearness_Index

        if (k_t <= 0.22):
            ratio = 1 - 0.09*k_t
            self.Diffuse_Radiation = ratio * G
        elif (k_t > 0.22) & (k_t <= 0.8):
            ratio = 0.9511 - 0.1604*k_t + 4.338*k_t**2
            ratio = ratio - 16.638*k_t**3 + 12.336*k_t**4
            self.Diffuse_Radiation = ratio * G
        elif (k_t > 0.8):
            ratio = 0.165
            self.Diffuse_Radiation = ratio * G

        self.Beam_Radiation = G - self.Diffuse_Radiation

        return None

    def Calculate_Anistropy_Index(self):
        """
        Calculate the anistropy index.

        Parameters
        ----------
        self.Extraterrestrial_Horizontal_Radiation: float
            An average of the extraterrestrial horizontal radiation,
            in kW/m^2, incident on the earth's atmosphere,
            over the time-step.
        self.Beam_Radiation: float
            The beam component of the global horizontal radiation, in kW/m^2.
        Output
        ------
        self.Anistropy_Index: float
            The anistropy index, unitless.
        """
        # G_b = self.Beam_Radiation to make pep8 line length compliance easier
        G_b = self.Beam_Radiation
        # G_o = self.Extraterrestrial_Horizontal_Radiation, ditto
        G_o = self.Extraterrestrial_Horizontal_Radiation

        # If G_o is zero (such as in the night-time),
        # output an anistropy index of zero.
        # When G_o = 0, G_b and G_d = 0, therefore there is no effect from
        # self.Anistropy_Index on the calculation of self.Incident_Radiation,
        # i.e. our choice of anistropy index is arbitrary.
        if (G_o == 0):
            self.Anistropy_Index = 0
        else:
            self.Anistropy_Index = G_b / G_o

        return None

    def Calculate_Horizon_Factor(self, G):
        """
        Function to calculate the horizon brightening factor.

        Parameters
        ----------
        G: float
            The global horizontal radiation on the earth's surface
            averaged over the time-step, in kW/m^2.
        self.Beam_Radiation: float
            The beam component of the global horizontal radiation, in kW/m^2.
        Output
        ------
        self.Horizon_Factor: float
            The horizon brightening factor, unitless.
        """
        # if the GHI is zero then we must avoid NaN in results
        # when GHI is zero, the value of self.Horizon_Factor
        # has no effect on the results of self.Incident_Radiation.
        # Therefore we can set it to any arbitrary value.
        if (G == 0):
            self.Horizon_Factor = 0
        else:
            self.Horizon_Factor = np.sqrt(self.Beam_Radiation/G)

        return None

    def Calculate_Indcident_Radiation(self, G):
        """
        Calculate the global radiation incident on the surface of the PV panel.

        Parameters
        ----------
        G: float
            The global horizontal radiation on the earth's surface averaged
            over the time-step, in kW/m^2.
        self.Beam_Radiation: float
            The beam component of the global horizontal radiation, in kW/m^2.
            The function `Calculate_beam_Radiation(G)` should be used to
            calculate self.Beam_Radiation.
        self.Diffuse_Radiation: float
            The diffuse component of the global horizontal radiation,
            in kW/m^2. The function `Calculate_Diffuse_Radiation(G)`
            should be used to calculate self.Diffuse_Radiation.
        self.Anistropy_Index: float
            The anistropy index, unitless.
            The function `Calculate_Anistropy_Index()` should be used to
            calculate self.Anistropy_Index.
        self.Beam_Ratio: float
            The beam ratio, the ratio of beam radiation on the
            tilted surface to beam radiation on the horizontal surface.
            The function `Calculate_Beam_Ratio()` should be used to
            calculate self.Beam_Ratio.
        self.slope: float
            The angle between the ground and the surface of the panel,
            in degrees.
        self.Horizon_Factor: float
            The horizon brightening factor, unitless.
            The function `Calculate_Horizon_Factor()`
            should be used to calculate self.Horizon_Factor.
        self.albedo: float
            The ground reflectance, as a percentage.
        Output
        ------
        self.Incident_Radiation: float
            The global radiation incident on the surface of the PV panel,
            in kW.
        """
        # rename variables to fit line length
        G_b = self.Beam_Radiation
        G_d = self.Diffuse_Radiation
        A_i = self.Anistropy_Index
        R_b = self.Beam_Ratio
        f = self.Horizon_Factor
        albedo = self.albedo

        # convert all degrees to radians for calculations
        slope = np.radians(self.slope)

        term1 = (G_b + G_d*A_i)*R_b
        term2 = G_d*(1 - A_i)
        term3 = (1 + np.cos(slope))/2
        term4 = 1 + (f * (np.sin(slope/2))**3)
        term5 = G*albedo
        term6 = (1 - np.cos(slope)) / 2

        self.Incident_Radiation = term1 + (term2*term3*term4) + (term5*term6)

        return None

    def Calculate_Power_Output(self):
        """
        Calculate the power output of a PV array

        Parameters
        ----------
        self.Array_Capacity: float
            The rated capacity, in kW, of the solar photovoltaic
            array under Standard Test Conditions.
        self.Derating_Factor: float
            The derating factor, a scaling factor to account for reduced
            PV output in real-life conditions such as electrical losses,
            soiling and aging. Expressed as a decimal; for example,
            if these losses are modelling at 10% of the PV array power
            output, Derating_Factor = 0.9.
        self.Incident_Radiation: float
            The global radiation incident on the surface of the PV panel,
            in kW.
        self.Power_Output: float
            The power output of the solar PV array at the current time-step,
            in kW.
        """

        # rename variables to fit line length
        Y_PV = self.Array_Capacity
        f_PV = self.Derating_Factor
        G_T = self.Incident_Radiation

        # Global incident radiation at STC, 1 kW/m2.
        G_T_stc = 1.0

        term1 = Y_PV*f_PV
        term2 = G_T/G_T_stc

        self.Power_Output = term1*term2

        # If rounding causes the power output to be larger
        # than actual array capacity, scale down.
        if (self.Power_Output > self.Array_Capacity):
            self.Power_Output = self.Array_Capacity

        return None


__author__ = "Teddy Cheung"
__copyright__ = "Copyright 2021, Imperial College London"
__credits__ = ["Teddy Cheung"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Teddy Cheung"
__email__ = "tc20@ic.ac.uk"
__status__ = "Development"
