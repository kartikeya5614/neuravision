"""
NEURAVISION — Face Engine (DeepFace Edition)
No dlib, no compilation, works with Python 3.14
"""
import cv2
import numpy as np
import pickle
import logging
from typing import Optional
from deepface import DeepFace
from database import query_all

log = logging.getLogger(__name__)

_known_encodings = []
_known_ids       = []
_known_names     = []
THRESHOLD        = 0.40


def reload_encodings():
    global _known_encodings, _known_ids, _known_names
    try:
        rows = query_all(
            "SELECT subject_id, name, encoding FROM subjects WHERE is_active=TRUE AND encoding IS NOT NULL"
        )
        encs, ids, names = [], [], []
        for row in rows:
            enc = pickle.loads(bytes(row["encoding"]))
            encs.append(enc)
            ids.append(row["subject_id"])
            names.append(row["name"])
        _known_encodings = encs
        _known_ids       = ids
        _known_names     = names
        log.info(f"Loaded {len(encs)} face encodings ✓")
    except Exception as e:
        log.error(f"reload_encodings failed: {e}")


def encode_face_from_bytes(img_bytes: bytes) -> Optional[np.ndarray]:
    try:
        nparr = np.frombuffer(img_bytes, np.uint8)
        img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return None
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = DeepFace.represent(
            img_path          = rgb,
            model_name        = "Facenet",
            detector_backend  = "opencv",
            enforce_detection = True
        )
        if result:
            return np.array(result[0]["embedding"])
        return None
    except Exception as e:
        log.error(f"encode_face_from_bytes: {e}")
        return None


def recognise_faces(img_bytes: bytes) -> list:
    try:
        nparr = np.frombuffer(img_bytes, np.uint8)
        img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return []
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results_raw = DeepFace.represent(
            img_path          = rgb,
            model_name        = "Facenet",
            detector_backend  = "opencv",
            enforce_detection = False
        )

        results = []
        for face_data in results_raw:
            enc    = np.array(face_data["embedding"])
            region = face_data.get("facial_area", {})
            x = region.get("x", 0)
            y = region.get("y", 0)
            w = region.get("w", 100)
            h = region.get("h", 100)
            sid, name, conf = _match(enc)
            results.append({
                "subject_id": sid,
                "name":       name,
                "confidence": conf,
                "box":        [x, y, w, h],
            })
        return results
    except Exception as e:
        log.error(f"recognise_faces: {e}")
        return []


def _match(encoding):
    if not _known_encodings:
        return "UNKNOWN", "Unknown", 0.0
    distances = []
    for known_enc in _known_encodings:
        dot    = np.dot(encoding, known_enc)
        norm   = np.linalg.norm(encoding) * np.linalg.norm(known_enc)
        cosine = 1 - (dot / (norm + 1e-10))
        distances.append(cosine)
    best_idx  = int(np.argmin(distances))
    best_dist = float(distances[best_idx])
    if best_dist <= THRESHOLD:
        return _known_ids[best_idx], _known_names[best_idx], round(1.0 - best_dist, 4)
    return "UNKNOWN", "Unknown", 0.0
