import numpy as np
import matplotlib.pyplot as plt

class PairPlot(object):
    def __init__(self, pd_tb, figsize=(10,10)):
        self.arg = []
        self.columns = pd_tb.columns
        self.figsize = figsize
        for i in pd_tb.columns:
            self.arg.append(np.array(pd_tb[i]))
        
    def _canvas(self):
        l = len(self.arg)
        self.fig = plt.figure(figsize=self.figsize)

        # ax - 1
        setattr(self, 'ax%s%s'%(l,1), self.fig.add_subplot(l, l, l**2-l+1))

        # ax - 2
        for i in range(l-2):
            setattr(self, 'ax%s%s'%(i+2,1), self.fig.add_subplot(l, l, i*l+l+1, sharex=getattr(self, 'ax%s%s'%(l,1))))
            getattr(self, 'ax%s%s'%(i+2,1)).get_xaxis().set_visible(False)
            setattr(self, 'ax%s%s'%(l,i+2), self.fig.add_subplot(l, l, l*l-l+i+2, sharey=getattr(self, 'ax%s%s'%(l,1))))
            getattr(self, 'ax%s%s'%(l,i+2)).get_yaxis().set_visible(False)

        # ax - 3
        for i in range(l-3):
            y = i+3
            for j in range(i+1):
                x = j+2
                setattr(self, 'ax%s%s'%(y,x), self.fig.add_subplot(l, l, (y-1)*l+x, 
                        sharex=getattr(self, 'ax%s%s'%(l,x)), 
                        sharey=getattr(self, 'ax%s%s'%(y,1))))
                getattr(self, 'ax%s%s'%(y,x)).get_xaxis().set_visible(False)
                getattr(self, 'ax%s%s'%(y,x)).get_yaxis().set_visible(False)

        # ax - 4
        for i in range(l-1):
            setattr(self, 'ax%s%s'%(i+1,i+1), self.fig.add_subplot(l, l, i*l+i+1, sharex=getattr(self, 'ax%s%s'%(l,i+1))))
            getattr(self, 'ax%s%s'%(i+1,i+1)).get_xaxis().set_visible(False)
            getattr(self, 'ax%s%s'%(i+1,i+1)).get_yaxis().set_visible(False)
        setattr(self, 'ax%s%s'%(l,l), self.fig.add_subplot(l, l, l*l))
        getattr(self, 'ax%s%s'%(l,l)).get_yaxis().set_visible(False)

        # ax - 5
        for i in range(l-1):
            for j in range(l-1-i):
                setattr(self, 'ax%s%s'%(i+1,j+i+2), self.fig.add_subplot(l, l, i*l+i+j+2))
                getattr(self, 'ax%s%s'%(i+1,j+i+2)).get_xaxis().set_visible(False)
                getattr(self, 'ax%s%s'%(i+1,j+i+2)).get_yaxis().set_visible(False)
    
    def plot(self, Y=[]):
        self._canvas()
        l = len(self.arg)
        
        # Label
        getattr(self, 'ax%s%s'%(l,1)).set_xlabel(self.columns[0])
        for i in range(l-1):
            getattr(self, 'ax%s%s'%(l,i+2)).set_xlabel(self.columns[i+1])
            getattr(self, 'ax%s%s'%(i+2,1)).set_ylabel(self.columns[i+1])
            
        # Scatter
        for i in range(l-1):
            y = i+2
            for j in range(i+1):
                x = j+1
                if len(Y): getattr(self, 'ax%s%s'%(y,x)).scatter(y=self.arg[i+1], x=self.arg[j], s=1, c=Y)
                else: getattr(self, 'ax%s%s'%(y,x)).scatter(y=self.arg[i+1], x=self.arg[j], s=1)
        
        # Hist
        for i in range(l):
            getattr(self, 'ax%s%s'%(i+1,i+1)).hist(self.arg[i], bins=9)
        
        # Corr
        coef = np.corrcoef(self.arg)
        for i in range(l-1):
            for j in range(l-1-i):
                color = 'green' if abs(coef[i][j+i+1]) < 0.5 else 'red'
                corr = round(coef[i][j+i+1],2)
                getattr(self, 'ax%s%s'%(i+1,j+i+2)).text(0.5, 0.5, corr,
                                          horizontalalignment='center',
                                          verticalalignment='center',
                                          fontsize=20, color=color)