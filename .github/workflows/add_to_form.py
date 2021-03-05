import os
import sys
import yaml
import json
import pandas as pd
import numpy as np

config = yaml.safe_load(open('./.forms.yml'))
context = json.load(open(sys.argv[1]))

def typetodtype(t):
    if t == 'text':
        return str
    if t == 'number':
        return np.float64
    if t == 'date':
        return str
        
if os.path.exists(config['output']['file']):

    data = pd.read_csv(
        config['output']['file'],
        dtype={
            '_username': str,
            '_date': str,
            **{
                field['name']: typetodtype(field['type'])
                for field in config['fields']
            } 
        },
        parse_dates=['_date'] + [
            field['name']
            for field in config['fields']
            if field['type'] == 'date'
        ]
    )
else:
    data = pd.DataFrame(
        {
            '_username': pd.Series([], dtype=str),
            '_date': pd.Series([], dtype=str),
            **{
                field['name']: pd.Series([], dtype=typetodtype(field['type']))
                for field in config['fields']
            } 
        }
    )

body = json.loads(context['event']['issue']['body'])  # TODO maybe not JSON? why JSON?
data = data.append(pd.DataFrame([body | {
    '_username': context['event']['issue']['user']['login'],
    '_date': pd.to_datetime(context['event']['issue']['created_at']),
}]), ignore_index=False)

data.to_csv(config['output']['file'], index=False)