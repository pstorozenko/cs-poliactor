import numpy as np
import json
import face_recognition as fr
import pickle
import os
from sklearn.decomposition import PCA
from collections import defaultdict
import pandas as pd


class FacerKnn:

    def __init__(self, model_path, data_path):
        with open(model_path, 'rb') as f:
            self.knn_clf = pickle.load(f)
        df = pd.read_pickle(data_path).set_index('actor')

        photo_count = df.groupby(df.index).count().sort_values('enc_0', ascending=False).enc_0
        top_actors = photo_count[:50].index
        top_faces = df.loc[top_actors, :]

        self.pca = PCA()
        self.pca.fit(df.iloc[:, 2:])
        faces_components = self.pca.transform(top_faces.loc[:, 'enc_0':])
        self.top_pca = pd.DataFrame(faces_components[:, :2], index=top_faces.index, ).add_prefix('pca_').reset_index()
        self.top_pca.actor = self.top_pca.actor.astype('object')
        self.top_pca.insert(0, 'init', top_faces.initials.values)

        self.names = defaultdict(list)
        for index, row in df.iterrows():
            enc = np.asarray(row.iloc[2:]).astype('float64')
            self.names[index].append((enc, row['photo']))
        self.face_bank = None
        self.counter = 0
        print("FacerKnn initiated")

    def get_base_pca(self):
        return self.top_pca

    def get_average(self, vector, stride):
        if self.face_bank is None:
            self.face_bank = vector.reshape(1, -1)
        else:
            self.face_bank = np.insert(self.face_bank, 0, vector, axis=0)
            if stride < self.face_bank.shape[0]:
                self.face_bank = self.face_bank[:stride, :]

        return [self.face_bank.mean(axis=0)]

    def find_nearest(self, candidate_photo, stride):
        res = path = loc = coord_pca = None
        enc = fr.face_encodings(candidate_photo)
        if len(enc) == 1:
            loc = fr.face_locations(candidate_photo)[0]
            avg_enc = self.get_average(enc[0], stride)
            res = self.knn_clf.predict(avg_enc)
            actor_photos = self.names.get(res[0])
            min_d = 100
            path = None
            for photo in actor_photos:
                dist = fr.face_distance(avg_enc, photo[0])
                if dist < min_d:
                    min_d = dist
                    path = photo[1]

            coord_pca = self.pca.transform(avg_enc[0].reshape(1, -1))[0, :2]

            loc = {'x': loc[3],
                   'y': loc[2],
                   'wdth': loc[2] - loc[0],
                   'hght': loc[3] - loc[1]}

        return res, path, loc, coord_pca
