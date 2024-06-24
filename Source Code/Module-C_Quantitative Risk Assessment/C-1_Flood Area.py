# -*- coding: utf-8 -*-

# Author: Ziying Zhou
# Date: June 18, 2024
# Description: This script is used to calculate the flood area for combined scenarios.

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

polygon_dir = os.path.join(ModuleB_dir, "Polygon") # Folder for flood area in polygons(.shp)

exportarea_dir = os.path.join(ModuleC_dir, "ExportArea") # Folder for exported tables with area information
cityarea_dir = os.path.join(ModuleC_dir, "CityArea")  # Folder for flood area of different cities
generalarea_dir = os.path.join(ModuleC_dir, "GeneralArea") # Folder for total flood area under combined scenarios

# Global Constants ---------------------------------------------- #

## Lists 
listSurge = [r"0010a", r"0020a", r"0050a", r"0100a"]
listTide = [r"H", r"M"]
listSLR = [r"SSP0", r"SSP1", r"SSP5"]
listCity = [r"HK", r"SY", r"CJ", r"CM", r"DF", r"LD", r"LG", r"LS", r"QH", r"WN", r"WC", r"DZ"]
listGRIDCODE = [1, 2, 3, 4, 5, 6, 7, 8]

ratioArea = 1.0 / 1000000  # Conversion factor to square kilometers

######################################## Main Program ###########################################

# Calculate flood area ============================================================== #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):
        for k in range(len(listSLR)):

            polygon_path = os.path.join(polygon_dir, "polygon" + listSurge[i] + listTide[j] + listSLR[k] + ".shp")
            
            arcpy.management.AddField(in_table=polygon_path,
                                      field_name="Area",
                                      field_type="DOUBLE",
                                      field_precision=None,
                                      field_scale=None,
                                      field_length=None,
                                      field_alias="",
                                      field_is_nullable="NULLABLE",
                                      field_is_required="NON_REQUIRED",
                                      field_domain="")
            arcpy.management.CalculateGeometryAttributes(in_features=polygon_path,
                                                         geometry_property=[["Area", "AREA"]],
                                                         length_unit="",
                                                         area_unit="SQUARE_METERS",
                                                         coordinate_system="PROJCS[\"Albers_CN\",GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Albers\"],PARAMETER[\"false_easting\",0.0],PARAMETER[\"false_northing\",0.0],PARAMETER[\"central_meridian\",110.0],PARAMETER[\"standard_parallel_1\",25.0],PARAMETER[\"standard_parallel_2\",47.0],PARAMETER[\"latitude_of_origin\",0.0],UNIT[\"Meter\",1.0]]",
                                                         coordinate_format="SAME_AS_INPUT")
            print(polygon_path)

# Export area tables ================================================================ #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):
        for k in range(len(listSLR)):
            
            polygon_path = os.path.join(polygon_dir, "polygon" + listSurge[i] + listTide[j] + listSLR[k] + ".shp")
            exportarea_path = os.path.join(exportarea_dir, "exportarea" + listSurge[i] + listTide[j] + listSLR[k] + ".xlsx")

            arcpy.conversion.TableToExcel(Input_Table=polygon_path,
                                          Output_Excel_File=exportarea_path,
                                          Use_field_alias_as_column_header="NAME",
                                          Use_domain_and_subtype_description="CODE")
            print(exportarea_path)

# Calculate flood area for different cities ========================================= #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):
        for k in range(len(listSLR)):
            
            exportarea_path = os.path.join(exportarea_dir, "exportarea" + listSurge[i] + listTide[j] + listSLR[k] + ".xlsx")
            cityarea_path = os.path.join(cityarea_dir, "cityarea" + listSurge[i] + listTide[j] + listSLR[k] + ".xlsx")

            array = np.zeros((len(listCity), len(listGRIDCODE)))
            dfFrom = pd.read_excel(exportarea_path)
            for city_idx in range(len(listCity)):
                dfCity = dfFrom[dfFrom["Name"] == listCity[city_idx]]
                for gridcode_idx in range(len(listGRIDCODE)):
                    dfGRIDCODE = dfCity[dfCity["gridcode"] == listGRIDCODE[gridcode_idx]]    
                    array[city_idx, gridcode_idx] = np.sum(dfGRIDCODE["Area"]) * ratioArea         
            dfTo = pd.DataFrame(array, columns=listGRIDCODE)
            dfTo.insert(0, "City", listCity, allow_duplicates=False)
            dfTo.to_excel(cityarea_path, index=False)
            print(cityarea_path)
            
# Calculate total flood area under combined scenarios =============================== #

for j in range(len(listTide)):
    for k in range(len(listSLR)):
        
        array = np.zeros((len(listSurge), len(listGRIDCODE)))
        generalarea_path = os.path.join(generalarea_dir, "generalarea" + listTide[j] + listSLR[k] + ".xlsx")
        
        for i in range(len(listSurge)):
            file_path = os.path.join(cityarea_dir, "cityarea" + listSurge[i] + listTide[j] + listSLR[k] + ".xlsx")
            dfFrom = pd.read_excel(file_path)
            for gridcode_idx in range(len(listGRIDCODE)):
                array[i, gridcode_idx] = np.sum(dfFrom[str(listGRIDCODE[gridcode_idx])])
        dfTo = pd.DataFrame(array, columns=listGRIDCODE)
        dfTo.insert(0, "Surge", listSurge, allow_duplicates=False)
        dfTo.to_excel(generalarea_path, index=False)
        print(generalarea_path)