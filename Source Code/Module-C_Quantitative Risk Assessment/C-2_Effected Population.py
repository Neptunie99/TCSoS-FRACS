# -*- coding: utf-8 -*-

# Author: Ziying Zhou
# Date: June 18, 2024
# Description: This script is used to estimate the affected population for combined scenarios.

################################## Initialization Settings ######################################

# Importing necessary Python packages --------------------------- #

import os
import arcpy
import numpy as np
import pandas as pd

# Input/Output settings ----------------------------------------- #

System = r"A:/"
root = os.path.join(System, r"Project_StormSurge")
ModuleB_dir = os.path.join(root, r"ModuleB")
ModuleC_dir = os.path.join(root, r"ModuleC")

polygon_dir = os.path.join(ModuleB_dir, "Polygon") # Folder for flood areas in polygons(.shp)

prepare_dir = os.path.join(ModuleC_dir, "Prepare")  # Folder for prepared data
popfuture_dir = os.path.join(ModuleC_dir, "PopFuture")  # Folder for future population
range_dir = os.path.join(ModuleC_dir, "Range") # Folder for flood ranges under combined scenarios
extramask_dir = os.path.join(ModuleC_dir, "ExtractByMask")  # Folder for extracted population by flood range
zonaltable_dir = os.path.join(ModuleC_dir, "ZonalTable")  # Folder for zonal statistics of affected population
tablexlsx_dir = os.path.join(ModuleC_dir, "TabletoExcel")  # Folder for exported tables convert from (.dbf) to (.xlsx)
population_dir = os.path.join(ModuleC_dir, "Population")  # Folder for affected population under combined secenerios

hainan_path = os.path.join(prepare_dir,"Hainan_coast.shp") # Polygon(.shp) of Hainan Island

# Global Constants ---------------------------------------------- #

## Lists
listCity = [r"HK", r"SY", r"CJ", r"CM", r"DF", r"LD", r"LG", r"LS", r"QH", r"WN", r"WC", r"DZ"]
listSurge = [r"0010a", r"0020a", r"0050a", r"0100a"]
listTide = [r"H", r"M"]
listSLR = [r"SSP0", r"SSP1", r"SSP5"]  
  
######################################## Main Program ###########################################

# Generate flood ranges under combined scenerios ==================================== #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):
        for k in range(len(listSLR)):
            
            polygon_path = os.path.join(polygon_dir, "polygon" + listSurge[i] + listTide[j] + listSLR[k] + ".shp")
            range_path = os.path.join(range_dir, "range" + listSurge[i] + listTide[j] + listSLR[k] + ".shp") 
             
            arcpy.management.Dissolve(in_features=polygon_path,
                                      out_feature_class=range_path,
                                      dissolve_field=[],
                                      statistics_fields=[],
                                      multi_part="SINGLE_PART",
                                      unsplit_lines="DISSOLVE_LINES")
            print(range_path) 

# Extract population by flood ranges ================================================ #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):
        for k in range(len(listSLR)):
            
            range_path = os.path.join(range_dir, "range" + listSurge[i] + listTide[j] + listSLR[k] + ".shp")  
            extract_path = os.path.join(extramask_dir, "extract" + listSurge[i] + listTide[j] + listSLR[k] + ".tif")
            ras_path = os.path.join(popfuture_dir, "POP_" + listSLR[k] + ".tif")
            
            rasExtract = arcpy.sa.ExtractByMask(in_raster=ras_path, in_mask_data=range_path)
            rasExtract.save(extract_path)
            print(extract_path)
        
# Zonal statistics ================================================================== #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):
        for k in range(len(listSLR)):
                
            extramask_path = os.path.join(extramask_dir, "extract" + listSurge[i] + listTide[j] + listSLR[k] + ".tif")
            zonaltable_path = os.path.join(zonaltable_dir, "zonal" + listSurge[i] + listTide[j] + listSLR[k] + ".dbf")
            
            arcpy.sa.ZonalStatisticsAsTable(in_zone_data=hainan_path,
                                            zone_field="Name",
                                            in_value_raster=extramask_path,
                                            out_table=zonaltable_path,
                                            ignore_nodata="DATA",
                                            statistics_type="ALL",
                                            process_as_multidimensional="CURRENT_SLICE",
                                            percentile_values=90,
                                            percentile_interpolation_type="AUTO_DETECT")
            print(zonaltable_path)
        
# Convert from (.dbf) to (.xlsx) ==================================================== #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):
        for k in range(len(listSLR)):
            
            zonaltable_path = os.path.join(zonaltable_dir, "zonal" + listSurge[i] + listTide[j] + listSLR[k] + ".dbf")
            tablexlsx_path = os.path.join(tablexlsx_dir, "excel" + listSurge[i] + listTide[j] + listSLR[k] + ".xlsx")
            
            arcpy.conversion.TableToExcel(Input_Table=zonaltable_path,
                                          Output_Excel_File=tablexlsx_path,
                                          Use_field_alias_as_column_header="NAME",
                                          Use_domain_and_subtype_description="CODE")
            print(tablexlsx_path)

# Calculate affected population under combined scenrios ============================= #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):
        for k in range(len(listSLR)):
            
            tablexlsx_path = os.path.join(tablexlsx_dir, "excel" + listSurge[i] + listTide[j] + listSLR[k] + ".xlsx")
            population_path = os.path.join(population_dir, "population" + listSurge[i] + listTide[j] + listSLR[k] + ".xlsx")
            
            dfFrom = pd.read_excel(tablexlsx_path)
            array = np.array(dfFrom["SUM"])
            for n in range(len(array)):
                array[n] = round(array[n])
            dfTo = pd.DataFrame(listCity, columns=["City"])
            dfTo["Pop"] = array
            dfTo.to_excel(population_path, index=False)
            print(population_path)