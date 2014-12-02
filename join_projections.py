"""Script to reconcile names between projections and scoring data. Not going to go crazy, but just try to fix any important stuff.

"""
import sys
import csv
import os

MANUAL_CORRECTIONS = {
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


def format_player(week, raw_projection_name, scoring, manual_corrections):
    """This function manipulates names as necessary to match between
    projection data and scoring data.

    """
    # parse name and team from projection data
    name = raw_projection_name.split(' (')[0].strip()
    try:
        team = raw_projection_name.split(' (')[1].strip(') ').lower()
    except IndexError:  # sometimes there is no team name
        team = None
    else:
        # replace different abbreviation for Washington
        if team == 'was':
            team = 'wsh'

    # if there is an exact match with scoring data, return that
    match = scoring.get((week, name, team))

    # if there isn't an exact match with scoring data, but there is
    # after a manual replacement of the player name, return that
    if match is None and name in manual_corrections:
        name = manual_corrections[name]
        match = scoring.get((week, name, team))

    return match


def sorted_by_week(filename_list):
    # sort filenames by week
    sorted_filenames = []
    for filename in filename_list:
        basename, ext = os.path.splitext(filename)
        label, position, week, expert = basename.split('-')
        sorted_filenames.append((int(week), position, expert, filename))
        sorted_filenames.sort()
    return sorted_filenames


def join(scoring_filename, projection_filename_list):

    # get scoring data in dictionary
    scoring = read_scoring_data(scoring_filename)

    match_list = []
    miss_list = []
    decorated = sorted_by_week(projection_filename_list)
    for week, position, expert, filename in decorated:
        with open(filename) as stream:
            reader = csv.DictReader(stream)
            for row in reader:

                # get formatted player name
                player = format_player(
                    week,
                    row['Player'],
                    scoring,
                    MANUAL_CORRECTIONS,
                )

                if player is None:
                    miss_list.append(row)
                else:
                    match_list.append(row)

    print >> sys.stderr, '%i matches out of %i' % (len(match_list), len(match_list) + len(miss_list))


def read_scoring_data(scoring_filename):
    """Get "natural keys" from scoring file."""
    result = {}
    with open(scoring_filename) as stream:
        reader = csv.DictReader(stream)
        for row in reader:

            # use combo of week, player name, team as key, and player
            # name as value
            key = (int(row['week']), row['name'], row['team'].lower())
            value = row['name']

            # raise error if the key is not unique
            if key in result:
                raise ValueError('%s is not unique' % str(unique))
            else:
                result[key] = value

    return result

if __name__ == '__main__':

    # get filenames from command line
    scoring_filename = sys.argv[1]
    projection_filename_list = sys.argv[2:]

    # try to join scoring data and projection data
    join(scoring_filename, projection_filename_list)
