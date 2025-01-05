# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Ensure min_payload and max_payload are integers
min_payload = int(spacex_df['Payload Mass (kg)'].min())  # Cast to integer
max_payload = int(spacex_df['Payload Mass (kg)'].max())  # Cast to integer

# Create a Dash application
app = dash.Dash(__name__)

# Create the layout of the app
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Dropdown list for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',  # Define the ID of the dropdown
        options=[  # List of available options
            {'label': 'All Sites', 'value': 'ALL'},  # Option for all sites
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},  # Specific launch site 1
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},  # Specific launch site 2
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},  # Specific launch site 3
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'}  # Specific launch site 4
        ],
        value='ALL',  # Default value is 'ALL' meaning all sites selected by default
        placeholder="Select a Launch Site here",  # Placeholder text to guide the user
        searchable=True  # Allow users to search for a launch site by typing
    ),
    html.Br(),

    # TASK 2: Pie chart for showing total successful launches count for all sites
    dcc.Graph(id='success-pie-chart'),  # Pie chart component added to layout

    html.Br(),

    # TASK 3: Add a slider to select payload range (min and max values)
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=100,  # You can adjust this to make the slider more or less granular
        marks={i: f'{i}' for i in range(min_payload, max_payload + 1, 1000)},  # Mark at every 1000 kg interval
        value=[min_payload, max_payload]  # Default value range from min to max
    ),

    # TASK 4: Scatter chart for payload vs success
    dcc.Graph(id='success-payload-scatter-chart'),
])

# TASK 2: Callback function for Pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),  # Update the pie chart figure
    [Input('site-dropdown', 'value')]  # Input: the value selected from the site-dropdown
)
def update_pie_chart(selected_site):
    # If "ALL" sites are selected, show success vs failure for each site
    if selected_site == 'ALL':
        # Group by 'Launch Site' and calculate success rate
        site_data = spacex_df.groupby(['Launch Site', 'class']).size().unstack(fill_value=0)
        site_data['Success Percentage'] = site_data[1] / (site_data[0] + site_data[1]) * 100
        site_data = site_data.reset_index()

        # Create the pie chart
        fig = px.pie(site_data, 
                     names='Launch Site', 
                     values='Success Percentage', 
                     title='Success Percentage by Launch Site')
    else:
        # Filter data by the selected site
        site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        data = site_data.groupby('class')['class'].count().reset_index(name="count")
        
        # Create pie chart with success and failure counts
        fig = px.pie(data, names='class', values='count',
                     title=f'Success vs Failure for {selected_site}')

    return fig

# TASK 4: Callback function for Scatter plot (Payload vs Success)
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]  # Add the slider value as input
)
def update_scatter_chart(selected_site, payload_range):
    # Filter data by payload range
    filtered_data = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                              (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    # If a specific site is selected, filter further
    if selected_site != 'ALL':
        filtered_data = filtered_data[filtered_data['Launch Site'] == selected_site]
    
    # Create the scatter plot
    fig = px.scatter(filtered_data, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category', title=f'Payload vs Success for {selected_site if selected_site != "ALL" else "All Sites"}',
                     labels={'class': 'Launch Success (0=Fail, 1=Success)', 'Payload Mass (kg)': 'Payload Mass (kg)'},
                     color_continuous_scale='Viridis')

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server( debug=True)
