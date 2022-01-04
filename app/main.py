# Pandas for data management
import pandas as pd
import geopandas as gpd
import geoplot.crs as gcrs
import pathlib
import matplotlib.animation as animation
import matplotlib.pyplot as plt

# os methods for manipulating paths
from os.path import dirname, join

# Bokeh basics
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs

# Each tab is drawn by one script
from scripts.plot import plotting
from scripts.map import mapping

# Using included state data from Bokeh for map
from bokeh.sampledata.us_states import data as states

# Read data into dataframes
Confirmed = pd.read_csv(join(dirname(__file__), 'data', 'Confirmed.csv'))
Recovered = pd.read_csv(join(dirname(__file__), 'data', 'Recovered.csv'))
Death = pd.read_csv(join(dirname(__file__), 'data', 'Deaths.csv'))
Cases = pd.read_csv(join(dirname(__file__), 'data',
                         'countries-aggregated.csv'))
# Read Shapefile into dataframes
World = gpd.read_file(join(dirname(__file__), 'data', 'World_Countries.shp'))

# Create each of the tabs
tab1 = plotting(Confirmed, Recovered, Death)  # For Plotting
tab2 = mapping(World, Cases)  # For Mapping

# Put all the tabs into one application
tabs = Tabs(tabs=[tab1, tab2])

# Put the tabs in the current document for display
curdoc().add_root(tabs)
curdoc().title = "Kasus Persebaran Covid 19 di Seluruh Dunia"
