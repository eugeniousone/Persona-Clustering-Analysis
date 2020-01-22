import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from IPython.display import display
import Plot
import Cluster
import Anova

dict_ = {'CSP': 'Customer Sensitivity of Promotion',
         'NB': 'Number of Brand Purchased',
         'Q': 'Total Purchase Amount',
         'RFB': 'Ratio of The Most Purchased Brand',
         'NOFF': 'Number of Offline Brand',
         'ROFF': 'Ratio of Offline Brand',
         'NON': 'Number of Online Brand',
         'RON': 'Ratio of Online Brand',
         'ON': 'Number of Online Purchase',
         'PF': 'Purchase Frequency'}

def convince_degree(value, p):
    if p < 0.005: return '%s%s'%(round(value, 3), '***')
    elif p < 0.01: return '%s%s'%(value, '**')
    elif p < 0.05: return '%s%s'%(value, '*')
    else: return '%s'%round(value, 3)
    
def cluster(obj, tb, n):
    obj.run(n)
    tb_copy = tb.copy()
    tb_copy['y'] = obj.y
    Anova.Anova(tb_copy).run()
    del tb_copy
    return obj.y

class Analysis(object):
    def __init__(self, data, clusters, factors):
        self.feature_table = data
        self.CLUSTER = clusters
        self.cluster_factors = factors
        
    def plot(self, y):
        pic = Plot.PairPlot(self.feature_table[self.cluster_factors],(10,10))
        pic.plot(y)
        return pic.fig

    def clustering(self):
        X = np.array([np.array(self.feature_table[i]) for i in self.cluster_factors])
        for i in range(len(X)):
            X[i] = (X[i] - X[i].mean()) / X[i].std()
        X = X.T
        Cluster.KMeans(X).test()
        self.y_km = cluster(Cluster.KMeans(X), self.feature_table[self.cluster_factors], self.CLUSTER)
        fig_km = self.plot(self.y_km)
        
    def save(self):
        clustering_result = pd.DataFrame({'familyId': self.feature_table['familyId'], 'y_km': self.y_km})
        self.clustering_table = pd.concat([self.feature_table, clustering_result[['y_km']]], axis=1, keys='familyId')
        self.clustering_table.columns = ['familyId','CSP','NB','Q','RFB','NOFF','ROFF','NON','RON','ON','PF','city','familyIncome','familySize','y_km']
        self.clustering_table.to_excel('clustering_%s.xlsx'%self.CLUSTER)
        
    def clustering_detail(self):
        pivot = pd.pivot_table(self.clustering_table, values=['CSP', 'NB', 'Q', 'RFB', 'NOFF', 'ROFF', 'NON', 'RON', 'ON', 'PF'], columns='y_km')
        pivot.index = list(map(lambda x: dict_[x], list(pivot.index)))
        dist = pd.pivot_table(self.clustering_table, values=['CSP' , 'NB'], columns='y_km', aggfunc='count')
        dist.index = ['Amount', 'Percentage']
        dist.loc['Percentage'] /= len(self.clustering_table)
        report = pd.concat([pivot.round(3), dist.round(3)])
        F_list = []
        for i in ['CSP', 'NB', 'Q', 'RFB', 'NOFF', 'ROFF', 'NON', 'RON', 'ON', 'PF']:
            model = ols('%s ~ %s'%(i, 'y_km'), self.clustering_table).fit()
            anovat = anova_lm(model)
            F_list.append(convince_degree(anovat['F'][0], anovat['PR(>F)'][0]))
        while len(F_list)<len(report): F_list.append(np.nan)
        report['F_value'] = F_list
        display(report)

        # city
        city = pd.pivot_table(self.clustering_table, values='CSP', index='city', columns='y_km', aggfunc='count')
        city.loc['Guangzhou'] += city.loc['Guangzhou']
        city = city.iloc[:3]
        city.index = ['Shanghai', 'Beijing', 'Guangshen']
        city = city.fillna(0)
        cvs = convince_degree(stats.chi2_contingency(city.values)[0], stats.chi2_contingency(city.values)[1])
        for i in range(len(city)):
            city.iloc[i] /= city.iloc[i].sum()
        city['Chi'] = np.nan
        city['Chi'].iloc[0] = cvs

        # income
        income = pd.pivot_table(self.clustering_table, values='CSP', index='familyIncome', columns='y_km', aggfunc='count')
        income = income.fillna(0)
        cvs = convince_degree(stats.chi2_contingency(income.values)[0], stats.chi2_contingency(income.values)[1])
        for i in range(len(income)):
            income.iloc[i] /= income.iloc[i].sum()
        income['Chi'] = np.nan
        income['Chi'].iloc[0] = cvs

        # family size
        size = pd.pivot_table(self.clustering_table, values='CSP', index='familySize', columns='y_km', aggfunc='count')
        size = size.fillna(0)
        cvs = convince_degree(stats.chi2_contingency(size.values)[0], stats.chi2_contingency(size.values)[1])
        for i in range(len(size)):
            size.iloc[i] /= size.iloc[i].sum()
        size['Chi'] = np.nan
        size['Chi'].iloc[0] = cvs

        # combination
        demography_dist = pd.concat([city, income, size])
        for c in demography_dist.columns[:-1]:
            for i in range(len(demography_dist)):
                demography_dist[c].iloc[i] = '%s%%'%(int(round(demography_dist[c].iloc[i], 3)*1000)/10)

        display(demography_dist)
        
    def run(self):
        self.clustering()
        self.save()
        self.clustering_detail()