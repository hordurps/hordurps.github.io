import plotly.graph_objects as go


# plotly_express_figure(wd, season_str[i], stationId, daytime)

def plotly_express_figure(df=None, season=None, stationId=None, daytime=None):
    import plotly.express as px
    import plotly
    if df is None:
        df = px.data.wind()
        print(df)
    else:
        print(df.head())
    """
    template =  Available templates:
                ['ggplot2', 'seaborn', 'simple_white', 'plotly',
                                 'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
                                          'ygridoff', 'gridon', 'none']
    """
    fig = px.bar_polar(df, r="frequency", theta="direction",range_r=[0, 0.3],
            color=r"Vindhraði (m/s)", template="plotly", #template="plotly_dark",
            color_discrete_sequence= px.colors.qualitative.Pastel2) #sequential.PuBuGn) #px.colors.sequential.Plasma_r)
    #fig.show()
    #fig.write_image(os.path.join(os.getcwd(),'metdata',''.join(season.lower())+".png"))
    if stationId is None:
        plotly.offline.plot(fig,filename=os.path.join(os.getcwd(),'metdata',season.replace(" ","").lower()+daytime+".html"))
    else:
        plotly.offline.plot(fig,filename=os.path.join(os.getcwd(),'metdata',season.replace(" ","").lower()+"_"+stationId+daytime+".html"))

    # fig.write_image('image.png')
    # fig.write_html('image.html')
