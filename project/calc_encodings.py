import face_recognition as fr
import numpy as np
import glob
from PIL import Image
import json
import pandas as pd
import os


photos = glob.glob('images/*/*')
cols = ["actor", "photo"] + ["enc_" + str(i) for i in range(128)]
df = pd.DataFrame(columns = cols)

for i, photo in enumerate(photos):
    print(f"Photo {i} out of {len(photos) - 1}")

    start = photo.find('/')
    end = photo.find('/', start + 1)
    actor = photo[start+1:end]

    img = np.asarray(Image.open(photo).convert('RGB'))
    enc = fr.face_encodings(img)
    encoding = enc[0]

    record = [actor, photo] + list(encoding)
    df.loc[i] = record
    
df.to_pickle("actors_photos_encodings.pkl")
