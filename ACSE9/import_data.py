#!/usr/bin/env python

"""
This module defines a function to import resource data for use with
the ACSE9 package modules and their respective functions.
"""

import sys
import pandas as pd
import datetime


def import_resource(root_dir, model):
    """
    A function to import resource data for use with
    the ACSE9 package modules and their respective
    functions.

    Parameters
    ----------
    root_dir: str
        A string containing the root directory to the .csv
        file containing resource data.
    model: str
        A string, containing the module for which the resource
        imported by this function is to be used with. This
        parameter allows the function to ensure correct column
        naming.
        The possible values of 'model' are:
        - 'SolarModel'. In which case the required columns are
          "datetime" and "irradiance", where the data listed
          under "irradiance" are in kW/m^2.
        - 'WindModel'. In which case the required columns are
          "datetime" and "wind speed", where the data listed
          under "wind speed" are in m/s.
        - 'StorageModel'. In which case the required columns
          are "datetime" and "load", where the data listed
          under "load are in kW.
        - 'Load'. in which case the required columns
          are "datetime" and "load", where the data listed
          under "load" are in kW.
        - 'HOMER' (intended for use when validating your
           model power output results).
           In which case the required columns
           are  "datetime", "power solar", "power wind",
           and "power storage" where the data
           listed under power are in kW.
        - 'Power_Curve'. In which case the required columns
           are  "wind speed" and "power", where the data
           listed under "wind speed" are in m/s and under
           "power" are in kW.
    Output
    ------
    resource: pandas.DataFrame
        A dataframe containing the resource profile defined in the
        .csv file within root_dir.
    """
    # read csv file
    resource = pd.read_csv(root_dir)

    # define a nested function which checks column naming
    def check_column_naming(resource, name):
        check = False
        for i in range(len(resource.columns)):
            if (resource.columns[i] == name):
                check = True
                break
        if not check:
            print("Error: resource must contain a column named ",
                  name, ".")
            sys.exit()
        return check

    # check that the csv file contains a column named "datetime"
    # (unless the csv file contains a WTG power curve)
    if not (model == 'Power_Curve'):
        check_column_naming(resource, 'datetime')
        # convert string datetime to datetime
        foo = resource["datetime"]
        format = '%d/%m/%Y %H:%M'
        bar = foo.apply(lambda x: datetime.datetime.strptime(x, format))
        # replace converted column
        resource["datetime"] = bar

    # check the column naming in the csv file
    check_naming = False
    if (model == 'SolarModel'):
        check_naming = check_column_naming(resource, 'irradiance')
    if (model == 'WindModel'):
        check_naming = check_column_naming(resource, 'wind speed')
    if (model == 'StorageModel'):
        check_naming = check_column_naming(resource, 'load')
    if (model == 'Load'):
        check_naming = check_column_naming(resource, 'load')
    if (model == 'HOMER'):
        check_naming = check_column_naming(resource, 'power solar')
        check_naming = check_column_naming(resource, 'power wind')
        check_naming = check_column_naming(resource, 'power storage')
    if (model == 'Power_Curve'):
        check_naming = check_column_naming(resource, 'wind speed')
        check_naming = check_column_naming(resource, 'power')
    elif not check_naming:
        print("Error: model must be equal to 'SolarModel', ",
              "'WindModel', 'StorageModel', 'Load', 'Power', ",
              "or 'Power_Curve'.")
        sys.exit()

    return resource


__author__ = "Teddy Cheung"
__copyright__ = "Copyright 2021, Imperial College London"
__credits__ = ["Teddy Cheung"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Teddy Cheung"
__email__ = "tc20@ic.ac.uk"
__status__ = "Development"
