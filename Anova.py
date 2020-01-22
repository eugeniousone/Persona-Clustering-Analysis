from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

class Anova(object):
    def __init__(self, tb):
        self.tb = tb
        
    def _anova_sig(self, idpv, dpv='y'):
        model = ols('%s ~ %s'%(idpv,dpv), self.tb).fit()
        anovat = anova_lm(model)
        if anovat['PR(>F)'][0] > 0.05:
            print('WARNING: P_%s=%s'%(idpv, round(anovat['PR(>F)'][0],3)))
        else:
            print('Pass: P_%s=%s'%(idpv, round(anovat['PR(>F)'][0],3)))

    def run(self):
        for col in self.tb.columns[:-1]:
            self._anova_sig(col, dpv=self.tb.columns[-1])