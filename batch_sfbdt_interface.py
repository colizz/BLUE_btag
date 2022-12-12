import sys,os
import wget
import json

class sfbdt_interface():

    def __init__(self, path='20221201', prefix='bb_ULNanoV9', tagger='PNetXbbVsQCD', suffix='ak8_inclWP', year='2018', **kwargs):
        self.webpath = 'https://coli.web.cern.ch/coli/.cms/btv/boohft-calib/'
        self.file_name = 'sf_full_unce_breakdown.json'
        self.path = path
        self.prefix = prefix
        self.tagger = tagger
        self.suffix = suffix
        self.year = year
    
    def download(self):
        _file = f'{self.webpath}/{self.path}_{self.prefix}_{self.tagger}_{self.suffix}_{self.year}/4_fit/{self.file_name}'
        _store_dir = 'sfbdt_unc'
        if os.path.exists(f'./{_store_dir}'):
            pass
        else:
            os.mkdir(f'./{_store_dir}')
        self.store = f'./{_store_dir}/{self.tagger}_{self.year}.json'
        print(_file)
        if os.path.exists(self.store):
            os.remove(self.store)
        wget.download(_file, self.store)
    
    def convert(self):
        _wp_map = {'tight':'HP', 'medium':'MP', 'loose':'LP'}
        _ptbin_map = {'ptbin1':'pt450to500', 'ptbin2':'pt500to600', 'ptbin3':'pt600to100000'}
        with open(self.store, 'r') as f:
            jsons = json.load(f)
        
        new_jsons = {}
        for _wp in _wp_map.keys():
            _wp_dict = {}
            for _ptbin in _ptbin_map.keys():
                _ptbin_dict = jsons[f'{_wp_map[_wp]}_{_ptbin_map[_ptbin]}']
                _wp_dict[_ptbin] = _ptbin_dict
            new_jsons[_wp] = _wp_dict
        
        with open(self.store, 'w+') as f:
            f.write(json.dumps(new_jsons, indent=4))
    
    def run(self):
        self.download()
        self.convert()

if __name__ == '__main__':
    
    lists ={
        'b_list' : {
        'prefix':['bb_ULNanoV9'],
        'tagger':['PNetXbbVsQCD', 'DDBvLV2', 'DeepAK8ZHbbVsQCD','DoubleB'],
        'year':['2016APV', '2016', '2017', '2018']
        },
        'c_list' : {
        'prefix':['cc_ULNanoV9'],
        'tagger':['PNetXccVsQCD', 'DDCvLV2', 'DeepAK8ZHccVsQCD'],
        'year':['2016APV', '2016', '2017', '2018']
        }
    }
    
    for n in lists:
        xlist = lists[n]
        for prefix in xlist['prefix']:
            for tagger in xlist['tagger']:
                for year in xlist ['year']:
                    p = sfbdt_interface(prefix=prefix, tagger=tagger, year=year)
                    p.run()
    pass

