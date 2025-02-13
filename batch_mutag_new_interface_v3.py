import sys,os
import json
import shutil

class mutag_new_interface():

    def __init__(self, tagger='btag', year='2018', input_json=None, store_dir='mutag_unc', **kwargs):
        self.tagger = tagger
        self.year = year
        self._input_json = input_json
        self._store_dir = store_dir
        if year == '2016_PreVFP':
            year = '2016APV'
        if year == '2016_PostVFP':
            year = '2016'
        self.store = f'./{self._store_dir}/{tagger}_{year}.json'

    def convert(self):
        # map standard to mutag
        _wp_map = {'tight':'H', 'medium':'M', 'loose':'L'}
        _ptbin_map = {'ptbin1':'450to500', 'ptbin2':'500to600', 'ptbin3':'600toInf'}
        # map mutag to standard
        _unc_map ={
            'JER':'jer',
            'JES_Total':'jes',
            'lumi': 'lumi_13TeV',
            'all':'final',
            'frac_l':'fracLight',
            'frac_bb':'fracBB',
            'frac_cc':'fracCC',
            'pileup':'pu',
            'sf_L1prefiring': 'l1PreFiring',
            'psWeight_isr': 'psWeightIsr',
            'psWeight_fsr': 'psWeightFsr',
            'stat':'stats'
        }

        new_jsons = {}
        # loop over wp & ptbin
        for _wp in _wp_map.keys():
            _wp_dict = {}
            for _ptbin in _ptbin_map.keys():
                # rename unc
                for _unc in _unc_map.keys():
                    if _unc in self._input_json[_ptbin_map[_ptbin]][_wp_map[_wp]].keys():
                        self._input_json[_ptbin_map[_ptbin]][_wp_map[_wp]][_unc_map[_unc]] = self._input_json[_ptbin_map[_ptbin]][_wp_map[_wp]].pop(_unc)
                _wp_dict[_ptbin] = self._input_json[_ptbin_map[_ptbin]][_wp_map[_wp]]
                if self.year == '2018':
                    _wp_dict[_ptbin]['l1PreFiring'] = {'high':0.0, 'low':0.0}
            new_jsons[_wp] = _wp_dict
        
        with open(self.store, 'w+') as f:
            f.write(json.dumps(new_jsons, indent=4))
    
    def run(self):
        self.convert()

if __name__ == '__main__':
    
    lists ={
        'b_list' : {
        'tagger':['PNetXbbVsQCD', 'DDBvLV2', 'DeepAK8ZHbbVsQCD','DoubleB'],
        'year':['2016_PreVFP', '2016_PostVFP', '2017', '2018']
        },
        'c_list' : {
        'tagger':['PNetXccVsQCD', 'DDCvLV2', 'DeepAK8ZHccVsQCD'],
        'year':['2016_PreVFP', '2016_PostVFP', '2017', '2018']
        }
    }
    
    _tagger_map = {
        'PNetXbbVsQCD':'particleNetMD_Xbb_QCD',
        'PNetXccVsQCD':'particleNetMD_Xcc_QCD',
        'DDBvLV2':'btagDDBvLV2',
        'DDCvLV2':'btagDDCvLV2',
        'DeepAK8ZHbbVsQCD':'deepTagMD_ZHbbvsQCD',
        'DeepAK8ZHccVsQCD':'deepTagMD_ZHccvsQCD',
        'DoubleB':'btagHbb',
    }


    input_dir = 'mutag_input'
    store_dir = 'mutag_unc'
    
    if os.path.exists(f'./{store_dir}'):
        shutil.rmtree(f'./{store_dir}')
    os.mkdir(f'./{store_dir}')
        
    if not os.path.exists(f'./{input_dir}'):
        raise FileNotFoundError

    with open(f'{input_dir}/logsumcorrmass_final_results.json', 'r') as f:
    # with open(f'{input_dir}/logsv1mass_final_results.json', 'r') as f:
        jsons = json.load(f)
    for n in lists:
        xlist = lists[n]
        for tagger in xlist['tagger']:
            for year in xlist ['year']:
                input_json = jsons[year][_tagger_map[tagger]]
                p = mutag_new_interface(tagger=tagger, year=year, input_json=input_json, store_dir=store_dir)
                p.run()
    pass

