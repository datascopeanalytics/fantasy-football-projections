"""
Compares prognosticators making fantasy football projections
"""
from utils import ranker, bootstrap, histogram, boxplots
from mappings import ESPN_SCORING, FANTASY_RELEVANT, NAME_CORRECTIONS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from glob import glob

def calculate_points(df):
    """Vectorizing the fractional point calculation."""
    pass

def clean_name(player_name):
    """
    FantasyPros names have team names and other junk in them.
    This cleans them up.
    """
    name = player_name.split('(')[0].strip()
    if name in NAME_CORRECTIONS.keys():
        return NAME_CORRECTIONS[name].strip().lower()

    name = ''.join(char for char in name if char not in '.,')
    return name.strip().lower()

def read_projections():
    """
    get paths for expert projections; read into list of dataframes
    Returns unified dataframe with all projections
    """
    file_list = glob('data/projections-*.csv')
    frames = []
    for item in file_list:
        # don't want the projections-espn file
        # we have the same data from Fantasy Pros
        if 'espn' not in item:
            frames.append(pd.read_csv(item))
    return pd.concat([df.fillna(0) for df in frames])

def read_scoring():
    """
    calculate actual points scored; use fractional to be more precise
    ESPN only uses whole points; takes a bit bc of the looping
    """
    scoring = pd.read_csv('data/scoring.csv')
    scoring['PTS_SCORED'] = 0
    for idx, col in scoring.iterrows():
        if scoring.ix[idx, 'position'] == 'K':
            scoring.ix[idx, 'PTS_SCORED'] = scoring.ix[idx, 'total_pts']
        for k, v in ESPN_SCORING.iteritems():
            scoring.ix[idx, 'PTS_SCORED'] += scoring.ix[idx, k] * ESPN_SCORING[k]
    return scoring

def get_fantasy_relevant(projections_df):
    """
    get only fantasy relevant players; top N at each position
    see mappings.FANTASY_RELEVANT
    """
    cols_to_groupby = ['PLAYER_NAME', 'WEEK', 'EXPERT']
    ranked = projections_df.groupby(cols_to_groupby).apply(ranker)
    ranked.reset_index(inplace=True)

    cols = ['PLAYER_NAME', 'POSITION', 'WEEK', 'EXPERT', 'POSITION_RANK'
            'FPTS', 'PTS_SCORED', 'PTS_DIFF', 'REL_DIFF']
    relevant = []    
    for pos, n in FANTASY_RELEVANT.iteritems():
        cond = (ranked.POSITION == pos) & \
                (ranked.POSITION_RANK <= n)
        relevant.append(ranked[cond])
    return pd.concat(relevant)

def bootstrap_experts(df, col_to_bootstrap, statfunction=np.mean):
    """
    Runs the bootrapping method for each expert on the given column_name.
    """
    np.random.seed(42)
    
    experts = {}
    pass

if __name__ == '__main__':
    projections = read_projections()
    scoring = read_scoring()

    # clean up names for joining projections with actual scoring
    projections['PLAYER_NAME'] = projections.Player.apply(clean_name)
    scoring['PLAYER_NAME'] = scoring.name.apply(clean_name)
    joined = pd.merge(projections, scoring,
                        left_on=['PLAYER_NAME', 'WEEK', 'POSITION'],
                        right_on=['PLAYER_NAME', 'week', 'position'],
                        how='left')

    joined[joined.PTS_SCORED.isnull()].PLAYER_NAME.value_counts()
    cols = ['PLAYER_NAME', 'team', 'POSITION', 'WEEK',
            'EXPERT', 'FPTS', 'PTS_SCORED']
    joined = joined[cols]
    joined['PTS_DIFF'] = (joined.FPTS - joined.PTS_SCORED)
