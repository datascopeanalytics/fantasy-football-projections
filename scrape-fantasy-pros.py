"""
Quicky script to scrape projections from fantasypros.com
"""
import sys
import requests
import pandas as pd

# set up some parameters for scrape
base_url = 'https://www.fantasypros.com/nfl/rankings'
current_week = int(sys.argv[1])
week_list = range(1, current_week + 1)
position_list = ['qb', 'rb', 'wr', 'te', 'k']


def remove_short_name(full_name):
    last_index = full_name.rfind('.')
    return full_name[0:last_index - 1]


for position in position_list:
    for week in week_list:
        # make the request, use trick of expert:expert to get the
        # results from just one source
        url = '%s/%s.php' % (base_url, position)
        params = {
            'filters': '49153e5f2d',
        }
        response = requests.get(url, params=params)

        msg = 'getting projections for week {}, position {}'
        print(msg.format(week, position))

        # use expert:expert in request to get only one expert at a time
        # use pandas to parse the HTML table for us
        df = pd.io.html.read_html(
            response.text,
            attrs={'id': 'rank-data'},
            skiprows=[51]
        )[0]
        df['WEEK'] = week
        df['POSITION'] = position.upper()
        # df.rename(columns=COLUMN_MAPPINGS[position.upper()], inplace=True)
        # frames.append(df)
        filename = 'fantasypros-projections-{}-week{}.csv'.format(position,
                                                                  current_week)
        df = df.drop(columns=["WSIS"])
        if position == 'rb' or position == 'wr' or position == "te":
            df = df.drop(columns=["Unnamed: 8", "Unnamed: 9", "Unnamed: 10",
                                  "Unnamed: 11", "Unnamed: 12", "Unnamed: 13",
                                  "Unnamed: 14", "Unnamed: 15", "Unnamed: 16",
                                  "Unnamed: 17", "Unnamed: 18", "Unnamed: 19",
                                  "Unnamed: 20", "Unnamed: 21", "Unnamed: 22",
                                  "Unnamed: 23", "Unnamed: 24", "Unnamed: 25",
                                  "Unnamed: 26", "Unnamed: 27", "Unnamed: 28",
                                  "Unnamed: 29", "Unnamed: 30", "Unnamed: 31",
                                  "Unnamed: 32", "Unnamed: 33", "Unnamed: 34",
                                  "Unnamed: 35", "Unnamed: 36", "Unnamed: 37",
                                  "Unnamed: 38", "Unnamed: 39", "Unnamed: 40",
                                  "Unnamed: 41", "Unnamed: 42", "Unnamed: 43",
                                  "Unnamed: 44", "Unnamed: 45", "Unnamed: 46",
                                  "Unnamed: 47", "Unnamed: 48", "Unnamed: 49",
                                  "Unnamed: 50", "Unnamed: 51", "Unnamed: 52",
                                  "Unnamed: 53", "Unnamed: 54", "Unnamed: 55",
                                  "Unnamed: 56", "Unnamed: 57", "Unnamed: 58",
                                  "Unnamed: 59", "Unnamed: 60", "Unnamed: 61",
                                  "Unnamed: 62", "Unnamed: 63", "Unnamed: 64",
                                  "Unnamed: 65", "Unnamed: 66", "Unnamed: 67",
                                  "Unnamed: 68", "Unnamed: 69", "Unnamed: 70",
                                  "Unnamed: 71", "Unnamed: 72", "Unnamed: 73",
                                  "Unnamed: 74", "Unnamed: 75", "Unnamed: 76",
                                  "Unnamed: 77", "Unnamed: 78", "Unnamed: 79",
                                  "Unnamed: 80", "Unnamed: 81", "Unnamed: 82",
                                  "Unnamed: 83", "Unnamed: 84", "Unnamed: 85",
                                  "Unnamed: 86", "Unnamed: 87", "Unnamed: 88",
                                  "Unnamed: 89", "Unnamed: 90", "Unnamed: 91",
                                  "Unnamed: 92", "Unnamed: 93", "Unnamed: 94",
                                  "Unnamed: 95", "Unnamed: 96", "Unnamed: 97",
                                  "Unnamed: 98", "Unnamed: 99", "WEEK",
                                  "POSITION"])
        df.rename(columns=lambda x: x.lower().replace(' ', '_'), inplace=True)
        df.iloc[:, 1] = df.iloc[:, 1].apply(remove_short_name)

        df.to_csv(filename, index=False)
