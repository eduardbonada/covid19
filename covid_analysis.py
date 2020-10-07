"""
Script that analyzes Greece & Catalunya COVID data

@author: Eduard Bonada
Copyright 2020
"""

# TODO: Update plot_daily_values to accept subplots
# TODO: Create plot with daily confirmed on top and daily deaths below
# TODO: Read deaths data cat-comarques
# TODO: Compute deaths vs confirmed
# TODO: Design dashboard
# TODO: Implement missing plots
# TODO: Create Dashboard
# TODO: Recreate periferies from nomoi?
# TODO: Plot ia14-rho7: how to smooth the plot? rolling average? one point per week?
# TODO: Plot ia14-rho7: add date to hover box
# TODO: Plot ia14-rho7: add background colors
# TODO: Change perfieries names? Add perfieries names in english?
# TODO: Keep data in Covid19 class object
# TODO: Compute and plot deathly_rate comparing deaths and confirmed cases
# TODO: Implement other plots (log cumul cases, etc, ...)
# TODO: Add spanish ccaa data
# TODO: Add world data

import Covid19
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


# Config script
start_date = '2020-08-01 00:00:00'
end_date = '2020-12-31 00:00:00'

# create covid manager object
cov19 = Covid19.Covid19Manager()

# read greece periferies data
#gre_periferies_confirmed = cov19.get_greece_periferies_confirmed()
#gre_periferies_pop = cov19.get_greece_periferies_population()
#gre_periferies_confirmed = gre_periferies_data.merge(gre_periferies_pop, how='left', on='Area')

# read greece nomoi data
gre_nomoi_pop = cov19.get_greece_nomoi_population()
gre_nomoi_confirmed = cov19.get_greece_nomoi_confirmed().merge(gre_nomoi_pop, how='left', on='Area')
gre_nomoi_deaths = cov19.get_greece_nomoi_deaths().merge(gre_nomoi_pop, how='left', on='Area')
gre_data = gre_nomoi_confirmed.merge(gre_nomoi_deaths[['Area','Date','Deaths']], how='left', left_on=['Area','Date'], right_on = ['Area','Date'])
# gre_data = gre_periferies_data.append(gre_nomoi_data.drop(columns=['AreaParent', 'AreaParent2'])).reset_index(drop=True)

# read cat comarques data
cat_pop = cov19.get_catalunya_comarques_population()
cat_confirmed = cov19.get_catalunya_comarques_confirmed().merge(cat_pop, how='left', on='Area')
cat_data = cat_confirmed

# aggregate all confirmed data
data = gre_data.append(cat_data).reset_index(drop=True)

# compute additional measures
data['Confirmed_rollingmean'] = cov19.compute_rolling_mean(data=data,
                                                           value_column='Confirmed',
                                                           groupby_column='Area',
                                                           rolling_n=7)
data['Confirmed_rollingsum'] = cov19.compute_rolling_sum(data=data,
                                                        value_column='Confirmed',
                                                        groupby_column='Area',
                                                        rolling_n=14)
data['epg'] = cov19.compute_epg_v2(data=data,
                                   confirmed_column='Confirmed',
                                   area_column='Area')
data['Deaths_rollingmean'] = cov19.compute_rolling_mean(data=data,
                                                        value_column='Deaths',
                                                        groupby_column='Area',
                                                        rolling_n=7)

# select period
data = data[(data.Date >= start_date) & (data.Date <= end_date)].sort_values(['Area', 'Date']).reset_index(drop=True)

# select area
# gre-periferies: 'Ελλάδα' 'Περιφέρεια Ηπείρου' 'Περιφέρεια Κεντρικής Μακεδονίας'
# gre-nomoi: 'ΙΩΑΝΝΙΝΩΝ' 'ΘΕΣΠΡΩΤΙΑΣ' 'ΕΛΛΑΔΑ' 'ΑΧΑΪΑΣ' 'ΑΤΤΙΚΗΣ' 'ΘΕΣΣΑΛΟΝΙΚΗΣ'
area = 'ΘΕΣΣΑΛΟΝΙΚΗΣ'
area_data = data[data.Area == area].reset_index(drop=True)

# plots
plots_list = ['all_epgs_html']  # ['top_areas', 'daily_detailed', 'daily_confirmed', 'active_confirmed', 'epg', 'ia14_rho7', 'daily_deaths']


if 'all_epgs_html' in plots_list:
    with open('epgs.html', 'w') as f:
        for area in ['ΕΛΛΑΔΑ', 'ΙΩΑΝΝΙΝΩΝ', 'ΘΕΣΠΡΩΤΙΑΣ', 'ΑΤΤΙΚΗΣ', 'ΘΕΣΣΑΛΟΝΙΚΗΣ']:
            area_data_tmp = data[data.Area == area].reset_index(drop=True)
            fig = cov19.plot_epg(mode='object', data=area_data_tmp, title='{}'.format(area), column_date='Date')
            f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))

if 'daily_detailed' in plots_list:
    plots = [
        {'type': 'bar', 'column_value': 'Confirmed', 'name_value': 'Confirmed', 'color_value': 'lightgray'},
        {'type': 'line', 'column_value': 'rho', 'name_value': 'rho', 'color_value': 'yellowgreen', 'secondary_y': True},
        {'type': 'line', 'column_value': 'rho_7', 'name_value': 'rho_7', 'color_value': 'mediumseagreen', 'secondary_y': True},
        {'type': 'line', 'column_value': 'ia_14', 'name_value': 'ia_14', 'color_value': 'gold'},
        {'type': 'line', 'column_value': 'epg', 'name_value': 'epg', 'color_value': 'maroon'}
    ]
    cov19.plot_daily_values(mode='show', data=area_data, title='Daily Details {}'.format(area), column_date='Date', plots=plots)

if 'daily_confirmed' in plots_list:
    plots = [
        {'type': 'bar', 'column_value': 'Confirmed', 'name_value': 'Confirmed', 'color_value': 'lightskyblue'},
        {'type': 'line', 'column_value': 'Confirmed_rollingmean', 'name_value': 'Mean 7 days', 'color_value': 'royalblue'}
    ]
    cov19.plot_daily_values(mode='show', data=area_data, title='Daily Confirmed {}'.format(area), column_date='Date', plots=plots)

if 'daily_deaths' in plots_list:
    plots = [
        {'type': 'bar', 'column_value': 'Deaths', 'name_value': 'Deaths', 'color_value': 'lightcoral'},
        {'type': 'line', 'column_value': 'Deaths_rollingmean', 'name_value': 'Mean 7 days', 'color_value': 'crimson'}
    ]
    cov19.plot_daily_values(mode='show', data=area_data, title='Daily Deaths {}'.format(area), column_date='Date', plots=plots)

if 'active_confirmed' in plots_list:
    plots = [{'type': 'line', 'column_value': 'Confirmed_rollingsum', 'name_value': 'Sum {} days'.format(14), 'color_value': 'royalblue'}]
    cov19.plot_daily_values(mode='show', data=area_data, title='Active Confirmed {}'.format(area), column_date='Date', plots=plots)

if 'epg' in plots_list:
    cov19.plot_epg(mode='show', data=area_data, title='Effective Potential Growth (EPG) {}'.format(area), column_date='Date')

if 'ia14_rho7' in plots_list:
    cov19.plot_ia14_rho(mode='show', data=area_data, title='IA_14 vs RHO_7 {}'.format(area))

if 'top_areas' in plots_list:
    group = 'cat-comarques'
    last_n_days = 30

    # select group & last n days
    country_area = 'Ελλάδα' if group[:3] == 'gre' else ('Catalunya' if group[:3] == 'cat' else '?')
    df = data[(data.Group == group) & (data.Date >= (datetime.today() - timedelta(days=last_n_days))) & (data.Area != country_area)]

    # compute aggregated data per area (total_confirmed, total_confirmed_100k)
    df_areas = df.groupby(['Area', 'Population', 'Date']).Confirmed.agg('sum').reset_index()
    df_areas['Confirmed_100k'] = df_areas.Confirmed / (df_areas.Population/100000)

    # select top-n areas
    # select daily data from top-n areas from last n days

    # plot stacked bars
    px.bar(df_areas, x='Date', y='Confirmed_100k', color='Area', barmode='stack').show()


exit()