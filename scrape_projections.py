"""Quicky script to scrape projections from fantasypros.com

"""
import sys
from StringIO import StringIO

import requests
import bs4
import pandas

# set up some parameters for scrape
base_url = 'http://www.fantasypros.com/nfl/projections'
current_week = 13
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

# get each position, week, and "expert"
for position in position_list:
    for week in week_list:
        for expert_code, expert_name in sorted(experts.iteritems()):

            # make the request, use trick of expert:expert to get the
            # results from just one source
            url = '%s/%s.php' % (base_url, position)
            params = {
                'week': week,
                'filters': '%i:%i' % (expert_code, expert_code),
            }
            response = requests.get(url, params=params)

            # use nice function to parse HTML tables in pandas (get
            # first table with exact match of id=data)
            df = pandas.io.html.read_html(
                response.text,
                attrs={'id': 'data'},
            )[0]

            # write a CSV file
            filename = 'single/projection-%s-%i-%s.csv' % \
                (position, week, expert_code)
            print >> sys.stderr, 'writing %s' % filename
            df.to_csv(filename, index=False)
