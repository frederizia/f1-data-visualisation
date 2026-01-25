from invoke import collection

from . import download, season_stats


namespace = collection.Collection(download, season_stats)
