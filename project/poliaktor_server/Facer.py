import numpy as np
import json
import face_recognition as fr


class Facer:
    def __init__(self, encodings_path, photos_path):
        self.encodings = np.load(encodings_path)
        self.photos = json.load(open(photos_path))

    def find_nearest(self, photo_np):
        enc = fr.face_encodings(photo_np)
        if len(enc) == 1:  # one and only one face found
            dists = fr.face_distance(self.encodings, enc)
            return self.photos[np.argmin(dists)], np.amin(dists)
        else:
            return None
