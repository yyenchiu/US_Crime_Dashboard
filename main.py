import numpy as np
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px

import dash
from dash import dcc
from dash import html
from dash import ctx
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

external_stylesheets = {
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
# bootstrap themes: bootswatch.com

# ---------------------------------------------------------------------------------------------------------------------
# Import cleaned data

df_main = pd.read_csv("df_for_dash.csv", header=0, index_col=0,
                      dtype={"Year": int, "State": str, "City": str, "Population": int, "Violent_crime": int,
                             "Property_crime": int, "Violent_crime_per_100k": float, "Property_crime_per_100k": float,
                             "Violent_to_property_ratio": float})

# Dropping all locations with population under 1000, as that in general could be considered too small to be a city.
# This is a simple way to address the issue of outliers when crime rates are scaled to population (some locations
# have population under 100 with crime reports over 400, which is very weird).
df_main = df_main.drop(df_main[df_main["Population"] < 1000].index, axis=0)

abbrv = pd.read_csv("ABBRV.csv", header=0, index_col=0)

# ---------------------------------------------------------------------------------------------------------------------
# App layout
app.layout = html.Div([html.H1("Exploring Crime in the USA from 2001-2019", style={"text-align": "center"}),

                       dcc.Dropdown(id="select_city",
                                    options=df_main["City"].unique(),
                                    # the options line should be options=[{"label": city, "Value": city} for city in
                                    # list(df_main["City"].unique()] but it does not seem to work as intended.
                                    # Update: I got  the dict generation syntax from stackoverflow but I realize
                                    # it is probably unnecessary to turn my list into a dictionary in the first place
                                    # since label and value will always have the same string anyway. Therefore
                                    # a list of strings is enough.
                                    multi=True,
                                    value=[""]),
                       dcc.Dropdown(id="select_cat",
                                    options=[
                                        {"label": "Crime rate/100k population", "value": "Per_100k_Pop"},
                                        {"label": "Number of crime", "value": "Original_Value"}],
                                    multi=False,
                                    value="Per_100k_Pop"
                                    ),
                       dcc.RangeSlider(2001, 2019, 1, count=1,
                                       marks={2001: "2001",
                                              2002: "2002",
                                              2003: "2003",
                                              2004: "2004",
                                              2005: "2005",
                                              2006: "2006",
                                              2007: "2007",
                                              2008: "2008",
                                              2009: "2009",
                                              2010: "2010",
                                              2011: "2011",
                                              2012: "2012",
                                              2013: "2013",
                                              2014: "2014",
                                              2015: "2015",
                                              2016: "2016",
                                              2017: "2017",
                                              2018: "2018",
                                              2019: "2019"},
                                       value=[2001, 2019], id="select_year"),

                       html.Div(
                           [
                               dbc.Row(
                                   dbc.Stack(
                                       [
                                           dbc.Col(html.Div(dcc.Graph(id="g1", figure={}))),
                                           dbc.Col(html.Div(dcc.Graph(id="g2", figure={}))),
                                           dbc.Col(html.Div(dcc.Graph(id="g3", figure={})))
                                       ],
                                       direction="horizontal"
                                   ),
                                   align="start"
                               ),
                               dbc.Row(
                                   dbc.Stack(
                                       [
                                           dbc.Col(html.Div(id="text-output-left",
                                                            style={'whiteSpace': 'pre-line'},
                                                            children=[])),
                                           dbc.Col(html.Div(id="text-output-right",
                                                            style={'whiteSpace': 'pre-line'},
                                                            children=[])),
                                           dbc.Col(html.Div([
                                               dbc.Row(html.Div(dcc.Graph(id="g4", figure={}, style={"width": "33%"}))),
                                               dbc.Row(html.Div(dcc.Graph(id="g5", figure={}, style={"width": "33%"})))
                                           ]
                                           )),
                                       ],
                                       direction="horizontal"
                                   ),
                                   align="center"
                               )

                           ]
                       )
                       ])


# ---------------------------------------------------------------------------------------
# Connect Plotly graphs with Dash Components

@app.callback(
    Output(component_id="g1", component_property="figure"),
    Output(component_id="g2", component_property="figure"),
    Output(component_id="g3", component_property="figure"),
    Output(component_id="g4", component_property="figure"),
    Output(component_id="g5", component_property="figure"),
    Input(component_id="select_city", component_property="value"),
    Input(component_id="select_cat", component_property="value"),
    Input(component_id="select_year", component_property="value"),

)
def generate_graphs(cities, cat, years):
    scatter_df = df_main[(df_main["Year"] >= years[0]) & (df_main["Year"] <= years[1])].reset_index()
    scatter_df.replace(-1000, np.NaN, inplace=True)
    scatter_df = scatter_df.groupby(by=["City", "State"]).mean().reset_index()

    if type(cities) == str:
        cities = [cities]

    vio = "Violent_crime"
    prop = "Property_crime"

    if cat == "Original_Value":
        vio = "Violent_crime"
        prop = "Property_crime"
    elif cat == "Per_100k_Pop":
        vio = "Violent_crime_per_100k"
        prop = "Property_crime_per_100k"

    px.defaults.template = "plotly_dark"

    fig1 = px.scatter(scatter_df.drop(scatter_df[scatter_df["City"].isin(cities)].index, axis=0),
                      "Population",
                      vio,
                      hover_name="City",
                      color_discrete_sequence=["lightsteelblue"],
                      opacity=0.5,
                      width=600,
                      height=400)

    fig1.add_traces(px.scatter(scatter_df[scatter_df["City"].isin(cities)],
                               "Population",
                               vio,
                               hover_name="City").update_traces(marker_size=15, marker_color="orangered",
                                                                marker_symbol="triangle-up").data)

    fig2 = px.scatter(scatter_df.drop(scatter_df[scatter_df["City"].isin(cities)].index, axis=0),
                      "Population",
                      prop,
                      hover_name="City",
                      color_discrete_sequence=["lightsteelblue"],
                      opacity=0.5,
                      width=600,
                      height=400)

    fig2.add_traces(px.scatter(scatter_df[scatter_df["City"].isin(cities)],
                               "Population",
                               prop,
                               hover_name="City").update_traces(marker_size=15, marker_color="orangered",
                                                                marker_symbol="triangle-up").data)

    fig3 = px.bar(scatter_df[scatter_df["City"].isin(cities)],
                  "City",
                  [prop, vio],
                  width=600,
                  height=400)

    line_df = df_main[df_main["City"].isin(cities)].reset_index().drop("index", axis=1)

    fig4 = px.line(line_df,
                   "Year",
                   vio,
                   color="City",
                   markers=True,
                   width=600,
                   height=400)

    fig5 = px.line(line_df,
                   "Year",
                   prop,
                   color="City",
                   markers=True,
                   width=600,
                   height=400)

    return fig1, fig2, fig3, fig4, fig5


@app.callback(
    Output(component_id="text-output-left", component_property="children"),
    Output(component_id="text-output-right", component_property="children"),
    Input(component_id="select_cat", component_property="value"),
    Input(component_id="select_year", component_property="value"),
    Input(component_id="g1", component_property="clickData"),
    Input(component_id="g2", component_property="clickData"),
    Input(component_id="g3", component_property="clickData"),
    # Input(component_id="g4", component_property="clickData"),
    # Input(component_id="g5", component_property="clickData")
)
def generate_text(cat, years, clickData1, clickData2, clickData3):
    cur_city = "New York, NY"
    reference = {"g1": clickData1, "g2": clickData2, "g3": clickData3}
    for i in reference:
        if ctx.triggered_id == i:
            cur_city = list(reference[i]["points"][0].values())[5]


    if cat == "Original_Value":
        vio = "Violent_crime"
        prop = "Property_crime"
        vio_text = "violent crimes"
        prop_text = "property crimes"
    elif cat == "Per_100k_Pop":
        vio = "Violent_crime_per_100k"
        prop = "Property_crime_per_100k"
        vio_text = "violent crime rate"
        prop_text = "property crime rate"

    cur_df = df_main[(df_main["Year"] >= years[0]) & (df_main["Year"] <= years[1])].reset_index()
    cur_df.replace(-1000, np.NaN, inplace=True)
    cur_df = cur_df.groupby(by=["City", "State"]).mean().reset_index()

    national = cur_df[["City", "State", "Population", "Violent_crime", "Property_crime", "Violent_crime_per_100k",
                       "Property_crime_per_100k"]]
    state_abbrv = abbrv[abbrv["Abbrv"] == cur_city[-2:]]
    state_abbrv.reset_index(inplace=True)

    state = state_abbrv.loc[0, "State"]
    state_wide = cur_df[cur_df["State"] == state][
        ["City", "State", "Population", "Violent_crime", "Property_crime", "Violent_crime_per_100k",
         "Property_crime_per_100k"]]

    natinoal_pop_sorted = national.sort_values("Population", ascending=False).reset_index().drop(
        "index", axis=1)
    nation_pop = natinoal_pop_sorted[natinoal_pop_sorted["City"] == cur_city].index[0] + 1
    national_vio_sorted = national.sort_values(vio, ascending=False).reset_index().drop(
        "index", axis=1)
    nation_vio = national_vio_sorted[national_vio_sorted["City"] == cur_city].index[0] + 1
    national_prop_sorted = national.sort_values(prop, ascending=False).reset_index().drop(
        "index", axis=1)
    nation_prop = national_prop_sorted[national_prop_sorted["City"] == cur_city].index[0] + 1

    state_pop_sorted = state_wide.sort_values("Population", ascending=False).reset_index().drop(
        "index", axis=1)
    state_pop = state_pop_sorted[state_pop_sorted["City"] == cur_city].index[0] + 1
    state_vio_sorted = state_wide.sort_values(vio, ascending=False).reset_index().drop(
        "index", axis=1)
    state_vio = state_vio_sorted[state_vio_sorted["City"] == cur_city].index[0] + 1
    state_prop_sorted = state_wide.sort_values(prop, ascending=False).reset_index().drop(
        "index", axis=1)
    state_prop = state_prop_sorted[state_prop_sorted["City"] == cur_city].index[0] + 1

    left = f"{cur_city} is......\n\n" \
           f"the #{nation_pop} largest city in the Country\n" \
           f"Ranked #{nation_vio} in national {vio_text}\n" \
           f"Ranked #{nation_prop} in national {prop_text}\n"

    right = f"\n\n" \
            f"the #{state_pop} largest city in {state}\n" \
            f"Ranked #{state_vio} for {vio_text} in {state}\n" \
            f"Ranked #{state_prop} for {prop_text} in {state}\n"

    return left, right


if __name__ == "__main__":
    app.run_server(debug=True)
