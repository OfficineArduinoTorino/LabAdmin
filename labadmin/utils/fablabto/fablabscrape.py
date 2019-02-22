import json
import requests
import os.path

from lxml.html import fromstring
from PIL import Image
from io import BytesIO


BASE_URL = 'http://127.0.0.1:8090/Fablab/fablab/Members/'
INTERESTING_FIELDS = (
    'id', 'title', 'description', 'rfid', 'credits', 'address', 'fiscalCode', 'number', 'vat'
)
IDS_TO_SCRAPE = (
    'luogo', 'interessi', 'biografia'
)


def main():
    r = requests.get(BASE_URL + 'get_children')
    users = []
    available_users = [u for u in r.json() if u not in ('user_search', 'admin')]
    for u in available_users:
        r = requests.get(BASE_URL + u + '/get_item')
        data = r.json()
        user = {}
        for field in INTERESTING_FIELDS:
            user[field] = data[field]

        r = requests.get(BASE_URL + u)
        html = fromstring(r.text)
        for html_id in IDS_TO_SCRAPE:
            selection = html.cssselect('#' + html_id)
            if not selection:
                continue
            user[html_id] = selection[0].text_content()

        selection = html.cssselect('.member-portrait img')
        if selection:
            src = selection[0].get('src')
            if not src.endswith('defaultUser.png'):
                r = requests.get(src)
                try:
                    i = Image.open(BytesIO(r.content))
                    outfile = "{}.{}".format(user['id'], i.format.lower())
                    i.save(outfile)
                except:
                    pass
                else:
                    user['immagine'] = os.path.abspath(outfile)

        users.append(user)

    with open('fablabscrape.json', 'w') as f:
        json.dump(users, f)

if __name__ == '__main__':
    main()
