"""
Quicky script to scrape projections from fantasypros.com
"""
import sys
import requests
from bs4 import BeautifulSoup
from mappings import COLUMN_MAPPINGS
import pandas as pd

# set up some parameters for scrape
base_url = 'http://www.fantasypros.com/nfl/projections'
current_week = int(sys.argv[1])
week_list = range(1, current_week + 1)
position_list = ['qb', 'rb', 'wr', 'te', 'k']
experts = {
    44: 'Dave Richard, CBS Sports',
    45: 'Jamey Eisenberg, CBS Sports',
    71: 'ESPN',
    73: 'numberFire',
    120: 'Bloomberg Sports',
    152: 'FFToday',
    469: 'Pro Football Focus',
}

for expert_code, expert_name in sorted(experts.iteritems()):
    frames = []
    for position in position_list:
        for week in week_list:
            # make the request, use trick of expert:expert to get the
            # results from just one source
            url = '%s/%s.php' % (base_url, position)
            params = {
                'week': week,
                'filters': '%i:%i' % (expert_code, expert_code),
            }
            response = requests.get(url, params=params)

            msg = 'getting projections for {}, week {}, postition {}'
            print(msg.format(expert_name, week, position))
            
            # use expert:expert in request to get only one expert at a time
            # use pandas to parse the HTML table for us
            df = pd.io.html.read_html(
                    response.text,
                    attrs={'id': 'data'}
                )[0]
            df['WEEK'] = week
            df['POSITION'] = position.upper()
            df.rename(columns=COLUMN_MAPPINGS[position.upper()], inplace=True)
            frames.append(df)

    expert_df = pd.concat(frames)
    expert_df['EXPERT'] = expert_name
    filename = 'data/fantasypros-projections-{}.csv'.format(expert_code)
    expert_df.to_csv(filename, index=False)
