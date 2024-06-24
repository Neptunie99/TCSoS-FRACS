# -*- coding: utf-8 -*-

# Author: Ziying Zhou
# Date: June 18, 2024
# Description: This script is used to estimate economic loss for combined scenarios.

############################## Initialization Settings #####################################

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

prepare_dir = os.path.join(ModuleC_dir, "Prepare") # Folder for prepared data
population_dir = os.path.join(ModuleC_dir, "Population") # Folder for affected population under combined secenerios
intersect_dir = os.path.join(ModuleC_dir, "Intersect") # Folder for unit areas with flood and loss information
exportloss_dir = os.path.join(ModuleC_dir, "ExportLoss") # Folder for exported tables with loss information
cityrisk_dir = os.path.join(ModuleC_dir, "CityRisk") # Folder for economic loss of different cities
generalrisk_dir = os.path.join(ModuleC_dir, "GeneralRisk") # Folder for total economic loss under combined scenarios

landuse_path = os.path.join(prepare_dir, "Landuse.shp") # Land use data with each type linked to unit loss by flood depth

# Global Constants ---------------------------------------------- #

## Lists 
listSurge = [r"0010a", r"0020a", r"0050a", r"0100a"]
listTide = [r"H", r"M"]
listSLR = [r"SSP0", r"SSP1", r"SSP5"]
listCity = [r"HK", r"SY", r"CJ", r"CM", r"DF", r"LD", r"LG", r"LS", r"QH", r"WN", r"WC", r"DZ"]
listGRIDCODE = [1, 2, 3, 4, 5, 6, 7, 8]

## Ratios
ratioArea = 1.0 / 1000000
ratioLoss = 1.0 / 1000000000
ratioPop = 1.0 / 1000000

################################ Main Program ##############################################

# Combine flood and landuse information to calculate economic loss ================== #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):       
        for k in range(len(listSLR)):

            polygon_path = os.path.join(polygon_dir, "polygon" + listSurge[i] + listTide[j] + listSLR[k] + ".shp")
            intersect_path = os.path.join(intersect_dir, "intersect" + listSurge[i] + listTide[j] + listSLR[k] + ".shp")
            
            arcpy.analysis.Intersect(in_features=[[landuse_path, ""], [polygon_path, ""]],
                                     out_feature_class=intersect_path,
                                     join_attributes="ALL",
                                     cluster_tolerance="",
                                     output_type="INPUT")
            
            arcpy.management.AddField(in_table=intersect_path,
                                      field_name="Area",
                                      field_type="DOUBLE",
                                      field_precision=None,
                                      field_scale=None,
                                      field_length=None,
                                      field_alias="",
                                      field_is_nullable="NULLABLE",
                                      field_is_required="NON_REQUIRED",
                                      field_domain="")
            
            arcpy.management.CalculateGeometryAttributes(in_features=intersect_path,
                                                         geometry_property=[["Area", "AREA"]],
                                                         length_unit="", area_unit="SQUARE_METERS",
                                                         coordinate_system="PROJCS[\"Albers_CN\",GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Albers\"],PARAMETER[\"false_easting\",0.0],PARAMETER[\"false_northing\",0.0],PARAMETER[\"central_meridian\",110.0],PARAMETER[\"standard_parallel_1\",25.0],PARAMETER[\"standard_parallel_2\",47.0],PARAMETER[\"latitude_of_origin\",0.0],UNIT[\"Meter\",1.0]]",
                                                         coordinate_format="SAME_AS_INPUT")
            
            arcpy.management.AddField(in_table=intersect_path,
                                      field_name="UnitValue",
                                      field_type="DOUBLE",
                                      field_precision=None,
                                      field_scale=None,
                                      field_length=None,
                                      field_alias="",
                                      field_is_nullable="NULLABLE",
                                      field_is_required="NON_REQUIRED",
                                      field_domain="") 
            
            arcpy.management.CalculateField(in_table=intersect_path,
                                            field="UnitValue",
                                            expression="CalLoss(!Dep05!,!Dep10!,!Dep15!,!Dep20!,!Dep30!,!Dep40!,!Dep50!,!Dep60!,!gridcode!)",
                                            expression_type="PYTHON3",
                                            code_block="""def CalLoss(a1, a2, a3, a4, a5, a6, a7, a8, depth):
                                                        loss = 0
                                                        if depth == 1:
                                                            loss = a1
                                                        if depth == 2:
                                                            loss = a2
                                                        if depth == 3:
                                                            loss = a3
                                                        if depth == 4:
                                                            loss = a4
                                                        if depth == 5:
                                                            loss = a5
                                                        if depth == 6:
                                                            loss = a6
                                                        if depth == 7:
                                                            loss = a7
                                                        if depth == 8:
                                                            loss = a8
                                                        return loss""",
                                            field_type="TEXT",
                                            enforce_domains="NO_ENFORCE_DOMAINS")
                
            arcpy.management.AddField(in_table=intersect_path,
                                      field_name="Loss",
                                      field_type="DOUBLE",
                                      field_precision=None,
                                      field_scale=None,
                                      field_length=None,
                                      field_alias="",
                                      field_is_nullable="NULLABLE",
                                      field_is_required="NON_REQUIRED",
                                      field_domain="")
            
            arcpy.management.CalculateField(in_table=intersect_path,
                                            field="Loss",
                                            expression="!Area! * !UnitValue!",
                                            expression_type="PYTHON3",
                                            code_block="",
                                            field_type="TEXT",
                                            enforce_domains="NO_ENFORCE_DOMAINS")
            print(intersect_path)

# Export loss tables ================================================================ #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):       
        for k in range(len(listSLR)):
            
            intersect_path = os.path.join(intersect_dir, "intersect" + listSurge[i] + listTide[j] + listSLR[k] + ".shp")
            exportloss_path = os.path.join(exportloss_dir, "exportloss" + listSurge[i] + listTide[j] + listSLR[k] + ".xlsx")
            
            arcpy.conversion.TableToExcel(Input_Table=intersect_path,
                                          Output_Excel_File=exportloss_path,
                                          Use_field_alias_as_column_header="NAME",
                                          Use_domain_and_subtype_description="CODE")
            print(exportloss_path)

# Calculate city risk(flood area + affected population + economic loss) ============= #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):       
        for k in range(len(listSLR)):
            
            intersect_path = os.path.join(intersect_dir, "intersect" + listSurge[i] + listTide[j] + listSLR[k] + ".shp")
            exportloss_path = os.path.join(exportloss_dir, "exportloss" + listSurge[i] + listTide[j] + listSLR[k] + ".xlsx")
            population_path = os.path.join(population_dir, "population" + listSurge[i] + listTide[j] + listSLR[k] + ".xlsx")
            
            array = np.zeros((len(listCity), 3))
            dfFrom = pd.read_excel(exportloss_path)
            dfPop = pd.read_excel(population_path)
            for city_idx in range(len(listCity)):
                dfCity1 = dfFrom[dfFrom["Name"] == listCity[city_idx]]
                array[city_idx, 0] = np.sum(dfCity1["Area"]) * ratioArea
                array[city_idx, 1] = np.sum(dfCity1["Loss"]) * ratioLoss
                dfCity2 = dfPop[dfPop["City"] == listCity[city_idx]]
                array[city_idx, 2] = dfCity2["Pop"].values[0] * ratioPop
            dfTo = pd.DataFrame(array, columns=["Area", "Loss", "Pop"])
            dfTo.insert(0, "City", listCity, allow_duplicates=False)
            dfTo.to_excel(os.path.join(cityrisk_dir, "cityrisk" + listSurge[i] + listTide[j] + listSLR[k] + ".xlsx"), index=False)
            print(os.path.join(cityrisk_dir, "cityrisk" + listSurge[i] + listTide[j] + listSLR[k] + ".xlsx"))

# Calculate general risk(flood area + affected population + economic loss) ========== #

for j in range(len(listTide)):
    for k in range(len(listSLR)):
        
        generalrisk_path = os.path.join(generalrisk_dir, "generalrisk" + listTide[j] + listSLR[k] + ".xlsx")
        array = np.zeros((len(listSurge), 3))
        
        for i in range(len(listSurge)):
            file_path = os.path.join(cityrisk_dir, "cityrisk" + listSurge[i] + listTide[j] + listSLR[k] + ".xlsx")
            dfFrom = pd.read_excel(file_path)
            array[i, 0] = np.sum(dfFrom["Area"])
            array[i, 1] = np.sum(dfFrom["Loss"])
            array[i, 2] = np.sum(dfFrom["Pop"])
        dfTo = pd.DataFrame(array, columns=["Area", "Loss", "Pop"])
        dfTo.insert(0, "Surge", listSurge, allow_duplicates=False)
        dfTo.to_excel(generalrisk_path, index=False)
        print(generalrisk_path)