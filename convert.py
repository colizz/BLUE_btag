import csv
import os,sys
import json
import pandas as pd

def csv_to_json(file=None, **kwargs):
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
    pass

if __name__ == '__main__':
    # print(os.listdir('ZbbUncBreakdown'))
    with open('ZJets_bb_breakdown.json', 'w+') as f:
        total_jsons = {}
        for file in os.listdir('ZbbUncBreakdown'):
            if not file.startswith('18_'):
                continue
            ptbin = int(file.split('_')[5].split('.')[0]) + 1
            wp = file.split('_')[1]
            if total_jsons.__contains__(wp):
                total_jsons[wp][f'ptbin{ptbin}'] = csv_to_json(f'ZbbUncBreakdown/{file}')
            else:
                total_jsons[wp]={}
                total_jsons[wp][f'ptbin{ptbin}'] = csv_to_json(f'ZbbUncBreakdown/{file}')
        f.write(json.dumps(total_jsons, indent=4))

    # csv_to_json(file='ZbbUncBreakdown/18_loose_SF_ZJets_bc_0.csv')