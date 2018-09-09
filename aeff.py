import json
from datetime import datetime,date

def serialize(obj): #json serializator
    if isinstance(obj,date): return obj.isoformat()
    if isinstance(obj,datetime): return obj.isoformat()
    if isinstance(obj,bytes): return str(obj,"utf8")
    return obj.__dict__

now=datetime.now()
dd=date(1983,5,20)
a=dict(d=dd,now=now,b=b"kkk")
a=json.dumps(a,default=serialize)
print(a)
a=json.loads(a)
