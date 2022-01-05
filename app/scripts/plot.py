# pandas and numpy for data manipulation
import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.models import (HoverTool,
                          ColumnDataSource, Panel)
from bokeh.models.widgets import (
    RadioButtonGroup, Select, DateRangeSlider, CheckboxGroup)
from bokeh.layouts import column, row
import matplotlib.pyplot as plt

# Make plot with histogram and return tab


def plotting(df_confirmed, df_recovered, df_death):

    # function make columndatasource
    def make_source(case_list, country, date_range=None):

        ys = []
        color = []

    # if date_range is not None:
        # mask = (df_confirmed['date'] > np.datetime64(date_range[0])) & (
        # df_confirmed['date'] <= np.datetime64(date_range[1]))

        for i, case in enumerate(case_list):

            if case == "Confirmed":
                if date_range is not None:
                    ys.append(df_confirmed.loc[(df_confirmed['Date'] > date_range[0]) & (
                        df_confirmed['Date'] <= date_range[1])][country].tolist())
                else:
                    ys.append(df_confirmed[country].tolist())
                color.append('dodgerblue')
            elif case == "Recovered":
                if date_range is not None:
                    ys.append(df_recovered.loc[(df_recovered['Date'] > date_range[0]) & (
                        df_recovered['Date'] <= date_range[1])][country].tolist())
                else:
                    ys.append(df_recovered[country].tolist())
                color.append('green')
            else:
                if date_range is not None:
                    ys.append(df_death.loc[(df_death['Date'] > date_range[0]) & (
                        df_death['Date'] <= date_range[1])][country].tolist())
                else:
                    ys.append(df_death[country].tolist())
                color.append('red')

        if date_range is not None:
            Source = {'x': [df_confirmed.loc[(df_death['Date'] > date_range[0]) & (df_death['Date'] <= date_range[1])]['Date'].tolist()] * len(case_list),
                      'y': ys,
                      'label': case_list,
                      'color': color}
        else:
            Source = {'x': [df_confirmed['Date'].tolist()] * len(case_list),
                      'y': ys,
                      'label': case_list,
                      'color': color}

        source = ColumnDataSource(Source)

        return source

    # function make plot
    def make_plot(source):

        p = figure(x_axis_type='datetime')

        p.title.text = "Cases in " + country
        p.multi_line('x', 'y', color='color', legend='label',
                     line_width=1,
                     source=source)
        #plt.line(x='Date',y = 'Afghanistan', color='green', source=source)
        #plt.circle('Date', 'Albania', size=5, source=source)
        # hover = HoverTool(tooltips=[('Date', '@Date{%F}'), ('Confirmed case', '@Albania')],
        # formatters={'date': 'datetime'})
        # plt.add_tools(hover)
        hover = HoverTool(tooltips=[('Cases', '@label'),
                                    ('Date', '$x{%Y-%m-%d %H:%M:%S}'),
                                    ('Number of case', '$y')],
                          formatters={'$x': 'datetime'},
                          line_policy='next')

        # Add the hover tool and styling
        p.add_tools(hover)
        # fixed attributes
        p.xaxis.axis_label = "Date"
        p.yaxis.axis_label = "Total cases"
        p.axis.axis_label_text_font_style = "bold"
        p.grid.grid_line_alpha = 0.3

        return p

    # function update columndatasource from checkbox value
    def update(attr, old, new):
        cases_to_plot = [cases_selection.labels[i] for i in
                         cases_selection.active]

        new_src = make_source(cases_to_plot, country)

        source.data.update(new_src.data)

    # function update columndatasource from select value
    def update_country_case(attr, old, new):
        cases_to_plot = [cases_selection.labels[i] for i in
                         cases_selection.active]
        country = select.value
        p.title.text = "Cases in " + country

        new_src = make_source(cases_to_plot, country)

        source.data.update(new_src.data)

    # function update columndatasource from range value
    def update_range(attrname, old, new):
        cases_to_plot = [cases_selection.labels[i] for i in
                         cases_selection.active]
        slider_value = date_range_slider.value_as_datetime
        print(slider_value)
        new_src = make_source(cases_to_plot, country, slider_value)

        source.data.update(new_src.data)

    # Default value
    country = 'Indonesia'
    cases_info = ['Confirmed', 'Recovered', 'Death']
    # Convert all date dataframe type to datatime
    df_confirmed['Date'] = pd.to_datetime(df_confirmed['Date'])
    df_recovered['Date'] = pd.to_datetime(df_recovered['Date'])
    df_death['Date'] = pd.to_datetime(df_death['Date'])

    # make widget checkbox
    cases_selection = CheckboxGroup(labels=cases_info,
                                    active=[0, 1])
    # make interactive checkbox
    cases_selection.on_change('active', update)

    initial_cases = [cases_selection.labels[i] for
                     i in cases_selection.active]
    # make widget select
    select = Select(title="Country", value="Indonesia",
                    options=df_confirmed.columns.tolist()[1:], name="select")

    # make interactive select
    select.on_change('value', update_country_case)

    # make source
    source = make_source(initial_cases, country)

    # make plot
    p = make_plot(source)

    # convert to datetime for range date
    case_date = pd.to_datetime(source.data['x'][0])
    # initiate start and end value date range slider
    slider_value = case_date[0], case_date[-1]
    #mask = (df_confirmed['date'] > np.datetime64(case_date[0])) & (df_confirmed['date'] <= np.datetime64(case_date[-1]))

    # make widget date range slider
    date_range_slider = DateRangeSlider(value=(
        0, slider_value[1]), start=slider_value[0], end=slider_value[1], title="Date", name="date_range_slider")

    # make interactive date range slider
    date_range_slider.on_change('value', update_range)

    # Make a tab with the layout
    tab = Panel(child=row(column(cases_selection, select, date_range_slider), p),
                title='Grafik Kasus Covid-19')

    return tab
