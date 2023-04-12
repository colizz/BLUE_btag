import csv
import os,sys
import json
import pandas as pd

class Zbb_interface():
    def __init__(self, year='18', tagger='ParticleNet', path='/afs/cern.ch/work/s/sdeng/sftp/sfbdt/BLUE_btag/Zbb_input/Zbb_unc/', **kwargs):
        self.year = year
        self.path = path
        self.tagger = tagger
        tagger_map = {
            'ParticleNet': 'PNetXbbVsQCD',
            'DeepDoubleX': 'DDBvLV2',
            'DoubleB': 'DoubleB'
        }
        _store_dir = 'Zbb_unc'
        if os.path.exists(f'./{_store_dir}'):
            pass
        else:
            os.mkdir(f'./{_store_dir}')
        self.store = f'./{_store_dir}/{tagger_map[self.tagger]}_20{self.year}.json'

    def csv_to_json(self, file='', **kwargs):
        central = pd.read_csv(file, nrows=0).columns[0].split('=')[1]
        # print(central)

        column_index = ['FreezeAllhigh', 'FreezeAlllow', 'high', 'low']
        csv = pd.read_csv(file, names=column_index, index_col=0, skiprows=2)
        # csv = pd.read_csv(file, skiprows=1)
        jsons = {}
        
        unc_map = {
            "Total":"final",
            'lumi':"lumi_13TeV",
            "puUnc":"pu",
            "FSR":"psWeightFsr",
            "ISR":"psWeightIsr"
        }

        csv.rename(index=unc_map, inplace=True)

        jsons = csv.to_dict(orient = 'index')
        jsons['stats']={}
        jsons['stats']['high'] = jsons['trig']['FreezeAllhigh']
        jsons['stats']['low'] = jsons['trig']['FreezeAlllow']
        jsons['final']['central']=central
        jsons['final']['high']=jsons['final']['FreezeAllhigh']
        jsons['final']['low']=jsons['final']['FreezeAlllow']
        # print(jsons)
        # print(csv.index)
        return jsons
    
    def combine_json_year(self, **kwargs):
        new_jsons = {}
        _wp_list = ['tight','medium','loose']
        _ptbin_map= {'0':'ptbin1', '1':'ptbin2', '2':'ptbin3'}
        for _wp in _wp_list:
            _wp_dict = {}
            for _ptbin in _ptbin_map.keys():
                _csv_file = f'{self.path}/{self.tagger}/ZbbuncBreakdown/{self.year}_{_wp}_SF_ZJets_bc_{_ptbin}.csv'
                if os.path.exists(_csv_file):
                    _ptbin_dict = self.csv_to_json(_csv_file)
                    _wp_dict[_ptbin_map[_ptbin]] = _ptbin_dict
                else:
                    print(f'{_csv_file} not exists, skipping')
            new_jsons[_wp] = _wp_dict
            with open(self.store, 'w+') as f:
                f.write(json.dumps(new_jsons, indent=4))
        pass
    
    def run(self):
        self.combine_json_year()

if __name__ == '__main__':
    lists ={
        'b_list' : {
        'tagger':['ParticleNet', 'DeepDoubleX','DoubleB'],
        'year':['16APV', '16', '17', '18']
        },
    }
    for n in lists:
        xlist = lists[n]
        for tagger in xlist['tagger']:
            for year in xlist['year']:
                p = Zbb_interface(year=year, tagger=tagger)
                p.run()
    pass
