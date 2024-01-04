import pandas as pd
import requests
import io



# https://medium.com/towards-entrepreneurship/importing-a-csv-file-from-github-in-a-jupyter-notebook-e2c28e7e74a5
# https://stackoverflow.com/a/62509005

def get_session():
    import os
    from os.path import join, dirname
    from dotenv import load_dotenv
    # github credentials
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    user = os.environ.get("user")
    token = os.environ.get("token")
    
    # Creating a reusable session object with credentials built-in
    github_session = requests.Session()
    github_session.auth = (user, token)
    return github_session, user

def get_rawmetdata(github_session, user, source=None, stationId=None, dataFile=None):
    
    # Downloading the csv file from github
    repo = 'rawmetdata'

    if any([source is None, stationId is None, dataFile is None]): 
        source = 'vi'
        stationId = '1475'
        dataFile = 'VI_rvk_1475_10min_2005-2019.csv'

    path = '/'.join([source, stationId, dataFile])
    url = "https://raw.githubusercontent.com/{user}/{repo}/main/{path}".format(user=user, repo=repo, path=path)
    download = github_session.get(url).content
    
    # Reading the downloaded content and making it a pandas dataframe
    if (dataFile.endswith('.txt') or dataFile.endswith('.dat')):
        df = pd.read_csv(io.StringIO(download.decode('utf-8')),sep='\t')
    else:
        df = pd.read_csv(io.StringIO(download.decode('utf-8')))
    return df

def get_stationIds(github_session, user):

    # Downloading the csv file from github
    repo = 'rawmetdata'
    path = 'vedurstodvar.csv'
    url = "https://raw.githubusercontent.com/{user}/{repo}/main/{path}".format(user=user, repo=repo, path=path)
    download = github_session.get(url).content
    
    # Reading the downloaded content and making it a pandas dataframe
    df = pd.read_csv(io.StringIO(download.decode('utf-8')))
    return df

def get_projects(github_session, user):

    # Downloading the csv file from github
    repo = 'rawmetdata'
    path = 'verkefni.csv'
    url = "https://raw.githubusercontent.com/{user}/{repo}/main/{path}".format(user=user, repo=repo, path=path)
    download = github_session.get(url).content
    
    # Reading the downloaded content and making it a pandas dataframe
    df = pd.read_csv(io.StringIO(download.decode('utf-8')))
    return df

#github_session, user = get_session()
#stationIds = get_stationIds(github_session, user)
#stationId = '1475'
#dataFile = stationIds.query('nr=={stationId}'.format(stationId=stationId))['data']
#idx = stationIds.query('nr=={stationId}'.format(stationId=stationId)).index.tolist()[0]
#data = get_rawmetdata(github_session, user, source='vi', stationId=stationId, dataFile=dataFile[idx])
#print(data)
