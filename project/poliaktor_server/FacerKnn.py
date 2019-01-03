import numpy as np
import face_recognition as fr
import pickle
from sklearn.decomposition import PCA
from collections import defaultdict
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


class FacerKnn:

    def __init__(self, model_path, data_path):
        with open(model_path, 'rb') as f:
            self.knn_clf = pickle.load(f)
        df = pd.read_pickle(data_path)

        photo_count = df.groupby('actor').count().enc_0.sort_values(ascending=False)
        top_actors = photo_count[:50].index.values
        top_indexes = df.loc[df.actor.isin(top_actors), :].index

        self.pca = PCA(n_components=2)
        df = df.set_index('actor')
        all_pca = self.pca.fit_transform(df.iloc[:, 2:])
        self.all_actors_pca = pd.DataFrame(all_pca, index=df.index, ).add_prefix('pca_').reset_index()
        self.all_actors_pca.actor = self.all_actors_pca.actor.astype('object')
        self.all_actors_pca.insert(0, 'init', df.initials.values)
        self.top_pca = self.all_actors_pca.loc[top_indexes, :]

        self.names = defaultdict(list)
        for index, row in df.iterrows():
            enc = np.asarray(row.iloc[2:]).astype('float64')
            self.names[index].append((enc, row['photo']))
        self.face_bank = None
        self.found_actors = []
        self.counter = 0
        self.fig = None
        self.reset_plot()
        self.reset_limit = 15
        self.reset_counter = 0
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
        actor_name = path = loc = None
        coord_pca = [None, None]
        enc = fr.face_encodings(candidate_photo)
        if len(enc) == 1:
            loc = fr.face_locations(candidate_photo)[0]
            avg_enc = self.get_average(enc[0], stride)
            res = self.knn_clf.kneighbors(avg_enc, 1, False).item(0)
            init, actor_name, _, _ = self.all_actors_pca.loc[res, :]
            actor_photos = self.names.get(actor_name)
            min_d = 100
            path = None
            for photo in actor_photos:
                dist = fr.face_distance(avg_enc, photo[0])
                if dist < min_d:
                    actor_embedding = photo[0]
                    min_d = dist
                    path = photo[1]

            coord_pca = self.pca.transform(avg_enc[0].reshape(1, -1))[0, ...]
            pca_0, pca_1 = self.pca.transform(actor_embedding.reshape(1, -1))[0, ...]
            plot_data = (pca_0, pca_1, init)
            self.found_actors.append(plot_data)

            loc = {'x': loc[3],
                   'y': loc[2],
                   'wdth': loc[2] - loc[0],
                   'hght': loc[3] - loc[1]}

        if actor_name is None:
            self.reset_counter += 1

        print(self.reset_counter)
        return actor_name, path, loc, coord_pca

    def reset_plot(self):
        self.face_bank = None
        self.found_actors = []
        plt.clf()
        self.fig, self.axarr = plt.subplots(2, figsize=(13, 26))
        faces = self.get_base_pca()
        self.axarr[0].scatter(x=faces.pca_0, y=faces.pca_1, s=1, c='black')
        self.axarr[0].xaxis.label.set_visible(False)
        self.axarr[0].yaxis.label.set_visible(False)

        used = set()
        plt.legend(['Foo', 'bar'])
        legend_elements = []
        for i, (init, name, pca0, pca1) in pd.DataFrame.iterrows(faces):
            self.axarr[0].text(pca0, pca1, init, fontsize=12)
            if init not in used:
                used.add(init)
                legend_elements.append(
                    Line2D([0], [0], marker=f'${init}$', color='k', label=name, markersize=12))

        for arr in self.axarr:
            box = arr.get_position()
            arr.set_position([box.x0, box.y0, box.width * 0.9, box.height * 0.9])
        self.axarr[0].legend(handles=legend_elements, loc='center left', fontsize=11, bbox_to_anchor=(1, 0.5))

    def get_plot(self, x=None, y=None):
        if self.reset_counter >= self.reset_limit:
            print("reseting plot")
            self.reset_plot()

        self.reset_counter = 0

        if x is not None and y is not None:
            self.axarr[0].scatter(x, y, s=200, marker='x', color='red')
            self.axarr[1].scatter(x, y, s=200, marker='x', color='red')
            print(self.found_actors[-1])
            pca_0, pca_1, init = self.found_actors[-1]
            self.axarr[1].scatter(pca_0, pca_1, s=0.001, marker='x', color='black')
            self.axarr[1].text(pca_0, pca_1, init, fontsize=12)
            plt.draw()

        return self.fig
