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
df.female = df.female.map({0:'Male', 1:'Female'})
df['union'] = df['union'].map({0:'Not in union', 1:'In union'})
df = df.rename(columns={'female':'gender'})
a = []
for i in df[['manufacturing','construction']].values:
    if i[0] == 1:
        a.append('manufacturing')
    elif i[1] == 1:
        a.append('construction')
    else:
        a.append('other')
df['field'] = a

big_number_style = {'display': 'inline-block', 'padding':'10px 5px 5px 15px', "margin":'0px 100px'}

# Layout HTML/Dash
app = dash.Dash(external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.layout = html.Div(children=[
    html.Div(children=[
        html.H1('Exploring Wage per Hour Dataset',className='container'),
        html.Div(children=[
            html.Div([
                html.H3('Average Wage/hour'),
                html.H3(f'{round(df["wage_per_hour"].mean(), 2)} USD')], 
                style={'display':'inline-block'},
                className='four.columns'
                ),
            html.Div([
                html.H3('Average male wage/hour', style=big_number_style),
                html.H3(f'{round(df[df.gender == "Male"]["wage_per_hour"].mean(), 2)} USD')],  
                style={'display':'inline-block'},
                className='four.columns'
                ),
            html.Div([
                html.H3('Average female wage/hour', style=big_number_style),
                html.H3(f'{round(df[df.gender == "Female"]["wage_per_hour"].mean(), 2)} USD')], 
                style={'display':'inline-block'},
                className='four.columns'
                )
            ], style={'background-color':'#b4c3db', 'padding':'25px',},className='twelve.columns'),
        dcc.Dropdown(
            id='gender_dd',
            options=[{'label':'Male', 'value':'Male'}, {'label':'Female', 'value':'Female'}, {'label':'Both', 'value':'Both'}],
            style={'width':'200px', 'display':'inline-block','margin':'10px'},
            placeholder='Pick gender',
        ),
        dcc.Dropdown(
            id='field_dd',
            options=[{'label':c,'value':c} for c in df.field.unique()],
            style={'width':'200px', 'display':'inline-block','margin':'10px'},
            placeholder='Pick field of work',
        ),
        dcc.Dropdown(
            id='union_dd',
            options=[{'label':c,'value':c} for c in df.union.unique()],
            style={'width':'200px', 'display':'inline-block','margin':'10px'},
            placeholder='In union?',
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
],style={'textAlign':'center'})

# Useful placeholders and functions to reduce typing
callback_inputs =  [
    Input(component_id='gender_dd', component_property='value'),
    Input(component_id='field_dd', component_property='value'),
    Input(component_id='union_dd', component_property='value')]

def return_df_copy(gender, field, union):
    df_copy = df.copy(deep=True)
    if gender == 'both':
        df_copy['mask'] = (
            (df_copy['field'] == field) &
            (df_copy['union'] == union))
    else:
        df_copy['mask'] = (
            (df_copy['gender'] == gender) & 
            (df_copy['field'] == field) &
            (df_copy['union'] == union))
    df_copy['color'] = np.where(df_copy['mask'] == True, 'blue', 'red')
    return df_copy

# Callbacks
@app.callback(
    Output(component_id='education_plot', component_property='figure'),
    callback_inputs)

def update_edu_plot(gender, field, union):
    df_copy = return_df_copy(gender, field, union)
    education_wage = px.box(data_frame=df_copy[df_copy['mask'] == True], x='education_yrs', y='wage_per_hour', title='Education vs Wage per hour') 
    return education_wage

@app.callback(
    Output(component_id='age_plot', component_property='figure'),
    callback_inputs)

def update_age_plot(gender, field, union):
    df_copy = return_df_copy(gender, field, union)
    age_wage = px.scatter(data_frame=df_copy, x='age', y='wage_per_hour', title='Age vs Wage per hour', color=df_copy.color.values.tolist())
    return age_wage

@app.callback(
        Output(component_id='exp_plot', component_property='figure'),
        callback_inputs
)

def update_exp_plot(gender, field, union):
    df_copy = return_df_copy(gender, field, union)
    exp_wage = px.scatter(data_frame=df_copy, x='experience_yrs', y='wage_per_hour', title='Experience years vs Wage per hour', color=df_copy.color.values.tolist())
    return exp_wage

@app.callback(
        Output(component_id='gender_box', component_property='figure'),
        Input(component_id='field_dd', component_property='value'),
        Input(component_id='union_dd', component_property='value')
)

def update_gender_box(field, union):
    df_copy = df.copy(deep=True)
    df_copy['mask'] = (
        (df_copy['field'] == field) &
        (df_copy['union'] == union))
    gender_box = px.box(data_frame=df_copy[df_copy['mask'] == True], x='gender', y='wage_per_hour', title='Gender vs Wage per hour',
            color_discrete_map={'male':'#3295a8','female':'#cf6975'}, color='gender')

    return  gender_box

if __name__ == '__main__':
    app.run_server(debug=True)