import os,sys
import numpy as np
import pandas as pd
import json
import argparse
import logging
from decimal import Decimal

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description='Prepare BLUE combination')
parser.add_argument('-f', dest='file', default='summary_bb_dict.json', help='input summary json file')
parser.add_argument('-p', dest='path', default='./', help='input path which store all configurations')
# parser.add_argument('-w', dest='wp', default='loose', help='working point')
args = parser.parse_args()

class BLUE_combine():

    def __init__(self, unc_dict={}, tagger='DoubleB', year="2018", wp='loose', input_dir='./', **kwargs):
        self._unc_dict = unc_dict
        self._year = year
        self._tagger = tagger
        self._wp = wp.lower()
        self._unc_lists = []
        self._ptbins = self._unc_dict['ptbins']
        self._Ucolumn_index = [f'ptbin{ptbin}' for ptbin in range(1, self._ptbins+1)]
    
        self._store = f'./Combine_{self._tagger}_{wp}_{self._year}.txt'

        self.methods = []
        for method in self._unc_dict['methods']:
            _input_json = f'{input_dir}/{self._unc_dict["methods"][method]["input_prefix"]}/{self._tagger}_{self._year}.json'
            logging.info(f'loading {_input_json}')

            # Reorganize index since some wp/ptbin doesn't included for specific method
            if os.path.exists(_input_json):
                with open(f'{_input_json}', 'r') as f:
                    self._unc_dict['methods'][method]['input_json'] = json.load(f)
                if self._unc_dict['methods'][method]['input_json'].__contains__(self._wp):
                    if self._unc_dict['methods'][method]['input_json'][self._wp]:
                        self._unc_lists.extend(self._unc_dict['methods'][method]['uncertainty_list'])
                        self.methods.append(method)
                else:
                    logging.info(f'{self._year}/{self._tagger}/{method} doesn\'t include wp {self._wp}')

            else:
                logging.info(f'{self._year}/{self._tagger} doesn\'t include method {method}')

                
        self._Cindex = [f'{method}_ptbin{ptbin}' for ptbin in range(1, self._ptbins+1) for method in self.methods]
        self._Urow_index = [f'{method}_ptbin{ptbin}' for ptbin in range(1, self._ptbins+1) for method in self.methods]

        self._unc_lists = set(self._unc_lists)
        pass

    def BuildCovarianceMatrix(self, **kwargs):

        def _CompareString(input1, input_array):
            for input2 in input_array:
                if input1.lower() == input2.lower():# or input2.lower() in input1.lower():
                    return True 
            return False

        def _BuildBlock(row=(0,0), column=(0,0), **kwargs):
            logging.info(f'Constructing block for row {row} and column {column}')
            sigma = 0.
            methods = self._unc_dict['methods']
            for unc_type in self._unc_lists:
                unc_isExist = True
                if not _CompareString(unc_type, methods[row[0]]['uncertainty_list']):
                    logging.info(f'{row[0]} doesn\'t include {unc_type}, skipping')
                    unc_isExist = False
                if not _CompareString(unc_type, methods[column[0]]['uncertainty_list']):
                    logging.info(f'{column[0]} doesn\'t include {unc_type}, skipping')
                    unc_isExist = False
                if not unc_isExist: continue
                row_sigma = (float(methods[row[0]]['input_json'][self._wp][f'ptbin{row[1]}'][unc_type]['high']) + float(methods[row[0]]['input_json'][self._wp][f'ptbin{row[1]}'][unc_type]['low'])) / 2
                column_sigma = (float(methods[column[0]]['input_json'][self._wp][f'ptbin{column[1]}'][unc_type]['high']) + float(methods[column[0]]['input_json'][self._wp][f'ptbin{column[1]}'][unc_type]['low'])) / 2
                if row[0]==column[0] and row[1]==column[1]:
                    sigma += row_sigma * column_sigma
                else:
                    # correlation across bin
                    if self._unc_dict['correlation'].__contains__(unc_type):
                        sigma += row_sigma * column_sigma * np.sqrt(self._unc_dict['correlation'][unc_type])
                    else:
                        #*FIXME*
                        sigma += 0
            return sigma
            pass

        tuple_method_ptbin = [(method, ptbin) for ptbin in range(1, self._ptbins+1) for method in self.methods ]
        CMatrix = np.zeros((len(self._Cindex), len(self._Cindex)))
        CMatrix = pd.DataFrame(CMatrix, columns=self._Cindex, index=self._Cindex)

        for _row_index in range(len(tuple_method_ptbin)):
            for _column_index in range(_row_index, len(tuple_method_ptbin)):
                CMatrix.iloc[_row_index,_column_index] = _BuildBlock(row=tuple_method_ptbin[_row_index], column=tuple_method_ptbin[_column_index])
        
        CMatrix = CMatrix + CMatrix.T - pd.DataFrame(np.diag(np.diag(CMatrix)), columns=self._Cindex, index=self._Cindex)
        # print(CMatrix)
        return(CMatrix)

    def BuildUMatrix(self, **kwargs):
        # U_{ia}, 1 if Y_i is a measurement of the observable X_a, 0 otherwise.
        # Observables: each sigma in each method in each pt bin
        # Measurements: each pt bin
        _a = len(self.methods)*self._ptbins
        _i = self._ptbins
        UMatrix = []
        for i in range(1, self._ptbins+1):
            temp_array = []
            for ptbin in range(1, self._ptbins+1):
                for method in self.methods:
                    U_ia = 1 if i==ptbin else 0 
                    temp_array.append(U_ia)
            UMatrix.append(temp_array)
        UMatrix = np.matrix(UMatrix).T

        # use pandas to create index
        UMatrix = pd.DataFrame(UMatrix, columns=self._Ucolumn_index, index=self._Urow_index)
        # print(UMatrix)
        return UMatrix
        pass

    def BuildObservable(self, **kwargs):
        OCentral, OHigh, OLow = [], [], []
        for ptbin in range(1, self._ptbins+1):
            for method in self.methods:
                OCentral.append(float(self._unc_dict['methods'][method]['input_json'][self._wp][f'ptbin{ptbin}']['final']['central']))
                OHigh.append(float(self._unc_dict['methods'][method]['input_json'][self._wp][f'ptbin{ptbin}']['final']['high']))
                OLow.append(float(self._unc_dict['methods'][method]['input_json'][self._wp][f'ptbin{ptbin}']['final']['low']))
        OCentral = np.matrix(OCentral).T
        OHigh = np.matrix(OHigh).T
        OLow = np.matrix(OLow).T
        return OCentral, OHigh, OLow



    def run(self, **kwargs):
        UMatrix = np.matrix(self.BuildUMatrix())
        CMatrix = np.matrix(self.BuildCovarianceMatrix())
        lambda_ai = (UMatrix.T * CMatrix.I * UMatrix).I * (UMatrix.T * CMatrix.I)
        # print(f'Weight Matrix: {lambda_ai}')
        
        OCentral, OHigh, OLow = self.BuildObservable()
        # print(f'Original Observables: {OCentral} ')
        # print(f'Original up: {OHigh} ')
        # print(f'Original down: {OLow} ')
        X = pd.DataFrame(lambda_ai * OCentral, index=[f'ptbin{ptbin}' for ptbin in range(1,self._ptbins+1)], columns=['Combine Scale Factor'])
        # print(X)
        # XHigh = pd.DataFrame(lambda_ai * CMatrix * lambda_ai.T, index=[f'ptbin{ptbin}' for ptbin in range(1,self._ptbins+1)], columns=['Combine Scale Factor Up'])
        # XLow = pd.DataFrame(lambda_ai * CMatrix * lambda_ai.T, index=[f'ptbin{ptbin}' for ptbin in range(1,self._ptbins+1)], columns=['Combine Scale Factor Down'])
        # print(XHigh)
        # print(XLow)
        # print(np.sqrt(lambda_ai * CMatrix * lambda_ai.T))
        with open(self._store, 'w+') as f:
            f.write(f'UMatrix:\n {self.BuildUMatrix()}\n')
            f.write(f'CMatrix:\n {self.BuildCovarianceMatrix()}\n')
            f.write(f'Weight Matrix:\n {lambda_ai}\n')
            f.write(f'Original Observables:\n {OCentral}\n')
            f.write(f'Original up:\n {OHigh}\n')
            f.write(f'Original down:\n {OLow}\n ')
            f.write(f'\nFinal SF: {X}')
            f.write(f'\nFinal Variance: {np.diagonal(np.sqrt(lambda_ai * CMatrix * lambda_ai.T))}')
        pass

if __name__ == '__main__':
    logging.info(f'loading {args.path+args.file} for utils configurations')
    with open(args.path+args.file, 'r') as f:
        jsons = json.load(f)
    for tagger in jsons['tagger']:
        for year in jsons['year']:
            for wp in jsons['wp']:
                print(tagger, year, wp)
                BLUE_btag = BLUE_combine(unc_dict=jsons, tagger=tagger, year=year, wp=wp, input_dir=args.path)
                BLUE_btag.run()
