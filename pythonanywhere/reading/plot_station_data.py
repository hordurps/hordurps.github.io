import plotly.graph_objects as go
import pandas as pd 
import numpy as np
from PIL import Image
import os



def plot_meanws(df, stationName, months=None, hours=None, writeImage=None):
    import plotly.express as px
    # sorting
    try: # if __name__ == '__main__'
        from sort_station_data import sort_months, sort_hours
    except: # if running from dash-app
        from reading.sort_station_data import sort_months, sort_hours
    seasons = {r'Árið' : [1,2,3,4,5,6,7,8,9,10,11,12], 'Vetur (des-feb)' : [12,1,2],'Sumar (jún-ágú)' : [6,7,8], 'Vor (mar-maí)' : [3,4,5], 'Haust (sep-nóv)' : [9,10,11], 'Lengra sumar (maí-sep)' : [5,6,7,8,9]}
    timesofday = {'Dagtími (08-18)' : [8,18], 'Kvöldtími (18-24)' : [18,24], 'Næturtími (00-08)' : [0,8], 'Dagur (08-22)' : [8, 22], 'Allur dagur (08-24)' : [8, 24], 'Sólarhringur' : [0,24]}
    winddirs = {'0' : 'N', '30' : 'NNA', '60' : 'ANA', '90' : 'A', '120' : 'ASA', '150' : 'SSA', '180' : 'S', '210' : 'SSV', '240' : 'VSV', '270' : 'V', '300' : 'VNV', '330' : 'NNV'}

    # removing NaN from data set
    df.dropna(subset=['F'], inplace=True)
    # removing zeros from data set
    df = df[df.F > 0]

    fig = go.Figure()
    
    for season, months in seasons.items():
        ndata, months = sort_months(df, months)
        ndata, hours = sort_hours(ndata, hours)
        # finding the mean wind speed of each wind direction with group by
        ns = ndata.groupby('wdirs')['F'].mean()
        # turn into dataframe
        ndf = pd.DataFrame(ns)
        #ndf.columns = ['frequency']
        ndf.columns = ['meanws']
        x = ndf.index.tolist()
        y = ndf.meanws.values
        fig.add_trace(go.Scatter(x=x, y=y, name=season))


    wdirs = [winddirs[str(wd)] for wd in ndf.index.tolist()] # list of wind directions

    # Add image
    dirname = os.path.dirname(__file__)
    pyLogo = Image.open(os.path.join(dirname, "assets","ORUGG.png"))
    fig.add_layout_image(
        dict(
            #source="https://raw.githubusercontent.com/cldougl/plot_images/add_r_img/vox.png",
            source=pyLogo,
            xref="paper", yref="paper",
            x=1.0, y=1.0,
            sizex=0.25, sizey=0.25,
            opacity=0.8,
            xanchor="right", yanchor="top"
        )
    )
    fig.update_xaxes(
            ticktext=wdirs,
            tickvals=x,
    )
    fig.update_yaxes(ticksuffix='m/s')

    if (hours is not None):
        timeofday = [key for key, value in timesofday.items() if value == hours][0]
        plottitle = 'Meðalvindhraði vindátta fyrir {}. {}'.format(stationName, timeofday)
    else:
        plottile = 'Meðalvindhraði vindátta fyrir {}'.format(stationName)


    layout = dict(
            #height=350,
            #plot_bgcolor="#",
            #paper_bgcolor="#",
            #font={"color" : "#fff"},
            xaxis={
                #"title" : "Vindáttir",
                "showgrid" : False,
                "showline" : False,
                "zeroline" : False,
                "fixedrange" : True,
            },
            yaxis={
                "showgrid" : False,
                "showline" : False,
                "zeroline" : False,
                #"title" : "Meðalvindhraði",
                "fixedrange" : True,
            },
            autosize = True,
            hovermode = "closest",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                xanchor="right",
                x=1,
                y=1,
                font=dict(
                    size=8,
                    ),
                ),
            #legend = {
            #    "orientation" : "h",
            #    "yanchor" : "bottom",
            #    "xanchor" : "right",
            #    "y" : 1.02,
            #    "x" : 1,
            #}
        )
    fig.update_layout(layout)
    fig.update_layout(
            title = plottitle,
            )
    if writeImage is not None:
        fig.write_image(plottitle+'.png')
    return fig

def plot_directions(df, stationName, months=None, hours=None, writeImage=None):
    import plotly.express as px
    # sorting
    try: # if __name__ == '__main__'
        from sort_station_data import sort_months, sort_hours
    except: # if running from dash-app
        from reading.sort_station_data import sort_months, sort_hours
    seasons = {r'Árið' : [1,2,3,4,5,6,7,8,9,10,11,12], 'Vetur (des-feb)' : [12,1,2],'Sumar (jún-ágú)' : [6,7,8], 'Vor (mar-maí)' : [3,4,5], 'Haust (sep-nóv)' : [9,10,11], 'Lengra sumar (maí-sep)' : [5,6,7,8,9]}
    timesofday = {'Dagtími (08-18)' : [8,18], 'Kvöldtími (18-24)' : [18,24], 'Næturtími (00-08)' : [0,8], 'Dagur (08-22)' : [8, 22], 'Allur dagur (08-24)' : [8, 24], 'Sólarhringur' : [0,24]}
    winddirs = {'0' : 'N', '30' : 'NNA', '60' : 'ANA', '90' : 'A', '120' : 'ASA', '150' : 'SSA', '180' : 'S', '210' : 'SSV', '240' : 'VSV', '270' : 'V', '300' : 'VNV', '330' : 'NNV'}

    # removing NaN from data set
    df.dropna(subset=['F'], inplace=True)
    # removing zeros from data set
    df = df[df.F > 0]
    fig = go.Figure()
    
    for season, months in seasons.items():
        ndata, months = sort_months(df, months)
        ndata, hours = sort_hours(ndata, hours)
        # finding the frequency of each wind direction with group by, returns a series with wdirs as index and frequency as value
        ns = round((ndata.groupby('wdirs').size()[lambda x : x.index >= 0.0]/len(ndata['F']))*100.0,1)
        # turn into dataframe
        ndf = pd.DataFrame(ns)
        ndf.columns = ['frequency']
        x = ndf.index.tolist()
        y = ndf.frequency.values
        fig.add_trace(go.Scatter(x=x, y=y, name=season))


    wdirs = [winddirs[str(wd)] for wd in ndf.index.tolist()] # list of wind directions

    # Add image
    dirname = os.path.dirname(__file__)
    pyLogo = Image.open(os.path.join(dirname, "assets","ORUGG.png"))
    fig.add_layout_image(
        dict(
            #source="https://raw.githubusercontent.com/cldougl/plot_images/add_r_img/vox.png",
            source=pyLogo,
            xref="paper", yref="paper",
            x=1.0, y=1.0,
            sizex=0.25, sizey=0.25,
            opacity=0.8,
            xanchor="right", yanchor="top"
        )
    )
    fig.update_xaxes(
            ticktext=wdirs,
            tickvals=x,
    )
    fig.update_yaxes(ticksuffix='%')

    if (hours is not None):
        timeofday = [key for key, value in timesofday.items() if value == hours][0]
        plottitle = 'Tíðni vindátta fyrir {}. {}'.format(stationName, timeofday)
    else:
        plottile = 'Tíðni vindátta fyrir {}'.format(stationName)


    layout = dict(
            #height=350,
            #plot_bgcolor="#",
            #paper_bgcolor="#",
            #font={"color" : "#fff"},
            xaxis={
                #"title" : "Vindáttir",
                "showgrid" : False,
                "showline" : False,
                "zeroline" : False,
                "fixedrange" : True,
            },
            yaxis={
                "showgrid" : False,
                "showline" : False,
                "zeroline" : False,
                #"title" : "Tíðni",
                "fixedrange" : True,
            },
            autosize = True,
            hovermode = "closest",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                xanchor="right",
                x=1,
                y=1,
                font=dict(
                    size=8,
                    ),
                ),
        )
    fig.update_layout(layout)
    fig.update_layout(
            title = plottitle,
            )
    if writeImage is not None:
        fig.write_image(plottitle+'.png')
    return fig
    



def plot_weibull(df, stationName, months=None, hours=None, writeImage=None):
    seasons = {'Sumar (jún-ágú)' : [6,7,8], 'Vor (mar-maí)' : [3,4,5], 'Haust (sep-nóv)' : [9,10,11], 'Vetur (des-feb)' : [12,1,2], r'Árið' : [1,2,3,4,5,6,7,8,9,10,11,12], 'Lengra sumar (maí-sep)' : [5,6,7,8,9]}
    timesofday = {'Dagtími (08-18)' : [8,18], 'Kvöldtími (18-24)' : [18,24], 'Næturtími (00-08)' : [0,8], 'Dagur (08-22)' : [8, 22], 'Allur dagur (08-24)' : [8, 24], 'Sólarhringur' : [0,24]}
    winddirs = {'0' : 'N', '30' : 'NNA', '60' : 'ANA', '90' : 'A', '120' : 'ASA', '150' : 'SSA', '180' : 'S', '210' : 'SSV', '240' : 'VSV', '270' : 'V', '300' : 'VNV', '330' : 'NNV'}


    from scipy.stats import weibull_min

    groupped = df.groupby('wdirs')

    fig = go.Figure() 
    # Creating a x-vector with linearised wind speeds 
    x = np.linspace(0.0, round(df.max().F), int(round(df.max().F)/0.5))
    for wdir, group in groupped:
        # possibly need to add noise to the data set
        # possibly need to remove NaNs and zeros from the data set

        group.dropna(subset=['F'], inplace=True)
        group = group[group.F > 0]

        # Fitting the data set to extract the Weibull parameters for the wind direction
        shape, loc, scale = weibull_min.fit(group.F, floc=0)
        # Fitting the data set with the Weibull parameters for the wind direction
        y = weibull_min.pdf(x, shape, loc, scale)

        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name="{}, k={}, c={}".format(winddirs[str(wdir)],str(round(shape,1)),str(round(scale,1)))))

        #trace = dict(
        #        type="scatter",
        #        mode="lines",
        #        line={"color" : color.wdir},
        #        x=x,
        #        y=y,
        #        name="{}°".format(str(wdir)),
        #)
    layout = dict(
            #height=350,
            #plot_bgcolor="#",
            #paper_bgcolor="#",
            #font={"color" : "#fff"},
            xaxis={
                #"title" : "Vindhraði (m/s)",
                "showgrid" : False,
                "showline" : False,
                "fixedrange" : True,
            },
            yaxis={
                "showgrid" : False,
                "showline" : False,
                "zeroline" : False,
                #"title" : "Tíðni",
                "fixedrange" : True,
            },
            autosize = True,
            hovermode = "closest",
            margin=dict(
                b=120, # default bottom margin : 80 
                l=80, # default left margin : 80
                r=80, # default right margin : 80
                t=80, # default top margin : 100
                pad=0, # default padding between plotting area and the axis lines : 0
                ),
            legend=dict(
                orientation="h",
                yanchor="top",
                xanchor="center",
                x=0.5,
                y=-0.1,
                #bgcolor=fig.layout.plot_bgcolor,
                #yanchor="top",
                #xanchor="right",
                #x=1,
                #y=0.8,
                font=dict(
                    size=8,
                    ),
                ),
        )
    fig.update_layout(layout)
    fig.update_xaxes(ticksuffix='m/s')

    if (months is not None and hours is not None):
        season = [key for key, value in seasons.items() if value == months][0]
        timeofday = [key for key, value in timesofday.items() if value == hours][0]
        plottitle = 'Weibull fyrir {}. {}. {}'.format(stationName, season, timeofday)
    else:
        plottile = 'Weibull fyrir {}'.format(stationName)

    # Add image
    dirname = os.path.dirname(__file__)
    pyLogo = Image.open(os.path.join(dirname, "assets","ORUGG.png"))
    fig.add_layout_image(
        dict(
            #source="https://raw.githubusercontent.com/cldougl/plot_images/add_r_img/vox.png",
            source=pyLogo,
            xref="paper", yref="paper",
            x=1.0, y=1.0,
            sizex=0.25, sizey=0.25,
            opacity=0.8,
            xanchor="right", yanchor="top"
        )
    )
    fig.update_layout(
            title = plottitle,
            )
    fig.update_yaxes(rangemode='tozero')
    if writeImage is not None:
        fig.write_image(plottitle+'.png')
    return fig









def plot_windrose(df, stationName, months=None, hours=None, writeImage=None):

    # may assign colours to specific bin_names
    # marker_colours = {'0-2.5' : '#BAE3F2', '2.5-4' : '#C9F2EB', '4-6' : '#E6FCED', '6-8': '#FFFCF0', '8-10' : '#FFE1C7', '>15': '#F5C0B5'}
    # https://www.schemecolor.com/pastel-blue-with-red.php

    winddirs = {'0' : 'N', '30' : 'NNA', '60' : 'ANA', '90' : 'A', '120' : 'ASA', '150' : 'SSA', '180' : 'S', '210' : 'SSV', '240' : 'VSV', '270' : 'V', '300' : 'VNV', '330' : 'NNV'}
    seasons = {'Sumar (jún-ágú)' : [6,7,8], 'Vor (mar-maí)' : [3,4,5], 'Haust (sep-nóv)' : [9,10,11], 'Vetur (des-feb)' : [12,1,2], r'Árið' : [1,2,3,4,5,6,7,8,9,10,11,12], 'Lengra sumar (maí-sep)' : [5,6,7,8,9]}
    timesofday = {'Dagtími (08-18)' : [8,18], 'Kvöldtími (18-24)' : [18,24], 'Næturtími (00-08)' : [0,8], 'Dagur (08-22)' : [8, 22], 'Allur dagur (08-24)' : [8, 24], 'Sólarhringur' : [0,24]}

    direction_name = [winddirs[str(wd)] for wd in df[r'Vindátt (°)'].unique()] # name the wdirs (0 becomes N, 90 becomes E, etc.)

    """
        https://plotly.com/python/wind-rose-charts/

        When using graph objects, each bin name "2-4 m/s", "4-6 m/s" needs to be plotted seperately.

        So for each bin, an add_trace is required
    """ 

    # groups by Wind speed, then Wind direction, and sums up the frequencies of each direction
    fig = go.Figure()
    for bin_name in df[r'Vindhraði (m/s)'].unique():
        mask = df[r'Vindhraði (m/s)'] == bin_name
        tdf = df[mask]
        fig.add_trace(go.Barpolar(
            r = tdf[r'Tíðni (%)'],      # list of frequency of this velocity bin for each wind direction
            theta = [winddirs[str(wd)] for wd in tdf[r'Vindátt (°)']],  # list of wind directions
            name = bin_name,    # name of the velocity bin
            #marker_color = marker_colours[bin_name], #'rgb(106,81,163)'
            marker_line_color = "black",
            marker_line_width = 1,
            opacity = 0.8
        ))


    if (months is not None and hours is not None):
        season = [key for key, value in seasons.items() if value == months][0]
        timeofday = [key for key, value in timesofday.items() if value == hours][0]
        plottitle = 'Vindrós fyrir {}. {}. {}'.format(stationName, season, timeofday)
    else:
        plottile = 'Vindrós fyrir {}'.format(stationName)

    fig.update_layout(
            title = plottitle,
            #height=700,
            #width=1000,
            showlegend=False,
            polar_radialaxis_ticksuffix='%',
            #polar_angularaxis_rotation = 90,
            polar_angularaxis_direction = "clockwise",
            autosize=True,
            margin=dict(
                t=40,
                b=40,
                l=0,
                r=0,
                ),
            )

    legend_visible = True
    if legend_visible:
        fig.update_layout(
            showlegend=True,
            legend_title='Vindhraði (m/s)',
        )
    # Add image
    dirname = os.path.dirname(__file__)
    pyLogo = Image.open(os.path.join(dirname, "assets","ORUGG.png"))
    fig.add_layout_image(
        dict(
            #source="https://raw.githubusercontent.com/cldougl/plot_images/add_r_img/vox.png",
            source=pyLogo,
            xref="paper", yref="paper",
            x=0.90, y=0.15,
            sizex=0.25, sizey=0.25,
            opacity=0.8,
            xanchor="right", yanchor="top"
        )
    )

    if writeImage is not None:
        fig.write_image(plottitle+'.png')
    return fig
