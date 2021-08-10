import requests # $ python -m pip install requests
import json

url = 'http://beds-val.demohiberus.com/rest/promotions'

data = {
    'pageNumber': 0,
    'pageSize': 10,
}

username = 'beds'
password = 'Beds2018'

r = requests.post(url, auth=(username, password), data=data)

if r:
    data = r.json()

    print(json.dumps(data, indent=4, sort_keys=True))

else:
    print r
