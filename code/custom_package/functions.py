# connect libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs




# For FIFA team ranks
# get id and date by input date
def get_ranking_id_date(working_date):
    id_vs_date = pd.read_csv('../data/ids_dates.csv')
    ranking_date = id_vs_date[id_vs_date['date_str'] <= working_date].head(n = 1)['date_str'].item()
    ranking_id = id_vs_date[id_vs_date['date_str'] <= working_date].head(n = 1)['id_code'].item()
    
    print('Working date: {}'.format(working_date))
    print('Ranking date: {}'.format(ranking_date))
    print('Ranking ID: {}'.format(ranking_id))
    
    del id_vs_date
    
    return ranking_date, ranking_id




# import web ranking table to pandas
def get_ranking_table(url, ranking_date, ranking_id):
    print('Scraping ranks...')
    data = requests.get(url).text
    data_bs = bs(data, 'html5lib')
    table = data_bs.find('table')
    print('Done!\n')
    
    print('Writing to pandas...')
    df = pd.DataFrame(columns = {'date_id', 'rank', 'team_name', 'team_code', 'points'})
    
    for row in table.tbody.find_all('tr'):
        values = row.find_all('td')
        ranking = values[0].text
        team = values[1].text.replace('\n', '').strip()
        team_code = team.split()[-1]
        team_name = team[:len(team) - len(team_code)].strip()
        points = values[2].text.strip()
        
        df = df.append(
            {
                'date_id': ranking_date
                , 'rank': ranking
                , 'team_name': team_name
                , 'team_code': team_code
                , 'points': points
            }
            , ignore_index = True
        )
        
    print('Done!\n')
    
    del data, data_bs, table, values, ranking, team, team_code, team_name, points
    return df




# add ranks
def add_ranks(df, tournament_start_date):
    print('Adding ranks...')
    ranking_date, ranking_id = get_ranking_id_date(tournament_start_date)
    url = 'https://www.fifa.com/fifa-world-ranking/ranking-table/men/rank/{}/'.format(ranking_id)
    
    df_ranks = get_ranking_table(url, ranking_date, ranking_id)
    
    df = pd.merge(left = df, right = df_ranks.rename(columns = {'team_name': 'home_team', 'rank': 'home_rank', 'points': 'home_points'}).drop(columns = ['team_code', 'date_id']), how = 'left', on = 'home_team')
    df = pd.merge(left = df, right = df_ranks.rename(columns = {'team_name': 'away_team', 'rank': 'away_rank', 'points': 'away_points'}).drop(columns = ['team_code', 'date_id']), how = 'left', on = 'away_team')
    df['diff_rank'] = df['home_rank'].astype(int) - df['away_rank'].astype(int)
    
    print('Saving data...')
    df.to_csv('../data/uefa_euro_{}.csv'.format(tournament_start_date[:4]), index = False)
    print('Done!\n')
    
    del df_ranks