# -*- coding: utf-8 -*-

# Author: Ziying Zhou
# Date: June 18, 2024
# Description: This script is used to select and pre-process synthetic TC tracks from the STORM Dataset.

################################## Initialization Settings ######################################

# Importing necessary Python packages --------------------------- #

import os
import pandas as pd
import arcpy

# Time reference ------------------------------------------------ #

## Number of years
YearNum = 250 

# Spatial reference --------------------------------------------- #

## Geographic coordinate system
GeoReference = '''GEOGCS['GCS_WGS_1984'
                ,DATUM['D_WGS_1984'
                ,SPHEROID['WGS_1984',6378137.0,298.257223563]]
                ,PRIMEM['Greenwich',0.0]
                ,UNIT['Degree',0.0174532925199433]]
                ;-400 -400 1000000000
                ;-100000 10000
                ;-100000 10000
                ;8.98315284119522E-09
                ;0.001;0.001
                ;IsHighPrecision'''

# Input/Output settings ----------------------------------------- #

System = r"A:/"
root = os.path.join(System, r"Project_StormSurge")
ModuleA_dir = os.path.join(root, r"ModuleA")

prepare_dir = os.path.join(ModuleA_dir, "Prepare")  # Folder for prepared data
encode_dir = os.path.join(ModuleA_dir, "Encode")  # Folder for encoded data (N+[Year 3 characters]+[Number 2 characters])
table_encode_dir = os.path.join(ModuleA_dir, "TableByCode")  # Folder for output tables by Code
table_year_dir = os.path.join(ModuleA_dir, "TableByYear")  # Folder for output tables by Year
point_year_dir = os.path.join(ModuleA_dir, "PointByYear")  # Folder for points(.shp) by Year
line_year_dir = os.path.join(ModuleA_dir, "LineByYear")  # Folder for lines(.shp) by Year
merge_dir = os.path.join(ModuleA_dir, "Merge")  # Folder for merge lines
select_dir = os.path.join(ModuleA_dir, "Select")  # Folder for selected landfall tracks
point_encode_dir = os.path.join(ModuleA_dir, "PointByCode")  # Folder for points(.shp) by Code
range_dir = os.path.join(ModuleA_dir, "Range")  # Folder for extracted points within 800km buffer zone
record_dir = os.path.join(ModuleA_dir, "Record")  # Folder for table records converted from points(.shp)

txt_path = os.path.join(prepare_dir, "STORM_DATA_IBTRACS_WP_1000_YEARS_0.txt") # Original data of STORM dataset(.txt)
csv_path = os.path.join(prepare_dir, "STORM_DATA_IBTRACS_WP_1000_YEARS_0.csv") # Processed data of STORM dataset(.csv)
buf200_path = os.path.join(prepare_dir, "Hainan_Buffer200km.shp") # Buffer of Hainan Island with 200km radius
buf800_path = os.path.join(prepare_dir, "Hainan_Buffer800km.shp") # Buffer of Hainan Island with 800km radius

encode_path = os.path.join(encode_dir, "STORM_IBTRACS_Code_" + str(YearNum) + "yr.xlsx") # Encoded data of STORM dataset(.xlsx)
merge_line_path = os.path.join(merge_dir, "Merge_" + str(YearNum) + "yr_1.shp") # Merged lines(.shp) of TC tracks

select_table_path = os.path.join(select_dir, "Select_" + str(YearNum) + "yr_buf200km.xlsx") # Selected table records(.xlsx) of TC tracks 
select_line_path = os.path.join(select_dir, "Select_" + str(YearNum) + "yr_buf200km_1.shp") # Selected lines(.shp) of TC tracks 

# Global Constants ---------------------------------------------- #

## Header of STORM dataset
Header = ['Year', 'Month', 'Number', 'Time', 'Basin',
          'LAT', 'LONG', 'MP', 'MWS', 'RMW',
          'Category', 'Landfall', 'Distance']

######################################## Main Program ###########################################

# Convert original data format (txt->csv) =========================================== #

df = pd.read_csv(txt_path)
df = pd.DataFrame(df)
df.to_csv(csv_path, header=Header, index=False)

# Encoding (N+[Year 3 characters]+[Number 2 characters]) ==================================== #

dfFrom = pd.read_csv(csv_path)
dfYear = dfFrom[dfFrom["Year"] < YearNum]

listTCid = []
for i in range(len(dfYear)):
    dfTemp = dfYear.iloc[i]
    tcid = "TC" + str(int(dfTemp["Year"]) + 1000)[-3:] + str(int(dfTemp["Number"]) + 100)[-2:]
    listTCid.append(tcid)
dfYear["TCid"] = listTCid
dfYear.to_excel(encode_path, index=False)
print(encode_path)

# Output tables by Code ============================================================= #

dfFrom = pd.read_excel(encode_path)
listTCid = list(set(dfFrom["TCid"])) 
print(listTCid)

for i in range(len(listTCid)):
    dfTo = dfFrom[dfFrom["TCid"] == listTCid[i]]
    tcid_path = os.path.join(table_encode_dir, listTCid[i] + ".xlsx")
    dfTo.to_excel(tcid_path, index=False)
    print(tcid_path)

# Output tables by Year ============================================================= #

dfFrom = pd.read_excel(encode_path)
for year in range(YearNum):
    yearid = "Y" + str(year + 1000)[-3:]
    year_path = os.path.join(table_year_dir, yearid + ".xlsx")
    dfTo = dfFrom[dfFrom["Year"] == year]
    dfTo.to_excel(year_path, index=False)
    print(year_path)

# Generate points(.shp) by Year ===================================================== #

for year in range(YearNum):
    yearid = "Y" + str(year + 1000)[-3:]
    table_year_path = os.path.join(table_year_dir, yearid + ".xlsx\Sheet1$")
    point_year_path = os.path.join(point_year_dir, yearid + "_0.shp")
    arcpy.management.Delete(yearid)
    arcpy.MakeXYEventLayer_management(table_year_path, "LONG", "LAT", yearid, GeoReference, "")
    arcpy.CopyFeatures_management(yearid, point_year_path)
    print(point_year_path)    

# Generate lines(.shp) by Year ====================================================== #

for year in range(YearNum):
    yearid = "Y" + str(year + 1000)[-3:]
    point_year_path = os.path.join(point_year_dir, yearid + "_0.shp")
    line_year_path = os.path.join(line_year_dir, yearid + "_1.shp")
    arcpy.PointsToLine_management(point_year_path, line_year_path, "Number", "Time", "NO_CLOSE")
    arcpy.JoinField_management(line_year_path, "Number", point_year_path, "Number", fields=["Year", "TCid"])
    print(line_year_path)

# Merge lines ======================================================================= #

listLine = []
for year in range(YearNum): 
    yearid = "Y" + str(year + 1000)[-3:] 
    line_year_path = os.path.join(line_year_dir, yearid + r"_1.shp")
    listLine.append(line_year_path)
arcpy.management.Merge(inputs=listLine, output=merge_line_path, field_mappings="", add_source="NO_SOURCE_INFO")
print(merge_line_path)

# Select lines passing 200km buffer zone  =========================================== #

tempLayer = arcpy.management.SelectLayerByLocation(in_layer=merge_line_path,
                                                   overlap_type="INTERSECT",
                                                   select_features=buf200_path,
                                                   search_distance="0 DecimalDegrees",
                                                   selection_type="NEW_SELECTION",
                                                   invert_spatial_relationship="NOT_INVERT")

arcpy.management.CopyFeatures(in_features=tempLayer, out_feature_class=select_line_path,
                              config_keyword="", spatial_grid_1=None,
                              spatial_grid_2=None, spatial_grid_3=None)

arcpy.conversion.TableToExcel(Input_Table=select_line_path, Output_Excel_File=select_table_path,
                              Use_field_alias_as_column_header="NAME", Use_domain_and_subtype_description="CODE")

df = pd.read_excel(select_table_path)
listReID = []
for i in range(len(df)):
    reid = "RE" + str(10000 + i)[-4:]
    listReID.append(reid)
df["REid"] = listReID
df.to_excel(select_table_path, index=False)

# Generate points(.shp) by Code ===================================================== #

df = pd.read_excel(select_table_path)
for i in range(len(df)):
    dfTemp = df.iloc[i]
    tcid = str(dfTemp["TCid"])
    reid = str(dfTemp["REid"])
    table_code_path = os.path.join(table_encode_dir, tcid + r".xlsx\Sheet1$")
    point_code_path = os.path.join(point_encode_dir, reid + r"_0.shp")
    arcpy.MakeXYEventLayer_management(table_code_path, "LONG", "LAT", reid, GeoReference, "")
    arcpy.CopyFeatures_management(reid, point_code_path)
    print(point_code_path)

# Extract points within 800km buffer zone =========================================== #

df = pd.read_excel(select_table_path)
for i in range(len(df)):
    dfTemp = df.iloc[i]
    reid = str(dfTemp["REid"])
    point_code_path = os.path.join(point_encode_dir, reid + r"_0.shp")
    range_path = os.path.join(range_dir, reid + r"_0.shp") 
    arcpy.analysis.Clip(in_features=point_code_path, clip_features=buf800_path,
                        out_feature_class=range_path, cluster_tolerance="")
    print(range_path)

# Convert points(.shp) to table records(.xlsx) ====================================== #

df = pd.read_excel(select_table_path)
for i in range(len(df)):
    dfTemp = df.iloc[i]
    reid = str(dfTemp["REid"])
    range_path = os.path.join(range_dir, reid + r"_0.shp")
    record_path = os.path.join(record_dir, reid + ".xlsx")  
    arcpy.conversion.TableToExcel(Input_Table=range_path,
                                  Output_Excel_File=record_path,
                                  Use_field_alias_as_column_header="NAME",
                                  Use_domain_and_subtype_description="CODE")
    print(record_path)