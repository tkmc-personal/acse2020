#!/usr/bin/env python

"""
This module defines a function to plot the power output and/or
state-of-charge results from running the models defined by the
SolarModel, WindModel and StorageModel modules in the ACSE9
package.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt


def plot(data, model, root_dir, HOMER=False):
    """
    Plot power output data.

    Parameters
    ----------
    data: numpy array of floats
        An array containing the power output or state-of-charge
        results at every time-step modelled by either
        ACSE9.SolarModel, ACSE9.WindModel or ACSE9.StorageModel.
    model: str
        A string describing the model used to generated P_data.
        model is used to label the axis of the plot.
    root_dir: str
        The root directory to the folder where the colour map
        should be saved. Note: do not include the file name
        in root_dir, the filename is provided by the function.
    HOMER: bool
        If HOMER=True, the data to be plotted is a result
        generated in HOMER and will be labelled as such.
    """
    # check that the function parameters are of the correct type
    if not isinstance(data, np.ndarray):
        sys.exit("Error: P_data must be of type <numpy.ndarray>")
    if not isinstance(model, str):
        sys.exit("Error: model must be of type <str>")

    # check that the power data to be plotted is hourly data over 365 days
    if (len(data) != 8760):
        print("Error: plot_colour_map.plot(data, model) is intended",
              " for plotting a data simulated hourly over 365 days only.",
              " If your data is of a different size you must write",
              " your own plotting function.")
        sys.exit()

    # Rearrange data into list with appropriate dimensions for plotting
    z = []

    i = 0
    while (i < len(data)):
        # Pull out daily power data with hourly data-points
        foo = data[i:i+24]
        # Append to z for plotting
        z.append(foo)
        i += 24

    # Convert to array and transpose to get dimensions for plotting
    bar = np.array(z)
    foo = bar.T
    z = foo.tolist()

    # Plot results
    fig, axs = plt.subplots(1, figsize=(10, 5))
    # Number of days in year
    n = np.linspace(1, 365, 365)
    # Number of hours in day
    h = np.linspace(0, 23, 24)
    # Plot results
    out = axs.contourf(n, h, z)
    fig.colorbar(out, ax=axs, label='Power output (kW)')
    axs.set_xlabel("Day of year (1-365)")
    axs.set_ylabel("Hour of day (0 - 23)")
    if (HOMER):
        axs.set_title("HOMER " + model + " Results")
        fname = root_dir+'HOMER-'+model+'.png'
    else:
        axs.set_title(model + " Results")
        fname = root_dir+model+'.png'

    fig.tight_layout()
    fig.savefig(fname)


__author__ = "Teddy Cheung"
__copyright__ = "Copyright 2021, Imperial College London"
__credits__ = ["Teddy Cheung"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Teddy Cheung"
__email__ = "tc20@ic.ac.uk"
__status__ = "Development"
