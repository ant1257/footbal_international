import json
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from custom_package.functions import get_ranking_id_date, get_ranking_table, add_ranks

print('UEFA EURO 2004\n')
url = 'https://en.wikipedia.org/wiki/UEFA_Euro_2004'
data = requests.get(url).text
data_bs = bs(data, 'html5lib')
tables = data_bs.find_all('table')

df = pd.DataFrame(columns = {
    'date'
    , 'home_team'
    , 'away_team'
    , 'home_scored'
    , 'away_scored'
})

print('Scrapping results...')
for counter, table in enumerate(tables):
    if (counter >= 17 and counter <= 51 and counter not in [44]):
        temp = table.find_all('td')
        temp = temp[1].find('a')
        
        if temp is None:
            continue
        else:
            game_url = temp['href']
            game_data = requests.get(game_url).text
            game_data_bs = bs(game_data, 'html5lib')
            game_info = game_data_bs.find('script', type = "application/ld+json").find_next('script', type = "application/ld+json")
            json_data = json.loads(game_info.text)
            result = json_data['name']

            for team_side in ['homeTeam', 'awayTeam']:
                result = result.replace(json_data[team_side]['name'], '').strip()
            
            df = df.append(
                {
                    'date': json_data['startDate'][:10]
                    , 'home_team': json_data['homeTeam']['name']
                    , 'away_team': json_data['awayTeam']['name']
                    , 'home_scored': result.split('-')[0]
                    , 'away_scored': result.split('-')[1]
                }
                , ignore_index = True
            )
    else:
        continue
print('Done!\n')
        
# Add ranks
add_ranks(df, df[df.index == 0]['date'].item())