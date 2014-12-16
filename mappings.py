"""
FantasyPros' table has a primary and secondary header.
We need to rename all the columns by position so that they line up.
These are the mappings by position.
"""

ESPN_SCORING = {
    'pass_yards': .04,
    'pass_TD': 4.,
    'interceptions': -2.,
    'rush_yards': .1,
    'rush_TD': 6.,
    'receptions': 0., # standard ESPN is not PPR
    'receiving_yards': .1,
    'receiving_TD': 6.,
    'misc_TD': 6., # punt/kick returns
    'two_pt_conversions': 2.,
    'fumbles_lost': -2.
}

# Top N players relevant to each position
FANTASY_RELEVANT = {
    'QB': 20,
    'RB': 60,
    'WR': 60,
    'TE': 20,
    'K': 15,
    'D/ST': 15
}

# FantasyPros name : ESPN name
NAME_CORRECTIONS = {
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

COLUMN_MAPPINGS = {
    'QB': {
        'Player': 'PLAYER',
        'ATT': 'PASS_ATT',
        'TDS': 'PASS_TD',
        'YDS': 'PASS_YDS',
        'ATT.1': 'RUSH_ATT',
        'TDS.1': 'RUSH_TD',
        'YDS.1': 'RUSH_YDS',
        'CMP': 'CMP',
        'FG': 'FG',
        'FGA': 'FGA',
        'FL': 'FL',
        'FPTS': 'FPTS',
        'INTS': 'INTS',
        'Player': 'Player',
        'REC': 'REC',
        'XPT': 'XPT',
        'position': 'POSITION',
        'week': 'WEEK',
        'expert': 'EXPERT'
    },
    'RB': {
        'Player': 'PLAYER',
        'ATT': 'RUSH_ATT',
        'YDS': 'RUSH_YDS',
        'TDS': 'RUSH_TD',
        'ATT.1': 'PASS_ATT',
        'YDS.1': 'REC_YDS',
        'TDS.1': 'REC_TD',
        'CMP': 'CMP',
        'FG': 'FG',
        'FGA': 'FGA',
        'FL': 'FL',
        'FPTS': 'FPTS',
        'INTS': 'INTS',
        'Player': 'Player',
        'REC': 'REC',
        'XPT': 'XPT',
        'position': 'POSITION',
        'week': 'WEEK',
        'expert': 'EXPERT'
    },
    'WR': {
        'Player': 'PLAYER',
        'ATT': 'RUSH_ATT',
        'TDS': 'RUSH_TD',
        'YDS': 'RUSH_YDS',
        'ATT.1': 'PASS_ATT',
        'TDS.1': 'REC_TD',
        'YDS.1': 'REC_YDS',
        'CMP': 'CMP',
        'FG': 'FG',
        'FGA': 'FGA',
        'FL': 'FL',
        'FPTS': 'FPTS',
        'INTS': 'INTS',
        'Player': 'Player',
        'REC': 'REC',
        'XPT': 'XPT',
        'position': 'POSITION',
        'week': 'WEEK',
        'expert': 'EXPERT'
    },
    'TE': {
        'Player': 'PLAYER',
        'ATT': 'RUSH_ATT',
        'TDS': 'REC_TD',
        'YDS': 'REC_YDS',
        'ATT.1': 'PASS_ATT',
        'TDS.1': 'RUSH_TD',
        'YDS.1': 'RUSH_YDS',
        'CMP': 'CMP',
        'FG': 'FG',
        'FGA': 'FGA',
        'FL': 'FL',
        'FPTS': 'FPTS',
        'INTS': 'INTS',
        'Player': 'Player',
        'REC': 'REC',
        'XPT': 'XPT',
        'position': 'POSITION',
        'week': 'WEEK',
        'expert': 'EXPERT'
    },
    'K': {
        'Player': 'PLAYER',
        'ATT': 'RUSH_ATT',
        'TDS': 'REC_TD',
        'YDS': 'REC_YDS',
        'ATT.1': 'PASS_ATT',
        'TDS.1': 'RUSH_TD',
        'YDS.1': 'RUSH_YDS',
        'CMP': 'CMP',
        'FG': 'FG',
        'FGA': 'FGA',
        'FL': 'FL',
        'FPTS': 'FPTS',
        'INTS': 'INTS',
        'Player': 'Player',
        'REC': 'REC',
        'XPT': 'XPT',
        'position': 'POSITION',
        'week': 'WEEK',
        'expert': 'EXPERT'
    }
}