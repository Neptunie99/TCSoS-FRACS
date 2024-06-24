# **TCSoS-FRACS**: Tropical Cyclone Storm Surge-Based Flood Risk Assessment under Combined Scenarios of High Tides and Sea Level Rises

## Overview

This repository contains the source code and processed data used in the study titled "Tropical Cyclone Storm Surge-Based Flood Risk Assessment under Combined Scenarios of High Tides and Sea Level Rises". The study develops and applies the TCSoS-FRACS model to assess the TC storm surge flood risk under various combined scenarios.

## Table Content

```
TCSoS-FRACS
├── Source Code
│   ├── Module-A_Storm Surge Estimation
│   │   ├── A-1_TC-tracks Selection.py
│   │   ├── A-2_ADCIRC Batch Running.py
│   │   ├── A-3_Annual Maximum Statistics.py
│   ├── Module-B_Combined Scenario Construction
│   │   ├── B-1_Combined Scenario.py
│   │   ├── B-2_Inundation Calculation.py
│   ├── Module-C_Quantitative Risk Assessment
│   │   ├── C-1_Flood Area.py
│   │   ├── C-2_Effected Population.py
│   │   ├── C-3_Economic Loss.py
├── Processed Data
│   ├── Select_250yr_buf200km.xlsx
│   ├── Record.rar
│   ├── MaxSurge/
│   ├── MaxSurge_Year/
│   ├── MaxSurge_Return.csv
│   ├── Inundation.rar
│   ├── CityArea/
│   ├── GeneralArea/
│   ├── CityRisk/
│   ├── GeneralRisk/
├── LICENSE
└── README.md
```

## Source Code


   ### Module-A: Storm Surge Estimation

   - **A-1_TC-tracks Selection.py**: This script is used to select and preprocess synthetic TC tracks from the STORM Dataset.
   - **A-2_ADCIRC Batch Running.py**: This script is used to batch generate and run ADCIRC models.
   - **A-3_Annual Maximum Statistics.py**: This script is used to calculate the annual maximum storm surges.
   - **A-4_Return Period Calculation.py**: This script is used to estimate return periods of storm surges using GEV functions.

   ### Module-B: Combined Scenario Construction

   - **B-1_Combined Scenario.py**: This script is used to estimate the total water level under combined scenarios (mean sea level + astronomical tide + storm surge).
   - **B-2_Inundation Calculation.py**: This script is used to calculate inundation for combined scenarios.

   ### Module-C: Quantitative Risk Assessment

   - **C-1_Flood Area.py**: This script is used to calculate the flood areas for combined scenarios.
   - **C-2_Effected Population.py**: This script is used to estimate the affected population for combined scenarios.
   - **C-3_Economic Loss.py**: This script is used to estimate economic loss for combined scenarios.

## Processed Data
- `Select_250yr_buf200km.xlsx`: Selected TC tracks from the STORM dataset passing within a 200km buffer zone of Hainan Island over a 250-year period. This file includes fields such as original ID ("TCid"), re-encoded ID ("REid"), and year ("Year").
- `Record.rar`: Hourly records of selected TC tracks during the impact process, including fields such as latitude ("LAT"), longitude ("LONG"), minimum pressure ("MP"), maximum wind speed ("MWS"), and maximum wind radius ("RMW"). The data is compressed into a RAR file due to its large size.
- `MaxSurge/`: Maximum storm surges at all locations for each ADCIRC simulation.
- `MaxSurge_Year/`: Annual maximum storm surges at all locations based on the corresponding years of TC tracks.
- `MaxSurge_Return.csv`: Storm surges at all locations for 10-year, 20-year, 50-year, and 100-year return periods.
- `Inundation.rar`: Inundation data for 24 combined scenarios in TIFF  format. The naming rule is "inundation+[storm surge (5 characters)]+[astronomical tide (1 character)]+[sea level (4 characters)]+.tif". The data is compressed into a RAR file due to its large size.
- `CityArea/`: City flood area grouped by depth for 24 combined scenarios, measured in km<sup>2</sup>.
- `GeneralArea/`: General flood area grouped by depth for 24 combined scenarios, measured in km<sup>2</sup>. Scenarios with same astronomical tide and sea level are consolidated into a file.
- `CityRisk/`: City risk for 24 combined scenarios, including flood area (km<sup>2</sup>), affected population (million), and  economic loss (million $).
- `GeneralRisk/`: General risk for 24 combined scenarios, including flood area (km<sup>2</sup>), affected population (million), and  economic loss (million $). Scenarios with same astronomical tide and sea level are consolidated into a file.


## Requirements

The following Python packages are required to run the scripts: 
- `arcpy` (recommended version >= 2.8.4)
- `datetime`
- `pandas`
- `scipy`
- `shutil`

## Data Availability

The data used in this study are sourced from publicly accessible datasets:

- **[General Bathymetric Chart of the Oceans (GEBCO)](https://www.gebco.net/data_and_products/gridded_bathymetry_data/)**: Provides bathymetry maps with a resolution of 15 arc-seconds (approximately 450 m).
- **[Shuttle Radar Topography Mission Version 4 (SRTM V4)](https://srtm.csi.cgiar.org/srtmdata/)**: Provides digital elevation maps with a resolution of 90 m.
- **[China National Marine Data Center](http://mds.nmdis.org.cn/pages/tidalCurrent.html)**: Supplies hourly observations from tidal gauges across China.
- **[China Meteorological Administration Tropical Cyclone Database](http://tcdata.typhoon.org.cn)**: Supplies historical TC tracks in the   Northwest Pacific, including records of  time, location, and intensity.
- **[Synthetic Tropical cyclOne geneRation Model (STORM) Dataset](https://data.4tu.nl/datasets/01b2ebc7-7903-42ef-b46b-f43b9175dbf4/4)**: Supplies synthetic TC tracks globally, including records of  time, location, and intensity.
- **[Essential Urban Land Use Categories in China (EULUC-China)](http://data.starcloud.pcl.ac.cn/zh)**: Contains urban land uses such as residential, commercial, industrial, transport, and public areas.
- **[WorldPop Gridded Population Count Dataset](https://hub.worldpop.org)**: Offers current population distributions with a resolution of 100 m.
- **[Gridded datasets for population and economy under Shared Socioeconomic Pathways](https://doi.org/10.57760/sciencedb.01683)**: Offers future population distributions under  Shared Socioeconomic Pathways. 
- **[IPCC 6th Assessment Report Sea Level Projections](https://sealevel.nasa.gov/ipcc-ar6-sea-level-projection-tool)**: Provides future sea level projections under Shared Socioeconomic Pathways, relative to the period 1995–2014.
- **[Global flood depth-damage functions](https://publications.jrc.ec.europa.eu/repository/handle/JRC105688)**: Provides the global flood damage databas, including economic exposure and flood depth-loss functions for agriculture, transport, commercial, industrial, and residential areas.

## Applications

The TCSoS-FRACS model holds significant value for multiple stakeholders, including urban planners, disaster management authorities, and policymakers. Its applications include:

- **Urban Planning**: Helps in designing resilient urban infrastructure by identifying areas prone to flooding under various scenarios. 
- **Disaster Management**: Assists in developing effective evacuation plans and emergency response strategies by predicting potential flood impacts. 
- **Policy Making**: Informs policy decisions regarding land use, zoning, and investment in flood defense mechanisms. 
- **Climate Change Adaptation**: Provides insights into the future risks associated with sea-level rise and extreme weather events, facilitating long-term adaptation strategies. 

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute the code and data provided in this repository, provided that the following conditions are met:

- **Attribution**: You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- **Non-Commercial**: You may not use the material for commercial purposes.
- **No Additional Restrictions**: You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

The full text of the license can be found in the `LICENSE` file included in this repository. For more details, see the MIT License.
