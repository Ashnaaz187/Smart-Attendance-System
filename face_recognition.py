import os
import cv2
import numpy as np
import pickle
from keras_facenet import FaceNet

embedder = FaceNet()

DATASET_PATH = "dataset"
EMBEDDINGS_PATH = "embeddings/embeddings.pkl"


def create_embeddings():
    os.makedirs("embeddings", exist_ok=True)  # ✅ FIX

    embeddings = []
    labels = []

    for person in os.listdir(DATASET_PATH):
        person_path = os.path.join(DATASET_PATH, person)

        for img_name in os.listdir(person_path):
            img_path = os.path.join(person_path, img_name)
            img = cv2.imread(img_path)

            if img is None:
                continue

            img = cv2.resize(img, (160, 160))
            embedding = embedder.embeddings([img])[0]

            embeddings.append(embedding)
            labels.append(person)

    with open(EMBEDDINGS_PATH, "wb") as f:
        pickle.dump((embeddings, labels), f)

    print("Embeddings created!")


def recognize_face(face_img):
    if not os.path.exists(EMBEDDINGS_PATH):
        return "No Data"

    with open(EMBEDDINGS_PATH, "rb") as f:
        embeddings, labels = pickle.load(f)

    face_img = cv2.resize(face_img, (160, 160))
    emb = embedder.embeddings([face_img])[0]

    min_dist = float("inf")
    identity = "Unknown"

    for i, db_emb in enumerate(embeddings):
        dist = np.linalg.norm(emb - db_emb)

        if dist < min_dist:
            min_dist = dist
            identity = labels[i]

    if min_dist > 1.0:
        return "Unknown"

    return identity