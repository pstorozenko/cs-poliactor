import os
import glob

files = glob.glob('videos/*')

for file_f in files:
    file = os.path.basename(file_f)
    os.mkdir('photos/' + file[0:-4])
    command = 'ffmpeg -i ' + file_f + ' -r 2 ' + 'photos/' + file[0:-4] + '/%04d.jpeg'
    os.system(command)


