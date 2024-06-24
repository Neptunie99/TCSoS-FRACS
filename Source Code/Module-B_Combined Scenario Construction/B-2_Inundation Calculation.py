# -*- coding: utf-8 -*-

# Author: Ziying Zhou
# Date: June 18, 2024
# Description: This script is used to calculate inundation for combined scenarios.

################################## Initialization Settings ######################################

# Importing necessary Python packages --------------------------- #

import os
import arcpy

# Input/Output settings ----------------------------------------- #

System = r"A:/"
root = os.path.join(System, r"Project_StormSurge")
ModuleB_dir = os.path.join(root, r"ModuleB")

prepare_dir = os.path.join(ModuleB_dir, "Prepare")  # Folder for prepared data
combined_dir = os.path.join(ModuleB_dir, "Combined")  # Folder for combined scenarios
inundation_dir = os.path.join(ModuleB_dir, "Inundation")  # Folder for inundation under combined scenarios
project_dir = os.path.join(ModuleB_dir, "Project")  # Folder for projected data (Albers Equal-Area Conic Projection)
reclass_dir = os.path.join(ModuleB_dir, "Reclass")  # Folder for reclassified data by depth
polygon_dir = os.path.join(ModuleB_dir, "Polygon")  # Folder for flood areas in polygons(.shp)

dem_path = os.path.join(prepare_dir, "dem.tif") # DEM data
dist_path = os.path.join(prepare_dir, "Distance.tif") # Distance from coastline
attenu_path = os.path.join(prepare_dir, "Attenuation.tif") # Attenuation for Hainan Island

# Spatial reference --------------------------------------------- #

## Geographic coordinate system
GCSReference = '''GEOGCS['GCS_WGS_1984'
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
 
## Projected coordinate system
PCSReference = '''PROJCS['Albers_CN'
                ,GEOGCS['GCS_WGS_1984'
                ,DATUM['D_WGS_1984'
                ,SPHEROID['WGS_1984',6378137.0,298.257223563]]
                ,PRIMEM['Greenwich',0.0]
                ,UNIT['Degree',0.0174532925199433]]
                ,PROJECTION['Albers']
                ,PARAMETER['False_Easting',0.0]
                ,PARAMETER['False_Northing',0.0]
                ,PARAMETER['Central_Meridian',110.0]
                ,PARAMETER['Standard_Parallel_1',25.0]
                ,PARAMETER['Standard_Parallel_2',47.0]
                ,PARAMETER['Latitude_Of_Origin',0.0]
                ,UNIT['Meter',1.0]]'''

## Spatial Analyst Environment 
arcpy.EnvManager(cellSize=dem_path, mask=dem_path, snapRaster=dem_path)
arcpy.env.overwriteOutput = True

# Global Constants ---------------------------------------------- #

## Lists
listSurge = [r"0010a", r"0020a", r"0050a", r"0100a"]
listTide = [r"H", r"M"]
listSLR = [r"SSP0", r"SSP1", r"SSP5"]

######################################## Main Program ###########################################

# Calculate inundation ============================================================== #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):
        for k in range(len(listSLR)):
            
            combined_path = os.path.join(combined_dir, "combined" + listSurge[i] + listTide[j] + listSLR[k] + ".tif") 
            inundation_path = os.path.join(inundation_dir, "inundation" + listSurge[i] + listTide[j] + listSLR[k] + ".tif") 
            
            rasDEM = arcpy.Raster(dem_path)
            rasDist = arcpy.Raster(dist_path) 
            rasAttenu = arcpy.Raster(attenu_path) 
            rasCombined = arcpy.Raster(combined_path)
            rasInundation = arcpy.sa.Con((rasCombined - rasDEM - rasAttenu*rasDist) > 0, rasCombined - rasDEM - rasAttenu*rasDist, 0)
            rasInundation.save(inundation_path)
            print(inundation_path)

# Project raster ==================================================================== #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):
        for k in range(len(listSLR)):
            
            inundation_path = os.path.join(inundation_dir, "inundation" + listSurge[i] + listTide[j] + listSLR[k] + ".tif") 
            project_path = os.path.join(project_dir, "project" + listSurge[i] + listTide[j] + listSLR[k] + ".tif")
            
            arcpy.management.ProjectRaster(in_raster=inundation_path,
                                           out_raster=project_path,
                                           out_coor_system=PCSReference,
                                           resampling_type="NEAREST",
                                           cell_size="91.9975987229944 91.9975987229944",
                                           geographic_transform=[],
                                           Registration_Point="",
                                           in_coor_system=GCSReference,
                                           vertical="NO_VERTICAL")
            print(project_path)

# Reclassify by flood depth ========================================================= #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):
        for k in range(len(listSLR)):
            
            project_path = os.path.join(project_dir, "project" + listSurge[i] + listTide[j] + listSLR[k] + ".tif")
            reclass_path = os.path.join(reclass_dir, "reclass" + listSurge[i] + listTide[j] + listSLR[k] + ".tif")  
            
            rasReclass = arcpy.sa.Reclassify(in_raster=project_path,
                                             reclass_field="VALUE",
                                             remap="0 NODATA;0 0.500000 1;0.500000 1 2;1 1.500000 3;1.500000 2 4;2 3 5;3 4 6;4 5 7;5 6 8",
                                             missing_values="DATA")
            rasReclass.save(reclass_path)
            print(reclass_path)

# Convert raster(.tif) to polygon(.shp) ============================================= #

for i in range(len(listSurge)):   
    for j in range(len(listTide)):
        for k in range(len(listSLR)):
            
            reclass_path = os.path.join(reclass_dir, "reclass" + listSurge[i] + listTide[j] + listSLR[k] + ".tif")
            polygon_path = os.path.join(polygon_dir, "polygon" + listSurge[i] + listTide[j] + listSLR[k] + ".shp") 
            
            arcpy.conversion.RasterToPolygon(in_raster=reclass_path,
                                             out_polygon_features=polygon_path,
                                             simplify="NO_SIMPLIFY",
                                             raster_field="Value",
                                             create_multipart_features="SINGLE_OUTER_PART",
                                             max_vertices_per_feature=None)
            print(polygon_path)