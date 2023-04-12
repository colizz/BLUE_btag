import sys,os
import wget
import json
import shutil

class mutag_new_interface():

    def __init__(self, tagger='btag', year='2018', input_dir='fit_summary', store_dir='mutag_unc', **kwargs):
        self.tagger = tagger
        self.year = year
        self._input_dir = input_dir
        self._store_dir = store_dir
        self.store = f'./{self._store_dir}/{tagger}_{year}.json'

    def convert(self):
        # map standard to mutag
        _wp_map = {'tight':'Hwp', 'medium':'Mwp', 'loose':'Lwp'}
        _tagger_map = {
            'PNetXbbVsQCD':'particleNetMD_Xbb_QCD',
            'PNetXccVsQCD':'particleNetMD_Xcc_QCD',
            'DDBvLV2':'btagDDBvLV2',
            'DDCvLV2':'btagDDCvLV2',
            'DeepAK8ZHbbVsQCD':'deepTagMD_ZHbbvsQCD',
            'DeepAK8ZHccVsQCD':'deepTagMD_ZHccvsQCD',
            'DoubleB':'btagHbb',
        }
        _ptbin_map = {'ptbin1':'450to500', 'ptbin2':'500to600', 'ptbin3':'600toInf'}
        _year_map = {'2016APV':'2015', '2016':'2016', '2017':'2017', '2018':'2018'}
        # map mutag to standard
        _unc_map ={
            'JER':'jer',
            'JES_Total':'jes',
            'all':'final',
            'frac_l':'fracLight',
            'frac_bb':'fracBB',
            'frac_cc':'fracCC',
            'pileup':'pu',
        }

        new_jsons = {}
        # loop over wp & ptbin
        for _wp in _wp_map.keys():
            _wp_dict = {}
            for _ptbin in _ptbin_map.keys():
                _ptbin_dict = {}
                _input_json = f'events_logsumcorrmass_1_{_year_map[self.year]}_msd40{_tagger_map[self.tagger]}{_wp_map[_wp]}_Pt-{_ptbin_map[_ptbin]}.json'
                if not os.path.exists(f'{self._input_dir}/{_input_json}'):
                    print(f'{self._input_dir}/{_input_json} not Existed!! Please notice')
                else:
                    print(_input_json)
                    with open(f'{self._input_dir}/{_input_json}') as f:
                        jsons = json.load(f)
                        # rename unc
                        for _unc in _unc_map.keys():
                            if _unc in jsons.keys():
                                jsons[_unc_map[_unc]] = jsons.pop(_unc)
                    _ptbin_dict = jsons
                    _wp_dict[_ptbin] = _ptbin_dict
            new_jsons[_wp] = _wp_dict
        
        with open(self.store, 'w+') as f:
            f.write(json.dumps(new_jsons, indent=4))
    
    def run(self):
        self.convert()

if __name__ == '__main__':
    
    lists ={
        'b_list' : {
        'tagger':['PNetXbbVsQCD', 'DDBvLV2', 'DeepAK8ZHbbVsQCD','DoubleB'],
        'year':['2016APV', '2016', '2017', '2018']
        },
        'c_list' : {
        'tagger':['PNetXccVsQCD', 'DDCvLV2', 'DeepAK8ZHccVsQCD'],
        'year':['2016APV', '2016', '2017', '2018']
        }
    }
    
    input_dir = 'fit_summary'
    store_dir = 'mutag_unc'
    
    if os.path.exists(f'./{store_dir}'):
        shutil.rmtree(f'./{store_dir}')
    os.mkdir(f'./{store_dir}')
        
    if not os.path.exists(f'./{input_dir}'):
        raise FileNotFoundError

    for n in lists:
        xlist = lists[n]
        for tagger in xlist['tagger']:
            for year in xlist ['year']:
                p = mutag_new_interface(tagger=tagger, year=year, input_dir=input_dir, store_dir=store_dir)
                p.run()
    pass

