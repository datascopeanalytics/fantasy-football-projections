import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='white', palette='colorblind')
np.random.seed(42)

def ranker(df):
    """Used for getting the top N players at a given position and week"""
    df.sort('projected_pts', inplace=True, ascending=False)
    df['position_rank'] = np.arange(len(df)) + 1
    return df

def bootstrap(data, statfunction=np.mean):
    """Returns a Series of 10,000 boostrapped values with the given statistical funcion applied"""
    samples = pd.DataFrame(np.random.choice(data, size=(10000, len(data)), replace=True))
    return samples.apply(statfunction, axis=1)

def get_ci(data, alpha=0.05):
    lower, upper = (alpha/2), 1 - (alpha/2)
    return np.percentile(data, [lower, upper])

def histogram(data, filename, title=None, xlim=(-2.5, 2.5)):
    plt.figure(figsize=(13, 5))
    plt.title(title, fontdict={'fontsize': 13})
    r = sns.distplot(data)
    r.set_yticklabels('')
    r.set_xlim(xlim)
    # r.set_xticks(xticks)
    r.vlines(0, 0, 4, linestyles=':', color='r', linewidth=.7)
    r.spines['top'].set_visible(False)
    r.spines['left'].set_visible(False)
    r.spines['right'].set_visible(False)
    plt.savefig(filename)

def boxplots(data, filename, title=None, xlabel='', ylabel='', xlim=(-5,5), order=None):
    boxes = 1
    if not isinstance(data, list):
        boxes = len(data.keys())

    plt.figure(figsize=(13, 5))
    plt.title(title, fontdict={'fontsize': 13})
    b = sns.boxplot(data, vert=False, linewidth=1, fliersize=0,
                    order=order, widths=[.3] * boxes)
    b.set_xlabel(xlabel)
    b.set_ylabel(ylabel)
    b.set_xlim(xlim)
    # b.set_xticks(xticks)
    b.vlines(0, 0, boxes + 1, linestyles=':', color='r', linewidth=.7)
    b.spines['top'].set_visible(False)
    b.spines['left'].set_visible(False)
    b.spines['right'].set_visible(False)
    plt.savefig(filename)

projections = pd.read_csv('data/projections.csv', index_col=['player_id', 'name', 'season', 'week'])
scoring = pd.read_csv('data/scoring.csv', index_col=['player_id', 'name', 'season', 'week'])

espn = scoring.join(projections.query('projected_pts > 0').projected_pts, how='right')
espn['point_diff'] = (espn.projected_pts - espn.total_pts)
espn['relative_diff'] = espn.point_diff / espn.projected_pts
espn.reset_index(inplace=True)
ranked = espn.groupby(['position', 'week']).apply(ranker)


# only fantasy relevant players
frames = []
relevant = {'QB': 20, 'RB': 60, 'WR': 60, 'TE': 20, 'K': 15, 'D/ST': 15}
booted_positions = {'points': {}, 'relative': {}}
for pos, n in relevant.iteritems():
    condition = (ranked.position == pos) & (ranked.position_rank <= n)
    frames.append(ranked[condition])
    booted_positions['points'][pos] = bootstrap(ranked[condition]['point_diff'])
    booted_positions['relative'][pos] = bootstrap(ranked[condition]['relative_diff'])
fantasy_relevant = pd.concat(frames)

booted_weeks = {'points': {}, 'relative': {}}
for i in range(1, espn.week.max() + 1):
    condition = fantasy_relevant.week == i
    booted_weeks['points'][i] = bootstrap(fantasy_relevant[condition]['point_diff'])
    booted_weeks['relative'][i] = bootstrap(fantasy_relevant[condition]['relative_diff'])

# plots, plots, plots, plots plots plots
# absolute distribution
histogram(
    data=bootstrap(espn.point_diff),
    filename='charts/all-point-histogram.png',
    title='Point Difference (Projected - Actual)\n All Players Projected > 0'
)
histogram(
    data=bootstrap(fantasy_relevant.point_diff),
    filename='charts/relevant-point-histogram.png',
    title='Point Difference (Projected - Actual)\n FFB Relevant Players Only'
)

# relative distribution
histogram(
    data=bootstrap(espn.relative_diff),
    filename='charts/all-relative-histogram.png',
    title='Relative Difference\n FFB Relevant Players Only',
    xlim=(-.5, .5)
)
histogram(
    data=bootstrap(fantasy_relevant.relative_diff),
    filename='charts/relevant-relative-histogram.png',
    title='Relative Difference\nFFB Relevant Players Only',
    xlim=(-.5, .5)
)

# by position
positions = ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST']
boxplots(
    data=pd.DataFrame(booted_positions['points'], columns=positions),
    filename='charts/position-point-boxplot.png',
    title='Point Difference by Position\nFFB Relevant Players Only',
    xlabel='Point Difference (Projected - Actual)',
    ylabel='Position',
    order=positions[::-1]
)
boxplots(
    data=pd.DataFrame(booted_positions['relative'], columns=positions),
    filename='charts/position-relative-boxplot.png',
    title='Relative Difference by Position\n FFB Relevant Players Only',
    xlabel='Relative Difference',
    ylabel='Position',
    xlim=(-.5, .5),
    order=positions[::-1]
)

# by week
boxplots(
    data=pd.DataFrame(booted_weeks['points']),
    filename='charts/weekly-point-boxplot.png',
    title='Point Difference by Week',
    xlabel='Point Difference (Projected - Actual)',
    ylabel='Week',
    order=sorted(booted_weeks['points'].keys(), reverse=True)
)
boxplots(
    data=pd.DataFrame(booted_weeks['relative']),
    filename='charts/weekly-relative-boxplot.png',
    title='Relative Difference by Week',
    xlabel='Relative Difference',
    ylabel='Week',
    xlim=(-.5, .5),
    order=sorted(booted_weeks['relative'].keys(), reverse=True)
)