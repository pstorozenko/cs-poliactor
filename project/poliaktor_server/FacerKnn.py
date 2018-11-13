import numpy as np
import json
import face_recognition as fr
import pickle
import os
from collections import defaultdict


class FacerKnn:
    def __init__(self, model_path, encodings_path, photos_path):
        with open(model_path, 'rb') as f:
            self.knn_clf = pickle.load(f)
        encodings = np.load(encodings_path)
        photos = json.load(open(photos_path))
        self.names = defaultdict(list)
        for i, photo in enumerate(photos):
            file_base = os.path.basename(photo)
            end = file_base.find('_')
            self.names[file_base[:end]].append((encodings[i], photo))
        print("FacerKnn initiated")

    def find_nearest(self, candidate_photo):
        enc = fr.face_encodings(candidate_photo)
        if len(enc) == 1:
            res = self.knn_clf.predict(enc)
            actor_photos = self.names.get(res[0])
            min_d = 100
            path = None
            for photo in actor_photos:
                dist = fr.face_distance(enc, photo[0])
                if dist < min_d:
                    min_d = dist
                    path = photo[1]

            return res, path
        else:
            return None
