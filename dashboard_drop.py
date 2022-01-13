import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)





app = Dash(__name__)


df = pd.read_csv("D:/My Tableau Repository/Datasources/google_reviews_ca_filterless.csv")

cols=['score','thumbsupcount','reviewcreatedversion','at']
df=df[cols]

df = df.groupby(['at'])[['score','thumbsupcount']].mean()
df.reset_index(inplace=True)

df['at']= pd.to_datetime(df['at'], format='%y-%m-%d', errors='ignore')


df['year']=df['at'].str.split('-').str[0].astype(int)
print(df[:5])






app.layout = html.Div([

    html.H1("Google Play Store Dashboard Application: Drop", style={'text-align': 'center'}),

    dcc.Dropdown(id="slct_year",
                 options=[
                     {"label": "2021", "value": 2021},
                     {"label": "2020", "value": 2020},
                     {"label": "2019", "value": 2019},
                     {"label": "2018", "value": 2018}],
                 value=2021,
                 clearable=False,
                 style={'width': "40%"}
                 
                 ),

    dcc.Dropdown(id="slct_data",
                 options=[
                     {"label": "Score", "value": 'score'},
                     {"label": "Thumbs Up", "value": 'thumbsupcount'}],
                 value='score',
                 clearable=False,
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='graph1', figure={})

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='graph1', component_property='figure')],
    [Input(component_id='slct_year', component_property='value'),
     Input(component_id='slct_data', component_property='value'),
    ],
)
def update_graph(option_slctd,option_slctd2):
    print(option_slctd,option_slctd2)
    print(type(option_slctd),type(option_slctd2))

    #### dunno why "container" variable outputs to the dashboard, or how that works???
    container=''
    #container = "The year chosen by user was: {}\n Visualizing: {}".format(option_slctd,option_slctd2)
    
    
    dff = df.copy()
    dff = dff[dff["year"] == option_slctd]
    #dff = dff[dff["Affected by"] == "Varroa_mites"]
    Y=option_slctd2
    # Plotly Express
    fig = px.scatter(
        data_frame=dff,
        x='at',
        y=Y,
    )
    

    return container, fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)