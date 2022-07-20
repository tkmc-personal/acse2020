#!/usr/bin/env python

"""
This module defines a li-ion storage power output model, inside a python class.

The modelling methods used in this module are based upon
Hybrid Optimisation of Multiple Energy Resources (HOMER) software,
developed by HOMER Energy LLC.

Descriptions of the modelling choices can be found at either:
- https://www.homerenergy.com/products/pro/docs/latest/homers_calculations.html
"""

import sys
import numpy as np


class StorageArray:
    """
    A class defining a li-ion storage power output model.

    Fixed attributes
    ----------------
    self.eff_round: float
        The round trip efficiency of each li-ion cell, as a decimal.
        For example, for a li-ion cell which loses 5% of power output when
        discharging, or 5% of power input when charging; eff_round = 0.95.
    self.v_nominal: float
        The nominal voltage of each li-ion cell, in V.
    self.count: int
        The number of li-ion cells in the storage array.
    self.dt: float
        The time-step size, in hours.
    self.q_nominal: float
        The nominal capacity of each li-ion cell, in Ah.
    self.SoC_min: float
        The minimum state-of-charge of each li-ion cell, in %.
    self.i_discharge: float
        The maximum discharge current of each li-ion cell, in A.
    self.i_charge: float
        The maximum charging current of each li-ion cell, in A.

    Variable attributes
    -------------------
    self.Power_Output: float
        The power output of the li-ion storage array at the current time-step,
        in kW. A positive power output indicates discharge, a negative power
        output indicates charging.
    self.SoC: float
        The state-of-charge of the li-ion cell storage array (assumed to be
        equal to the SoC of each li-ion cell) at the current time-step, in %.

    """
    # Note: SoC = State-of-Charge
    def __init__(self, dt, count, v_nominal, SoC, SoC_min, i_charge,
                 i_discharge, q_nominal, eff_round):
        # Initialise class attributes
        # ----- fixed class attributes: -----
        # time-step size, in hours.
        if isinstance(dt, float):
            self.dt = dt
        elif not isinstance(dt, float):
            sys.exit("Error: dt must be of type <float>")
        # number of li-ion cells in the storage array.
        self.count = count
        # nominal voltage of each li-ion cell, in V.
        if isinstance(v_nominal, float):
            self.v_nominal = v_nominal
        elif not isinstance(v_nominal, float):
            sys.exit("Error: v_nominal must be of type <float>")
        # The minimum SoC of each li-ion cell, in %.
        if isinstance(SoC_min, float):
            self.SoC_min = SoC_min
        elif not isinstance(SoC_min, float):
            sys.exit("Error: SoC_min must be of type <float>")
        # The maximum charging current of each li-ion cell, in A.
        if isinstance(i_charge, float):
            self.i_charge = i_charge
        elif not isinstance(i_charge, float):
            sys.exit("Error: i_charge must be of type <float>")
        # The maximum discharge current of each li-ion cell, in A.
        if isinstance(i_discharge, float):
            self.i_discharge = i_discharge
        elif not isinstance(i_discharge, float):
            sys.exit("Error: i_discharge must be of type <float>")
        # The nominal capacity of each li-ion cell, in Ah.
        if isinstance(q_nominal, float):
            self.q_nominal = q_nominal
        elif not isinstance(q_nominal, float):
            sys.exit("Error: q_nominal must be of type <float>")
        # The round trip efficiency of each li-ion cell, as a decimal.
        if isinstance(eff_round, float):
            self.eff_round = eff_round
        elif not isinstance(eff_round, float):
            sys.exit("Error: eff_round must be of type <float>")

        # ----- variable class attributes: -----
        # initial SoC, in %.
        if isinstance(SoC, float):
            self.SoC = SoC
        elif not isinstance(SoC, float):
            sys.exit("Error: SoC must be of type <float>")
        # The power output of the li-ion storage array at the current
        # time-step, in kW. A positive power output indicates
        # discharge, a negative power output indicates charging.
        self.Power_Output = None

    # ------ Class methods: ------
    def Check_Current(self, i, charge, P_delta, SoC_end):
        """
        A function which checks whether the storage array can handle the
        charge/discharge current. If not 

        Parameters
        ----------
        i: float
            The current to be checked, in A.
        charge: bool
            If charge=True then i will be checked against the maximum
            charge current, else i will be checked against the maximum
            discharge current.
        P_delta: float
            Pre-check metered power output of storage array, in W.
        SoC_end: float
            Pre-check end-of-time-step SoC of storage array, in %.
        
        Output
        ------
        check: bool
            True/False the storage can handle the current.
        P_delta: float
            Post-check metered power output of storage array, in W.
        SoC_end: float
            Post-check end-of-time-step SoC of storage array, in %.
        """
        check=False
        i  = np.abs(i)

        if (charge == True) & (i >= self.i_charge):
            check = True
            '''
            see comment within Calculate_Charge_Discharge
            for description of electrical calculations.
            '''
            # current to large, curtail to i_charge
            I = -(self.i_charge * self.count)  # convention: charging is -ve
            P_out = I * self.v_nominal
            P_delta = P_out / self.eff_round
            Q = I * self.dt
            SoC_delta = (Q / (self.count*self.q_nominal))*100
            SoC_end = self.SoC - SoC_delta
        if (charge == False) & (i >= self.i_discharge):
            check = True
            # current to large, curtail to i_discharge
            I = self.i_discharge * self.count
            P_out = I * self.v_nominal
            P_delta = P_out * self.eff_round
            Q = I * self.dt
            SoC_delta = (Q / (self.count*self.q_nominal))*100
            SoC_end = self.SoC - SoC_delta
        
        return check, P_delta, SoC_end
    
    def Calculate_Charge_Discharge(self, P_solar, P_wind, P_load):
        """
        A function which decides whether to charge or discharge a li-ion
        storage array based on generation and load data, and outputs the
        power generated by the storage array and its SoC after the
        charge/discharge event.

        Parameters
        ----------
        P_solar: float
            The power output of the associated solar PV array at the
            current time-step, in kW.
        P_wind: float
            The power output of the associated WTG array at the current
            time-step, in kW.
        P_load: float
            The power required to meet the associated load at the current
            time-step, in kW.
        self.eff_round: float
            The round trip efficiency of each li-ion cell, as a decimal.
            For example, for a li-ion cell which loses 5% of power output
            when discharging, or 5% of power input when charging;
            eff_round = 0.95.
        self.v_nominal: float
            The nominal voltage of each li-ion cell, in V.
        self.count: int
            The number of li-ion cells in the storage array.
        self.dt: float
            The time-step size, in hours.
        self.q_nominal: float
            The nominal capacity of each li-ion cell, in Ah.
        self.SoC: float
            The state-of-charge of the li-ion cell storage array
            (assumed to be equal to the SoC of each li-ion cell)
            at the start of the current time-step, in %.
        self.SoC_min: float
            The minimum state-of-charge of each li-ion cell, in %.
        self.i_discharge: float
            The maximum discharge current of each li-ion cell, in A.
        self.i_charge: float
            The maximum charging current of each li-ion cell, in A.

        Outputs
        -------
        self.Power_Output: float
            The power output of the li-ion storage array at the current
            time-step, in kW. A positive power output indicates discharge,
            a negative power output indicates charging.
        self.SoC: float
            The state-of-charge of the li-ion cell storage array (assumed
            to be equal to the SoC of each li-ion cell) at the end of the
            current time-step, in %.

        Example
        -------
        # Define li-ion storage array power output model,
        # where ... = fixed attributes
        >> Example_Model = Storage(...)
        # Set up the power inputs
        P_solar = ...
        P_wind = ...
        P_load = ...
        >> Example_Model.Calculate_Charge_Discharge(P_solar, P_wind, P_load)
        """
        # check the datatypes of P_solar, P_wind, P_load
        # can't all be done in one line due to pep8.
        if not (isinstance(P_solar, float)):
            sys.exit("Error: P_solar must be of type <float>")
        if not (isinstance(P_wind, float)):
            sys.exit("Error: P_wind must be of type <float>")
        if not (isinstance(P_load, float)):
            sys.exit("Error: P_load must be of type <float>")

        if (self.count == 0):
            self.Power_Output = 0.0
        else:            
            # default power output
            self.Power_Output = 0.0
            
            # Convert power data from kW to W
            P_solar = P_solar*1000
            P_wind = P_wind*1000
            P_load = P_load*1000

            # Determine whether the storage should charge or discharge
            # Calculate surplus/deficit in serving the load, in W
            P_delta = P_load - (P_solar + P_wind)

            '''
            P_delta is the 'meter' power output required from the storage.
            During discharge (positive power output), the output from the
            storage must go through the inverter in order to convert from
            DC to AC. During charging (negative power output), the output
            from the generation must go through the rectifier to convert
            from AC to DC. Both components, the inverter and rectifier,
            have an efficiency equal to self.eff_round. Thus, while the
            metered power output of the storage (self.Power_Output) should
            equal P_delta, the actual power output, P_out (in W):
            - During discharge = P_delta/self.eff_round
            - During charge = P_delta*self.eff_round
            With regards to the model, these considerations affect how
            we calculate the charge consumption in each scenario (charge/
            discharge). Assuming a parallel configuration, the current 
            through the entire storage array (in A):
            - I = P_out/self.v_nominal
            Thus, the charge gain/consumption (In Ah):
            - Q = I*self.dt
            And, the change in SoC (%):
            - SoC_delta = Q/(self.count*self.q_nominal)
            '''

            # ----------charge algorithm (generation surplus)----------
            if (P_delta < 0):
                P_out = P_delta * self.eff_round
                I = P_out / self.v_nominal
                Q = I * self.dt
                SoC_delta = (Q / (self.count*self.q_nominal))*100
                SoC_end = self.SoC - SoC_delta

                # only charge if there is enough space
                if (self.SoC == 100.0):
                    None
                # if accepting the power would over charge, curtail
                if (self.SoC != 100.0) & (SoC_end > 100.0):
                    # maximum possible SoC_delta:
                    SoC_delta = -(100.0 - self.SoC)  # convention: charging is -ve
                    SoC_end = 100.0
                    # corresponding variables:
                    Q = (SoC_delta/100) * (self.count*self.q_nominal)
                    I = Q / self.dt
                    P_out = I * self.v_nominal
                    P_delta = P_out / self.eff_round
                    i = I / self.count  # current through each cell (assuming parallel)
                    # check if storage can handle charge current
                    charge = True
                    check = self.Check_Current(i, charge, P_delta, SoC_end)
                    if (check[0] == True):
                        P_delta = check[1]
                        SoC_end = check[2]
                    # output
                    self.Power_Output = P_delta
                    self.SoC = SoC_end
                # else, charge
                if (SoC_end < 100.0):
                    # output
                    self.Power_Output = P_delta
                    self.SoC = SoC_end

            # ----------discharge algorithm (generation deficit)----------
            if (P_delta > 0):
                P_out = P_delta / self.eff_round
                I = P_out / self.v_nominal
                Q = I * self.dt
                SoC_delta = (Q / (self.count*self.q_nominal))*100
                SoC_end = self.SoC - SoC_delta

                # only discharge if safe
                if (self.SoC <= self.SoC_min):
                    None
                # if accepting the power would bring below safe SoC, curtail
                if (self.SoC > self.SoC_min) & (SoC_end < self.SoC_min):
                    # maximum possible SoC_delta:
                    SoC_delta = self.SoC - self.SoC_min
                    SoC_end = self.SoC_min
                    # corresponding variables:
                    Q = (SoC_delta/100) * (self.count*self.q_nominal)
                    I = Q / self.dt
                    P_out = I * self.v_nominal
                    P_delta = P_out * self.eff_round
                    i = I / self.count  # current through each cell (parallel)
                    # check if storage can handle charge current
                    charge = False
                    check = self.Check_Current(i, charge, P_delta, SoC_end)
                    if (check[0]):
                        P_delta = check[1]
                        SoC_end = check[2]
                    # output
                    self.Power_Output = P_delta
                    self.SoC = SoC_end
                # else, discharge
                if (SoC_end > self.SoC_min):
                    # output
                    self.Power_Output = P_delta
                    self.SoC = SoC_end

            # convert back to kW
            self.Power_Output = self.Power_Output / 1000
        return None


__author__ = "Teddy Cheung"
__copyright__ = "Copyright 2021, Imperial College London"
__credits__ = ["Teddy Cheung"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Teddy Cheung"
__email__ = "tc20@ic.ac.uk"
__status__ = "Development"
