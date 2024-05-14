# install requirements
# pip install pandas dash

# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
booster_list = spacex_df['Booster Version'].unique().tolist()



# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
launch_sites_df = spacex_df.groupby(['Launch Site'], as_index=False).first()
launch_sites_list = launch_sites_df['Launch Site'].tolist()

dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
dropdown_options.extend([ {'label': site_name, 'value': site_name} for site_name in launch_sites_df['Launch Site'].tolist() ])

app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=dropdown_options,
                                            value='All',
                                            placeholder='Select a Launch Site here',
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                marks={
                                                    0: '0',
                                                    2500: '2500',
                                                    5000: '5000',
                                                    7500: '7500',
                                                    10000: '10000'
                                                },
                                                value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # success by luanch site
        successes = [ spacex_df.where(spacex_df['Launch Site'] == site_name)['class'].sum() for site_name in launch_sites_list]
        fig = px.pie(values=successes, 
        names=launch_sites_list, 
        title='Launches Statistics')
        return fig
    else:
        # return the outcomes piechart for a selected site
        successes = spacex_df.where(spacex_df['Launch Site'] == entered_site).where(spacex_df['class'] == 1)['class'].count()
        fails = spacex_df.where(spacex_df['Launch Site'] == entered_site).where(spacex_df['class'] == 0)['class'].count()
        fig = px.pie(values=[successes, fails], names=['success', 'fail'], title=f'{entered_site} launches')
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [
                Input(component_id='site-dropdown', component_property='value'),
                Input(component_id='payload-slider', component_property='value')
              ]
              )
def get_scatter_chart(entered_site, payload):
    if entered_site == 'ALL':
        payloads = []
        classes = []
        boosters = []
        for idx, row in spacex_df.iterrows():
            payloads.append(row['Payload Mass (kg)'])
            classes.append(row['class'])
            boosters.append(row['Booster Version'])
        filtered_df = pd.DataFrame({'payload':payloads, 'class':classes, 'booster':boosters})
        filtered_df = filtered_df.where(filtered_df['payload'] > payload[0]).where(filtered_df['payload'] < payload[1])
        
        fig = px.scatter(filtered_df, x='payload', y='class', color='booster')
        return fig
    else:
        # return the outcomes piechart for a selected site
        site_df = pd.DataFrame(spacex_df.where(spacex_df['Launch Site'] == entered_site))

        payloads = []
        classes = []
        boosters = []
        for idx, row in site_df.iterrows():
            payloads.append(row['Payload Mass (kg)'])
            classes.append(row['class'])
            boosters.append(row['Booster Version'])
        filtered_df = pd.DataFrame({'payload':payloads, 'class':classes, 'booster':boosters})
        filtered_df = filtered_df.where(filtered_df['payload'] > payload[0]).where(filtered_df['payload'] < payload[1])
 
        fig = px.scatter(filtered_df, x='payload', y='class', color='booster')
        
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
