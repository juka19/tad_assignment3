import plotly.express as px
import pandas as pd

df = pd.read_csv("data\\data_28_11_sponsors.csv")
df['date'] = pd.to_datetime(df.date)

spons_df = pd.read_csv('data\\cosponsors_sponsors.csv')

grp_dat =(spons_df
 .groupby(['number', 'cosponsor_party'])
 .agg({'cosponsor_name': 'count'})
 .reset_index()
)
grp_dat['perc'] = grp_dat.groupby('number')['cosponsor_name'].apply(lambda x: x*100/x.sum())

test = grp_dat.merge(df, left_on='number', right_on='bill.number')
test = test[test['cosponsor_party'] == 'D'].groupby(['session', 'policy_area']).agg({'perc': 'mean'}).reset_index()

a = px.colors.qualitative.T10[2]
b = px.colors.qualitative.T10[-1]
c = px.colors.qualitative.T10[0]

fig = px.line_polar(
    test, 
    r='perc',
    theta='policy_area',
    color='session',
    line_close=True,
    color_discrete_sequence=[a,b,c],
    # color_discrete_sequence=px.colors.sequential.Plasma_r,
    template='plotly_dark',
    custom_data=['perc', 'policy_area', 'session']
              )

fig.update_layout(showlegend=False)
fig.update_layout(font_size=6, font_color='#000000')
fig.update_traces(hovertemplate='Session: %{customdata[2]} <br>Policy Area: %{customdata[1]} <br>Democratic Cosponsors: %{customdata[0]:.0%}')
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
fig.update_polars('rgba(0,0,0,0)')
fig.show()



