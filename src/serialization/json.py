import json
import pandas as pd
import datetime


class _JSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        ret = {}
        for key, value in obj.items():
            if key in {'timestamp', 'whatever'}:
                ret[key] = datetime.fromisoformat(value) 
            else:
                ret[key] = value
        return ret

    
class _JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime, pd.Timestamp, )):
            return obj.isoformat()
        return json.JSONEncoder.default(obj)

    
def serialize_df(df: pd.DataFrame):
    json_messages = []
    
    for message in df.to_dict(orient='records'):
        json_messages.append(json.dumps(message, cls=_JSONEncoder))
    
    return json_messages