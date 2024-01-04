import os
import pandas as pd

#with open(os.path.join('metdata','VI','stodvar'), 'r') as fr:
#    lines = fr.readlines()
#    print("***** Need to specify which met station to sort ' -- stationId'")
#    print("*******************************************************")
#    for line in lines:
#        print(line)
#    print("*******************************************************")

def readvis(cwd, stationId=None):
    """
    Read the vtk files and collect the wind directions 
    into a list called wdir and the vtk files into 
    a list called vtkfiles
    """
    if stationId is None:
        vifiles = [f for f in os.listdir(os.path.join(cwd,'metdata','VI')) if f.endswith('.csv') and "1475" in f]
    elif stationId == "3470":
        vifiles = [f for f in os.listdir(os.path.join(cwd,'metdata','VI',stationId)) if f.endswith('_sj.txt')]
    elif stationId == "1473":
        vifiles = [f for f in os.listdir(os.path.join(cwd,'metdata','VI',stationId)) if f.endswith('.txt')]
    else:
        vifiles = [f for f in os.listdir(os.path.join(cwd,'metdata','VI',stationId)) if "unnid" in f]
        if not vifiles:
            vifiles = [f for f in os.listdir(os.path.join(cwd,'metdata','VI',stationId)) if (f.endswith('.csv') and stationId in f)]
    return vifiles

def getMet(cwd, vifiles,stationId=None):
	for vifile in vifiles:
		vi = readvifiles(cwd, vifile,stationId)
		vi = vi[vi['F'].notna()] # removing rows where the velocity is NaN
		vi = vi[vi['F'] > 0.5] # removing rows where the recorded velocity is less than 0.5 m/s
        #summer = vi.query("MAN < 9 & MAN > 5")	
        #winter = vi.query("MAN > 11 | MAN < 3")
        #allyear = vi
	return vi #(summer, winter, allyear)

def readvifiles(cwd, vifile, stationId=None):
    """
    Read the input file that contains:
    	* The wind directions, wdir
    
    :return: dataframe with the information from the input file
    """
    if stationId is None:
        df = pd.read_csv(os.path.join(cwd,'metdata','VI','1475',vifile),header=0, index_col=0, delimiter=",")
    elif stationId == "3470":
        df = pd.read_csv(os.path.join(cwd,'metdata','VI',stationId,vifile),header=0,index_col=0, delimiter="\t")
    elif stationId == "1473":
        from routes.windrose_app_lib.read_straumsvik import read_from_station as rfs
        df = rfs()
    else:
        df = pd.read_csv(os.path.join(cwd,'metdata','VI',stationId, vifile),header=0, index_col=0, delimiter=",")
    return df


def run_readMetdata(cwd, stationIds=None):
    #    if stationId is None:
    #        stationIds = ['1475', '1477', '3471']
    #    else:
    #        stationIds = [stationId]
    dictmet = {}
    for stationId in stationIds:
        vi = readvis(cwd, stationId=stationId)
        dictmet[stationId] = getMet(cwd, vi, stationId)
    return dictmet
#    print(dictmet['1475'])
