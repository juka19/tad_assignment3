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

df_final = grp_dat.merge(df, left_on='number', right_on='bill.number')

df_final = df_final[df_final['cosponsor_party'] == 'D'].groupby(['session', 'policy_area']).agg({'perc': 'mean'}).reset_index()

a = px.colors.qualitative.T10[2]
b = px.colors.qualitative.T10[-1]
c = px.colors.qualitative.T10[0]

df_final.sort_values(by=['session', 'policy_area'], inplace=True)
df_final = df_final[df_final['policy_area'] != 'Housing and Community Development']
plot_df = df_final.round(1)
fig = px.line_polar(
    plot_df, 
    r='perc',
    theta='policy_area',
    color='session',
    line_close=True,
    color_discrete_sequence=[a,b,c],
    # color_discrete_sequence=px.colors.sequential.Plasma_r,
    template='plotly_dark'
              )

fig.update_layout(showlegend=False)
fig.update_layout(font_size=6)
fig.update_traces(hovertemplate='Policy Area: %{theta} <br>Democratic Cosponsors: %{r}')
# fig.update_layout(
#     paper_bgcolor='rgba(0,0,0,0)',
#     plot_bgcolor='rgba(0,0,0,0)'
# )
fig.show()


fig.to_plotly_json('')


