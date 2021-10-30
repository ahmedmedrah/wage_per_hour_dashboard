# Import 
import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input,Output
import numpy as np

# Load data
df = pd.read_csv('wph.csv')
df = df.drop(index = df[df.wage_per_hour == 44.5].index)
df.female = df.female.map({0:'male',1:'female'})
df = df.rename(columns={'female':'gender'})

# Predictions
default_values = {
    'union' : 0,
    'gender' : 0,
    'manufacturing': 0,
    'construction': 0
}

# Graph
# education_wage = px.scatter(
#     data_frame=df, x='education_yrs', y='wage_per_hour', title='Education vs Wage per hour') 
#     # color='education_yrs', color_continuous_scale='bluered')

# age_wage = px.scatter(
#     data_frame=df, x='age', y='wage_per_hour', title='Age vs Wage per hour')
#     # color='age', color_continuous_scale='bluered')

# exp_wage = px.scatter(
#     data_frame=df, x='experience_yrs', y='wage_per_hour', title='Experience years vs Wage per hour')
#     # color='experience_yrs', color_continuous_scale='bluered')

# gender_box = px.box(data_frame=df, x='gender', y='wage_per_hour', title='Gender vs Wage per hour',
#             color_discrete_map={'male':'#3295a8','female':'#cf6975'},color='gender')

# Layout HTML/Dash
app = dash.Dash()
app.layout = html.Div(children=[
    html.Div(children=[
        dcc.Dropdown(
            id='gender_dd',
            options=[{'label':c, 'value':c} for c in df.gender.unique()],
            style={'width':'200px', 'display':'inline-block','margin':'10px'}
        ),
        dcc.Dropdown(
            id='construction_dd',
            options=[{'label':c,'value':c} for c in df.construction.unique()],
            style={'width':'200px', 'display':'inline-block','margin':'10px'}
        ),
        dcc.Dropdown(
            id='union_dd',
            options=[{'label':c,'value':c} for c in df.union.unique()],
            style={'width':'200px', 'display':'inline-block','margin':'10px'}
        ),
        dcc.Dropdown(
            id='manufacturing_dd',
            options=[{'label':c,'value':c} for c in df.manufacturing.unique()],
            style={'width':'200px', 'display':'inline-block','margin':'10px'}
        )
    ]),    
    html.Div(children=[
        dcc.Graph(id='education_plot', style={'display':'inline-block'}), 
        dcc.Graph(id='age_plot', style={'display':'inline-block'})
    ]), 
    html.Div(children=[
        dcc.Graph(id='exp_plot', style={'display':'inline-block'}),
        dcc.Graph(id='gender_box',  style={'display':'inline-block'})
    ])
])

# Useful placeholders and functions to reduce typing
callback_inputs =  [
    Input(component_id='gender_dd', component_property='value'),
    Input(component_id='construction_dd', component_property='value'),
    Input(component_id='union_dd', component_property='value'),
    Input(component_id='manufacturing_dd', component_property='value')]

def return_df_copy(gender, construction, union, manufacturing):
    df_copy = df.copy(deep=True)
    df_copy['mask'] = (
        (df_copy['gender'] == gender) & 
        (df_copy['construction'] == construction) &
        (df_copy['union'] == union) &
        (df_copy['manufacturing'] == manufacturing))
    df_copy['color'] = np.where(df_copy['mask'] == True, 'blue', 'red')
    return df_copy

# Callbacks
@app.callback(
    Output(component_id='education_plot', component_property='figure'),
    callback_inputs)

def update_edu_plot(gender, construction, union, manufacturing):
    df_copy = return_df_copy(gender, construction, union, manufacturing)
    education_wage = px.scatter(data_frame=df_copy, x='education_yrs', y='wage_per_hour', title='Education vs Wage per hour', color=df_copy.color.values.tolist()) 
    return education_wage

@app.callback(
    Output(component_id='age_plot', component_property='figure'),
    callback_inputs)

def update_age_plot(gender, construction, union, manufacturing):
    df_copy = return_df_copy(gender, construction, union, manufacturing)
    age_wage = px.scatter(data_frame=df_copy, x='age', y='wage_per_hour', title='Age vs Wage per hour', color=df_copy.color.values.tolist())
    return age_wage

@app.callback(
        Output(component_id='exp_plot', component_property='figure'),
        callback_inputs
)

def update_exp_plot(gender, construction, union, manufacturing):
    df_copy = return_df_copy(gender, construction, union, manufacturing)
    exp_wage = px.scatter(data_frame=df_copy, x='experience_yrs', y='wage_per_hour', title='Experience years vs Wage per hour', color=df_copy.color.values.tolist())
    return exp_wage

@app.callback(
        Output(component_id='gender_box', component_property='figure'),
        callback_inputs
)

def update_gender_box(gender, construction, union, manufacturing):
    df_copy = return_df_copy(gender, construction, union, manufacturing)
    gender_box = px.box(data_frame=df_copy[df_copy['mask'] == True], x='gender', y='wage_per_hour', title='Gender vs Wage per hour',
            color_discrete_map={'male':'#3295a8','female':'#cf6975'}, color='gender')

    return  gender_box

if __name__ == '__main__':
    app.run_server(debug=True)