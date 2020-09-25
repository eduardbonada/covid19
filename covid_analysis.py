"""
Script that analyzes Greece & Catalunya COVID data

@author: Eduard Bonada
Copyright 2020
"""

# TODO: List or plot with cases per region last days (bar plot with regions as colors? only top-N regions?)
# TODO: Plot ia14-rho7: add parameter to show only some values (1 of every N) to smooth the plot
# TODO: Plot ia14-rho7: add date to hover
# TODO: Plot ia14-rho7: add background colors
# TODO: Add perfieries names in english?
# TODO: Keep data in Covid19 class object
# TODO: Create Dashboard
# TODO: Read deaths data
# TODO: Implement other plots (log cumul cases, etc, ...)
# TODO: Add world data

import Covid19

# Config script
start_date = '2020-06-01 00:00:00'
end_date = '2020-12-31 00:00:00'
plots = ['daily_detailed'] # ['daily_detailed', 'daily_confirmed', 'active_confirmed', 'epg', 'ia14_rho7']

# create covid manager object
cov19 = Covid19.Covid19Manager()

# read greece data
gre_data = cov19.get_greece_confirmed(mode='periferies')
gre_pop = cov19.get_greece_population(mode='periferies')
gre_data = gre_data.merge(gre_pop, how='left', on='Area')

# read cat data
cat_data = cov19.get_catalunya_confirmed(mode='comarques')
cat_pop = cov19.get_catalunya_population(mode='comarques')
cat_data = cat_data.merge(cat_pop, how='left', on='Area')

# aggregate all data into single dataframe
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

# select period
data = data[(data.Date >= start_date) & (data.Date <= end_date)].sort_values(['Area','Date']).reset_index(drop=True)

# select area
area = 'Catalunya'  # 'Περιφέρεια Ηπείρου' 'Ελλάδα' 'Περιφέρεια Κεντρικής Μακεδονίας'
area_data = data[data.Area == area].reset_index(drop=True)

# plots
if 'daily_detailed' in plots:
    plots = [
        {'type': 'bar', 'column_value': 'Confirmed', 'name_value': 'Confirmed', 'color_value': 'lightgray'},
        {'type': 'line', 'column_value': 'rho', 'name_value': 'rho', 'color_value': 'yellowgreen', 'secondary_y': True},
        {'type': 'line', 'column_value': 'rho_7', 'name_value': 'rho_7', 'color_value': 'mediumseagreen', 'secondary_y': True},
        {'type': 'line', 'column_value': 'ia_14', 'name_value': 'ia_14', 'color_value': 'gold'},
        {'type': 'line', 'column_value': 'epg', 'name_value': 'epg', 'color_value': 'maroon'}
    ]
    cov19.plot_daily_values(mode='show', data=area_data, title='Daily Detailed Data {}'.format(area), column_date='Date', plots=plots)

if 'daily_confirmed' in plots:
    plots = [
        {'type': 'bar', 'column_value': 'Confirmed', 'name_value': 'Confirmed', 'color_value': 'lightskyblue'},
        {'type': 'line', 'column_value': 'Confirmed_rollingmean', 'name_value': 'Mean 7 days', 'color_value': 'royalblue'}
    ]
    cov19.plot_daily_values(mode='show', data=area_data, title='Daily Detailed Data {}'.format(area), column_date='Date', plots=plots)

if 'active_confirmed' in plots:
    plots = {'type': 'line', 'column_value': 'Confirmed_rollingsum', 'name_value': 'Sum {} days'.format(14), 'color_value': 'royalblue'}
    cov19.plot_daily_values(mode='show', data=area_data, title='Active Confirmed {}'.format(area), column_date='Date', plots=plots)

if 'epg' in plots:
    cov19.plot_epg(mode='show', data=area_data, title='Effective Potential Growth (EPG) {}'.format(area), column_date='Date')

if 'ia14_rho7' in plots:
    cov19.plot_ia14_rho(mode='show', data=area_data, title='IA_14 vs RHO_7 {}'.format(area))

exit()