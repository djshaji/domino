import face_recognition
import sys
import db

class FR:
    def recognize (self, filename):
        image = face_recognition.load_image_file(filename)
        return face_recognition.face_encodings(image)
    
    def get_faces (self, filename):
        image = face_recognition.load_image_file(filename)        
        return face_recognition.face_locations(image)

    def compare (self, face1, face2):
        return face_recognition.compare_faces([face1], face2)
    
    def compare_many (self, faces, face):
        return face_recognition.compare_faces(faces, face2)

class FRTrainer:
    db = DB ()
    
