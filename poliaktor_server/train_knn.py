from sklearn import neighbors
import numpy as np
import json
import math
import pickle
import pandas as pd

df = pd.read_pickle('resources/actors_photos_encodings.pkl')
y = df.loc[:,'actor']
X = df.iloc[:, 3:]

n_neighbors = 7 # int(round(math.sqrt(len(X))))

knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm='ball_tree', weights='distance')
knn_clf.fit(X, y)

with open("resources/knn_model.clf", 'wb') as f:
            pickle.dump(knn_clf, f)
