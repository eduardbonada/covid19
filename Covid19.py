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

        # TODO: read data from online sources

        data = pd.DataFrame()

        return data

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
    cat_pop = cov19.get_catalunya_population(mode='comarques')

    area = 'Barcelonès'
    data = cat_data[cat_data.Area == area].reset_index(drop = True)
    cat_roll = cov19.compute_rolling_mean(data, 'Confirmed', rolling_n=14)
    cat_epg = cov19.compute_epg(data, 'Confirmed', cat_pop[area])
    exit()
    # cov19.GetGreeceConfirmed(mode='periferies')
    # cov19.GetGreecePopulation(mode='periferies')
    