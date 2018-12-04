import numpy as np
import json
import face_recognition as fr
import pickle
import os
from collections import defaultdict
import pandas as pd


class FacerKnn:

    def __init__(self, model_path, data_path):
        with open(model_path, 'rb') as f:
            self.knn_clf = pickle.load(f)
        df = pd.read_pickle(data_path)

        self.names = defaultdict(list)
        for index, row in df.iterrows():
            enc = np.asarray(row.iloc[2:])
            self.names[row['actor']].append((enc, row['photo']))

        print("FacerKnn initiated")

    def find_nearest(self, candidate_photo):
        res = path = loc = None
        enc = fr.face_encodings(candidate_photo)
        if len(enc) == 1:
            loc = fr.face_locations(candidate_photo)[0]
            res = self.knn_clf.predict(enc)
            actor_photos = self.names.get(res[0])
            min_d = 100
            path = None
            for photo in actor_photos:
                dist = fr.face_distance(enc, photo[0])
                if dist < min_d:
                    min_d = dist
                    path = photo[1]

            loc = {'x': loc[3],
                   'y': loc[2],
                   'wdth': loc[2] - loc[0],
                   'hght': loc[3] - loc[1]}

        return res, path, loc
