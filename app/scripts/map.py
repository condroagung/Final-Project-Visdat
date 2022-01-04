import geoplot as gplt
import geopandas as gpd
import geoplot.crs as gcrs
import imageio
import pandas as pd
import pathlib
import matplotlib.animation as animation
import matplotlib.pyplot as plt
#import mapclassify as mc
import numpy as np
import json
from bokeh.io import show, curdoc, output_notebook
from bokeh.models import (ColorBar, ColumnDataSource,
                          GeoJSONDataSource, HoverTool, Slider, CategoricalColorMapper, LabelSet, Button, TableColumn, DataTable, Label, Div, Panel)
from bokeh.layouts import row, layout
from bokeh.palettes import brewer
from bokeh.plotting import figure

# %matplotlib inline

pd.options.display.max_rows = 500
pd.options.display.max_columns = 500


def mapping(World, Cases):

    World['geometry'] = World['geometry'].to_crs(epsg=4326)

    World['point'] = World['geometry'].centroid

    World['x'] = World['point'].x
    World['y'] = World['point'].y

    World.drop(columns='point', inplace=True)

    range_time = Cases.Date.unique().tolist()

    day = []

    for date in Cases.Date:
        day.append(range_time.index(date)+1)

    Cases["Day"] = day

    conditions = [
        (Cases['Confirmed'] < 1),
        (Cases['Confirmed'] >= 1) & (Cases['Confirmed'] < 20),
        (Cases['Confirmed'] >= 20) & (Cases['Confirmed'] < 100),
        (Cases['Confirmed'] >= 100) & (Cases['Confirmed'] < 1000),
        (Cases['Confirmed'] >= 1000) & (Cases['Confirmed'] < 10000),
        (Cases['Confirmed'] >= 10000) & (Cases['Confirmed'] < 50000),
        (Cases['Confirmed'] >= 50000) & (Cases['Confirmed'] < 100000),
        (Cases['Confirmed'] >= 100000) & (Cases['Confirmed'] < 500000),
        (Cases['Confirmed'] >= 500000) & (Cases['Confirmed'] < 1000000),
        (Cases['Confirmed'] >= 1000000) & (Cases['Confirmed'] <= 5000000),
        (Cases['Confirmed'] > 5000000)
    ]

    # create a list of the values we want to assign for each condition
    list_category = ['0', '1-19', '20-99', '100-999', '1000-9999', '10000-49999',
                     '50000-99999', '100000-499999', '500000-999999', '1M-5M', '>5M']

    category = np.select(conditions, list_category)
    Cases['Category'] = category

    def json_data(selectedDay):

        sd = selectedDay
        # Pull selected year
        df_dt = Cases[Cases['Day'] == sd]

        # Merge the GeoDataframe object (sf) with the covid19 data
        merge = World.merge(df_dt, how='left', left_on=[
                            'COUNTRY'], right_on=['Country'])
        # remove columns
        merge.dropna(inplace=True)
        merge.drop(columns=['COUNTRY'], inplace=True)

        # Bokeh uses geojson formatting, representing geographical   features, with json
        # Convert to json
        merge_json = json.loads(merge.to_json())

        # Convert to json preferred string-like object
        json_data = json.dumps(merge_json)
        return json_data

    def columndata(selectedDay):
        cd = selectedDay
        # Pull selected day
        column = Cases[Cases['Day'] == cd]
        column = column.sort_values(by='Confirmed', ascending=False)
        rank = []
        for i in range(column.index.shape[0]):
            rank.append(i+1)
        column['rank'] = rank
        most_country = column.head(10)
        source = dict(
            rank=[rank for rank in most_country['rank']],
            country=[country for country in most_country['Country']],
            confirmed=[confirmed for confirmed in most_country['Confirmed']]
        )
        return source

    def update_plot(attr, old, new):
        day = slider.value
        new_data = json_data(day)
        geosource.geojson = new_data
        source.data = columndata(day)

    def animate_update():
        val = slider.value + 1
        if val > 710:
            val = 0
        slider.value = val

    def animate():

        global callback_id
        if button.label == 'Play':
            button.label = 'Pause'
            callback_id = curdoc().add_periodic_callback(animate_update, 20)
        else:
            button.label = 'Play'
            curdoc().remove_periodic_callback(callback_id)

    # Geosource information for mapping
    geosource = GeoJSONDataSource(geojson=json_data(1))  # Default Day 1
    # Source for DataTable
    source = ColumnDataSource(columndata(1))  # Default Day 1
    # List Color Palette For Each Category Confirmed
    palet = ['#242424', '#5e5b5b', '#d9d9d9', '#6c3778', '#9e5aad', '#cf87e0', '#f3c2ff',
             '#67000d', '#cb181d', '#ef3b2c', '#fc9272']
    palet = palet[::-1]
    # Categorical per palette
    color_mapper = CategoricalColorMapper(
        factors=list_category,  palette=palet)
    # menampilkan legend categorical mapper
    color_bar = ColorBar(color_mapper=color_mapper, title='Confirmed Case',
                         # title=color.value.title(),
                         title_text_font_style='bold',
                         title_text_font_size='20px',
                         title_text_align='center',
                         orientation='vertical',
                         major_label_text_font_size='16px',
                         major_label_text_font_style='bold',
                         label_standoff=8,
                         major_tick_line_color='black',
                         major_tick_line_width=3,
                         major_tick_in=12,
                         location=(0, 0))

    # Create figure object.
    r = figure(title='',
               plot_height=600, plot_width=1000,
               toolbar_location='below',
               tools=['pan, wheel_zoom, box_zoom, reset'])
    r.title.align = 'center'
    r.xaxis.visible = False
    r.yaxis.visible = False
    r.xgrid.grid_line_color = None
    r.ygrid.grid_line_color = None
    # Add patch renderer to figure.
    states = r.patches('xs', 'ys', source=geosource,
                       fill_color={'field': 'Category',
                                   'transform': color_mapper},
                       line_color='gray',
                       line_width=0.25,
                       fill_alpha=1)
    # menambahkan label nama negara ditiap geografinya
    labels = LabelSet(x='x', y='y', text='ISO_A3', text_font_size='3pt', text_font_style='bold', text_align='center',
                      x_offset=0, y_offset=0, source=geosource, render_mode='canvas')
    # membuat hover
    r.add_tools(HoverTool(renderers=[states],
                          tooltips=[('Country', '@Country'),
                                    ('Confirmed', '@Confirmed{,}'),
                                    ('Recovered', '@Recovered{,}'),
                                    ('Deaths', '@Deaths{,}')]))
    # Make a slider object: slider
    slider = Slider(title='Days', start=1, end=710, step=1, value=1)
    slider.on_change('value', update_plot)
    # membuat tombol animasi
    callback_id = None
    button = Button(label='Play', width=60)
    button.on_click(animate)
    # teks Div
    div = Div(text="""Visualisasi Data berikut menunjukkan persebaran kasus covid 19 di seluruh dunia mulai dari tanggal <b>22 Januari 2020</b> hingga <b>31 Desember 2021</b>. Slider menunjukkan pemetaan dari hari ke
    1 yaitu (22 Januari 2020) hingga hari ke 710 yaitu (31 Desember 2021).""",
              width=250, height=100)
    # membuat tabel
    columns = [
        TableColumn(field='rank', title='Rank'),
        TableColumn(field='country', title='Country'),
        TableColumn(field='confirmed', title='Confirmed'),
    ]
    tabel = DataTable(source=source, columns=columns,
                      width=300, height=600, index_position=None)
    judul = Label(x=400, y=500, x_units='screen', y_units='screen',
                  text='World Covid19 History', render_mode='css',
                  text_font_size='23pt', text_color="black", text_font_style="bold", text_font="times")
    # Make a column layout of widgetbox(slider) and plot, and add it to the current document
    r.add_layout(color_bar)
    r.add_layout(labels)
    r.add_layout(judul)
    Layout = layout([
        [r],
        [slider, button, div],
    ])
    # Make a tab with the layout
    tab = Panel(child=row(Layout, tabel), title='Pemetaan Kasus Covid-19')

    return tab
