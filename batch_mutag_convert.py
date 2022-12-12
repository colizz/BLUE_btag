import sys,os
import json

class mutag_interface():

    def __init__(self, path='', tagger='btagDDBvLV2', year='2018UL_all', **kwargs):
        self.path = path
        self.tagger = tagger
        self.year = year
        tagger_map = {
            'ParticleNetMD_Xbb_QCD': 'PNetXbbVsQCD',
            'ParticleNetMD_Xcc_QCD': 'PNetXccVsQCD',
            'btagDDBvLV2': 'DDBvLV2',
            'btagDDCvLV2': 'DDCvLV2',
            'deepTagMD_ZHbbvsQCD': 'DeepAK8ZHbbVsQCD',
            'deepTagMD_ZHccvsQCD': 'DeepAK8ZHccVsQCD',
            'btagHbb': 'DoubleB',
            # 'DoubleB': 'DoubleB'
        }
        year_map = {
            '2016UL_PostVFP_all_v01':'2016',
            '2016UL_PreVFP_all':'2016APV',
            '2017UL_all_v01':'2017',
            '2018UL_all':'2018',
        }
        _store_dir = 'mutag_unc'
        if os.path.exists(f'./{_store_dir}'):
            pass
        else:
            os.mkdir(f'./{_store_dir}')
        self.store = f'./{_store_dir}/{tagger_map[self.tagger]}_{year_map[self.year]}.json'
    
    def convert(self):
        unc_map = {
            "JER":"jer",
            "JES_Total":"jes",
            "frac_bb":"fracBB",
            "frac_cc":"fracCC",
            "frac_l":"fracLight",
            "pileup":"pu",
            "frac_cc":"fracCC",
            'lumi':"lumi_13TeV",
            'sf_L1prefiring':"l1PreFiring",
            "stat":"stats",
            "all":"final"
        }
        new_jsons = {}
        _wp_map = {'H':'tight', 'M':'medium', 'L':'loose'}
        _ptbin_map= {'Pt-450to500':'ptbin1', 'Pt-500to600':'ptbin2', 'Pt-600toInf':'ptbin3'}

        for _wp in _wp_map.keys():
            _wp_dict = {}
            for _ptbin in _ptbin_map.keys():
                _input_json = f'{self.path}/{self.year}/fitdir/msd40{self.tagger}{_wp}wp_{_ptbin}/breakdown.json'
                if os.path.exists(_input_json):
                    with open(_input_json, 'r') as f:
                        _ptbin_dict = json.load(f)
                    for key in _ptbin_dict.keys():
                        if unc_map.__contains__(key):
                            _ptbin_dict[unc_map[key]] = _ptbin_dict[key]
                            del _ptbin_dict[key]
                    _wp_dict[_ptbin_map[_ptbin]] = _ptbin_dict
                    new_jsons[_wp_map[_wp]] = _wp_dict
                    with open(self.store, 'w+') as f:
                        f.write(json.dumps(new_jsons, indent=4))
                else:
                    print(f'{_input_json} not exists, skipping')

    def run(self):
        self.convert()

if __name__ == '__main__':
    path = '/afs/cern.ch/user/m/mmarcheg/public/BTV/ScaleFactors/'
    lists ={
        'b_list' : {
        'tagger':['ParticleNetMD_Xbb_QCD', 'btagDDBvLV2', 'deepTagMD_ZHbbvsQCD', 'btagHbb'],
        'year':['2016UL_PostVFP_all_v01', '2016UL_PreVFP_all', '2017UL_all_v01', '2018UL_all']
        },
        'c_list' : {
        'tagger':['ParticleNetMD_Xcc_QCD', 'btagDDCvLV2', 'deepTagMD_ZHccvsQCD' ],
        'year':['2016UL_PostVFP_all_v01', '2016UL_PreVFP_all', '2017UL_all_v01', '2018UL_all']
        }
    }
    for n in lists:
        xlist = lists[n]
        for tagger in xlist['tagger']:
            for year in xlist ['year']:
                p = mutag_interface(path=path, tagger=tagger, year=year)
                p.run()
    p = mutag_interface(path=path)
    p.run()