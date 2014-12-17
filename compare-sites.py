"""
Compares prognosticators making fantasy football projections.
"""
from mappings import ESPN_SCORING, FANTASY_RELEVANT, NAME_CORRECTIONS
import utils
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import re

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

def get_team_name(player_name):
    team = re.findall('\((.*)\)', player_name)
    if team:
        if team == 'WAS':
            return 'Wsh'
        return team[0].capitalize()

def read_projections():
    """
    get paths for expert projections; read into list of dataframes
    Returns unified dataframe with all projections
    """
    file_list = glob('data/fantasypros-*.csv')
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
    scoring = pd.read_csv('data/scoring-espn.csv')
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
    see mappings.FANTASY_RELEVANT; uses utils.ranker function
    """
    cols_to_groupby = ['EXPERT', 'POSITION', 'WEEK']
    ranked = projections_df.groupby(cols_to_groupby).apply(utils.ranker)
    # ranked.reset_index(inplace=True)

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
    Uses bootstrapped mean by default.
    
    Parameters
    ----------
    df: pandas.DataFrame
    col_to_bootstrap: string
        Column to apply bootstrapping technique to
    statfunction: function
        Statistical function to use for bootstrapping.

    Returns
    -------
    """
    np.random.seed(42) # set random seed for consistent results
    experts = {}
    for expert_name in df.EXPERT.unique().tolist():
        # filter to the relevant expert and column
        data = df[ df.EXPERT == expert_name ][col_to_bootstrap]
        # use the bootstrap to create 10000 x N matrix
        sims = np.random.choice(data, size=(10000, len(data)), replace=True)
        # apply statfunction to each row (simulation) of the matrix
        booted_vals = pd.DataFrame(sims).apply(statfunction, axis=1).tolist()
        experts[expert_name] = booted_vals
    return experts

def bootstrap_experts_positions(df, col_to_bootstrap, statfunction=np.mean):
    np.random.seed(42) # set random seed for consistent results
    results = {}
    experts = df.EXPERT.unique().tolist()
    positions = df.POSITION.unique().tolist()
    for ex_name in experts:
        pos_results = {}

        for pos in positions:
            # filter to the relevant expert and position
            condition = (df.EXPERT == ex_name) & (df.POSITION == pos)
            data = df[condition][col_to_bootstrap]
            # use the bootstrap to create 10000 x N matrix
            sims = np.random.choice(data, size=(10000, len(data)), replace=True)
            # apply statfunction to each row (simulation) of the matrix
            booted_vals = pd.DataFrame(sims).apply(statfunction, axis=1).tolist() 
            pos_results[pos] = booted_vals

        results[ex_name] = pos_results
    return results

def generate_histograms(data):
    for expert, values in data.iteritems():
        filename = ''.join(char for char in expert if char not in '.,')
        filename = filename.strip().replace(' ', '-').lower()
        utils.histogram(
            data=values,
            filename='charts/fantasypros/{}'.format(filename),
            title='Mean Point Error - {}'.format(expert),
            figsize=(10,5),
            titlesize=26,
            xsize=26,
            xlim=(-2.75, 2.75),
            small=True
        )

def generate_histogram_grid(data):
    pass

if __name__ == '__main__':
    projections = read_projections()
    scoring = read_scoring()
    fantasy_relevant = get_fantasy_relevant(projections)

    # clean up names for joining projections with actual scoring
    fantasy_relevant['PLAYER_NAME'] = fantasy_relevant.Player.apply(clean_name)
    fantasy_relevant['TEAM'] = fantasy_relevant.Player.apply(get_team_name)
    scoring['PLAYER_NAME'] = scoring.name.apply(clean_name)

    joined = pd.merge(fantasy_relevant, scoring,
                        left_on=['PLAYER_NAME', 'WEEK', 'POSITION'],
                        right_on=['PLAYER_NAME', 'week', 'position'],
                        how='left')
    cols = ['PLAYER_NAME', 'TEAM', 'POSITION', 'WEEK', 'EXPERT',
            'POSITION_RANK', 'FPTS', 'PTS_SCORED']
    
    # drop players that don't have teams - Brandon Jacobs, JP Wilson, etc.
    joined.dropna(how='all', subset=['TEAM', 'PTS_SCORED'], inplace=True)
    joined['PTS_DIFF'] = (joined.FPTS - joined.PTS_SCORED)
    joined['REL_DIFF'] = (joined.PTS_DIFF / joined.FPTS)

    abs_err_by_expert = bootstrap_experts(joined, 'PTS_DIFF')
    abs_err_by_expert_position = bootstrap_experts_positions(joined, 'PTS_DIFF')
    rel_err_by_expert = bootstrap_experts(joined, 'REL_DIFF')
    rel_err_by_expert_position = bootstrap_experts_positions(joined, 'REL_DIFF')

    generate_histograms(abs_err_by_expert)