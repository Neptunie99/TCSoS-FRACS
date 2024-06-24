# -*- coding: utf-8 -*-

# Author: Ziying Zhou
# Date: June 18, 2024
# Description: This script is used to estimate the total water level under combined scenarios (mean sea level + astronomical tide + storm surge).

################################## Initialization Settings ######################################

# Importing necessary Python packages --------------------------- #

import os
import arcpy

# Input/Output settings ----------------------------------------- #

System = r"A:/"
root = os.path.join(System, r"Project_StormSurge")
ModuleA_dir = os.path.join(root, r"ModuleA")
ModuleB_dir = os.path.join(root, r"ModuleB")

return_dir = os.path.join(ModuleA_dir, "ReturnPeriod")  # Folder for return periods

prepare_dir = os.path.join(ModuleB_dir, "Prepare")  # Folder for prepared data
surge_dir = os.path.join(ModuleB_dir, "StormSurge")  # Folder for storm surge data
tide_dir = os.path.join(ModuleB_dir, "AstronomicalTide")  # Folder for astronomical tide data
ssp_dir = os.path.join(ModuleB_dir, "SeaLevel")  # Folder for sea level data
combined_dir = os.path.join(ModuleB_dir, "Combined")  # Folder for combined scenarios

buf500m_path = os.path.join(prepare_dir, "Hainan_Buffer500m.shp") # Buffer of Hainan Island with 500m radius
coastline_path = os.path.join(prepare_dir, "Coastline_point.shp") # Coastline of Hainan Island
dem_path = os.path.join(prepare_dir, "dem.tif") # DEM data

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
   
## Spatial Analyst Environment 
arcpy.EnvManager(cellSize=dem_path, mask=dem_path, snapRaster=dem_path)
arcpy.env.overwriteOutput = True

# Global Constants ---------------------------------------------- #

## Lists 
listReturnPeriod = [10, 20, 50, 100]
listSurge = [r"0010a", r"0020a", r"0050a", r"0100a"]
listTide = [r"H", r"M"]
listSLR = [r"SSP0", r"SSP1", r"SSP5"]

######################################## Main Program ###########################################

# Generate storm surge raster ======================================================= #

for i in range(len(listReturnPeriod)):
    
    period = listReturnPeriod[i]
    periodid = str(10000 + period)[-4:]

    return_path_csv = os.path.join(return_dir, r"RP"+periodid+r".csv") 

    point_path = os.path.join(surge_dir, 'point' + periodid + '.shp')
    erase_path = os.path.join(surge_dir, 'erase' + periodid + '.shp')
    surge_path = os.path.join(surge_dir, 'S' + periodid + 'a.tif') 
    extract_path = os.path.join(surge_dir, 'Coastline' + periodid + '.shp') 
 
    ## Generate points(.shp)
    tempLayer = os.path.basename(return_path_csv)
    arcpy.MakeXYEventLayer_management(table=return_path_csv,
                                      in_x_field="lon", in_y_field="lat",
                                      out_layer=tempLayer,
                                      spatial_reference=GCSReference,
                                      in_z_field="")
    arcpy.CopyFeatures_management(tempLayer, point_path)
    print("Completed generating vector points")
    
    ## Erase internal points
    arcpy.analysis.Erase(in_features=point_path, erase_features=buf500m_path,
                         out_feature_class=erase_path, cluster_tolerance="")
    print("Completed erasing internal vector points")
                
    ## Interpolate raster
    surgeRaster = arcpy.ddd.Idw(in_point_features=erase_path, z_field="surge",
                                out_raster=surge_path, cell_size=dem_path,
                                power=2, search_radius="VARIABLE 12",
                                in_barrier_polyline_features="")
    print("Completed raster interpolation")   
    
    ## Extract values at coastline
    arcpy.CopyFeatures_management(coastline_path, extract_path)
    arcpy.sa.ExtractMultiValuesToPoints(in_point_features=extract_path,
                                        in_rasters=[[surgeRaster, "surge"]],
                                        bilinear_interpolate_values="BILINEAR")
    print("Completed extracting boundary point values")

# Calculate combined scenarios ====================================================== #

for i in range(len(listSurge)):   
    surge_path = os.path.join(surge_dir, "S" + listSurge[i] + ".tif")

    for j in range(len(listTide)):
        tide_path = os.path.join(tide_dir, "Tide" + listTide[j] + ".tif")  
        
        for k in range(len(listSLR)):
            slr_path = os.path.join(ssp_dir, listSLR[k] + ".tif")
            combined_path = os.path.join(combined_dir, "combined" + listSurge[i] + listTide[j] + listSLR[k] + ".tif")         
            
            rasSurge = arcpy.Raster(surge_path)
            rasTide = arcpy.Raster(tide_path)
            rasSLR = arcpy.Raster(slr_path)
            rascombined = arcpy.sa.Con((rasTide + rasSurge + rasSLR) > 0, rasTide + rasSurge + rasSLR, 0)
            rascombined.save(combined_path)
            print(combined_path)