import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

'''
STEP 1: CREATE A DATASET FOR MY DASHBOARD
'''

url = 'https://en.wikipedia.org/wiki/List_of_FIFA_World_Cup_finals'
tables = pd.read_html(url)

# World Cup table
df = tables[3]

# Drop the 2026 World Cup
df = df[df['Year'] != 2026]

# Take only relevant columns
df = df[['Year', 'Winners', 'Runners-up']].copy()

# Normalise Germany name
df['Winners'] = df['Winners'].replace({"West Germany":'Germany'})
df['Runners-up'] = df['Runners-up'].replace({'West Germany':'Germany'})

# Convert to csv
# df.to_csv('df_cleaned.csv', index=False)

'''
STEP 2: CREATE DASHBOARD
'''

# Load cleaned data
# df = pd.read_csv('df_cleaned.csv')

# Clean df containing WC win totals for each country
win_totals = df.groupby('Winners').size().reset_index(name='Wins')
win_totals = win_totals.rename(columns={'Winners':'Country'})

# Load ISO codes for the choropleth maps
iso = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')
iso = iso.rename(columns={'COUNTRY':'Country', 'CODE':'ISO'})

# Merge WC data with the ISO codes for choropleth map 
merged = pd.merge(iso, win_totals, on='Country', how='left')
merged['Wins'] = merged['Wins'].fillna(0)

# Create choropleth map
fig = px.choropleth(
    merged, 
    locations = 'ISO',
    color = 'Wins',
    hover_name = 'Country',
    hover_data = {'Wins':True, 'ISO':False},
    color_continuous_scale = 'YlOrBr',
    range_color = (0, merged['Wins'].max())
)

# Style the map layout
fig.update_layout(
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    dragmode=False,
    geo=dict(
        projection_type='natural earth',
        showcountries=True,
        showframe=False,
        showcoastlines=True,
        fitbounds='locations'
    ),
    coloraxis_colorbar=dict(
        title=dict(text='# of Wins', font=dict(size=24)),
        tickfont=dict(size=16)
    )
)

# Create dashboard
app = dash.Dash(__name__)

server=app.server

# Dashboard layout
app.layout = html.Div(
    style={
        'padding':'30px',
        'fontFamily':'Arial, sans-serif',
        'textAlign':'center',
        'backgroundColor':'#f9f9f9'
    }, 
    children=[
        # Title and subheader
        html.H1('FIFA World Cup Wins by Country', style={'marginBottom':'20px', 'fontSize':'40px'}),
        html.P('📌 Tip: Click on a country to see how many times it has won the World Cup.',
               style={'fontSize': '22px', 'color': '#555', 'marginBottom': '20px'}),

        # implement chorpleth into dashboard
        dcc.Graph(
            id='wc-map', 
            figure=fig,
            style={'height':'65vh', 'width':'100%'}
        ),
        # Create section for Part B and C
        html.Div(
            style={
                'height': '15vh',
                'marginTop': '30px',
                'marginBottom':'30px',
                'padding': '25px',
                'borderRadius': '10px',
                'backgroundColor': 'white',
                'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.1)',
                'maxWidth': '50%',
                'marginLeft': 'auto',
                'marginRight': 'auto',
                'overflowY':'auto'
            },
            children=[
                # Output for country click (part b)
                html.Div(id='click-output', style={'fontSize': '28px', 'marginBottom': '35px', 'fontWeight':'500'}),

                # Year input (part c)
                html.Label('Enter a World Cup Year:', style={'fontSize': '40px'}),

                # Input box
                dcc.Input(
                    id='year-input',
                    type='number',
                    placeholder='e.g. 2014',
                    debounce=True,
                    style={
                        'marginTop': '10px',
                        'fontSize': '20px',
                        'padding': '20px 14px',
                        'borderRadius': '6px',
                        'border': '1px solid #ccc',
                        'width': '180px',
                        'appearance': 'none',
                        'MozAppearance': 'textfield'
                    }
                ),

                # Error and output messages for year search
                html.Div(id='year-error', style={'color': 'red', 'marginTop': '10px', 'fontSize': '18px'}),
                html.Div(id='year-winner', style={'marginTop': '20px', 'fontSize': '40px'}),
                html.Div(id='year-runner-up', style={'fontSize': '40px'})
            ]
        )
    ]
)

# Callback for country click (part b)
@app.callback(
    Output('click-output', 'children'),
    Input('wc-map', 'clickData')
)

def display_win_count(clickData):
    if clickData is None:
        return ''
    
    country = clickData['points'][0]['hovertext']
    wins = merged.loc[merged['Country'] == country, 'Wins'].values[0]
    return f'{country} has won the World Cup {int(wins)} time(s)'

# Callback for year input (part c)
@app.callback(
    Output('year-error', 'children'),
    Output('year-winner', 'children'),
    Output('year-runner-up', 'children'),
    Input('year-input', 'value')
)

def show_final_result(year):
    if year is None:
        return '', '', ''
    if year not in df['Year'].values:
        return 'Invalid WC year', '', ''
    row = df[df['Year'] == year].iloc[0]
    winner = row['Winners']
    runnerup = row['Runners-up']
    return '', f'World Cup Winner in {year}: {winner}', f'Runner up in {year}: {runnerup}'

# Run
if __name__ == '__main__':
    app.run(debug=True)