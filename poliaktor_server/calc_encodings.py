import face_recognition as fr
import numpy as np
import glob
from PIL import Image
import pandas as pd


photos = glob.glob('images/*/*')
cols = ["actor", "photo"] + ["enc_" + str(i) for i in range(128)]
df = pd.DataFrame(columns = cols)
i = 0
for _, photo in enumerate(photos):
    print("Photo {} out of {}".format(i, (len(photos) - 1)))

    start = photo.find('/')
    end = photo.find('/', start + 1)
    actor = photo[start+1:end]
    try:
        img = np.asarray(Image.open(photo).convert('RGB'))
        enc = fr.face_encodings(img)
        encoding = enc[0]

        record = [actor, photo] + list(encoding)
        df.loc[i] = record
        i += 1
    except Exception as e:
        print(e)
    
df.to_pickle("actors_photos_encodings.pkl")
