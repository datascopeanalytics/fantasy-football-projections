import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator
sns.set(style='white', palette='muted')

def ranker(df):
    """Used for getting the top N players at a given position and week"""
    df.sort('FPTS', inplace=True, ascending=False)
    df['POSITION_RANK'] = np.arange(len(df)) + 1
    return df

def bootstrap(data, statfunction=np.mean):
    """Returns a Series of 10,000 boostrapped values with the given statfunction applied"""
    np.random.seed(42)
    samples = pd.DataFrame(np.random.choice(data, size=(10000, len(data)), replace=True))
    return samples.apply(statfunction, axis=1)

def histogram(data, filename, small=False, title='', titlesize=22, bins=25, figsize=(13,5), xlim=None, xlabel='', xsize=22, ylabel=''):
    fig = plt.figure(figsize=figsize)
    axes = fig.add_subplot(111)
    [item.set_fontsize(xsize) for item in axes.get_xticklabels()]
    axes.xaxis.set_major_locator(MaxNLocator(symmetric=True))
    axes.locator_params(nbins=7)
    if small:
        axes.locator_params(nbins=5)
    plt.title(title, fontdict={'fontsize': titlesize})
    r = sns.distplot(data, color='#ff6000', bins=bins, kde=False)
    r.set_xlabel(xlabel)
    r.set_ylabel(ylabel)
    r.set_xlim(xlim)
    r.set_yticklabels('')
    r.axvline(x=0, ls=':', color='k', linewidth=1.5)
    r.spines['top'].set_visible(False)
    r.spines['left'].set_visible(False)
    r.spines['right'].set_visible(False)
    plt.savefig(filename, bbox_inches='tight')

def boxplots(data, filename, title='', xlabel='', ylabel='', xlim=(-5,5), order=None):
    boxes = 1
    if not isinstance(data, list):
        boxes = len(data.keys())

    plt.figure(figsize=(13, 6))
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

