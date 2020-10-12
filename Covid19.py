"""
Covid19 library with helper function definitions and implementations

@author: Eduard Bonada
Copyright 2020
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from plotly.utils import PlotlyJSONEncoder
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from math import floor, ceil

class Covid19Manager():
    """
    Object that contains actions and processes related to Covid19 data sources
    """

    def __init__(self):
        """
        Initialize
        """
        
        # self.test = test

    def get_catalunya_comarques_confirmed(self, add_aggregate=True):
        """
        Read Catalunya data at the level of 'comarques' and return a Dataframe with [Date, Area, Confirmed].
        If add_aggregate is True, the aggregation values at Catalunya level are added as new rows of the Dataframe
        """

        # check if today's file already exists
        today_filename = 'data/catalunya_confirmed_comarques_v{}.csv'.format(datetime.today().strftime('%Y%m%d'))
        if os.path.exists(today_filename):
            # read and return the file if it already exists
            data = pd.read_csv(today_filename, sep=',').astype({'Date': 'datetime64[ns]'})
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

            # add group columm
            data['Group'] = 'cat-comarques'

            # store result into csv
            data.to_csv(today_filename, sep=',', index=False, header=True)
            print('File {} stored'.format(today_filename))

        return data.sort_values(['Area', 'Date']).reset_index(drop=True)

    def get_catalunya_comarques_population(self):
        """
        Returns a dict with the population of Catalunya comarques
        """

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

        # construct dataframe
        pop_df = pd.DataFrame.from_dict(data=pop,
                                        orient='index',
                                        columns=['Population']
                                        ).reset_index().rename(columns={'index': 'Area'})

        return pop_df

    def get_greece_periferies_confirmed(self, add_aggregate=True):
        """
        Read Greece data at the level of 'periferies' and return a Dataframe with [Date, Area, Confirmed].
        If add_aggregate is True, the aggregation values at Greece level are added
        """

        # check if today's file already exists
        today_filename = 'data/greece_confirmed_periferies_v{}.csv'.format(datetime.today().strftime('%Y%m%d'))
        if os.path.exists(today_filename):
            # read and return the file if it already exists
            data = pd.read_csv(today_filename, sep=',').astype({'Date': 'datetime64[ns]'})
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
            data = gre_cases.fillna(0)

            # add group columm
            data['Group'] = 'gre-periferies'

            # store result into csv
            data.to_csv(today_filename, sep=',', index=False, header=True)
            print('File {} stored'.format(today_filename))

        return data.sort_values(['Area', 'Date']).reset_index(drop=True)

    def get_greece_periferies_population(self):
        """
        Returns the population of Greece periferies
        """ 

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

        # construct dataframe
        pop_df = pd.DataFrame.from_dict(data=pop,
                                        orient='index',
                                        columns=['Population']
                                        ).reset_index().rename(columns={'index': 'Area'})

        return pop_df

    def get_greece_nomoi_confirmed(self, add_aggregate=True):
        """
        Read Greece data at the level of 'nomoi' and return a Dataframe with [Date, Area, Confirmed].
        If add_aggregate is True, the aggregation values at Greece level are added
        """

        # check if today's file already exists
        today_filename = 'data/greece_confirmed_nomoi_v{}.csv'.format(datetime.today().strftime('%Y%m%d'))
        if os.path.exists(today_filename):
            # read and return the file if it already exists
            data = pd.read_csv(today_filename, sep=',').astype({'Date': 'datetime64[ns]'})
        else:
            # otherwise read and process from online source
            greece_cases_raw = pd.read_csv('https://raw.githubusercontent.com/iMEdD-Lab/open-data/master/COVID-19/greece_cases_v2.csv')

            # drop unwanted  columns
            columns_to_drop = [c for c in greece_cases_raw.columns if 'Unnamed' in c]
            greece_cases_raw = greece_cases_raw.drop(columns=columns_to_drop)

            # unpivot dataframe
            gre_cases = pd.melt(greece_cases_raw.drop(columns=['county', 'pop_11']),
                               id_vars=['Γεωγραφικό Διαμέρισμα', 'Περιφέρεια', 'county_normalized'], var_name='date', value_name='total_confirmed')

            # rename columns
            gre_cases = gre_cases.rename(columns={'county_normalized': 'Area', 'Γεωγραφικό Διαμέρισμα': 'AreaParent', 'Περιφέρεια': 'AreaParent2'})

            # format Date
            gre_cases['Date'] = pd.to_datetime(gre_cases['date'], format='%m/%d/%y')

            # compute daily confirmed
            gre_cases['Confirmed'] = gre_cases.total_confirmed - gre_cases.groupby('Area').total_confirmed.shift(1)

            # remove columns
            gre_cases = gre_cases.drop(columns=['date', 'total_confirmed'])

            # update registers with unknown area
            gre_cases.loc[gre_cases.Area == 'ΕΛΛΑΔΑ', 'Area'] = 'UNKNOWN'
            gre_cases.loc[gre_cases.Area == 'ΕΛΛΑΔΑ', 'AreaParent'] = '-'
            gre_cases.loc[gre_cases.Area == 'ΕΛΛΑΔΑ', 'AreaParent2'] = '-'

            # add greece as area
            if add_aggregate:
                gre_cases_total = gre_cases.groupby('Date').agg({'Confirmed': 'sum'}).reset_index()
                gre_cases_total['Area'] = 'ΕΛΛΑΔΑ'
                gre_cases_total['AreaParent'] = '-'
                gre_cases_total['AreaParent2'] = '-'
                gre_cases = gre_cases.append(gre_cases_total).reset_index(drop=True)

            # fill nulls with 0
            data = gre_cases.fillna(0)

            # add group columm
            data['Group'] = 'gre-nomoi'

            # store result into csv
            data.to_csv(today_filename, sep=',', index=False, header=True)
            print('File {} stored'.format(today_filename))

        return data.sort_values(['Area', 'Date']).reset_index(drop=True)

    def get_greece_nomoi_deaths(self, add_aggregate=True):
        """
        Read Greece data at the level of 'nomoi' and return a Dataframe with [Date, Area, Deaths].
        If add_aggregate is True, the aggregation values at Greece level are added
        """

        # check if today's file already exists
        today_filename = 'data/greece_deaths_nomoi_v{}.csv'.format(datetime.today().strftime('%Y%m%d'))
        if os.path.exists(today_filename):
            # read and return the file if it already exists
            data = pd.read_csv(today_filename, sep=',').astype({'Date': 'datetime64[ns]'})
        else:
            # otherwise read and process from online source
            greece_deaths_raw = pd.read_csv('https://raw.githubusercontent.com/iMEdD-Lab/open-data/master/COVID-19/greece_deaths_v2.csv')\
                                .drop(columns=['8/27/20.1'])

            # unpivot dataframe
            gre_deaths = pd.melt(greece_deaths_raw.drop(columns=['county', 'pop_11']),
                                 id_vars=['Γεωγραφικό Διαμέρισμα', 'Περιφέρεια', 'county_normalized'], var_name='date', value_name='total_deaths')

            # rename columns
            gre_deaths = gre_deaths.rename(columns={'county_normalized': 'Area', 'Γεωγραφικό Διαμέρισμα': 'AreaParent', 'Περιφέρεια': 'AreaParent2'})

            # format Date
            gre_deaths['Date'] = pd.to_datetime(gre_deaths['date'], format='%m/%d/%y')

            # compute daily deaths
            gre_deaths['Deaths'] = gre_deaths.total_deaths - gre_deaths.groupby('Area').total_deaths.shift(1)

            # remove columns
            gre_deaths = gre_deaths.drop(columns=['date', 'total_deaths'])

            # update registers with unknown area
            gre_deaths.loc[gre_deaths.Area == 'ΕΛΛΑΔΑ', 'Area'] = 'UNKNOWN'
            gre_deaths.loc[gre_deaths.Area == 'ΕΛΛΑΔΑ', 'AreaParent'] = '-'
            gre_deaths.loc[gre_deaths.Area == 'ΕΛΛΑΔΑ', 'AreaParent2'] = '-'

            # add greece as area
            if add_aggregate:
                gre_deaths_total = gre_deaths.groupby('Date').agg({'Deaths': 'sum'}).reset_index()
                gre_deaths_total['Area'] = 'ΕΛΛΑΔΑ'
                gre_deaths_total['AreaParent'] = '-'
                gre_deaths_total['AreaParent2'] = '-'
                gre_deaths = gre_deaths.append(gre_deaths_total).reset_index(drop=True)

            # fill nulls with 0
            data = gre_deaths.fillna(0)

            # add group columm
            data['Group'] = 'gre-nomoi'

            # store result into csv
            data.to_csv(today_filename, sep=',', index=False, header=True)
            print('File {} stored'.format(today_filename))

        return data.sort_values(['Area', 'Date']).reset_index(drop=True)

    def get_greece_nomoi_population(self):
        """
        Returns the population of Greece nomoi
        """

        pop = {
            'ΑΓΙΟ ΟΡΟΣ': 1811, 'ΑΙΤΩΛΟΑΚΑΡΝΑΝΙΑΣ': 210802, 'ΑΡΓΟΛΙΔΑΣ': 97044, 'ΑΡΚΑΔΙΑΣ': 86685, 'ΑΡΤΑΣ': 67877,
            'ΑΤΤΙΚΗΣ': 3828434, 'ΑΧΑΪΑΣ': 309694, 'ΒΟΙΩΤΙΑΣ': 117920, 'ΓΡΕΒΕΝΩΝ': 31757, 'ΔΡΑΜΑΣ': 98287,
            'ΔΩΔΕΚΑΝΗΣΩΝ': 190988, 'ΕΒΡΟ': 147947, 'ΕΥΒΟΙΑΣ': 191206, 'ΕΥΡΥΤΑΝΙΑΣ': 20081, 'ΖΑΚΥΝΘΟΥ': 40759,
            'ΗΛΕΙΑΣ': 159300, 'ΗΜΑΘΙΑΣ': 140611, 'ΗΡΑΚΛΕΙΟΥ': 305490, 'ΘΕΣΠΡΩΤΙΑΣ': 43587, 'ΘΕΣΣΑΛΟΝΙΚΗΣ': 1110551,
            'ΙΩΑΝΝΙΝΩΝ': 167901, 'ΚΑΒΑΛΑΣ': 138687, 'ΚΑΡΔΙΤΣΑΣ': 113544, 'ΚΑΣΤΟΡΙΑΣ': 50322, 'ΚΕΡΚΥΡΑΣ': 104371,
            'ΚΕΦΑΛΛΟΝΙΑΣ': 39032, 'ΚΙΛΚΙΣ': 80419, 'ΚΟΖΑΝΗΣ': 150196, 'ΚΟΡΙΝΘΟΥ': 145082, 'ΚΥΚΛΑΔΩΝ': 118027,
            'ΛΑΚΩΝΙΑΣ': 89138, 'ΛΑΡΙΣΑΣ': 284325, 'ΛΑΣΙΘΙΟΥ': 75381, 'ΛΕΣΒΟΥ': 103698, 'ΛΕΥΚΑΔΑΣ': 23693,
            'ΜΑΓΝΗΣΙΑΣ': 203808, 'ΜΕΣΣΗΝΙΑΣ': 159954, 'ΞΑΝΘΗΣ': 111222, 'ΠΕΛΛΑΣ': 139680, 'ΠΙΕΡΙΑΣ': 126698,
            'ΠΡΕΒΕΖΑΣ': 57491, 'ΡΕΘΥΜΝΟΥ': 85609, 'ΡΟΔΟΠΗΣ': 112039, 'ΣΑΜΟΥ': 42859, 'ΣΕΡΡΩΝ': 176430,
            'ΤΡΙΚΑΛΩΝ': 131085, 'ΦΘΙΩΤΙΔΑΣ': 158231, 'ΦΛΩΡΙΝΑΣ': 51414, 'ΦΩΚΙΔΑΣ': 40343, 'ΧΑΛΚΙΔΙΚΗΣ': 107719,
            'ΧΑΝΙΩΝ': 156585, 'ΧΙΟΥ': 52674, 'ΕΛΛΑΔΑ': 10413243
        }

        # construct dataframe
        pop_df = pd.DataFrame.from_dict(data=pop,
                                        orient='index',
                                        columns=['Population']
                                        ).reset_index().rename(columns={'index': 'Area'})

        return pop_df

    def compute_rolling_mean(self, data, value_column, groupby_column, rolling_n=7):
        """Returns the rolling mean with a 'rolling_n' window  of 'value_column' in 'data' grouping by column 'groupby_column'"""
        return data.groupby(groupby_column)[value_column].rolling(window=rolling_n, min_periods=1).mean().reset_index(0, drop=True)

    def compute_rolling_sum(self, data, value_column, groupby_column, rolling_n=14):
        """Returns the rolling sum with a 'rolling_n' window  of 'value_column' in 'data' grouping by column 'groupby_column'"""
        return data.groupby(groupby_column)[value_column].rolling(window=rolling_n, min_periods=1).sum().reset_index(0, drop=True)

    def compute_epg(self, data, confirmed_column, population):
        """Returns the EPG (Effective Potential Growth) of 'data' where 'confirmed_column' is the column with daily confirmed values
        It assumes a single area is passed in data
        EPG as described in LINK? """

        # loop groupby(area)'s and perform calculation

        # compute ratio of infected people per infected person
        # rho = rho_A / rho_B = (n + n-1 + n-2) / (n-5 + n-6 + n-7) (rho_7 is the average of the last 7 days)
        data['rho_A'] = data[confirmed_column].rolling(window=3, min_periods=1).sum()
        data['rho_B'] = data[confirmed_column].shift(5).rolling(window=3, min_periods=1).sum()
        data['rho'] = data.apply(lambda d: d.rho_A / d.rho_B if (d.rho_B != 0 and not pd.isnull(d.rho_B)) else 0.0, axis=1)  # data.rho_A / data.rho_B if data.rho_B != 0 else 0.0
        data['rho_7'] = data.rho.rolling(window=7, min_periods=1).mean().reset_index(0, drop=True)

        # compute number of potentially infectious people
        # ia_14 = sum of confirmed during last 14 days / 100.000 inhabitants
        data['ia_14'] = data[confirmed_column].rolling(window=14, min_periods=1).sum() / (population / 100000)

        # compute index of potential growth (EPG)
        data['epg'] = data.rho_7 * data.ia_14

        return data.epg.drop(columns=['rho_A', 'rho_B']).fillna(0)

    def compute_epg_v2(self, data, confirmed_column, area_column):
        """Returns the EPG (Effective Potential Growth) of 'data' where 'confirmed_column' is the column with daily confirmed values
        and 'area_column' is the column with the areas.
        EPG as described in LINK? """

        # compute ratio of infected people per infected person
        # rho = rho_A / rho_B = (n + n-1 + n-2) / (n-5 + n-6 + n-7) (rho_7 is the average of the last 7 days)
        data['rho_A'] = data.groupby(area_column)[confirmed_column].rolling(window=3, min_periods=1).sum().reset_index(0, drop=True)
        # data['rho_B'] = data.groupby(area_column)[confirmed_column].shift(5).rolling(window=3, min_periods=1).sum().reset_index(0, drop=True)
        data['rho_B'] = data.groupby(area_column).shift(4).rho_A # rho_B is actually equal to rho_A of 4 days earlier
        data['rho'] = data.apply(lambda d: d.rho_A / d.rho_B if (d.rho_B != 0 and not pd.isnull(d.rho_B)) else 0.0, axis=1)  # data.rho_A / data.rho_B if data.rho_B != 0 else 0.0
        data['rho_7'] = data.groupby(area_column).rho.rolling(window=7, min_periods=1).mean().reset_index(0, drop=True)

        # compute number of potentially infectious people
        # ia_14 = sum of confirmed during last 14 days / 100.000 inhabitants
        data['ia_14'] = data.groupby(area_column)[confirmed_column].rolling(window=14, min_periods=1).sum().reset_index(0, drop=True) / (data.Population/100000)

        # compute index of potential growth (EPG)
        data['epg'] = data.rho_7 * data.ia_14

        # drop columns
        data = data.drop(columns=['rho_A', 'rho_B'])

        return data.epg.fillna(0)

    def plot_daily_values(self, mode, data, title, column_date, plots):
        """
        Creates the plot with daily values and either shows it or returns the requested type of object
        - mode: indicates the type of return ('show', 'object', 'json')
        - data: dataframe with data to plot
        - title: title of the plot
        - column_date: column including the dates of the x-axis
        - plots: array of dicts describing which plots to include
        """

        # create plot figure
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # add plots to plot
        min_value = max_value = 0
        for p in plots:
            if p['type'] == 'bar':
                fig.add_trace(
                    go.Bar(name=p['name_value'], x=data[column_date], y=data[p['column_value']], marker_color=p['color_value']),
                    secondary_y=p['secondary_y'] if 'secondary_y' in p.keys() else False
                )
            elif p['type'] == 'line':
                fig.add_trace(
                    go.Scatter(name=p['name_value'], x=data[column_date], y=data[p['column_value']], marker_color=p['color_value']),
                    secondary_y=p['secondary_y'] if 'secondary_y' in p.keys() else False
                )

            # set min-max to later set plot limits
            min_value = data[p['column_value']].min() if data[p['column_value']].min() < min_value else min_value
            max_value = data[p['column_value']].max() if data[p['column_value']].max() > max_value else max_value

        # plot daily data
        fig.update_layout(
            title=title,
            legend=dict(orientation='h', yanchor="top", y=0.98, xanchor="right", x=0.99),
            yaxis=dict(range=(min_value, max_value * 1.2))
        )

        if mode == 'show':
            fig.show()
        elif mode == 'object':
            return fig
        elif mode == 'json':
            return json.dumps(fig, cls=PlotlyJSONEncoder)

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
                    type="rect", xref="x", yref="y", x0="2020-01-01", y0=100, x1="2020-12-31", y1=50000,
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
            return json.dumps(fig, cls=PlotlyJSONEncoder)

    def plot_ia14_rho(self, mode, data, title):
        """
        Creates the plot of ia14 vs rho_7
        - mode: indicates the type of return ('show', 'object', 'json')
        - data: dataframe with data to plot
        - the rest of variables are used to configure what to plot and how to visualize
        """

        # setup arrays to print risk area limits
        x = [x for x in range(0, 10000, 1)]
        y_green = [(30/x if x != 0 else None) for x in x]
        y_yellow = [(70/x if x != 0 else None) for x in x]
        y_orange = [(100/x if x != 0 else None) for x in x]
        y_red = [(10000/x if x != 0 else None) for x in x]

        # create plot
        fig = go.Figure(data=[
            go.Scatter(name='green', x=x, y=y_green, marker_color='palegreen', fill='tonexty', line=dict(width=0), hoverinfo='none'),
            go.Scatter(name='yellow', x=x, y=y_yellow, marker_color='yellow', fill='tonexty', line=dict(width=0), hoverinfo='none'),
            go.Scatter(name='orange', x=x, y=y_orange, marker_color='orange', fill='tonexty', line=dict(width=0), hoverinfo='none'),
            go.Scatter(name='red', x=x, y=y_red, marker_color='red', fill='tonexty', line=dict(width=0), hoverinfo='none'),
            go.Scatter(
                name='IA_14 vs RHO_7',
                x=data.ia_14, y=data.rho_7,
                marker_color='darkslategray'
            ),
        ]).update_layout(
            title=title,
            width=800, height=800,
            xaxis=dict(range=(data.ia_14.min() if data.ia_14.min() < 0 else 0, data.ia_14.max() * 1.2)),
            yaxis=dict(range=(data.rho_7.min() if data.rho_7.min() < 0 else 0, data.rho_7.max() * 1.2)),
            showlegend=False
        )

        if mode == 'show':
            fig.show()
        elif mode == 'object':
            return fig
        elif mode == 'json':
            return json.dumps(fig, cls=PlotlyJSONEncoder)



if __name__ == "__main__":
    cov19 = Covid19Manager()

    cov19.get_greece_nomoi_confirmed()
    cov19.get_greece_nomoi_population()
