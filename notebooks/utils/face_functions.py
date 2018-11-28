import face_recognition

def face_to_vec(path):
    picture_of_me = face_recognition.load_image_file(path)
    return face_recognition.face_encodings(picture_of_me)[0]
