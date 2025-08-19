# A pipeline on portfolio-level tropical cyclone exceedance risk

This repository is used for a master thesis for KU Leuven Master program of Statistics and Data Science (AY2024 - AY2025).

While there are three branches, the 'main' branch contains all of the final work directly related with the thesis results. The other two branches, 'prisk' and 'storm', store the intermediate results and record some expriments.

If you want to operate the notebooks, please note that, besides the 'requirements.txt', you will need a CLIMADA environment to run certain Python modules. To configure a CLIMADA environment, please prepare a 'mini-forge' environment management system. It is a lighter, fully open-source version of Conda. The instruction for downloading it could be seen at https://github.com/conda-forge/miniforge.

Once 'mini-forge' is installed, please open its terminal and run the following mamba command line:

`mamba create -n climada_env -c conda-forge climada`

Everytime, to activate it, please run the mamba command line below in the 'mini-forge' terminal:

`mamba activate climada_env`

**results**: The key result is in the 'results' folder in the 'main' branch. Since this thesis highly relies on geographical locations, the results are presented in the format of visualizations. 

**Data**: The data used are all stored in 'Data' folder. It contains data from historical TC tracks, energy aassets information in India, STORM synthetic track database, exceedance for different energy sectors (they are results from initial procedure).

**shape_file**: The file helps to form the coastlines of India for better visualizations.

**images**: The images consist of results from different visualizations, such as for asset locations and track movements.

**exposures**: The folder contains the necessary information used to generate local exceedance intensities.

**prisk_tc**: The folder contains core functions from PRISK (https://github.com/rubenkerkhofs/PRISK). Please note that the second part of this thesis is to extend PRISK framework and its code implementation on tropical cyclones. Therefore, this functional package is originally from PRISK repository. We get the permission to apply the package to our thesis. However, please note that some details of the package is adapted to become this folder for tropical-cyclone-specific characteristics.
