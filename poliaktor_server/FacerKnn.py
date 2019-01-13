import pickle
import numpy as np
import pandas as pd
import face_recognition as fr
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from sklearn.decomposition import PCA
from collections import defaultdict


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
        self.display_bank = None
        self.colnames = ['init', 'name', *df.iloc[:, 2:].columns.values]
        self.found_actors = pd.DataFrame(columns=self.colnames)
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

        face_mean = self.face_bank.mean(axis=0)

        if self.display_bank is None:
            self.display_bank = vector.reshape(1, -1)
        else:
            self.display_bank = np.insert(self.display_bank, 0, face_mean, axis=0)

        return [face_mean]

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
            plot_data = [init, actor_name, *actor_embedding]
            self.found_actors.loc[len(self.found_actors)] = plot_data

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
        self.display_bank = None
        self.found_actors = pd.DataFrame(columns=self.colnames)
        plt.clf()
        self.fig, self.axarr = plt.subplots(2, figsize=(13, 23))
        faces = self.get_base_pca()
        self.axarr[1].scatter(x=faces.pca_0, y=faces.pca_1, s=1, c='black')
        self.axarr[1].xaxis.label.set_visible(False)
        self.axarr[1].yaxis.label.set_visible(False)
        for ax in self.axarr:
            ax.tick_params(axis='both',          # changes apply to the x-axis
                                  which='both',      # both major and minor ticks are affected
                                  labelbottom=False,
                                  labeltop=False,
                                  labelleft=False,
                                  labelright=False)  # labels along the bottom edge are off)

        used = set()
        legend_elements = []
        for i, (init, name, pca0, pca1) in pd.DataFrame.iterrows(faces):
            self.axarr[1].text(pca0, pca1, init, fontsize=12)
            if init not in used:
                used.add(init)
                legend_elements.append(
                    Line2D([0], [0], marker=f'${init}$', color='k', label=name, markersize=12))

        for arr in self.axarr:
            box = arr.get_position()
            arr.set_position([box.x0, box.y0, box.width * 0.9, box.height * 0.9])
        self.axarr[1].legend(handles=legend_elements, loc='center left', fontsize=11, bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        plt.subplots_adjust(wspace=0, hspace=0)

    def get_plot(self, x=None, y=None):
        if self.reset_counter >= self.reset_limit:
            print("reseting plot")
            self.reset_plot()
            self.reset_counter = 0
        elif x is not None and y is not None:
            self.reset_counter = 0
            self.axarr[1].scatter(x, y, s=200, marker='x', color='red')

            if self.display_bank.shape[0] > 2:
                faces, actors = self.compute_tsne()
                self.axarr[0].clear()
                self.axarr[0].scatter(faces[:, 0], faces[:, 1], s=200, marker='x', color='red')

                used = set()
                legend_elements = []
                for i, (tsne0, tsne1, init, name) in pd.DataFrame.iterrows(actors):
                    self.axarr[0].scatter(tsne0, tsne1, s=0.001, marker='x', color='black')
                    self.axarr[0].text(tsne0, tsne1, init, fontsize=12)
                    if init not in used:
                        used.add(init)
                        legend_elements.append(
                            Line2D([0], [0], marker=f'${init}$', color='k', label=name, markersize=12))

                self.axarr[0].legend(handles=legend_elements, loc='center left', fontsize=11, bbox_to_anchor=(1, 0.5))
                plt.savefig('example.png')

            plt.draw()

        return self.fig

    def compute_tsne(self):
        whole_data = np.vstack((self.display_bank, self.found_actors.iloc[:, 2:].values))
        # embedding = umap.UMAP(n_neighbors=min(floor(whole_data.shape[0]/2), 5),
        #                       min_dist=0.3,
        #                       metric='correlation').fit_transform(whole_data)
        # embedding = TSNE(n_components=2).fit_transform(whole_data)
        embedding = PCA(n_components=2).fit_transform(whole_data)

        faces = np.array(embedding[:self.display_bank.shape[0], :])
        actors = pd.DataFrame(embedding[self.display_bank.shape[0]:, :], columns=['v1', 'v2'])
        actors.loc[:, 'init'] = self.found_actors.init
        actors.loc[:, 'name'] = self.found_actors.name

        return faces, actors



