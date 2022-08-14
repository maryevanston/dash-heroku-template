import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
from dash import dcc # import dash_core_components as dcc
from dash import html # import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#%%capture
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = '''
The gap in pay between men and women has long been a topic of heated conversation in the United States. As early as 1944 a bill was introduced to amend the National Labor Relations Act [The Prohibiting Discrimination in Pay on Account of Sex Bill](https://catalog.archives.gov/id/4397822) but was not ratified . Congress finally passed the Equal Pay Act 20 years later in 1963 that prohibits sex-based wage discrimination between men and women in substatially the same job (https://www.eeoc.gov/statutes/equal-pay-act-1963). Since then, there have been many attempts to measure this wage gap to determine if it is shrinking or growing. 

The General Social Survey (GSS) is a United States national survey that collects data on trends in "opinions, attitudes and behavious" since 1972. (http://www.gss.norc.org/About-The-GSS) The data is collected with the aim of keeping the questions themselves and the collection design the same over time. They ask a core set of questions in every survey and also add special topical modules that are appropriate to the time. They make the data available to the public at the URL listed above. 
'''
gss_prob2_data = gss_clean[['income', 'job_prestige', 'socioeconomic_index', 'education', 'sex']]
gss_prob2_table = gss_prob2_data.groupby('sex').agg({'income':'mean', 'job_prestige':'mean',
                                                 'socioeconomic_index':'mean', 'education':'mean'})

gss_prob2_table = gss_prob2_table[['income', 'job_prestige','socioeconomic_index','education']]
gss_prob2_table = gss_prob2_table.rename({'income':'Annual Income',
                                   'job_prestige':'Occupational Prestige Score',
                                   'socioeconomic_index':'Socioeconomic Index Status',
                                   'education':'Years Formal Education'}, axis=1)
gss_prob2_table = round(gss_prob2_table, 2)
table = ff.create_table(gss_prob2_table)

gss_prob3_clean = gss_clean[['sex', 'male_breadwinner']]
gss_prob3_clean.dropna(inplace = True)

gss_prob3_data = gss_prob3_clean.groupby(['sex', 'male_breadwinner'], as_index=False).size()

fig3 = px.bar(gss_prob3_data, x='male_breadwinner', y='size', 
              category_orders={"male_breadwinner": ['strongly agree', 'agree', 'disagree', 'strongly disagree']},
             facet_col='sex',
             #hover_data = ['votes', 'Biden thermometer', 'Trump thermometer'],
            labels={'sex':'Sex of Respondent', 
                    'male_breadwinner':'Agrees Man is the achiever outside the home',
                    'size':'Number of Responses'})

gss_prob4_clean = gss_clean[['job_prestige', 'income', 'sex', 'education', 'socioeconomic_index']]
gss_prob4_clean.dropna(inplace = True)
gss_prob4_clean
#gss_prob4_clean.to_csv('gss_prob4_clean.csv', index=False)

fig4 = px.scatter(gss_prob4_clean, x='job_prestige', y='income', color='sex',
                 #height=600, width=600,
                 trendline='lowess',
                 labels={'job_prestige':'Occupational Prestige Score', 
                        'income':'Annual Income'},
                 hover_data=['education', 'socioeconomic_index'])

gss_prob5_clean = gss_clean[['job_prestige', 'income', 'sex']]
gss_prob5_clean.dropna(inplace = True)
gss_prob5_clean

fig5a = px.box(gss_prob5_clean, x='income', y = 'sex', color='sex',
                   labels={'income':'Annual Income', 'sex':''})
fig5a.update_layout(showlegend=False)


fig5b = px.box(gss_prob5_clean, x='job_prestige', y = 'sex', color='sex',
                   labels={'job_prestige':'Occupational Prestige Score', 
                        'income':'Annual Income', 'sex':''})
fig5b.update_layout(showlegend=False)

gss_prob6_clean = gss_clean[['job_prestige', 'income', 'sex']]

# create a new feature that breaks job_prestige into six categories with equally sized ranges
gss_prob6_clean['job_pres_bins'] = pd.cut(gss_prob6_clean.job_prestige, bins=6)

# Finally, drop all rows with any missing values in this dataframe.
gss_prob6_clean.dropna(inplace = True)

# Then create a facet grid with three rows and two columns in which each cell contains an interactive box plot comparing the 
# income distributions of men and women for each of these new categories.

# need to cast job_pres_bins from category to string in order to plot
gss_prob6_clean.job_pres_bins = gss_prob6_clean.job_pres_bins.astype('str')

fig6 = px.box(gss_prob6_clean, x='sex', y='income',
             color='sex',
             color_discrete_map = {'male':'blue', 'female':'red'},
             facet_col='job_pres_bins', 
             facet_col_wrap=2,
             category_orders={"job_pres_bins": ['(15.936, 26.667]', '(26.667, 37.333]', '(37.333, 48.0]', '(48.0, 58.667]', '(58.667, 69.333]', '(69.333, 80.0]']},
             labels={'job_pres_bins':'Job Prestige Range', 'sex':'', 'income':'Annual Income'},
             width=800, height=1000)

import dash
from jupyter_dash import JupyterDash # displays dashboards in jupyter notebooks
from dash import dcc  
# import dash_core_components as dcc
 # import dash_html_components as html
from dash import html #from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # all dashboards use css stylesheets


app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.H1("Exploring the 2019 General Social Survey"),    
        
        dcc.Markdown(children = markdown_text),
        
        html.H2("Mean of income, occupational prestige, socioeconomic index, and years of education for men and for women"),
        dcc.Graph(figure=table),
        
        html.H2("Count and resonse, by sex to if men should be the primary breadwinner in the family"),
        dcc.Graph(figure=fig3),
        
        html.H2("Job Prestige vs. Income by Sex"),
        dcc.Graph(figure=fig4),
        
        html.Div([ 
            
            html.H2("Distribution of income for men and for women"), # element 1
            
            dcc.Graph(figure=fig5a) # element 2
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H2("Distribution of job prestige for men and for women"),
            
            dcc.Graph(figure=fig5b)
            
        ], style = {'width':'48%', 'float':'right'}),
        
        html.H2("Income distributions of men and women by job prestige"),
        dcc.Graph(figure=fig6)

    ]
            
)

if __name__ == '__main__':
    app.run_server(debug=True, port=8061)
