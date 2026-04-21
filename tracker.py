from deep_sort_realtime.deepsort_tracker import DeepSort

tracker = DeepSort(max_age=30)

def track_faces(faces, frame):
    detections = []

    for (x, y, w, h) in faces:
        detections.append(([x, y, w, h], 1.0, 'face'))

    tracks = tracker.update_tracks(detections, frame=frame)

    tracked = []
    for track in tracks:
        if not track.is_confirmed():
            continue
        track_id = track.track_id
        l, t, w, h = map(int, track.to_ltrb())
        tracked.append((l, t, w, h, track_id))

    return tracked