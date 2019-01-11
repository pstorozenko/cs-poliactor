from FacerKnn import FacerKnn
import face_recognition as fr
import glob
import numpy as np
import os
from PIL import Image
import pandas as pd

fn = FacerKnn('../resources/knn_model.clf', '../resources/actors_photos_encodings.pkl')

people = os.listdir('photos')
data = pd.read_pickle('../resources/actors_photos_encodings.pkl')
points = []
for person in people:
    photos = glob.glob('photos/'+person + '/*')
    person_embs = []
    nearest_embs = []
    for photo in photos:
        print(photo)
        try:
            photo_np = np.array(Image.open(photo).convert('RGB'))
            enc_l = fr.face_encodings(np.array(photo_np))
            if len(enc_l) != 1:
                os.remove(photo)
            else:
                enc = enc_l[0]
                nearest = fn.find_nearest(photo_np, 1)
                r = data[data.photo == nearest[1]]
                r = np.array(r.iloc[0, 3:].astype(np.float))
                person_embs.append(enc)
                nearest_embs.append(r)

        except Exception as e:
            print(e)
    person_embs_arr = np.array(person_embs)
    nearest_embs_arr = np.array(nearest_embs)

    for per, near in zip(person_embs, nearest_embs):
        tmp_per = np.sqrt(((person_embs_arr - per) ** 2).mean(axis=1))
        tmp_near = np.sqrt(((nearest_embs_arr - per) ** 2).mean(axis=1))
        for x, y in zip(tmp_per, tmp_near):
            points.append((person, x, y))

df = pd.DataFrame(points)
df.columns = ['Person', 'x', 'y']
df.to_csv('stability2_pd_df.csv', index=False)
