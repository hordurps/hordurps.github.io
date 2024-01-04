import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns


#from sortMet import ( readvis, getMet, sortMet, sortTime )

def sortMet(season):
	D = season['D']
	wdirs = np.arange(0,360,30)
	ws, wg = {}, {}
	# sorting into dicts with keys and values based on the wind direction
	for wdir in wdirs:
		#print("wind direction", wdir)
		if wdir==0: # for 0 deg, the range is from 345 to 15 deg
			ws[str(wdir)] = (season.query("D < "+str(wdir+15)+"| D >= "+str(wdirs[-1]+15)))['F'].values	# wind speed
			wg[str(wdir)] = (season.query("D < "+str(wdir+15)+"| D >= "+str(wdirs[-1]+15)))['FG'].values # gust speed
		else: # for other degs, the range is -15 degs to +15 degs
			ws[str(wdir)] = (season.query("D < "+str(wdir+15)+"& D >= "+str(wdir-15)))['F'].values		# wind speed
			wg[str(wdir)] = (season.query("D < "+str(wdir+15)+"& D >= "+str(wdir-15)))['FG'].values		# gust speed
	return (ws, wg)

def sortTime(stationId=None):
    vifiles = readvis(stationId)
    seasons = getMet(vifiles, stationId)
    sorted_seasons = []
    for season in seasons:
        newseason = season.query("klst >= 6")
        sorted_seasons.append(newseason)
    return tuple(sorted_seasons)

def readvifiles(vifile, stationId=None):
    """
    Read the input file that contains:
    	* The wind directions, wdir
    
    :return: dataframe with the information from the input file
    """
    import pandas as pd
    if stationId is None:
        df = pd.read_csv(os.path.join(os.getcwd(),'metdata','VI','1475',vifile),header=0, index_col=0, delimiter=",")
    else:
        df = pd.read_csv(os.path.join(os.getcwd(),'metdata','VI',stationId, vifile),header=0, index_col=0, delimiter=",")
    return df

def readvis(stationId=None):
    """
    Read the vtk files and collect the wind directions 
    into a list called wdir and the vtk files into 
    a list called vtkfiles
    """
    if stationId is None:
        vifiles = [f for f in os.listdir(os.path.join(os.getcwd(),'metdata','VI')) if f.endswith('.csv') and "1475" in f]
    else:
        vifiles = [f for f in os.listdir(os.path.join(os.getcwd(),'metdata','VI',stationId)) if "unnid" in f]
        if not vifiles:
            vifiles = [f for f in os.listdir(os.path.join(os.getcwd(),'metdata','VI',stationId)) if (f.endswith('.csv') and stationId in f)]
    return vifiles

def getMet(vifiles,stationId=None):
	for vifile in vifiles:
		print(vifile)
		vi = readvifiles(vifile,stationId)
		vi = vi[vi['F'].notna()] # removing rows where the velocity is NaN
		vi = vi[vi['F'] > 0.5] # removing rows where the recorded velocity is less than 0.5 m/s
		summer = vi.query("MAN < 9 & MAN > 5")	# MAN 6, 7, 8
		winter = vi.query("MAN > 11 | MAN < 3") # MAN 12, 1, 2
		autumn = vi.query("MAN > 8 & MAN < 12") # MAN 9, 10, 11
		spring = vi.query("MAN > 2 & MAN < 6") # MAN 3, 4, 5
		allyear = vi
	return (summer, winter, allyear, spring, autumn)

def addNoise(metws,angles):
    mn = 0
    std = 25722.0/100000
    nr = metws.shape[0] # number of rows
    metws_index = metws.index
    noise_df = pd.DataFrame(index=metws_index,columns=angles)
    for angle in angles:
        noise = np.random.normal(mn,std,nr)
        noise_df[angle] = noise.T
    # mn is the mean of the normal distribution you are choosing from
    # std is the standard deviation of the normal distribution
    # nr is the number of elements you get in array noise
    metws_noise = metws+noise_df
    return metws_noise



def getWeibull_min(ws,outputName):
    """ ws can be wind speeds or wind gusts, or turbulent intensity
        metfile is the name to give the csv and imgs
    """
    # extracting the stationId from the output name 'stationId_...'
    stationId = outputName.split('_')[0]
    # creating a folder for the weibulls inside the folder for the stationId
    if not os.path.exists(os.path.join(stationId,'weibulls')):
        os.makedirs(os.path.join(stationId,'weibulls'))
    # creating a data frame from the dicts for the wind speeds
    wsdata = pd.DataFrame(dict([ (k, pd.Series(v)) for k,v in ws.items() ]))
    wdirs = wsdata.columns.to_list()
    wsdata = addNoise(wsdata, wdirs)
    
    # calculating the frequency of each wind direction
    #print(wsdata)
    wsdata_modified = wsdata.fillna(0)
    wdirOccurrances = wsdata_modified.astype(bool).sum(axis=0)
    totalOccurrances = wdirOccurrances.sum()
    #wdirOccurrances = (wsdata > 0).sum()
    #totalOccurrances = wdirOccurrances.values.sum()
    frequencies = wdirOccurrances/totalOccurrances
    frequency = frequencies.to_frame()
    frequency = frequency.transpose()
    frequency.index  = ['A']
    
    # Getting the weibull distribution
    from scipy.stats import weibull_min
    weibdict, weibpdf = {}, {}
    if "windspeed" in outputName:
        factor = 1.0
    elif "windgust" in outputName:
        factor = 1.85
    for wdir in wdirs:
        fig, ax = plt.subplots(1,1)
        # extract the wind speeds for this wind directions
        wsdir = wsdata[wdir]
        # need to wdir.dropna(how='any') to remove Nan as they are included in scipy calcs
        wsdir = wsdir.dropna(how='any')
        # remove zero velocities
        wsdir = wsdir[wsdir>0]/factor

        # fit weibull and extract the parameters
        shape, loc, scale = weibull_min.fit(wsdir, floc=0) #, method="MLE")
        #print(wdir, str(shape), str(loc), str(scale))
        weibdict[wdir] = [shape, loc, scale]
        weibpdf[wdir] = weibull_min.pdf(wsdir, shape, loc, scale)
    
        # plotting PDF
        titletxt = str(wdir)+"°, A = %.6f, c = %.6f, k = %0.6f" % (frequency[wdir]['A'], shape, scale)
        #Display the probability density function (pdf):
        x = np.linspace(weibull_min.ppf(0.01, shape, loc, scale), weibull_min.ppf(0.99, shape, loc, scale), 100)
        ax.plot(x, weibull_min.pdf(x, shape, loc, scale), 'r-', lw=5, alpha=0.6, label='weibull_min pdf')
        # Distributing the wind speeds to bins and creating a histogram
        (n, bins, patches) = ax.hist(wsdir, density=True, histtype='stepfilled', alpha=0.2, bins=30)
        # create a pdf based on the parameters from fitting the wind speed
        dist = weibull_min(shape, loc, scale)
        # plotting the pdf with the bins (another method same result)
        ax.plot(bins, dist.pdf(bins), 'b+', lw=10, alpha=0.7, label='weibull_min_pdf')
   #     ax.legend(loc='best', frameon=False)
        plt.title(titletxt)
        plt.savefig(os.path.join(stationId,'weibulls',outputName+'_weibull_min_'+wdir+'.png'))
        #plt.savefig(os.path.join(os.getcwd(),'metdata','weibulls',outputName+'_weibull_min_'+wdir+'.png'))
        plt.close()
    
    weib = pd.DataFrame(weibdict)
    weib.index = ['shape', 'loc', 'scale']
    myweib = pd.concat([weib, frequency])
    print(myweib)
    myweib.to_csv(os.path.join(stationId,'weibulls',outputName+'_weib_min.csv'))
    #myweib.to_csv(os.path.join(os.getcwd(),'metdata','weibulls',outputName+'_weib_min.csv'))


def getWeibull_expon(ws,outputName):
    """ ws can be wind speeds or wind gusts, or turbulent intensity
        outputName is the name to give the csv and imgs
    """
    stationId = outputName.split('_')[0]
    if not os.path.exists(os.path.join(stationId,'weibulls')):
        os.makedirs(os.path.join(stationId,'weibulls'))
    # creating a data frame from the dicts for the wind speeds
    wsdata = pd.DataFrame(dict([ (k, pd.Series(v)) for k,v in ws.items() ]))
    wdirs = wsdata.columns.to_list()
    wsdata = addNoise(wsdata, wdirs)
    
    # calculating the frequency of each wind direction
    #print(wsdata)
    wsdata_modified = wsdata.fillna(0)
    wdirOccurrances = wsdata_modified.astype(bool).sum(axis=0)
    totalOccurrances = wdirOccurrances.sum()
    #wdirOccurrances = (wsdata > 0).sum()
    #totalOccurrances = wdirOccurrances.values.sum()
    frequencies = wdirOccurrances/totalOccurrances
    frequency = frequencies.to_frame()
    frequency = frequency.transpose()
    frequency.index  = ['A']
    
    # Getting the weibull distribution
    from scipy.stats import weibull_min
    from scipy.stats import exponweib
    weibdict, weibpdf = {}, {}
    if "windspeed" in outputName:
        factor = 1.0
    elif "windgust" in outputName:
        factor = 1.85
    for wdir in wdirs:
        fig, ax = plt.subplots(1,1)
        # extract the wind speeds for this wind directions
        wsdir = wsdata[wdir]
        # need to wdir.dropna(how='any') to remove Nan as they are included in scipy calcs
        wsdir = wsdir.dropna(how='any')
        # remove zero velocities
        wsdir = wsdir[wsdir>0]
        wsdir = wsdir[wsdir>0]/factor

        # fit weibull and extract the parameters
        # fixed exponential weibull distribution
        a, shape, loc, scale = exponweib.fit(wsdir, floc=0, f0=1) 

        print(wdir, str(a), str(shape), str(loc), str(scale))
        weibdict[wdir] = [shape, loc, scale]
        weibpdf[wdir] = exponweib.pdf(wsdir, a, shape, loc, scale)

        # https://stackoverflow.com/a/36603591
        # plotting histogram
        values, bins, hist = ax.hist(wsdir, bins=51, range=(0,25), density=True) #, normed=True)
        center = (bins[:-1]+bins[1:])/2.0

        ax.plot(center,exponweib.pdf(center, a, shape, loc, scale), lw=4, label='scipy')
        
        def weibull(wsdir, shape, scale):
            """ Weibull distribution for wind speed U with shape parameter k and scale parameter A"""
            return (shape/scale)*(wsdir/scale)**(shape-1)*np.exp(-(wsdir/scale)**shape)
        ax.plot(center,weibull(center,shape, scale), label="Wind analysis",lw=2)
        titletxt = str(wdir)+"°, A = %.6f, c = %.6f, k = %0.6f" % (frequency[wdir]['A'], shape, scale)
        plt.title(titletxt)
        #plt.savefig(os.path.join(os.getcwd(),'metdata','weibulls',outputName+'_weibull_expon_'+wdir+'.png'))
        plt.savefig(os.path.join(stationId,'weibulls',outputName+'_weibull_expon_'+wdir+'.png'))
        plt.close()
    
#        # plotting PDF
#        titletxt = str(wdir)+"°, A = %.6f, c = %.6f, k = %0.6f" % (frequency[wdir]['A'], shape, scale)
#        #Display the probability density function (pdf):
#        x = np.linspace(exponweib.ppf(0.01, a, shape, loc, scale), exponweib.ppf(0.99, a, shape, loc, scale), 100)
#        ax.plot(x, exponweib.pdf(x, a, shape, loc, scale), 'r-', lw=5, alpha=0.6, label='exponweib pdf')
#        # Distributing the wind speeds to bins and creating a histogram
#        (n, bins, patches) = ax.hist(wsdir, density=True, histtype='stepfilled', alpha=0.2, bins=30)
#        # create a pdf based on the parameters from fitting the wind speed
#        dist = exponweib(a, shape, loc, scale)
#        # plotting the pdf with the bins (another method same result)
#        ax.plot(bins, dist.pdf(bins), 'b+', lw=10, alpha=0.7, label='exponweib_pdf')
#   #     ax.legend(loc='best', frameon=False)
#        plt.title(titletxt)
#        plt.savefig(os.path.join(os.getcwd(),'metdata','weibulls',metfile+'_weibull_expon_'+wdir+'.png'))
#        plt.close()
    
    weib = pd.DataFrame(weibdict)
    weib.index = ['shape', 'loc', 'scale']
    myweib = pd.concat([weib, frequency])
    print(myweib)
    myweib.to_csv(os.path.join(stationId,'weibulls',outputName+'_weib_expon.csv'))
    #myweib.to_csv(os.path.join(os.getcwd(),'metdata','weibulls',outputName+'_weib_expon.csv'))

def main(analysis=None,stationId=None):
    vifiles = readvis(stationId)

    if "all" in analysis:
        seasons = getMet(vifiles, stationId) # (summer, winter, allyear)
    elif "day" in analysis:
        seasons = sortTime(stationId)
    else: 
        import sys
        sys.exit("STOP: need to specify -- all/day")

    if os.path.exists(os.path.join(os.getcwd(),'metdata','weibulls')):
        pass
    else:
        os.mkdir(os.path.join(os.getcwd(),'metdata','weibulls'))
    for i, season in enumerate(seasons):
        # identifying the month to determine the season
        months = season['MAN'].unique()
        print(months)
        if (8 in months and 1 in months and len(months) ==  12):
            arstid = 'allyear'
        elif (8 in months and 6 in months and 7 in months):
            arstid = 'summer'
        elif (1 in months and 2 in months and 12 in months):
            arstid = 'winter'
        elif (3 in months and 4 in months and 5 in months):
            arstid = 'spring'
        elif (9 in months and 10 in months and 11 in months):
            arstid = 'autumn'
        else:
            import sys
            sys.exit("ERROR: don't recognize the month")
        print("ARSTID", arstid)
    
        # creating the name based on the met data file and the season
        metfile = vifiles[0].split('.')[0]+'_'+arstid
    
#        print(season.query("klst < 6")) # checking if sorting the time is working, and it is.
        # Returning the wind speeds and wind gusts ordered by wdirs
        (ws, wg) = sortMet(season)
        getWeibull_expon(ws, metfile+'_windspeed')
        getWeibull_min(ws, metfile+'_windspeed')
        #getWeibull_min(wg, metfile+'_windgust')

if __name__ == "__main__":
    import sys
    argv = sys.argv
    try:
        index = argv.index("--") + 1
        argv = argv[index:]
        analysis = argv[0]
        if len(argv) == 2:
            stationId = argv[1]
        else:
            stationId = None
        print(analysis)
        main(analysis,stationId)
    except ValueError:
        index = len(argv)
        print("***** Need to specify which analysis type to perform -- all/day")
        index = len(argv)
        with open(os.path.join('metdata','VI','stodvar'), 'r') as fr:
            lines = fr.readlines()
            print("***** Need to specify which met station to sort ' -- stationId'")
            print("*******************************************************")
            for line in lines:
                print(line)
            print("*******************************************************")

