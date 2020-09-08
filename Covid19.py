"""
Covid19 library with helper function definitions and implementations

@author: Eduard Bonada
Copyright 2020
"""

import pandas as pd
import os
from datetime import datetime

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

        # TODO: store downloaded file
        # TODO: check existing today's file and avoid downloading

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

                data = catdata_cases_areas

                # store result into csv
                data.to_csv(today_filename, sep=',', index=False, header=True)
                print('File {} stored'.format(today_filename))

        else:
            # return an empty dataframe
            data = pd.DataFrame()

        return data

    def get_greece_confirmed(self, mode, add_aggregate=True):
        """
        Read Greece data, aggregate it according to 'mode' and return a Dataframe with [Date, Area, Confirmed]. 
        If add_aggregate is True, the aggregation values at Catalunya level are added
        """

        # TODO: read data from online sources

        data = pd.DataFrame()

        return data

    def get_catalunya_population(self, mode):
        """
        Returns a dict with the population of Catalunya depending on 'mode'
        """

        # TODO: add population data from all comarques

        if mode == 'comarques':
            pop = {
                'Catalunya': 7565099,
                'Barcelonès': 2220000
            }
        
        else:
            # return an empty datafresame
            pop = {}
        
        return pop

    def get_greece_population(self, mode):
        """
        Returns the population of Greece depending on 'mode'
        """ 

        if mode == 'periferies':
            # TODO: read from online csv
            pop = pd.DataFrame()
        
        else:
            # return an empty datafresame
            pop = pd.DataFrame()
        
        return pop

    def compute_rolling_mean(self, data, column, rolling_n=7):
        """Returns the rolling mean with a 'rolling_n' window  of 'column' in 'data'"""
        return data[column].rolling(rolling_n).mean().reset_index(0, drop=True)

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
        
        return data.epg.drop(columns=['rho_A', 'rho_B'])
    
    
if __name__ == '__main__':

    cov19 = Covid19Manager()
    cat_data = cov19.get_catalunya_confirmed(mode='comarques')
    exit()
    # cov19.GetCatalunyaPopulation(mode='comarques')
    # cov19.GetGreeceConfirmed(mode='periferies')
    # cov19.GetGreecePopulation(mode='periferies')
    