[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- ABOUT THE PROJECT -->
## About The Project

A Hybrid Power Plant (HPP) seeks to improve the predictability, dispatchability, and economics of
stand-alone intermittent generation by combining different types of generation and storage assets.
Optimal HPP sizing can be formulated as an objective-based optimisation problem with n
optimisation variables. The industry standard software for HPP sizing optimisation is HOMER Pro.
HOMER Pro allows the user to optimise the count each of desired generation/storage asset, with the
objective to minimise Net Present Cost (NPC) subject to several optional constraints, such as the
ability of the HPP to fulfil a representative load profile. Because HOMER Pro is proprietary and
utilises inefficient exhaustive search, there exists an opportunity for an open-source software to be
developed which enables higher complexity HPP models with state-of-the-art global optimisation
methods.

This project developed an open-source HPP sizing software (the ACSE9 tool), which uses
power output and financial models verified and validated by HOMER Pro results. Validation was
performed for a range of geographical scenarios; the equator test case achieved a 0.031%, 0.161% and
6.35% error against HOMER Pro’s wind, solar and storage power output models respectively. The
ACSE9 tool was developed with the ability to optimise using exhaustive search, and with prepackaged modules such as `scipy.optimize`. Using SciPy’s differential evolution optimiser, the
ACSE9 tool found a better optimal solution than discrete exhaustive search with a resolution of 10
components. In addition to its optimisation options, the ACSE9 tool provides the ability to script HPP
simulations and sensitivity analyses, which the industry standard does not.

## Built With
* [NumPy 1.21.1](https://numpy.org/)
* [SciPy 1.7.1](https://www.scipy.org/)
* [pandas 1.3.2](https://pandas.pydata.org/)
* [HOMER Pro 3.14](https://www.homerenergy.com/products/pro/index.html)

<!-- GETTING STARTED -->
## Getting Started

### Installation
To get a local copy up and running follow these steps.

1. Clone the repo
   ```sh
   git clone https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/
   ```
2. ```sh
   cd to the directory where requirements.txt is located.
   ```
3. Activate your virtualenv
4. Install prequisites
   ```sh
   pip install -r requirements.txt
   ```

<!-- REPOSITORY STRUCTURE -->
## Repository Structure
| Item | Description |
|------|-------------|
| 00 Documentation  | A folder containing the detailed report on this project and the documentation for the code contained in the /ACSE9 folder.|
| 01 Validation  | A folder containing the input data used for validation of the projects results against HOMER Pro, and plots of the validation results. |
| 02 Validation  |  A folder which is intended to be used as a root directory for the saving of data from any runs of `main_exhaustive_search.py` or `main_differential_evolution.py`|
| ACSE9  |  The parent folder to for the ACSE9 tool package and its associated modules and functions (See Note). |
| `main_exhaustive_search.py`  | Provides a template script for performing exhaustive search sizing optimisation of a HPP (discussed further in 'Usage').|
| `main_differential_evolution.py`  | Provides a template script for performing differential evolution sizing optimisation of a HPP (discussed further in 'Usage').|
| `validation_EQUATOR.py`  | Provides the script used for power output model validation against the equator test case.|
| `validation_NORTHERN.py`  | Provides the script used for power output model validation against the northern hemisphere test case.|
| `validation_SOUTHERN.py`  | Provides the script used for power output model validation against the southern hemisphere test case.|

### Note
* `Differential_Evolution.py` is a module which contains the objective and constraint functions for optimising an HPP configuration using the `scipy.optimize.differential_evolution` method.
* `FinancialModel.py` is a module which defines functions for calculating a discounted cash flow of a given HPP configuration, and its subsequent Net Present Cost (NPC) over the project lifetime.|
* `import_data.py` is a module which defines a data import function. The the function can import and check the structure of resource (i.e. wind and irradiance), load, and power curve data - all used as inputs when running a full HPP sizing optimisation.
* `plot_contour_map.py` is a module which defines a function for plotting the (x, y, z) = (time, date, power output) results of a power output model.
* `RunSolarModel.py`, `RunStorageModel.py` and `RunWindModel.py` define compact functions which can be used to run power output models over an entire exhaustive search, search space using the classes defined in `SolarModel.py`, `Storagemode.py` and `WindModel.py` respectively.
* `SolarModel.py` defines a `SolarArray` class with numerous attributes and methods to model the power output of a solar photovoltaic array at a given time-step.
* `WindModel.py` defines a `WindArray` class with numerous attributes and methods to model the power output of a wind turbine generator array at a given time-step.
* `StorageModel.py` defines a `StorageArray` class with numerous attributes and methods to model the power output of a storage cell array at a given time-step.


<!-- USAGE EXAMPLES -->
## Usage
### Exhaustive search HPP sizing optimisation in `main_exhaustive_search.py`
1. Define the search space over which you would like to run exhaustive search.
The below image shows a search space of 0 to 100 of the given component, with a resolution of 10 components (i.e. 0, 10, 20, ..., 80, 90, 100):
![Search Space](https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/blob/master/00%20Documentation/Repository%20Images/ExhaustiveSearch-Example1.png)
2. Specify the maximum capacity shortage factor, over which a HPP will be considered infeasible:
![Capacity Shortage Factor](https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/blob/master/00%20Documentation/Repository%20Images/ExhaustiveSearch-Example2.png)
3. Define the root directory from which you want to import the power curve of the WTG model, and wind resource profile:
![Wind Imports](https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/blob/master/00%20Documentation/Repository%20Images/ExhaustiveSearch-Example3.png)
4. Define the physical specifications of the WTG model:
![Wind Specifications](https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/blob/master/00%20Documentation/Repository%20Images/ExhaustiveSearch-Example4.png)
5. Define the root directory from which you want to import the irradiance resource profile:
![Solar Imports](https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/blob/master/00%20Documentation/Repository%20Images/ExhaustiveSearch-Example5.png)
6. Define the physical specifications and coordinate location of the solar photovoltaic module model:
![Solar Specifications](https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/blob/master/00%20Documentation/Repository%20Images/ExhaustiveSearch-Example6.png)
7. Define the root directory from which you want to import the load profile:
![Load Imports](https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/blob/master/00%20Documentation/Repository%20Images/ExhaustiveSearch-Example7.png)
8. Define the physical specifications of the storage cell model:
![Storage Specifications](https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/blob/master/00%20Documentation/Repository%20Images/ExhaustiveSearch-Example8.png)
9. Define the economic data for which the financial model should be run:
![Economic Data](https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/blob/master/00%20Documentation/Repository%20Images/ExhaustiveSearch-Example9.png)
10. Define the financial specifications of the components to be simulated:
![Storage Financial Data](https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/blob/master/00%20Documentation/Repository%20Images/ExhaustiveSearch-Example10.png)
![Wind Financial Data](https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/blob/master/00%20Documentation/Repository%20Images/ExhaustiveSearch-Example11.png)
![Solar Financial Data](https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/blob/master/00%20Documentation/Repository%20Images/ExhaustiveSearch-Example12.png)
11. Run:
```sh
python -m exhaustive_search.py
```


### Differential evolution HPP sizing optimisation in `main_differential_evolution.py`
The data import, component definitions, and financial definitions for running differential evolution are performed in the same way as described in the above section, however these definitions must be entered in `./ACSE9/Differential_Evolution.py`, where the objective function and feasibility constraint for differential evolution are defined.

To run differential evolution in `main_differential_evolution.py`, the user should define their desired bounds. NB: an evolutionary algorithm interprets the search-space not as a set of configurations to evaluate, but as a set of boundary conditions within which configurations can be generated.
![Differential Evolution Bounds](https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/blob/master/00%20Documentation/Repository%20Images/DifferentialEvolution-Example1.png)

To run:
```sh
python -m differential_evolution.py
```

<!-- FUTURE PLANS -->
## Future PLans

The architecture of the ACSE9 tool provides a useful platform for the development of a better-than industry standard software. The first step to improve the tool would be to reduce all validation errors near-zero. When the results are considered exactly equal to HOMER Pro, the run time of the ACSE9 tool could be improved with parallelisation. Since the ACSE9 tool in conjunction with SciPy’s differential evolution optimisation is already comparable in runtime to HOMER Pro discrete exhaustive search parallelisation would give a significant improvement on HPP optimisation runtime compared with the industry standard. Using the opportunity presented by the decreased runtime (i.e., reduced computational
load), the ACSE9 tool should seek to increase the complexity of the power output models used in its simulation. Opportunities from power output model improvement include, but are not limited to, a dynamic consideration of WTG wake effects, a dynamic model for PV module and li-ion cell aging, and the development of increased complexity storage models which consider, for example, SoC versus nominal voltage effects. Development could also continue by comparing to industry standard; developing higher resolution power output models which seek to match the performance of industry standard energy yield
analysis software such as PVSyst and WaSP. Future work should also include the inclusion and analysis of additional global optimisation methods, such as those presented by Anoune et al ( 2018). Notably, well designed multi-objective optimisation methods would allow for optimisation not only based
on NPC, but also added constraints and/or objectives such as lifecycle emissions and grid
stability. Finally, regarding the grid placement of the optimised HPP, it would be useful to develop a power trading revenue model which would reflect a grid-connected plant. HOMER Energy provides the industry standard for grid connected HPP sizing optimisation in its HOMER Grid software.


<!-- CONTRIBUTING -->
## Contributing

This tool is intended to be open-source, please feel free to contribute!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b foo/bar`)
3. Commit your Changes (`git commit -m 'Added bar'`)
4. Push to the Branch (`git push origin foo/bar`)
5. Open a Pull Request


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.


<!-- CONTACT -->
## Contact

Teddy Cheung - tc20@ic.ac.uk


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* [Professor Matthew Piggott](https://www.imperial.ac.uk/people/m.d.piggott)
* [Zoe Goss](https://www.imperial.ac.uk/people/z.goss15)
* [Dr. Roy Brown](https://www.linkedin.com/in/royhuttonbrown/?originalSubdomain=uk)


<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/github_username/repo.svg?style=for-the-badge
[contributors-url]: https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/graphs/contributors
[issues-shield]: https://img.shields.io/github/issues/github_username/repo.svg?style=for-the-badge
[issues-url]: https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/issues
[license-shield]: https://img.shields.io/github/license/github_username/repo.svg?style=for-the-badge
[license-url]: https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/teddy-cheung-5a4937a1/
