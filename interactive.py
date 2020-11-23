from typing import Tuple

import json

import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

# Vision:
# Allow selecting multiple different results.
# Selecting the results plots them.
# Allow choice of plot.
# Feature-wise hist, sample-wise hist, maybe box + whisker?

#Make  a drop-down with the list of result names. Later: is there some way to give them a better name?
def dash_task():
    df = pd.read_table('diana_tables_all.tsv', sep='\t')
    df = df[(df['value_name'] != 'qiime2_type')&(df['value_name']!='qiime2_format')]

    r_names= df['results_name'].unique()

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = dbc.Container(fluid=True, children=[
        html.Div('Select Results (up to 6)'),
        #select results/
        dcc.Dropdown(id='result-input',
                    options=[{'label': result, 'value':result} for result in r_names],
                    value=r_names[0],
                    multi=True,
                    clearable=True,
        ),
        #select plot type
        dcc.Dropdown(id='output-type',
                    options=[{'label': 'Table Stats', "value": "table"},
                             {'label': 'Feature-wise Stats', 'value':"feature"},
                             {'label':"Sample-wise Stats", 'value':"sample"}],
                    value='table',
                    multi=False,
                    clearable=False,

        ),
        dbc.Button('Update Plots', id='interactive_button', color='success'),
        html.Div(
            id='plot-area'
        ),

    ])
    #Function for plots. Will display following:
    # Table: Table stats + box+whisker plot
    @app.callback(
        Output('plot-area', 'children'),
        [Input('interactive_button', 'n_clicks'),
        State('result-input', 'value'),
        State('output-type', 'value')]
    )
    def plot(click, results, focus):
        if results==[]:
            return "Select one or more results."
        if type(results) == str:
            results = [results]

        fig = None
        r_sel = df[df['results_name'].isin(results)]
        #box+whisker showing dist. of features per sample
        if focus=="table":
            tablewise = r_sel[['results_name','samples__name', 'features__pk', 'frequency']].drop_duplicates()
            fig = px.box(tablewise, x='samples__name', y='frequency', facet_col='results_name')
        #frequency per sample
        if focus=='feature':
            featurewise = r_sel[['results_name', 'features__pk', 'frequency']].drop_duplicates()
            fig = px.histogram(featurewise.groupby(['results_name', 'features__pk']).sum().reset_index(), x='frequency', nbins=20, facet_col='results_name')

        if focus=='sample':
            samplewise = r_sel[['results_name', 'samples__name', 'frequency']].drop_duplicates()
            fig = px.histogram(samplewise.groupby(['results_name', 'samples__name']).sum().reset_index(), x='frequency', nbins=20, facet_col='results_name')


        return dcc.Graph(figure=fig)



    return app

if __name__ == "__main__":
    print("RUN")
    app = dash_task()
    app.run_server(debug=True)
