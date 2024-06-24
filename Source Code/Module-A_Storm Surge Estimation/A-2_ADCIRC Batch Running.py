# -*- coding: utf-8 -*-

# Author: Ziying Zhou
# Date: June 18, 2024
# Description: This script is used to batch generate and run ADCIRC models.

################################## Initialization Settings ######################################

# Importing necessary Python packages --------------------------- #

import os
import time
import pandas as pd
import datetime as dt
import shutil

# Time reference ------------------------------------------------ #

## Number of years
YearNum = 250

## Control settings for ADCIRC models
timeStart = dt.datetime(2020, 9, 25, 0, 0, 0)
timeDelt = dt.timedelta(hours=3) 
dayForward = 2
dayBackward = 2

# Input/Output settings ----------------------------------------- #

System = r"A:/"
root = os.path.join(System, r"Project_StormSurge")
ModuleA_dir = os.path.join(root, r"ModuleA")

prepare_dir = os.path.join(ModuleA_dir, "Prepare")  # Folder for prepared data
select_dir = os.path.join(ModuleA_dir, "Select")  # Folder for selected landfall tracks
record_dir = os.path.join(ModuleA_dir, "Record")  # Folder for table records converted from points(.shp)
format_dir = os.path.join(ModuleA_dir, "Format")  # Folder for input files of Fujita-Takahashi models
windset_dir = os.path.join(ModuleA_dir, "Windset")  # Folder for control settings of Fujita-Takahashi models
fort22_dir = os.path.join(ModuleA_dir, "Fort22")  # Folder for Fort22 files
fort15_dir = os.path.join(ModuleA_dir, "Fort15")  # Folder for Fort15 files
adcirc_dir = os.path.join(ModuleA_dir, "ADCIRC")  # Folder for batch running ADCIRC model files

fort13_path_in = os.path.join(prepare_dir, "fort.13") # Fort13 file
fort14_path_in = os.path.join(prepare_dir, "fort.14") # Fort14 file
fort15_path_in = os.path.join(prepare_dir, "fort.15") # Fort15 file
adcirc_source = os.path.join(prepare_dir, "ADCIRC.exe") # ADCIRC program

select_table_path = os.path.join(select_dir, "Select_" + str(YearNum) + "yr_buf200km.xlsx") # Selected table records(.xlsx) of TC tracks 

# Global Constants ---------------------------------------------- #

## Wind field control parameter
chBool = True

######################################## Main Program ###########################################

# Generate input files for Fujita-Takahashi models ================================== #

df = pd.read_excel(select_table_path)
for i in range(len(df)):
    dfTemp = df.iloc[i]
    reid = str(dfTemp["REid"])
    
    record_path = os.path.join(record_dir, reid + ".xlsx") 
    format_path = os.path.join(format_dir, "StormPath" + reid + ".txt") 
    
    dfFrom = pd.read_excel(record_path)
    datalist = []
    for j in range(len(dfFrom)):
        templist = []
        lat = round(dfFrom["LAT"][j], 1)  # Round latitude to one decimal place
        lon = round(dfFrom["LONG"][j], 1)  # Round longitude to one decimal place
        tp = int(round(dfFrom["MP"][j], 0))  # Round central pressure to integer
        mw = int(round(dfFrom["MWS"][j], 0))  # Round maximum wind speed to integer
        hp = 1010  # Background pressure
        
        time = timeStart + dt.timedelta(hours=3) * j 
        year = int(time.year)  # Year
        month = int(time.month)  # Month
        day = int(time.day)  # Day
        hour = int(time.hour)  # Hour
    
        templist = [lat, lon, tp, mw, hp, year, month, day, hour]
        datalist.append(templist)

    dfTo = pd.DataFrame(datalist)
    dfTo.to_csv(format_path, header=None, index=False, sep=' ')
    print(format_path)

# Generate control settings for Fujita-Takahashi models ============================= #

df = pd.read_excel(select_table_path)
for i in range(len(df)):
    dfTemp = df.iloc[i]
    reid = str(dfTemp["REid"])
    
    format_path = os.path.join(format_dir, "StormPath" + reid + ".txt") 
    windset_path = os.path.join(windset_dir, "WindSet" + reid + ".txt")
    
    with open(format_path, 'r') as stormpath:
        lines = stormpath.readlines()
        firstline = lines[0].split()
        startTime = firstline[-4:]
        lastline = lines[len(lines)-1].split()
        endTime = lastline[-4:]    
    
    startTime = dt.datetime(int(startTime[0]), int(startTime[1]), int(startTime[2]), int(startTime[3]), 0, 0)        
    endTime = dt.datetime(int(endTime[0]), int(endTime[1]), int(endTime[2]), int(endTime[3]), 0, 0)
    
    refStartTime = startTime - dt.timedelta(days=dayForward) 
    refEndTime = endTime + dt.timedelta(days=dayBackward)
    
    dayNum = (endTime - startTime).total_seconds() / 3600 / 24 + dayForward + dayBackward
    
    with open(windset_path, 'w') as windset:
        if chBool:
            windset.write("T  0\n")
            windset.write("StormPath" + reid + ".txt\n")
        else:
            windset.write("F  0\n")
    
        windset.write(f"{refStartTime.year}  {refStartTime.month}  {refStartTime.day}  {refStartTime.hour}\n")
        windset.write(f"{refEndTime.year}  {refEndTime.month}  {refEndTime.day}  {refEndTime.hour}\n")
        windset.write(f"{-dayNum}\n")
    
        for _ in range(3):
            windset.write("1.000\n")
        
    print(windset_path)

# Generate Fort22 files ============================================================= #

df = pd.read_excel(select_table_path)
for i in range(len(df)):
    dfTemp = df.iloc[i]
    reid = str(dfTemp["REid"])
        
    fort22_sub_dir = os.path.join(fort22_dir, reid)
    fort14_path_out = os.path.join(fort22_sub_dir, "fort.14")
    
    os.mkdir(fort22_sub_dir)
    shutil.copyfile(fort14_path_in, fort14_path_out)
    print(fort14_path_out)

# Generate Fort15 files ============================================================= #

def ChangeFort15(input_path, output_path, reid, dayNum):
    with open(input_path, 'r') as fort15_in:
        with open(output_path, 'w') as fort15_out:
            lines = fort15_in.readlines()
            for i, line in enumerate(lines):
                tag = (line.split("!"))[-1]
                if i <= 1:
                    line = reid + "\n"
                elif tag == " RNDAY - TOTAL LENGTH OF SIMULATION (IN DAYS)\n":
                    line = f"{dayNum} !" + tag
                elif tag == " NOUTE, TOUTSE, TOUTFE, NSPOOLE - FORT 61 OPTIONS\n":
                    line = f"-1 2.000000 {dayNum-2} 720 !" + tag
                elif tag == " NOUTGE, TOUTSGE, TOUTFGE, NSPOOLGE - GLOBAL ELEVATION OUTPUT INFO (UNIT 63)\n":
                    line = f"-1 2.000000 {dayNum-2} 720 !" + tag
                elif tag == " NOUTGV, TOUTSGV, TOUTFGV, NSPOOLGV - GLOBAL VELOCITY OUTPUT INFO (UNIT 64)\n":
                    line = f"-1 2.000000 {dayNum-2} 720 !" + tag
                fort15_out.write(line)

df = pd.read_excel(select_table_path)
for i in range(len(df)):
    dfTemp = df.iloc[i]
    reid = str(dfTemp["REid"])
     
    windset_path = os.path.join(windset_dir, "WindSet" + reid + ".txt")   
    with open(windset_path, 'r') as windset:
        lines = windset.readlines()
        dayNum = float(lines[4]) * -1
    
    fort15_sub_dir = os.path.join(fort15_dir, reid)
    fort15_path_out = os.path.join(fort15_sub_dir, "fort.15")
    
    os.mkdir(fort15_sub_dir)
    ChangeFort15(fort15_path_in, fort15_path_out, reid, dayNum)
    print(fort15_path_out)

# Batch run ADCIRC programs ========================================================= #

df = pd.read_excel(select_table_path)
for i in range(len(df)):
    dfTemp = df.iloc[i]
    reid = str(dfTemp["REid"])
    
    fort15_sub_dir = os.path.join(fort15_dir, reid)
    fort22_sub_dir = os.path.join(fort22_dir, reid)
    adcirc_sub_dir = os.path.join(adcirc_dir, reid)
    os.mkdir(adcirc_sub_dir)    
    
    fort15_path_in = os.path.join(fort15_sub_dir, "fort.15")
    fort22_path_in = os.path.join(fort22_sub_dir, "fort.22")
    
    fort13_path_out = os.path.join(adcirc_sub_dir, "fort.13")
    fort14_path_out = os.path.join(adcirc_sub_dir, "fort.14")
    fort15_path_out = os.path.join(adcirc_sub_dir, "fort.15")
    fort22_path_out = os.path.join(adcirc_sub_dir, "fort.22")
    
    target_dir = os.path.join(adcirc_sub_dir, "ADCIRC.exe")
    
    shutil.copyfile(fort13_path_in, fort13_path_out)
    shutil.copyfile(fort14_path_in, fort14_path_out)
    shutil.copyfile(fort15_path_in, fort15_path_out)
    shutil.copyfile(fort22_path_in, fort22_path_out)
    shutil.copyfile(adcirc_source, target_dir)
        
    os.system(System[:-1] + r" && cd " + adcirc_sub_dir + r" && start ADCIRC.exe")
    print(target_dir + r"/ADCIRC.exe")
    
    if (i + 1) % 8 == 0:
        time.sleep(3600 * 2)  # Pause for 2 hours every 8 runs
    print(adcirc_sub_dir)