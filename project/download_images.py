import os, glob, json
from urllib.request import urlretrieve

files = glob.glob('data_jsons/*.json')

try:
    os.mkdir('images')
except Exception as e:
    print(e)

for file in files:
    with open(file) as f:
        data = json.load(f)
        for person, links in data.items():
            if person not in os.listdir('images'):
                print('Downloading', person, '...')
                try:
                    os.mkdir('images/' + person)
                except Exception as e:
                    print(e)
                for i, link in enumerate(links):
                    print('\tPhoto', i)
                    try:
                        res = urlretrieve(link, 'images/' + person + '/' + str(i) + '.jpg')
                    except Exception as e:
                        print(e)
