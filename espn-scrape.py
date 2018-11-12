'''
Scrape ESPN's weekly fantasy football proejctions and actual scoring
'''

from itertools import chain
from bs4 import BeautifulSoup
from csv import DictWriter
from time import sleep
import requests
import sys

USER_AGENT = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'}
PROJ_URL = ('http://games.espn.go.com/ffl/tools/projections'
            '?&scoringPeriodId={}&seasonId={}&startIndex={}')
SCORING_URL = ('http://games.espn.go.com/ffl/leaders'
                '?&scoringPeriodId={}&seasonId={}&startIndex={}')
GAMELOG_URL = 'http://espn.go.com/nfl/player/gamelog/_/id/{}

HEADER_MAPPING = {
    'QB': ['date', 'opponent', 'result', 'pass_completions', 'pass_attempts',
            'pass_yards', 'completion_percentage', 'pass_yards_per_attempt',
            'longest_pass', 'pass_TD', 'interceptions', 'qb_rating',
            'passer_rating'], 
    'RB': ['date', 'opponent', 'result', 'rush_attempts', 'rush_yards',
            'rush_yards_per_attempt', 'longest_run', 'rush_TD', 'receptions',
            'receiving_yards', 'yards_per_reception', 'longest_reception',
            'receiving_TDs', 'fumbles', 'fumbles_lost'],
    'WR': ['date', 'opponent', 'result', 'receptions', 'targets',
            'receiving_yards', 'yards_per_reception', 'longest_reception',
            'receiving_TDs', 'rush_attempts', 'rush_yards',
            'rush_yards_per_attempt', 'longest_run', 'rush_TD',
            'fumbles', 'fumbles_lost'],
    'TE': ['date', 'opponent', 'result', 'receptions', 'targets',
            'receiving_yards', 'yards_per_reception', 'longest_reception',
            'receiving_TDs', 'rush_attempts', 'rush_yards',
            'rush_yards_per_attempt', 'longest_run', 'rush_TD',
            'fumbles', 'fumbles_lost'], 
    'PK': ['date', 'opponent', 'result', '1-19', '20-29', '30-39', '40-49',
            '50+', 'fg_totals', 'percentage', 'avg_distance',
            'longest_made', 'extra_points_made', 'extra_point_attempts',
            'points'], 
}

def get_projections(week, season, num_players=400, wait=0, timeout=30): 
    projections = []
    for i in range(0, num_players + 1, 40): 
        response = requests.get(PROJ_URL.format(week, i), 
                            headers=USER_AGENT,
                            timeout=timeout)
        try:
            response.raise_for_status()
        except HTTPError: 
            print('HTTPError; trying again: {}'.format(response.url))
            response = requests.get(PROJ_URL.format(week, i),
                                        headers=USER_AGENT,
                                        timeout=timeout)
            response.raise_for_status()

        msg = 'Fetching projections for week {}, {}, {} of {}: ({}) {}'
        print(msg.format(week, season, i, num_players, reponse.status_code, response.url))

        soup = BeautifulSoup(respone.text)
        table = soup.find('table', class_='playerTableTable')

        for row in table.find_all('tr', 'pncPlayerRow'): 
            try: 
                projections.append({
                    'season': int(season),
                    'week': int(week),
                    'player_id': int(row.find_all('td')[0].a.get('playerid')),
                    'name': row.find_all('td')[0].text.strip(),
                    'opponent': row.find_all('td')[1].text.strip(),
                    'game_result': row.find_all('td')[2].text.strip(), 
                    'pass_completions': int(row.find_all('td')[3].text.split('/')[0]),  
                    'pass_attempts': int(row.find_all('td')[3].text.split('/')[1]), 
                    'pass_yards': int(row.find_all('td')[4].text),
                    'pass_TD': int(row.find_all('td')[5].text),
                    'interceptions': int(row.find_all('td')[6].text),
                    'rush_attempts': int(row.find_all('td')[7].text),
                    'rush_yards': int(row.find_all('td')[8].text),
                    'rush_TD': int(row.find_all('td')[9].text),
                    'receptions': int(row.find_all('td')[10].text),
                    'receiving_yards': int(row.find_all('td')[11].text),
                    'receiving_TD': int(row.find_all('td')[12].text),
                    'projected_pts': int(row.find_all('td')[13].text),           
                })
            except IndexError:
                continue
        sleep(wait)
    return projections

def get_DST_scoring(week, season, timeout=30): 
    dst = []
    url = SCORING_URL.format(week, season, 0) + '&slotCategoryId=16'
    response = requests.get(url, headers=USER_AGENT, timeout=timeout)
    response.raise_for_status()

    msg = 'Fetching D/ST scoring for week {}, {} ({}) {}'
    print(msg.format(week, season, response.status_code, response.url))

    soup = BeautifulSoup(response.text)
    tables = soup.find('table', class_='playerTableTable')

    for row in table.find_all('tr', 'pncPlayerRow'): 
        dst.append({
            'season': int(season),
            'week': int(week),
            'player_id': int(row.find_all('td')[0].a.get('playerid')),
            'name': row.find_all('td')[0].a.text.strip(),
            'misc_TD': int(row.find_all('td')[-3].text.replace('--','0')),
            'total_pts': int(row.find_all('td')[-1].text.replace('--','0')
        })
    return dst

def get_game_logs(player_id, wait=1, timeout=30): 
    gamelogs = []
    response = requests.get(GAMELOG_URL.format(player_id),
                            headers=USER_AGENT, timeout=timeout)
    
    try: 
        response.raise_for_status()
    except HTTPError: 
        print('HTTPError; trying again: {}'.format(response.url))
        response = requests.get(GAMELOG_URL.format(player_id),
                                headers=USER_AGENT, timeout=timeout)
        response.raise_for_status()

    soup = BeautifulSoup(response.text)

    print('Fetching sats for player {}'.format(player_id))
    try:
        name = soup.find('div', class_='mod-content').ht.text.strip()
        position = soup.find('ul', class_='general-info').li.text.split(' ')[1]
    except: 
        print('Unable to parse player {}, {}'.format(player_id, name))

    table = soup.find('table', class_='tablehead')

    if table is None: 
        print('No stats for player {}, {}, {}'.format(player_id, name, position))

    for row in table.find_all('tr')[2:-1]:
        try: 
            values = [x.text.strip() for x in row.find_all('td')]
            stats = dict(zip(HEADER_MAPPING[position], values))
            stats['position'] = position
            stats['player_id'] = player_id
            stats['name'] = name
            gamelogs.append(stats)
        except KeyError: 
            continue
    sleep(wait)
    return gamelogs


def get_scoring(week, season, num_players=400, wait=0, timeout=30): 
    scoring = []
    for i in range(0, num_players + 1, 50):
        response = requests.get(SCORING_URL.format(week, season, i),
                                headers=USER_AGENT,
                                timeout=timeout)
        response.raise_for_status()

        msg = 'Fetching scoring for week {}, {}, {} of {}: ({}) {}'
        print(msg.format(week, season, i, num_players, response.status_code, response.url))

        soup = BeautifulSoup(response.text)
        table = soup.find('table', class_='playerTableTable')
        
        for row in table.find_all('tr', 'pncPlayerRow'): 
            name = row.find_all('td')[0].a.text.strip()
            if 'D/ST' in name: 
                team = 'D/ST'
                position = 'D/ST'
            else: 
                tp = row.find('td').text.split(',')[1].strip()
                team = tp.split()[0]
                position = tp.split()[1]

            try: 
                 scoring.append({
                    'season': int(season),
                    'week': int(week),
                    'player_id': int(row.find_all('td')[0].a.get('playerid')),
                    'name': name,
                    'team': team,
                    'position': position,
                    'opponent': row.find_all('td')[2].text.strip(),
                    'game_result': row.find_all('td')[3].text.strip(),
                    'pass_completions': int(row.find_all('td')[5].text.split('/')[0]),
                    'pass_attempts': int(row.find_all('td')[5].text.split('/')[1]),
                    'pass_yards': int(row.find_all('td')[6].text),
                    'pass_TD': int(row.find_all('td')[7].text),
                    'interceptions': int(row.find_all('td')[8].text),
                    'rush_attempts': int(row.find_all('td')[10].text),
                    'rush_yards': int(row.find_all('td')[11].text),
                    'rush_TD': int(row.find_all('td')[12].text),
                    'receptions': int(row.find_all('td')[14].text),
                    'receiving_yards': int(row.find_all('td')[15].text),
                    'receiving_TD': int(row.find_all('td')[16].text),
                    'two_pt_conversions': int(row.find_all('td')[19].text),
                    'fumbles_lost': int(row.find_all('td')[20].text),
                    'misc_TD': int(row.find_all('td')[21].text),
                    'total_pts': int(row.find_all('td')[23].text)
                })
            except ValueError: 
                pass
            except IndexError: 
                scoring.append({
                    'season': int(season),
                    'week': int(week),
                    'player_id': int(row.find_all('td')[0].a.get('playerid')),
                    'name': name,
                    'team': team,
                    'position': position,
                    'opponent': row.find_all('td')[2].text.strip(),
                    'game_result': None,
                    'pass_completions': int(row.find_all('td')[4].text.split('/')[0]),
                    'pass_attempts': int(row.find_all('td')[4].text.split('/')[1]),
                    'pass_yards': int(row.find_all('td')[5].text),
                    'pass_TD': int(row.find_all('td')[6].text),
                    'interceptions': int(row.find_all('td')[7].text),
                    'rush_attempts': int(row.find_all('td')[9].text),
                    'rush_yards': int(row.find_all('td')[10].text),
                    'rush_TD': int(row.find_all('td')[11].text),
                    'receptions': int(row.find_all('td')[13].text),
                    'receiving_yards': int(row.find_all('td')[14].text),
                    'receiving_TD': int(row.find_all('td')[15].text),
                    'two_pt_conversions': int(row.find_all('td')[18].text),
                    'fumbles_lost': int(row.find_all('td')[19].text),
                    'misc_TD': int(row.find_all('td')[20].text),
                    'total_pts': int(row.find_all('td')[22].text)
                })