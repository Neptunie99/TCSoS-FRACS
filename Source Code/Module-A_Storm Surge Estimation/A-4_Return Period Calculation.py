# -*- coding: utf-8 -*-

# Author: Ziying Zhou
# Date: June 18, 2024
# Description: This script is used to estimate return periods of storm surges using GEV functions.

################################## Initialization Settings ######################################

# Importing necessary Python packages --------------------------- #

import os
import pandas as pd
import numpy as np
from scipy import stats

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
select_dir = os.path.join(ModuleA_dir, "Select")  # Folder for selected landfall tracks
sort_dir = os.path.join(ModuleA_dir, "Sort")  # Folder for sorted annual maximum storm surge
gev_dir = os.path.join(ModuleA_dir, "GEV")  # Folder for GEV fittings
return_dir = os.path.join(ModuleA_dir, "ReturnPeriod")  # Folder for return periods

fort14_path_in = os.path.join(prepare_dir, "fort.14") # Fort14 file
select_table_path = os.path.join(select_dir, "Select_" + str(YearNum) + "yr_buf200km.xlsx") # Selected table records(.xlsx) of TC tracks
sort_path = os.path.join(sort_dir, "MaxSurge_Sort.csv") # Sorted annual maximum storm surge
gev_path = os.path.join(gev_dir, "MaxSurge_GEV.csv") # GEV fittings
return_path = os.path.join(return_dir, "ReturnPeriod_NID.csv") # Return periods sorted by NID

# Global Constants ---------------------------------------------- #

## List of return periods
listReturnPeriod = [10, 20, 50, 100]

######################################## Main Program ###########################################

# GEV fittings ====================================================================== #

df_sort = pd.read_csv(sort_path)
listNID = df_sort["NID"]
df_sort = df_sort.drop("NID", axis=1)

listARG = [] 
for i in range(len(df_sort)):
    dfTemp = df_sort.iloc[i]
    args = stats.genextreme.fit(list(dfTemp))
    listTemp = list(args)
    ks = stats.kstest(list(dfTemp), 'genextreme', args)
    listTemp.append(ks[1])
    listARG.append(listTemp)
    print(i)
    
df_arg = pd.DataFrame(listARG, columns=["Shape", "Location", "Scale", "P-value"])
df_arg.insert(loc=0, column='NID', value=listNID)
df_arg.to_csv(gev_path, index=False)

# Return period calculation ========================================================= #

## Non-exceedance probability for a given return period
def ReturnPeriod(t):
    p = 1.0 - 1.0 / t
    return p

## Convert csv file to maxele.63 format
def WriteMaxele63(input_path, output_path, period):
    df = pd.read_csv(input_path)
    periodid = "RP" + str(10000 + period)[-4:]
    with open(output_path, mode='w') as Fort63:
        Fort63.write("!  \n")
        Fort63.write("!  " + str(len(df)) + "\n")
        Fort63.write("!  \n") 
        for i in df.index:
            dfTemp = df.iloc[i]
            nid = int(dfTemp["NID"])
            maxele = dfTemp[periodid]
            Fort63.write(f"{nid}    {maxele}\n")

## Pair maxele.63 with fort.14 to add locations into csv
def MergeMaxele63Fort14(fort14_path, maxele63_path, output_path):
    # Read Node attributes from fort.14
    with open(fort14_path, 'r') as Fort14: 
        lines14 = Fort14.readlines()
        meta = lines14[1].split() 
        nodeNum = int(meta[1])  # Number of nodes
        fort14List = []
        for i in range(nodeNum):
            temp = lines14[2 + i].split() 
            temp[0] = int(temp[0])
            for j in range(1, 4):
                temp[j] = float(temp[j])
            fort14List.append(temp[0:3])
    # Read Node water levels from maxele.63
    with open(maxele63_path, 'r') as Maxele: 
        lines63 = Maxele.readlines()
        meta = lines63[1].split() 
        nodeNum = int(meta[1])  # Number of nodes
        array = np.empty(nodeNum + 1)
        MaxeleList = []          
        tempList = []
        for i in range(nodeNum):
            temp = lines63[i + 3].split() 
            array[i] = temp[1]     
            temp = float(temp[1])
            tempList.append(temp)
        MaxeleList.append(tempList)
        MaxeleList = list(map(list, zip(*MaxeleList)))
    # Merge fort.14 and maxele.63 information 
    List = []
    for i in range(nodeNum):
        List.append(fort14List[i] + MaxeleList[i])
    df = pd.DataFrame(List)
    Header = ['ID', 'lon', 'lat', 'surge']
    df.to_csv(output_path, header=Header, index=False)

## Calculate return periods by GEV fittings
df_arg = pd.read_csv(gev_path)
listNID = df_arg["NID"]
df_return = pd.DataFrame()
for period in listReturnPeriod:
    prob = ReturnPeriod(period)
    listPredict = []
    for i in range(len(df_arg)):
        dfTemp = df_arg.iloc[i]
        predict = stats.genextreme.ppf(prob, dfTemp["Shape"], dfTemp["Location"], dfTemp["Scale"])
        listPredict.append(predict)
        print(i)
    df_return["RP" + str(10000 + period)[-4:]] = listPredict
df_return.insert(loc=0, column='NID', value=listNID)
df_return.to_csv(return_path, index=False)

## Add locations to csv files
for period in listReturnPeriod:
    periodid = "RP" + str(10000 + period)[-4:]
    return_path_63 = os.path.join(return_dir, periodid+r".63")
    return_path_csv = os.path.join(return_dir, periodid+r".csv")  
    WriteMaxele63(return_path, return_path_63, period)
    print(return_path_63)
    MergeMaxele63Fort14(fort14_path_in, return_path_63, return_path_csv)
    print(return_path_csv)