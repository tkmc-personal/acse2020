#!/usr/bin/env python

"""
This module defines a financial model, which returns a discounted
cash flow analysis and the NPC of a given array of components;
e.g. an array of Solar PV modules.

The modelling methods used in this module are based upon
Hybrid Optimisation of Multiple Energy Resources (HOMER) software,
developed by HOMER Energy LLC.

Descriptions of the modelling choices can be found at either:
- https://www.homerenergy.com/products/pro/docs/latest/homers_calculations.html
"""

import numpy as np
import pandas as pd


def Calculate_Discount_Factor(year, inflation_rate,
                              nominal_discount_rate):
    """
    A function to calculate the discount factor for the given year


    Parameters
    ----------
    year: float
        The year of the project lifetime,
        where the first year of operation is year zero.
        self.year can be expressed as a partial year,
        and does not have to be an integer. For example,
        when the project is half way through its third
        year, self.year = 2.5.
    inflation_rate: float
        The expected rate of inflation in the economy,
        a percentage expressed in decimal.
    nominal_discount_rate: float
        The rate at which you expect to borrow money,
        a percentage expressed in decimal.

    Output
    ------
    discount_factor: float
        A factor used to adjust a nominal nominal cash
        flow value to its present value in the given year,
        by account for interest and inflation rates.
    """
    # define shorthand for inputs
    d_nom = nominal_discount_rate
    inf = inflation_rate

    # calculate the real discount rate;
    # which is the nominal discount rate adjusted for inflation
    real_discount_rate = (d_nom - inf)/(1 + inf)

    # calculate the discount factor
    discount_factor = 1/(1 + real_discount_rate)**year
    discount_factor = np.round(discount_factor, 3)

    return discount_factor


def Calculate_Salvage_Value(replacement_cost,
                            component_lifetime,
                            project_lifetime):
    """
    A function to calculate the salvage value of a component

    Parameters
    ----------
    replacement_cost: float
        The cost to replace one component in the given array;
        e.g. the cost to replace one WTG in a WTG array.
    component_lifetime: float
        The amount of time, in years, one component in the
        given array can operate before needing to be replaced.
    project_lifetime: float
        The lifetime of the entire HPP project, in years,
        prior to decommissioning.
    Output
    ------
    salvage_value: float
        The remaining value of one component in the given
        array at the end of the project lifetime;
        e.g. the value at which one WTG in a WTG array can
        be sold for at decommissioning.
    """
    # define shorthand for inputs
    C_rep = replacement_cost
    R_comp = component_lifetime
    R_proj = project_lifetime

    # calculate the replacement cost duration, in years
    R_rep = R_comp * np.floor(R_proj/R_comp)
    # calcuate the remaining life of the component
    # at the end of the project lifetime
    R_rem = R_comp - (R_proj - R_rep)
    # calculate the salvage value of all components
    salvage_value = np.abs((C_rep*(R_rem/R_comp)))

    return salvage_value


def Calculate_Financial_Years(component_lifetime,
                              project_lifetime):
    """
    A function to calculate the years over which the
    financial model should be simulated.

    Parameters
    ----------
    component_lifetime: float
        The amount of time, in years, one component in the
        given array can operate before needing to be replaced.
    project_lifetime: float
        The lifetime of the entire HPP project, in years,
        prior to decommissioning.

    Output
    ------
    years_financial: numpy.array
        The years at which the finanical model should be
        simulated; i.e. each integer year annually, with
        years at which components must be replaced in between.
    years_rep: numpy.array
        The years at which the finanical model should be
        simulated; i.e. each integer year annually, with
        years at which components must be replaced in between.
    """
    years_rep = []  # years at which components require replacement
    # calculate years_rep during the project lifetime
    foo = component_lifetime
    while (foo < project_lifetime):
        years_rep.append(foo)
        foo += component_lifetime

    years_financial = []  # years which financial model will need to run
    # calculate financial years
    foo = 0
    bar = 0
    while (foo <= project_lifetime):
        if (bar < len(years_rep)):
            check = years_rep[bar]
        if (bar < len(years_rep)) & (foo > check):
            years_financial.append(years_rep[bar])
            bar += 1
        else:
            years_financial.append(foo)
            foo += 1

    years_financial = np.array(years_financial)

    return years_financial, years_rep


def Calculate_NPC(component_lifetime,
                  project_lifetime,
                  inflation_rate,
                  nominal_discount_rate,
                  capital_cost,
                  replacement_cost,
                  OM_cost,
                  component_count):

    """
    A function to perform discounted cash flow analysis.

    Parameters
    ----------
    component_lifetime: float
        The amount of time, in years, one component in the
        given array can operate before needing to be replaced.
    project_lifetime: float
        The lifetime of the entire HPP project, in years,
        prior to decommissioning.
    inflation_rate: float
        The expected rate of inflation in the economy,
        a percentage expressed in decimal.
    nominal_discount_rate: float
        The rate at which you expect to borrow money,
        a percentage expressed in decimal.
    capital_cost: float
        The initial capital cost of each component.
    replacement_cost: float
        The cost to replace one component in the given array;
        e.g. the cost to replace one WTG in a WTG array.
    OM_cost: float
        Operations and maintenance cost per year, per component
    component_count: int
        The number of components in the given array;
        e.g. the number of WTGs in the WTG array.

    Outputs:
    --------
    discounted_cash_flow: pandas.DataFrame
        A dataframe containing the discounted cash flow
        analysis for the given component array.
    NPC: float
        The Net Present Cost of the component array.
    """

    # years at which cash flow analysis must be performed
    years = Calculate_Financial_Years(component_lifetime,
                                      project_lifetime)

    years_financial = years[0]  # annual years
    years_rep = years[1]  # years in which component replacement occurs

    discount_factors = Calculate_Discount_Factor(years_financial,
                                                 inflation_rate,
                                                 nominal_discount_rate)

    capitals = np.zeros(len(years_financial))
    # capital expenditure is only realised in the initial project year
    capitals[0] = capital_cost*component_count

    replacements = np.zeros(len(years_financial))
    # set replacement cost at indices corresponding to replacement years
    foo = 0
    for i in range(len(years_financial)):
        if (foo < len(years_rep)):
            if (years_financial[i] == years_rep[foo]):
                replacements[i] = replacement_cost*component_count
                foo += 1

    salvage_value = Calculate_Salvage_Value(replacement_cost,
                                            component_lifetime,
                                            project_lifetime)
    salvages = np.zeros(len(years_financial))
    # salvage revenue is only realised in final project year
    salvages[-1] = salvage_value*component_count

    O_and_Ms = np.zeros(len(years_financial))
    # operations and maintenance cost at indices correspond to annual years
    foo = 0
    for i in range(len(years_financial)):
        if (i != 0):
            O_and_Ms[i] = OM_cost*component_count
        if (foo < len(years_rep)):
            if (years_financial[i] == years_rep[foo]):
                O_and_Ms[i] = 0
                foo += 1

    capitals = -discount_factors*capitals
    replacements = -discount_factors*replacements
    salvages = discount_factors*salvages
    O_and_Ms = -discount_factors*O_and_Ms
    totals = capitals + replacements + salvages + O_and_Ms

    data = {'Year': np.round(years_financial, 3),
            'Discount Factor': np.round(discount_factors, 3),
            'Capital': np.round(capitals),
            'Replacement': np.round(replacements),
            'Salvage': np.round(salvages),
            'O&M': np.round(O_and_Ms),
            'Total': np.round(totals)}

    discounted_cash_flow = pd.DataFrame(data=data)

    # calculate the Net Present Cost of the array
    NPC = np.abs(np.sum(totals))

    return discounted_cash_flow, NPC


__author__ = "Teddy Cheung"
__copyright__ = "Copyright 2021, Imperial College London"
__credits__ = ["Teddy Cheung"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Teddy Cheung"
__email__ = "tc20@ic.ac.uk"
__status__ = "Development"
