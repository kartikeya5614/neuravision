"""NEURAVISION — Liveness Detection"""
import numpy as np
import time

_motion_buffer = {}

def compute_liveness_score(face: dict) -> float:
    sid  = face.get("subject_id", "unknown")
    box  = face.get("box", [0,0,100,100])
    conf = face.get("confidence", 0.5)

    conf_score   = min(conf, 1.0)
    motion_score = _motion_component(sid, box)
    w, h         = box[2], box[3]
    area_score   = 1.0 if 40 < w < 800 and 40 < h < 800 else 0.3
    aspect       = w / max(h, 1)
    aspect_score = 1.0 if 0.5 < aspect < 1.2 else 0.4

    score = (conf_score*0.35 + motion_score*0.40 + area_score*0.15 + aspect_score*0.10)
    return round(min(max(score, 0.0), 1.0), 4)


def _motion_component(sid, box):
    cx  = box[0] + box[2]/2
    cy  = box[1] + box[3]/2
    buf = _motion_buffer.setdefault(sid, [])
    buf.append((cx, cy, time.time()))
    if len(buf) > 30:
        buf.pop(0)
    if len(buf) < 5:
        return 0.65
    xs      = [p[0] for p in buf]
    ys      = [p[1] for p in buf]
    total_v = float(np.var(xs)) + float(np.var(ys))
    if   total_v < 0.5:  return 0.20
    elif total_v < 5:    return 0.55
    elif total_v < 50:   return 0.85
    else:                return 0.70
