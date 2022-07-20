#!/usr/bin/env python

"""
This file sets up and runs a full wind-solar PV-storage
differential evolution sizing optimisation using the ACSE9 package
and its associated modules.

For help running this file, see the readme at:
<https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20.git>
"""


import ACSE9.Differential_Evolution as differential_evolution
from scipy.optimize import NonlinearConstraint
from scipy.optimize import differential_evolution
import numpy as np
import time


# feasibility constraint
capacity_shortage_max = 0.01  # percentage expressed in decimal

# ----------------------- DIFFERENTIAL EVOLUTION ---------------------------
# define constraint function
nlc1 = NonlinearConstraint(differential_evolution.constraint1,
                           0.0, capacity_shortage_max)
# define the bounds on component counts, upon which the DE will run
bounds = [(0, 100), (0, 100), (0, 100)]  # [(Cell), (WTG), (PV)]

# run differential evolution using:
# ACSE9.differential_evolution.objective as NPC objective function
# ACSE9.differential_evolution.constraint1 as feasibility constraint
t0 = time.time()
result = differential_evolution(differential_evolution.objective,
                                bounds,
                                tol=100.0,
                                mutation=(0.25, 0.5),
                                constraints=nlc1)
t1 = time.time()
print('time taken (minutes): ', (t1 - t0)/60)
print(result.x)
print(result.fun)


__author__ = "Teddy Cheung"
__copyright__ = "Copyright 2021, Imperial College London"
__credits__ = ["Teddy Cheung"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Teddy Cheung"
__email__ = "tc20@ic.ac.uk"
__status__ = "Development"