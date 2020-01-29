import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash_table

import numpy
from datetime import datetime as dt
import calendar

import re

from dateutil import parser

#from preprocessing import load_data
import preprocessing
#from 

df= preprocessing.load_data()

app= dash.Dash()
server= app.server

app.layout= html.Div([
    
    html.Div(
        html.H1('Umuzi Department Applications',
        style={
        'textAlign':'center',
        'color':'red'
        }
        ), 
    ),


    html.Label('Choose a Department:'),
    dcc.Dropdown(
        id='Department-Dropdown',
        options= [
            {'label': 'Data Science', 'value':'Data Science'},
            {'label': 'Web Development', 'value': 'Web Development'},
            {'label': 'Strategy', 'value': 'Strategy'},
            {'label': 'Copywriting', 'value': 'Copywriting'},
            {'label': 'UX/UI Design', 'value': 'UX/UI Design'},
            {'label': 'Multimedia', 'value': 'Multimedia'},

        ],
        value=['Data Science',],
        multi=True
    ),

    html.Br(),
    
    html.Label('Date Range:'),
    html.Br(),
    html.Br(),
    dcc.DatePickerRange(
        id='my-date-picker',
        start_date= df.index.min(),
        end_date = df.index.max()
    ),

    html.Br(),
    html.Br(),
    html.Div([
        html.Div(html.Img(src=app.get_asset_url('applicant.png'),
         style={'height':'100px', 'widhth':'200px'})),

        html.H2(
            id='total-applicants'
        ),

        dcc.Graph(
        id='Time-Graph'
    ),    

    html.Br(),

    html.Div(
        id='output-text'
    )


    ], style={'width':'50%', 'float':'left', 'display':'inline-block'} )   
,
    html.Div([
        html.Div(html.Img(src=app.get_asset_url('qualified.png'), style={'height':'100px', 'widhth':'200px'})),

        html.H2(
            id='qualified-output'
        ),
        dcc.Graph(
            id='bar-chart'
        )

    ], style={'width':'50%', 'float':'right', 'display':'inline-block'}),
    html.Div(
        id='applicants-table'
    ),
    html.Div([
    dash_table.DataTable(
        id='datatable',
        columns=[{"name": i, "id": i, 'deletable': True} for i in df[['Name', 'Surname', 'department']].columns], 
        data=df.to_dict('records'),
        editable=True,
        filter_action= 'native',
        #n_fixed_columns=2,
        style_table={'maxWidth': '1500px'},
        row_selectable="multi",
        selected_rows=[0],
        style_cell = {"fontFamily": "Arial", "size": 10, 'textAlign': 'left'}
        )
    ])

#end of main container
])

#populate dash table
@app.callback(Output(component_id='datatable', component_property='data'),
[Input('Department-Dropdown', 'value')])
def update_dash_table(departments):
    USEFUL_COLS= ['department', 'Email Address', 'Cellphone number', 'Name', 'Surname']
    #qualified
    #df_table= df[df.math_course=='Mathematics']
    #of selected departments
    df_table= df[( df.department.isin(departments) )]
    df_table= df_table[USEFUL_COLS]
    
    #df_table= df_table[(df_table.index>start_date) & (df_table.index<end_date)]

    return df_table.to_dict('records')
    



#populate the table
@app.callback(Output('applicants-table', 'children'),
[Input('Department-Dropdown', 'value'),
Input(component_id='my-date-picker', component_property='start_date'),
Input(component_id='my-date-picker', component_property='end_date')])
def update_table(departments, start_date, end_date, max_rows=10):

    #parse the dates as datetime objects instead of strings
    start_date= parser.isoparse(start_date)
    end_date= parser.isoparse(end_date)

    USEFUL_COLS= ['department', 'Email Address', 'Cellphone number', 'Name', 'Surname']
    #qualified
    df_table= df[df.math_course=='Mathematics']
    #of selected departments
    df_table= df_table[( df_table.department.isin(departments) )]
    df_table= df_table[USEFUL_COLS]
    
    df_table= df_table[(df_table.index>start_date) & (df_table.index<end_date)]

    
    

    return html.Table(
    #header
        [html.Tr([html.Th(col) for col in df_table.columns])]+
    #Body
    [html.Tr([
        html.Td(df_table.iloc[i][col]) for col in df_table.columns
    ]) for i in range(min(len(df), max_rows))],

    style={'border':'1px solid',
    'width': '100%'}
    )


    

@app.callback([Output('Time-Graph', 'figure'),
Output('total-applicants', 'children'),
Output('qualified-output', 'children')],
[Input('my-date-picker', 'start_date'),
Input(component_id='my-date-picker', component_property='end_date'), 
Input('Department-Dropdown', 'value')])
def update_graph(start_date, end_date, department):

    new_df= df.loc[start_date: end_date]

    #count how many in each department to get total applicants in respective departments
    total_applicants=0
    qualified_applicants=0
    for each in department:
        temp_df= new_df[new_df.department==each]
        qualified_applicants+= len(temp_df[temp_df.math_course=='Mathematics'])
        total_applicants+= len(temp_df)
        

    #group by month and department
    new_df= new_df.groupby(pd.Grouper(freq='m')).apply(lambda x: x.groupby('department').count())['Name']
    

    


    x= new_df.unstack().index
    """
    data=[]
    
    for each in department:
        y= new_df.loc[:, department]
        trace1= {
            'data': [go.Scatter(
                x= x,
                y= y,
                mode= 'lines'
            )],
            'layout': go.Layout(
                xaxis={'title':'date'},
                yaxis={'title': 'count'}
                )
            }

        """
    figure = {
            'data' : [
                go.Scatter(
                x = x,
                y = new_df.loc[:, dep],
                mode = "markers+lines",
                name = dep
                )for dep in department


            ],
            'layout' : go.Layout(
                title = "line department by month",
                xaxis = {'title': 'months'},
                yaxis = {'title': 'number of applicants'}

            )}    
        #data.append(trace1)
        
    return figure, f'{total_applicants} total applicants', f'{qualified_applicants} qualified applicants math '


@app.callback(Output('bar-chart', 'figure'),
[Input('my-date-picker', 'start_date'),
Input(component_id='my-date-picker', component_property='end_date'), 
Input('Department-Dropdown', 'value')])
def update_bar_chart(start_date, end_date, department):
    #qualified applicants
    new_df= df[df['math_course']=='Mathematics']

    #filter by date
    new_df= new_df.loc[start_date: end_date]
    #group monthly by department
    new_df= new_df.groupby(pd.Grouper(freq='m')).apply(lambda x: x.groupby('department').count())['Name']

    x_ticks= new_df.unstack().index


    figure = {
            'data' : [
                go.Bar(
                x = x_ticks,
                y = new_df.loc[:, dep],
                #df.loc[(df["B"] > 50) & (df["C"] == 900), "A"].values
                name = dep
                )for dep in department


            ],
            'layout' : go.Layout(
                title = "Qualified Applicants math",
                xaxis = {'title': 'months',
                'tickmode' : 'array',
        'tickvals': [x for x in x_ticks.month],
        'ticktext' :[calendar.month_abbr[x] for x in x_ticks.month]},
                yaxis = {'title': 'number of applicants'}

            )}    
        #data.append(trace1)
        
    return figure




if __name__ == "__main__":
    app.run_server(debug= True)
