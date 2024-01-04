import os
import pandas as pd



def readAvailableStations(cwd=None):
    if cwd is None:
        cwd = os.getcwd()
    if 'windrose_app_lib' not in cwd:
        cwd+='/windrose_app_lib'
    stodvar_data = 'vedurstodvar.csv'
    stodvar_df = pd.read_csv(os.path.join(cwd,'metdata','VI',stodvar_data))
    stodvar_df['type'] = r'Veðurstöðvar'
    return stodvar_df

if __name__ == '__main__':
    readAvailableStations()

