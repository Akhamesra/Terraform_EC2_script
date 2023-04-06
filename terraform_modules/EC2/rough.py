import json
count =0 
with open('file1.json') as f:
    data = json.load(f)
    for d in data['resource_changes']:
        if d['type']=='aws_instance':
            count+=1
print(count)
    
