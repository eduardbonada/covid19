"""
Covid19 library with helper function definitions and implementations

@author: Eduard Bonada
Copyright 2020
"""

import pandas as pd
import os
from datetime import datetime, timedelta
import plotly
import plotly.graph_objects as go
import json

# TODO: List or plot with cases per region last days (bar plot with regions as colors? only top-N regions?)
# TODO: Compute epg and rolling of all areas together in the same dataframe
# TODO: Create plot ia14-rho7
# TODO: Add perfieries names in english?
# TODO: Keep data in Covid19 class object
# TODO: Create Dashboard
# TODO: Read deaths data
# TODO: Implement other plots (log cumul cases, etc, ...)
# TODO: Add world data

class Covid19Manager():
    """
    Object that contains actions and processes related to Covid19 data sources
    """

    def __init__(self):
        """
        Initialize
        """
        
        # self.test = test

    def get_catalunya_confirmed(self, mode, add_aggregate=True):
        """
        Read Catalunya data, aggregate it according to 'mode' and return a Dataframe with [Date, Area, Confirmed].
        If add_aggregate is True, the aggregation values at Catalunya level are added as new rows of the Dataframe
        """

        if mode == 'comarques':

            # check if today's file already exists
            today_filename = 'data/catalunya_confirmed_{}_v{}.csv'.format(mode, datetime.today().strftime('%Y%m%d'))
            if os.path.exists(today_filename):
                # read and return the file if it already exists
                data = pd.read_csv(today_filename, sep=',')
            else:
                # otherwise read and process from online source

                # read cases from catalunya data from api
                catdata_cases_raw = pd.read_csv('https://analisi.transparenciacatalunya.cat/api/views/jj6z-iyrp/rows.csv?accessType=DOWNLOAD&sorting=true/')

                # select and rename columns
                catdata_cases = catdata_cases_raw[['TipusCasData', 'ComarcaDescripcio', 'TipusCasDescripcio', 'NumCasos']]\
                                .rename(columns={'ComarcaDescripcio': 'Area', 'TipusCasDescripcio': 'Type', 'NumCasos': 'Confirmed'})

                # parse date correctly
                catdata_cases['Date'] = pd.to_datetime(catdata_cases.TipusCasData, format='%d/%m/%Y')
                catdata_cases = catdata_cases.drop(columns = ['TipusCasData'])

                # remove character '\xa0' from Areas
                catdata_cases['Area'] = catdata_cases.Area.str.replace('\xa0', '')

                print('Read data from Catalunya: {} registers from {} to {}'.format(len(catdata_cases), min(catdata_cases.Date), max(catdata_cases.Date)))

                # filter by type pf case: 'Epidemiològic', 'Positiu PCR', 'Positiu per ELISA', 'Positiu per Test Ràpid', 'Sospitós'
                types = ['Epidemiològic', 'Positiu PCR', 'Positiu per ELISA', 'Positiu per Test Ràpid']
                catdata_cases = catdata_cases[catdata_cases.Type.isin(types)].drop(columns='Type')
                print('Filtering by type: {} registers'.format(len(catdata_cases)))

                # aggregate areas
                catdata_cases_areas = catdata_cases.groupby(['Date', 'Area']).sum().reset_index()
                print('Aggregate by areas: {} confirmed cases from {} areas'.format(catdata_cases_areas.Confirmed.sum(), catdata_cases_areas.Area.nunique()))

                # add Catalunya as area
                if add_aggregate:
                    cat_cases = catdata_cases_areas.groupby('Date').agg({'Confirmed': 'sum'}).reset_index()
                    cat_cases['Area'] = 'Catalunya'
                    catdata_cases_areas = catdata_cases_areas.append(cat_cases).reset_index(drop=True)


                # adding days with 0 confirmed cases (https://stackoverflow.com/questions/14856941/insert-0-values-for-missing-dates-within-multiindex)
                df = catdata_cases_areas.copy()
                all_dates = [df.Date.min() + timedelta(days=x) for x in range((df.Date.max()-df.Date.min()).days + 1)]
                df.set_index(['Date', 'Area'], inplace=True)
                (date_index, area_index) = df.index.levels
                new_index = pd.MultiIndex.from_product([all_dates, area_index])
                new_df = df.reindex(new_index)
                new_df = new_df.fillna(0).astype(int)
                new_df = new_df.reset_index().rename(columns={'level_0': 'Date'})
                data = new_df.copy()

                # store result into csv
                data.to_csv(today_filename, sep=',', index=False, header=True)
                print('File {} stored'.format(today_filename))

        else:
            # return an empty dataframe
            data = pd.DataFrame()

        return data

    def get_catalunya_population(self, mode):
        """
        Returns a dict with the population of Catalunya depending on 'mode'
        """

        if mode == 'comarques':
            pop = {"Alt Camp": 44424, "Alt Empordà": 137951, "Alt Penedès": 108339, "Alt Urgell": 20155,
                   "Alta Ribagorça": 3820, "Anoia": 120842, "Aran": 9971, "Bages": 176891, "Baix Camp": 192245,
                   "Baix Ebre": 77199, "Baix Empordà": 132284, "Baix Llobregat": 818883, "Baix Penedès": 104473,
                   "Barcelonès": 2264301, "Berguedà": 39274, "Cerdanya": 18061, "Conca de Barberà": 19852,
                   "Garraf": 147635, "Garrigues": 18880, "Garrotxa": 56467, "Gironès": 188504, "Maresme": 446872,
                   "Moianès": 13483, "Montsià": 68297, "Noguera": 38226, "Osona": 158758, "Pallars Jussà": 12914,
                   "Pallars Sobirà": 6896, "Pla d'Urgell": 37035, "Pla de l'Estany": 32085, "Priorat": 9180,
                   "Ribera d'Ebre": 21610, "Ripollès": 24917, "Segarra": 22617, "Segrià": 206129, "Selva": 168469,
                   "Solsonès": 13639, "Tarragonès": 257454, "Terra Alta": 11352, "Urgell": 36462,
                   "Vallès Occidental": 923976, "Vallès Oriental": 408672, "Catalunya": 7619494, "Metropolità": 4866555,
                   "Comarques Gironines": 740677, "Camp de Tarragona": 523155, "Terres de l'Ebre": 178458,
                   "Ponent": 359349, "Comarques Centrals": 403480, "Alt Pirineu i Aran": 71817, "Penedès": 476003,
                   "Barcelona": 5627752, "Girona": 755396, "Lleida": 430255, "Tarragona": 806091}

        else:
            # return an empty dict
            pop = {}

        return pop

    def get_greece_confirmed(self, mode, add_aggregate=True):
        """
        Read Greece data, aggregate it according to 'mode' and return a Dataframe with [Date, Area, Confirmed]. 
        If add_aggregate is True, the aggregation values at Catalunya level are added
        """

        if mode == 'periferies':

            # check if today's file already exists
            today_filename = 'data/greece_confirmed_{}_v{}.csv'.format(mode, datetime.today().strftime('%Y%m%d'))
            if os.path.exists(today_filename):
                # read and return the file if it already exists
                data = pd.read_csv(today_filename, sep=',')
            else:
                # otherwise read and process from online source
                greece_cases_raw = pd.read_csv('https://raw.githubusercontent.com/iMEdD-Lab/open-data/master/COVID-19/regions_greece_cases.csv')

                # unpivot dataframe
                gre_cases = pd.melt(greece_cases_raw.drop(columns=['district_EN', 'pop_11']),
                                   id_vars=['district'], var_name='date', value_name='total_confirmed')

                # rename columns
                gre_cases = gre_cases.rename(columns={'district': 'Area'})

                # format Date
                gre_cases['Date'] = pd.to_datetime(gre_cases['date'], format='%m/%d/%y')

                # compute daily confirmed
                gre_cases['Confirmed'] = gre_cases.total_confirmed - gre_cases.groupby('Area').total_confirmed.shift(1)

                # remove columns
                gre_cases = gre_cases.drop(columns=['date', 'total_confirmed'])

                # add greece as area
                if add_aggregate:
                    gre_cases_total = gre_cases.groupby('Date').agg({'Confirmed': 'sum'}).reset_index()
                    gre_cases_total['Area'] = 'Ελλάδα'
                    gre_cases = gre_cases.append(gre_cases_total).reset_index(drop=True)

                # store result into csv
                data = gre_cases
                data.to_csv(today_filename, sep=',', index=False, header=True)
                print('File {} stored'.format(today_filename))

        else:
            # return an empty dataframe
            data = pd.DataFrame()

        return data

    def get_greece_population(self, mode):
        """
        Returns the population of Greece depending on 'mode'
        """ 

        if mode == 'periferies':
            pop = {
                    'Άγιον Όρος': 1811,
                    'Περιφέρεια Ανατολικής Μακεδονίας Θράκης': 608182,
                    'Περιφέρεια Αττικής': 3753783,
                    'Περιφέρεια Βορείου Αιγαίου': 199231,
                    'Περιφέρεια Δυτικής Ελλάδας': 679796,
                    'Περιφέρεια Δυτικής Μακεδονίας': 283689,
                    'Περιφέρεια Ηπείρου': 336856,
                    'Περιφέρεια Θεσσαλίας': 732762,
                    'Περιφέρεια Ιονίων Νήσων': 207855,
                    'Περιφέρεια Κεντρικής Μακεδονίας': 1882108,
                    'Περιφέρεια Κρήτης': 623065,
                    'Περιφέρεια Νοτίου Αιγαίου': 309015,
                    'Περιφέρεια Πελοποννήσου': 577903,
                    'Περιφέρεια Στερεάς Ελλάδας και Εύβοιας': 547390,
                    'Ελλάδα': 10413243
            }

        else:
            # return an empty dict
            pop = {}

        return pop

    def compute_rolling_mean(self, data, column, rolling_n=7):
        """Returns the rolling mean with a 'rolling_n' window  of 'column' in 'data'"""
        return data[column].rolling(rolling_n).mean().reset_index(0, drop=True)

    def compute_rolling_sum(self, data, column, rolling_n=14):
        """Returns the rolling sum with a 'rolling_n' window  of 'column' in 'data'"""
        return data[column].rolling(rolling_n).sum().reset_index(0, drop=True)

    def compute_epg(self, data, column, population):
        """Returns the EPG (Effective Potential Growth) of 'data' where 'column' is the column with daily confirmed values.
        EPG as described in LINK? """

        # compute ratio of infected people per infected person
        # rho = rho_A / rho_B = (n + n-1 + n-2) / (n-5 + n-6 + n-7) (rho_7 is the average of the last 7 days)
        data['rho_A'] = data[column].rolling(min_periods=1, window=3).sum()
        data['rho_B'] = data[column].shift(5).rolling(min_periods=1, window=3).sum()
        data['rho'] = data.rho_A / data.rho_B
        data['rho_7'] = data.rho.rolling(7).mean().reset_index(0, drop=True)

        # compute number of potentially infectious people
        # ia_14 = sum of confirmed during last 14 days / 100.000 inhabitants
        data['ia_14'] = data[column].rolling(14).sum() / (population/100000)

        # compute index of potential growth (EPG)
        data['epg'] = data.rho_7 * data.ia_14
        
        return data.epg.drop(columns=['rho_A', 'rho_B']).fillna(0)

    def plot_daily_values_v2(self, mode, data, title, column_date, plots):
        """
        Creates the plot with daily values and either shows it or returns the requested type of object
        - mode: indicates the type of return ('show', 'object', 'json')
        - data: dataframe with data to plot
        - title: title of the plot
        - column_date: column including the dates of the x-axis
        - plots: array of dicts describing which plots to include
        """

        # add plots to plot
        data_plot = []
        for p in plots:
            if p['type'] == 'bar':
                data_plot.append(go.Bar(
                    name=p['name_value'],
                    x=data[column_date], y=data[p['column_value']],
                    marker_color=p['color_value']
                ))
            elif p['type'] == 'line':
                data_plot.append(go.Scatter(
                    name=p['name_value'],
                    x=data[column_date], y=data[p['column_value']],
                    marker_color=p['color_value']
                ))

        # plot daily data
        fig = go.Figure(data=data_plot).update_layout(
            title=title,
            legend=dict(orientation='h', yanchor="top", y=0.98, xanchor="right", x=0.99),
            yaxis=dict( range=(data[p['column_value']], data[p['column_value']] * 1.2) )
        )

        if mode == 'show':
            fig.show()
        elif mode == 'object':
            return fig
        elif mode == 'json':
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def plot_epg(self, mode, data, title, column_date):
        """
        Creates the plot with epg values
        - mode: indicates the type of return ('show', 'object', 'json')
        - data: dataframe with data to plot
        - the rest of variables are used to configure what to plot and how to visualize
        """

        # create plot
        fig = go.Figure(data=[
            go.Scatter(
                name='EPG',
                x=data[column_date], y=data.epg,
                marker_color='darkslategray'
            )
        ]).update_layout(
            title=title,
            shapes=[
                dict(
                    # add green area: low risk epg<30
                    type="rect", xref="x", yref="y", x0="2020-01-01", y0=0, x1="2020-12-31", y1=30,
                    fillcolor="palegreen", opacity=0.5, layer="below", line_width=0
                ),
                dict(
                    # add yellow area: moderate risk 30<epg<70
                    type="rect", xref="x", yref="y", x0="2020-01-01", y0=30, x1="2020-12-31", y1=70,
                    fillcolor="yellow", opacity=0.4, layer="below", line_width=0
                ),
                dict(
                    # add orange area: high risk 70<epg<100
                    type="rect", xref="x", yref="y", x0="2020-01-01", y0=70, x1="2020-12-31", y1=100,
                    fillcolor="orange", opacity=0.4, layer="below", line_width=0
                ),
                dict(
                    # add red area: very high risk 100<epg
                    type="rect", xref="x", yref="y", x0="2020-01-01", y0=100, x1="2020-12-31", y1=10000,
                    fillcolor="red", opacity=0.5, layer="below", line_width=0
                )
            ],
            yaxis=dict(
                range=(data.epg.min() if data.epg.min() < 0 else 0, data.epg.max() * 1.2)
            )
        )

        if mode == 'show':
            fig.show()
        elif mode == 'object':
            return fig
        elif mode == 'json':
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def plot_ia14_rho(self):
        """TBD"""

if __name__ == '__main__':

    cov19 = Covid19Manager()

    # greece
    gre_data = cov19.get_greece_confirmed(mode='periferies')
    gre_pop = cov19.get_greece_population(mode='periferies')

    area = 'Περιφέρεια Ηπείρου'  # 'Περιφέρεια Ηπείρου' 'Ελλάδα' 'Περιφέρεια Κεντρικής Μακεδονίας'
    data = gre_data[gre_data.Area == area].reset_index(drop=True)
    data['Confirmed_rollingmean'] = cov19.compute_rolling_mean(data, 'Confirmed', rolling_n=7)
    data['Confirmed_rollingsum'] = cov19.compute_rolling_sum(data, 'Confirmed', rolling_n=14)
    data['epg'] = cov19.compute_epg(data, 'Confirmed', gre_pop[area])

    # catalunya
    # cat_data = cov19.get_catalunya_confirmed(mode='comarques')
    # cat_pop = cov19.get_catalunya_population(mode='comarques')
    #
    # area = 'Bages'
    # data = cat_data[cat_data.Area == area].reset_index(drop = True)
    # data['Confirmed_rollingmean'] = cov19.compute_rolling_mean(data, 'Confirmed', rolling_n=7)
    # data['Confirmed_rollingsum'] = cov19.compute_rolling_sum(data, 'Confirmed', rolling_n=14)
    # data['epg'] = cov19.compute_epg(data, 'Confirmed', cat_pop[area])

    # plots
    cov19.plot_daily_values_v2(mode='show', data=data, title='Daily Confirmed {}'.format(area), column_date='Date',
                               plots=[
                                   {
                                       'type': 'bar',
                                       'column_value': 'Confirmed',
                                       'name_value': 'Confirmed',
                                       'color_value': 'lightskyblue'
                                    },
                                    {
                                       'type': 'line',
                                       'column_value': 'Confirmed_rollingmean',
                                       'name_value': 'Mean {} days'.format(7),
                                       'color_value': 'royalblue'
                                    }
                               ])
    cov19.plot_daily_values_v2(mode='show', data=data, title='Active Confirmed {}'.format(area), column_date='Date',
                               plots=[
                                   {
                                       'type': 'line',
                                       'column_value': 'Confirmed_rollingsum',
                                       'name_value': 'Sum {} days'.format(14),
                                       'color_value': 'royalblue'
                                   }
                               ])
    cov19.plot_epg(mode='show', data=data, title='Effective Potential Growth (EPG) {}'.format(area), column_date='Date')

    exit()
