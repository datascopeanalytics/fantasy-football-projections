"""
Scrape ESPN's weekly fantasy football projections and actual scoring.
"""
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
GAMELOG_URL = 'http://espn.go.com/nfl/player/gamelog/_/id/{}'
# stats on the gamelog page are position specific
# create a mapping of player position to column headers
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
    'DST': [] # no such thing as "gamelogs" for DST - have to parse all stats
}


def get_projections(week, season, num_players=400, wait=0, timeout=30):
    projections = []
    for i in range(0, num_players + 1, 40):
        response = requests.get(PROJ_URL.format(week, season, i),
                                headers=USER_AGENT,
                                timeout=timeout)
        
        try:
            response.raise_for_status()
        except HTTPError:
            # ESPN is throwing random 404s - let's at least try twice
            print('HTTPError; trying again: {}'.format(response.url))
            response = requests.get(PROJ_URL.format(week, i),
                                    headers=USER_AGENT,
                                    timeout=timeout)
            response.raise_for_status()

        msg = 'Fetching projections for week {}, {}, {} of {}: ({}) {}'
        print(msg.format(week, season, i, num_players, response.status_code, response.url))
        
        soup = BeautifulSoup(response.text)
        table = soup.find('table', class_='playerTableTable')

        for row in table.find_all('tr', 'pncPlayerRow'):
            try:
                projections.append({
                    'season': int(season),
                    'week': int(week),
                    'player_id': int(row.find_all('td')[0].a.get('playerid')),
                    'name': row.find_all('td')[0].a.text.strip(),
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
            except IndexError: # handle players on BYE week
                continue
        sleep(wait) # ESPN was throwing 404s, but the page loads when testing
    return projections

def get_dst_scoring(week, season, timeout=30):
    dst = []
    url = SCORING_URL.format(week, season, 0) + '&slotCategoryId=16'
    response = requests.get(url, headers=USER_AGENT, timeout=timeout)
    response.raise_for_status()

    msg = 'Fetching D/ST scoring for week {}, {} ({}) {}'
    print(msg.format(week, season, response.status_code, response.url))

    soup = BeautifulSoup(response.text)
    table = soup.find('table', class_='playerTableTable')

    for row in table.find_all('tr', 'pncPlayerRow'):
        dst.append({
            'season': int(season),
            'week': int(week),
            'player_id': int(row.find_all('td')[0].a.get('playerid')),
            'name': row.find_all('td')[0].a.text.strip(),
            'misc_TD': int(row.find_all('td')[-3].text.replace('--', '0')),
            'total_pts': int(row.find_all('td')[-1].text.replace('--', '0'))
        })
    return dst

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
            # Dealing with special case of D/ST. Oof
            name = row.find_all('td')[0].a.text.strip()
            if 'D/ST' in name:
                    team = 'D/ST'
                    position = 'D/ST'
            else:
                    tp = row.find('td').text.split(',')[1].strip()
                    team = tp.split()[0]
                    position = tp.split()[1]

            # I'm sorry for what I'm about to do ...
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
                # players on Bye
                pass
            except IndexError:
                # stupid players winding up on new teams midseason
                # i.e. Ben Tate played and scored points for the Browns during Week 10
                # but his new team (Minnesota) had a buy that week ...
                # so he now gets a BYE w/ his point totals
                # BYE weeks give a column colspan=2 and everything else shifts a column
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
        sleep(wait)
    return scoring


def get_gamelogs(player_id, wait=1, timeout=30):
    gamelogs = []
    response = requests.get(GAMELOG_URL.format(player_id),
                            headers=USER_AGENT, timeout=timeout)

    try:
        response.raise_for_status()
    except HTTPError:
        # ESPN is throwing random 404s - let's at least try twice
        print('HTTPError; trying again: {}'.format(response.url))
        response = requests.get(GAMELOG_URL.format(player_id),
                                headers=USER_AGENT, timeout=timeout)
        response.raise_for_status()

    soup = BeautifulSoup(response.text)

    print('Fetching stats for player {}'.format(player_id))
    try:
        name = soup.find('div', class_='mod-content').h1.text.strip()
        position = soup.find('ul', class_='general-info').li.text.split(' ')[1]
    except:
        print('Unable to parse player {}, {}'.format(player_id, name))

    table = soup.find('table', class_='tablehead')

    if table is None:
        print('No stats for player {}, {}, {}'.format(player_id, name, position))

    for row in table.find_all('tr')[2:-1]: # don't want headers or totals
        try:
            values = [x.text.strip() for x in row.find_all('td')]
            stats = dict(zip(HEADER_MAPPING[position], values))
            stats['position'] = position
            stats['player_id'] = player_id
            stats['name'] = name
            gamelogs.append(stats)
        except KeyError:
            # ESPN is inconsistent with no-name, free agent players
            # sorry, Michael Spurlock (10327)
            continue
    sleep(wait) # ESPN was throwing 404s, but the page loads when testing
    return gamelogs


def main(current_week):
    weekly_proj = []
    weekly_scoring = []
    
    for i in range(1, current_week + 1):
        weekly_proj.append(get_projections(week=i, season=2014))
        weekly_scoring.append(get_scoring(week=i, season=2014, num_players=1000))

    # flatten list of lists
    projections = list(chain.from_iterable(weekly_proj))
    scoring = list(chain.from_iterable(weekly_scoring))

    with open('data/projections-espn.csv', 'w') as f:
        writer = DictWriter(f, fieldnames=projections[0].keys())
        writer.writeheader()
        writer.writerows(projections)

    with open('data/scoring-espn.csv', 'w') as f:
        # DST scoring is in 0-index position of this -- use 32-index (not a DST)
        writer = DictWriter(f, fieldnames=scoring[32].keys())
        writer.writeheader()
        writer.writerows(scoring)

if __name__ == '__main__':
    main(int(sys.argv[1]))
