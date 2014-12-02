"""Script to reconcile names between projections site and ESPN.

"""
import sys
import csv

MAPPING = {
    'Benny Cunningham': 'Benjamin Cunningham',
    'Cecil Shorts': 'Cecil Shorts III',
    'Christopher Ivory': 'Chris Ivory',
    'E.J. Manuel': 'EJ Manuel',
    'Gator Hoskins': 'Harold Hoskins',
    'Josh Cribbs': 'Joshua Cribbs',
    'Matt Slater': 'Matthew Slater',
    'Mickey Shuler': 'Mickey Charles Shuler',
    'Robert Griffin III': 'Robert Griffin',
    'Robert Housler': 'Rob Housler',
    'Steve Johnson': 'Stevie Johnson',
    'Taylor Yates': 'T.J. Yates',
    'Timothy Wright': 'Tim Wright',
    'Ty Hilton': 'T.Y. Hilton',
    'Will Tukuafu': "Will Ta'ufo'ou",
}


def format_player(week, raw, unique_names):

    # get name and team
    name = raw.split(' (')[0].strip()
    try:
        team = raw.split(' (')[1].strip(') ').lower()
    except IndexError:  # no team name
        team = None
    else:
        # replace different version of team abbreviation
        if team == 'was':
            team = 'wsh'

    item = (week, name, team)
    if (week, name, team) in unique_names:
        return item
    elif name in MAPPING:
        return (week, MAPPING[name], team)
    else:
        return None

# get filenames from command line
scoring_filename = sys.argv[1]
filename_list = sys.argv[2:]

# sort filenames by week
sorted_filenames = []
for filename in filename_list:
    week = int(filename.split('-')[2])
    sorted_filenames.append((week, filename))
sorted_filenames.sort()

# get "natural keys" from scoring file
scoring = set()
with open(scoring_filename) as stream:
    reader = csv.DictReader(stream)
    for row in reader:
        unique = (int(row['week']), row['name'], row['team'].lower())
        if unique in scoring:
            raise ValueError('%s is not unique' % str(unique))
        else:
            scoring.add(unique)

match_count = 0
total_count = 0
hit = []
miss = []
for week, filename in sorted_filenames:
    if week > 12:
        continue
    with open(filename) as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            try:
                points = float(row['FPTS'])
            except ValueError:
                points = 0
            player = format_player(week, row['Player'], scoring)
            if player is None:
                miss.append(points)
                if points > 0:
                    print week, row
            else:
                hit.append(points)
                match_count += 1
            total_count += 1

print float(sum(hit)) / len(hit)
print float(sum(miss)) / len(miss)

print >> sys.stderr, '%i matches out of %i' % (match_count, total_count)
