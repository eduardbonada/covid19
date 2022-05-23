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
# TODO: Plot ia14-rho7: add markers to show where points are
# TODO: Plot ia14-rho7: how to smooth the plot? rolling average? one point per week?
# TODO: Plot ia14-rho7: add date to hover box
# TODO: Change perfieries names? Add perfieries names in english?
# TODO: Keep data in Covid19 class object
# TODO: Compute and plot deathly_rate comparing deaths and confirmed cases
# TODO: Implement other plots (log cumul cases, etc, ...)
# TODO: Add spanish ccaa data
# TODO: Add world data

import Covid19
from datetime import datetime, timedelta
import plotly.express as px
import yagmail

# Config script
run_in_local = True
# start_date = '2021-02-01 00:00:00'
# end_date = '2021-06-30 23:59:59'
end_date = datetime.today().strftime('%Y-%m-%d %H:%M')
start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M')

# create covid manager object
cov19 = Covid19.Covid19Manager(run_in_local)

# read greece periferies data
#gre_periferies_confirmed = cov19.get_greece_periferies_confirmed()
#gre_periferies_pop = cov19.get_greece_periferies_population()
#gre_periferies_confirmed = gre_periferies_data.merge(gre_periferies_pop, how='left', on='Area')

# read greece nomoi data
# gre_nomoi_pop = cov19.get_greece_nomoi_population()
# gre_nomoi_confirmed = cov19.get_greece_nomoi_confirmed().merge(gre_nomoi_pop, how='left', on='Area')
# gre_nomoi_deaths = cov19.get_greece_nomoi_deaths().merge(gre_nomoi_pop, how='left', on='Area')
# gre_data = gre_nomoi_confirmed.merge(gre_nomoi_deaths[['Area','Date','Deaths']], how='left', left_on=['Area','Date'], right_on = ['Area','Date'])
# # gre_data = gre_periferies_data.append(gre_nomoi_data.drop(columns=['AreaParent', 'AreaParent2'])).reset_index(drop=True)

# read cat comarques data
cat_pop = cov19.get_catalunya_comarques_population()
cat_confirmed = cov19.get_catalunya_comarques_confirmed().merge(cat_pop, how='left', on='Area')
cat_data = cat_confirmed

# aggregate all confirmed data
# data = gre_data#.append(cat_data).reset_index(drop=True)
data = cat_data

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
#data['Deaths_rollingmean'] = cov19.compute_rolling_mean(data=data,
#                                                        value_column='Deaths',
#                                                        groupby_column='Area',
#                                                        rolling_n=7)

# select period
data = data[(data.Date >= start_date) & (data.Date <= end_date)].sort_values(['Area', 'Date']).reset_index(drop=True)

# plots
# plots_list = ['bottom_n_html']
# plots_list = ['daily_confirmed', 'daily_deaths', 'active_confirmed', 'epg', 'ia14_rho7']
plots_list = ['daily_confirmed', 'ia14_rho7']

# select area
# gre-periferies: 'Ελλάδα' 'Περιφέρεια Ηπείρου' 'Περιφέρεια Κεντρικής Μακεδονίας'
# gre-nomoi: 'ΙΩΑΝΝΙΝΩΝ' 'ΘΕΣΠΡΩΤΙΑΣ' 'ΕΛΛΑΔΑ' 'ΑΧΑΪΑΣ' 'ΑΤΤΙΚΗΣ' 'ΘΕΣΣΑΛΟΝΙΚΗΣ'
area = 'BARCELONES'
area_data = data[data.Area == area].reset_index(drop=True)

email_body = ''

if 'bottom_n_html' in plots_list:

    # select bottom-n areas (greece)
    bottom_n = 0
    bottom_n_areas = ['ΕΛΛΑΔΑ', 'ΙΩΑΝΝΙΝΩΝ']
    bottom_n_areas.extend(data[(data.Group == 'gre-nomoi') & (data.Area != 'ΕΛΛΑΔΑ')][['Area', 'Date', 'epg']].groupby('Area').tail(1).sort_values('epg', ascending=False).head(bottom_n).Area.to_list())

    # select bottom-n areas (cat)
    #bottom_n_areas = data[(data.Group == 'cat-comarques') & (data.Area != 'Catalunya')][['Area', 'Date', 'epg']].groupby('Area').tail(1).sort_values('epg', ascending=False).head(10).Area.to_list()

    with open('epgs.html', 'w') as f:
        for a in bottom_n_areas:
            area_data_tmp = data[data.Area == a].reset_index(drop=True)
            #fig_epg = cov19.plot_epg(mode='object', data=area_data_tmp, title='{}'.format(a), column_date='Date')
            #f.write(fig_epg.to_html(full_html=False, include_plotlyjs='cdn'))
            fig_rho_ia14 = cov19.plot_ia14_rho(mode='object', data=area_data_tmp, title='{}'.format(a))
            f.write(fig_rho_ia14.to_html(full_html=False, include_plotlyjs='cdn'))

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
    # cov19.plot_daily_values(mode='show', data=area_data, title='Daily Confirmed {}'.format(area), column_date='Date', plots=plots)
    fig = cov19.plot_daily_values(mode='object', data=area_data, title='Daily Confirmed {}'.format(area), column_date='Date', plots=plots)
    fig.write_image('daily_confirmed.png' if run_in_local else '/home/ec2-user/covid/daily_confirmed.png')
    # email_body += fig.to_html(full_html=False, include_plotlyjs='cdn')
    # with open('plots.html', 'w') as f:
    #    f.write(fig.to_html(full_html=True, include_plotlyjs='cdn'))

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
    # cov19.plot_ia14_rho(mode='show', data=area_data, title='IA_14 vs RHO_7 {}'.format(area))
    fig = cov19.plot_ia14_rho(mode='object', data=area_data, title='IA_14 vs RHO_7 {}'.format(area))
    fig.write_image('ia14_rho7.png' if run_in_local else '/home/ec2-user/covid/ia14_rho7.png')

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

# send email
user = 'ebonadamapit@gmail.com'
app_password = 'mbovshitgkzhsopt'

with yagmail.SMTP(user, app_password) as yag:
    yag.send(to=['eduard.bonada@gmail.com'],
             subject='COVID UPDATE {}'.format(datetime.today().strftime('%Y-%m-%d')),
             contents=['daily_confirmed.png' if run_in_local else '/home/ec2-user/covid/daily_confirmed.png',
                       'ia14_rho7.png' if run_in_local else '/home/ec2-user/covid/ia14_rho7.png'])
    print('Email successfully sent')

exit()