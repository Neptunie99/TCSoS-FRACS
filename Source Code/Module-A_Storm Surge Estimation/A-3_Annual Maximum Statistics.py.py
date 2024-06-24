# -*- coding: utf-8 -*-

# Author: Ziying Zhou
# Date: June 18, 2024
# Description: This script is used to calculate the annual maximum storm surges.

################################## Initialization Settings ######################################

# Importing necessary Python packages --------------------------- #

import os
import pandas as pd
import numpy as np

# Time reference ------------------------------------------------ #

## Number of years
YearNum = 250

# Input/Output settings ----------------------------------------- #

System = r"A:/"
root = os.path.join(System, r"Project_StormSurge")
ModuleA_dir = os.path.join(root, r"ModuleA")

prepare_dir = os.path.join(ModuleA_dir, "Prepare")  # Folder for prepared data
select_dir = os.path.join(ModuleA_dir, "Select")  # Folder for selected landfall tracks
adcirc_dir = os.path.join(ModuleA_dir, "ADCIRC")  # Folder for batch running ADCIRC model files
surge_dir = os.path.join(ModuleA_dir, "StormSurge")  # Folder for storm surge(total water level - astronomical tide)
maxsurge_dir = os.path.join(ModuleA_dir, "MaxSurge")  # Folder for annual maximum storm surge
sort_dir = os.path.join(ModuleA_dir, "Sort")  # Folder for sorted annual maximum storm surge

fort14_path_in = os.path.join(prepare_dir, "fort.14") # Fort14 file
astroTideRef_dir = os.path.join(prepare_dir, "AstronomicalTide_Ref")  # Astronomical tide (ADCIRC input without storms)
select_table_path = os.path.join(select_dir, "Select_" + str(YearNum) + "yr_buf200km.xlsx") # Selected table records(.xlsx) of TC tracks
maxsurge_path = os.path.join(maxsurge_dir, "MaxSurge.csv") # Maximum storm surge including all runs
maxsurge_year_path = os.path.join(maxsurge_dir, "MaxSurge_Year.csv") # Annual maximum storm surge
sort_path = os.path.join(sort_dir, "MaxSurge_Sort.csv") # Sorted annual maximum storm surge

######################################## Main Program ###########################################

# Calculate storm surge ============================================================= #

## Convert Fort.63 to CSV file
def RewriteFort63(fort63_path, output_path):
    Header = ["NID"]
    Fort63 = open(fort63_path) 
    lines63 = Fort63.readlines()
    
    meta = lines63[1].split() 
    recordNum = int(meta[0])  # Number of records
    nodeNum = int(meta[1])  # Number of nodes
    
    array = np.empty((recordNum+1, nodeNum+1))
    fort63List = []
      
    for i in range(recordNum):
        timeID = "t" + str(1001 + i)[-3:]
        Header.append(timeID)    
        
        tempList = []
        
        for j in range(1, nodeNum + 1):
            temp = lines63[2 + (nodeNum + 1) * i + j].split() 
            array[i][j] = temp[1] 
            temp = float(temp[1]) 
            tempList.append(temp)
    
        fort63List.append(tempList)
        
    fort63List = list(map(list, zip(*fort63List)))
    
    List = []
    for i in range(nodeNum):
        temp = [i + 1]
        temp.extend(fort63List[i])
        List.append(temp)
        
    df = pd.DataFrame(List)
    df.to_csv(output_path, header=Header, index=False)

## Calculate storm surge
astrotide_path_fort63 = os.path.join(astroTideRef_dir, "fort.63")
astrotide_path_csv = os.path.join(astroTideRef_dir, "AstroTide.csv")
RewriteFort63(astrotide_path_fort63, astrotide_path_csv)

df = pd.read_excel(select_table_path)
for i in range(len(df)):
    dfTemp = df.iloc[i]
    reid = str(dfTemp["REid"])
    
    adcirc_sub_dir = os.path.join(adcirc_dir, reid)
    fort63_path = os.path.join(adcirc_sub_dir, "fort.63")    
    
    surge_sub_dir = os.path.join(surge_dir, reid)
    os.mkdir(surge_sub_dir)
    stormtide_path = os.path.join(surge_sub_dir, "StormTide.csv")
    stormsurge_path = os.path.join(surge_sub_dir, "StormSurge.csv")
    
    RewriteFort63(fort63_path, stormtide_path)
 
    df_wl = pd.read_csv(stormtide_path)
    df_at = pd.read_csv(astrotide_path_csv, usecols=df_wl.columns)

    df_ss = df_wl - df_at
    df_ss["maxele"] = df_ss.max(axis=1)  # Extract the maximum value
    df_ss["NID"] = df_wl["NID"]
    
    Header = list(df_wl.columns)
    Header.append("maxele")
    df_ss.to_csv(stormsurge_path, header=Header, index=False)
    
    print(stormsurge_path)   

# Calculate annual maximum storm surge ============================================== #

## Calculate maximum storm surge for each run
df_ss = pd.DataFrame()
df_mss = pd.DataFrame()

df = pd.read_excel(select_table_path)
Header = []

for i in range(len(df)):
    
    dfTemp = df.iloc[i]
    tcid = str(dfTemp["TCid"])
    reid = str(dfTemp["REid"])
    
    Header.append(reid)
   
    surge_sub_dir = os.path.join(surge_dir, reid)
    stormsurge_path = os.path.join(surge_sub_dir, "StormSurge.csv")    
          
    df_ss = pd.read_csv(stormsurge_path)
    df_mss[reid] = df_ss['maxele']
    
    print(reid)

df_mss["maxele"] = df_mss.max(axis=1)  # Extract the maximum value
df_mss["NID"] = df_ss["NID"]
df_mss.to_csv(maxsurge_path, index=False)
print(maxsurge_path)

## Calculate annual maximum surge
df_mss_year = pd.DataFrame()
df_mss_year["NID"] = df_mss["NID"]

df = pd.read_excel(select_table_path)
for year in range(YearNum):
    listYear = []
    dfYear = df[df["Year"] == year]
    if len(dfYear) > 0:
        listTC = list(dfYear["REid"])
        print(listTC)
        for i in range(len(df_mss)):
            listMax = []
            dfTemp = df_mss.iloc[i]
            for tcid in listTC:
                listMax.append(float(dfTemp[reid]))
            listYear.append(max(listMax))
    else:
        listYear = [0] * len(df_mss)
    
    df_mss_year["Year" + str(1000 + year)[-3:]] = listYear
df_mss_year.to_csv(maxsurge_year_path, index=False)
print(maxsurge_year_path)

# Sort annual maximum storm surge =================================================== #

df_sort = pd.DataFrame()

df_mss_year = pd.read_csv(maxsurge_year_path)
listNID = df_mss_year["NID"]
df_mss_year = df_mss_year.drop("NID", axis=1)
listSort = []

for i in range(len(df_mss_year)):
    dfTemp = df_mss_year.iloc[i]
    listTemp = sorted(list(dfTemp))
    listSort.append(listTemp)
    print(i)
    
listHeader = ["Sort" + str(1000 + j)[-3:] for j in range(YearNum)]
df_sort = pd.DataFrame(listSort, columns=listHeader)
df_sort.insert(loc=0, column='NID', value=listNID)
df_sort["NID"] = listNID 
df_sort.to_csv(sort_path, index=False)