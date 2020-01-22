import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.cluster import KMeans as km
from sklearn.cluster import MiniBatchKMeans as mbkm
from sklearn.cluster import AgglomerativeClustering as ac
from sklearn.cluster import Birch as bc
from sklearn.cluster import estimate_bandwidth

class Cluster(object):
    def __init__(self, X, figsize=(6,3)):
        self.X = X
        self.y = None
        self.fig = plt.figure(figsize=figsize)
        
    def TEST_RESULT(self, y):
        sil = metrics.silhouette_score(self.X, y, metric='euclidean')
        cal = metrics.calinski_harabaz_score(self.X, y)
        return sil, cal
    
    def run(self):
        raise AttributeError('Subclass must realize this function first!')
        
    def test(self, t=8):
        l = []
        for i in range(t):
            self.run(i+2)
            l.append(self.TEST_RESULT(self.y))
        ax1 = self.fig.add_subplot(1, 2, 1)
        ax1.plot([x+2 for x in range(t)], [s[0] for s in l])
        ax2 = self.fig.add_subplot(1, 2, 2)
        ax2.plot([x+2 for x in range(t)], [c[1] for c in l])

class KMeans(Cluster):
    def run(self, clusters=3):
        self.y = km(n_clusters=clusters).fit_predict(self.X)
        
class MiniBatchKMeans(Cluster):
    def run(self, clusters=3):
        self.y = mbkm(n_clusters=clusters).fit_predict(self.X)

class AgglomerativeClustering(Cluster):
    def run(self, clusters=3):
        self.y = ac(n_clusters=clusters).fit_predict(self.X)
        
class Birch(Cluster):
    def run(self, clusters=3):
        self.y = bc(n_clusters=clusters).fit_predict(self.X)
    