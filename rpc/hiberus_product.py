import requests # $ python -m pip install requests
import json
url = 'http://beds-val.demohiberus.com/rest/products'

data = {
    'pageNumber': 0,
    'pageSize': 100,
    'siteIds': 58,
    'productTypeIds': 1,
    'prices': True,
    'codeOnly': True,
}

username = 'beds'
password = 'Beds2018'

r = requests.post(url, auth=(username, password), data=data) # send auth unconditionally
if r:
    data = r.json()

    print(json.dumps(data, indent=4, sort_keys=True))

else:
    print r
