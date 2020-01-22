import pandas as pd

class DataTB(object):
    def __init__(self, table):
        self.tb = table

    # Table of CSP
    def _CSP(self):
        def ifPromotion(value):
            if value == '无促销': return 0
            else: return 1

        def CSP(subTable):
            return subTable['TB_CSP_FLAG'].sum()/subTable['TB_CSP_FLAG'].count()

        TB_CSP_FLAG = pd.DataFrame(self.tb.ix[:, '促销'].apply(ifPromotion))
        TB_CSP_FLAG.columns = ['TB_CSP_FLAG']
        TB_CSP_TEMP = pd.concat([self.tb[['家庭编号','促销']], TB_CSP_FLAG], axis=1)

        self.TB_CSP = pd.DataFrame(TB_CSP_TEMP[['TB_CSP_FLAG']].groupby(TB_CSP_TEMP['家庭编号']).apply(CSP), columns=['CSP'])

    # Table of NB
    def _NB(self):
        def countBrand(subTable):
            return subTable['品牌'].count()

        TB_NB_TEMP = self.tb[['家庭编号', '品牌']].drop_duplicates()
        self.TB_NB = pd.DataFrame(TB_NB_TEMP[['品牌']].groupby(TB_NB_TEMP['家庭编号']).apply(countBrand), columns=['NB'])
        
    # Table of Q
    def _Q(self):
        self.TB_Q = self.tb[['单价']].groupby(self.tb['家庭编号']).apply(sum)
        self.TB_Q.columns = ['Q']

    # Table of RFB
    def _RFB(self):
        def RFB(subTable):
            return subTable['单价'].max()/subTable['单价'].sum()

        TB_RFB_TEMP = self.tb[['家庭编号', '品牌', '单价']].groupby(['家庭编号', '品牌'], as_index=False).sum()
        self.TB_RFB = pd.DataFrame(TB_RFB_TEMP[['单价']].groupby(TB_RFB_TEMP['家庭编号']).apply(RFB), columns=['RFB'])

    # Table of NOFF
    def _NOFF(self):
        def countChannel(subTable):
            return subTable['购买地点'].count()

        TB_NOFF_TEMP = self.tb[['家庭编号', '购买地点']][self.tb['形式']=='线下'].drop_duplicates()
        self.TB_NOFF = pd.DataFrame(TB_NOFF_TEMP[['购买地点']].groupby(TB_NOFF_TEMP['家庭编号']).apply(countChannel), columns=['NOFF'])

    # Table of ROFF
    def _ROFF(self):
        TB_ROFF_TEMP = self.tb[['家庭编号', '形式', '单价']]
        TB_ROFF_TEMP2 = TB_ROFF_TEMP[['单价']][TB_ROFF_TEMP['形式']=='线下'].groupby(TB_ROFF_TEMP['家庭编号']).apply(sum) \
                / TB_ROFF_TEMP[['单价']].groupby(TB_ROFF_TEMP['家庭编号']).apply(sum)
        self.TB_ROFF = TB_ROFF_TEMP2.fillna(0)
        self.TB_ROFF.columns = ['ROFF']

    # Table of NON
    def _NON(self):
        def countChannel(subTable):
            return subTable['购买地点'].count()

        TB_NON_TEMP = self.tb[['家庭编号', '购买地点']][self.tb['形式']=='线上'].drop_duplicates()
        self.TB_NON = pd.DataFrame(TB_NON_TEMP[['购买地点']].groupby(TB_NON_TEMP['家庭编号']).apply(countChannel), columns=['NON'])

    # Table of RON
    def _RON(self):
        TB_RON_TEMP = self.tb[['家庭编号', '形式', '单价']]
        TB_RON_TEMP2 = TB_RON_TEMP[['单价']][TB_RON_TEMP['形式']=='线上'].groupby(TB_RON_TEMP['家庭编号']).apply(sum) \
                / TB_RON_TEMP[['单价']].groupby(TB_RON_TEMP['家庭编号']).apply(sum)
        self.TB_RON = TB_RON_TEMP2.fillna(0)
        self.TB_RON.columns = ['RON']
    
    # Table of ON
    def _ON(self):
        TB_ON_TEMP = pd.concat([self.TB_NON,self.TB_NOFF], axis=1).fillna(0)
        self.TB_ON = pd.DataFrame(TB_ON_TEMP['NON']/(TB_ON_TEMP['NON']+TB_ON_TEMP['NOFF']), columns=['ON'])
    
    def _PF(self):
        TB_PF_TEMP = self.tb[['家庭编号', '日期']]        
        _max = pd.to_datetime(TB_PF_TEMP[['日期']].groupby(TB_PF_TEMP['家庭编号']).apply(max)['日期'], format='%Y%m%d', errors='ignore')
        _min = pd.to_datetime(TB_PF_TEMP[['日期']].groupby(TB_PF_TEMP['家庭编号']).apply(min)['日期'], format='%Y%m%d', errors='ignore')
        _count = TB_PF_TEMP[['日期']].groupby(TB_PF_TEMP['家庭编号']).count()
        combine = pd.concat([_max, _min, _count], axis=1)
        combine.columns = ['max', 'min', 'count']
        pf = combine.apply(lambda line: line['count'] \
                              / (abs((line['max'].year - line['min'].year) * 12 \
                                 + (line['max'].month - line['min'].month) * 1) \
                                 + 1),
                            axis = 1)
        self.TB_PF = pd.DataFrame(pf)
        self.TB_PF.columns = ['PF']
        
    def FINAL(self):
        self._CSP()
        self._NB()
        self._Q()
        self._RFB()
        self._NOFF()
        self._ROFF()
        self._NON()
        self._RON()
        self._ON()
        self._PF()
        self.TB_FINAL = pd.concat([self.TB_CSP, 
                          self.TB_NB, 
                          self.TB_Q, 
                          self.TB_RFB, 
                          self.TB_NOFF, 
                          self.TB_ROFF, 
                          self.TB_NON, 
                          self.TB_RON, 
                          self.TB_ON,
                          self.TB_PF], axis=1).fillna(0)
        del self.tb