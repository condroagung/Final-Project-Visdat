# pandas and numpy for data manipulation
import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.models import (HoverTool,
                          ColumnDataSource, Panel)
from bokeh.models.widgets import (RadioButtonGroup, Select, DateRangeSlider)
from bokeh.layouts import column, row
import matplotlib.pyplot as plt

# Make plot with histogram and return tab


def plotting(Confirmed, Recovered, Death):

    case = "Confirmed"
    region = 'Indonesia'

    def create_data(region, case, date_range=None):

        if case == 'Confirmed':
            plot = Confirmed[region]
        elif case == 'Death':
            plot = Death[region]
        elif case == 'Recovered':
            plot = Recovered[region]

        if case == "All":
            df = pd.DataFrame(data={
                'date': pd.to_datetime(Confirmed['Date']),
                'death': Death[region],
                'recovered': Recovered[region],
                'plot': Death[region]
            })
        else:
            df = pd.DataFrame(data={
                'date': pd.to_datetime(Confirmed['Date']),
                'plot': plot
            })

        if date_range is not None:
            mask = (df['date'] > np.datetime64(date_range[0])) & (
                df['date'] <= np.datetime64(date_range[1]))
            df = df.loc[mask]
        return ColumnDataSource(df)

    def make_plot(source, title, case='Confirmed'):
        plt = figure(x_axis_type='datetime', name='plt')
        plt.title.text = title
        plt.line('date', 'plot', source=source, color="dodgerblue", line_width=1,
                 name='case', legend_label=case)
        plt.circle('date', 'plot', size=5, color="dodgerblue", source=source)

        hover = HoverTool(tooltips=[('Date', '@date'), ('Total case', '@plot')],
                          formatters={'date': 'datetime'})
        plt.add_tools(hover)
        plt.legend.location = "top_left"
        # fixed attributes
        plt.xaxis.axis_label = "Date"
        plt.yaxis.axis_label = "Total cases"
        plt.axis.axis_label_text_font_style = "bold"
        plt.grid.grid_line_alpha = 0.3
        return plt

    def update(date_range=None, force=False):
        plt.title.text = case.capitalize() + " case in " + region
        newdata = create_data(region, case, date_range).data
        source.data.update(newdata)

    def handle_region_change(attrname, old, new):
        region = select.value
        plt.title.text = case.capitalize() + " case in " + region
        newdata = create_data(region, case).data
        source.data.update(newdata)

    def handle_range_change(attrname, old, new):

        slider_value = date_range_slider.value_as_datetime
        update(date_range=slider_value)

    def handle_case_change(attrname, old, new):
        from bokeh.models.glyphs import Line
        cases = ["Confirmed", "Recovered", "Death", 'All']
        case = cases[new]
        print(case)
        newdata = create_data(region, case).data
        source.data.update(newdata)

        if case == 'Confirmed' or case == "All":
            color = 'dodgerblue'
        elif case == 'Death':
            color = 'red'
        elif case == 'Recovered':
            color = "green"

        if case != "All" or case == 'Global':

            plt.legend.items = [
                (case, [plt.renderers[0]])
            ]
            plt.renderers[0].glyph.line_color = color
            plt.renderers[1].glyph.line_color = color
            try:
                plt.renderers[2].visible = False
                plt.renderers[3].visible = False
            except IndexError:
                print(False)
        else:
            try:
                plt.renderers[0].glyph.line_color = 'dodgerblue'
                plt.renderers[1].glyph.line_color = 'dodgerblue'
                plt.renderers[2].visible = True
                plt.renderers[3].visible = True
                plt.legend.items = [
                    ("Confirmed", [plt.renderers[0]]),
                    ("Recovered", [plt.renderers[2]]),
                    ("Death", [plt.renderers[3]])
                ]
            except IndexError:
                plt.vbar('date', top='recovered', width=1, line_width=5, source=source, color='green',
                         name='recovered', legend_label="Recovered")
                plt.step(x='date', y='death', source=source, color='red', line_width=2,
                         name='death', legend_label="Death")

    # Default value
    source = create_data(region, case)
    case_date = pd.to_datetime(source.data['date'])
    slider_value = case_date[0], case_date[-1]

    plt = make_plot(source, case.capitalize() + " case in " +
                    region, case)
    date_range_slider = DateRangeSlider(value=(
        0, slider_value[1]), start=slider_value[0], end=slider_value[1], title="Date", name="date_range_slider")
    date_range_slider.on_change('value', handle_range_change)

    select = Select(title="Country", value="Indonesia",
                    options=Confirmed.columns.tolist()[1:], name="select")
    select.on_change('value', handle_region_change)

    case_select = RadioButtonGroup(
        labels=["Confirmed", "Recovered", "Death", "All"], active=0, name="case_select")
    case_select.on_change('active', handle_case_change)

    # Make a tab with the layout
    tab = Panel(child=row(column(select, case_select, date_range_slider), plt),
                title='Grafik Kasus Covid-19')

    return tab
