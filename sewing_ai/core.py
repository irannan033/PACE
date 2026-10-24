"""Shared analysis engine (offline now; feed frames from a camera in Phase 2)."""
import numpy as np, cv2

try:  # optional pose; falls back to motion energy
    import mediapipe as mp
    _POSE = mp.solutions.pose
except Exception:
    _POSE = None

def pose_available():
    return _POSE is not None

def _roi_px(roi, w, h):  # roi = (x,y,w,h) normalised 0-1
    x, y, rw, rh = roi
    return int(x*w), int(y*h), max(1, int(rw*w)), max(1, int(rh*h))

def extract_signals(path, start_roi, end_roi, use_pose=False, max_frames=None):
    """Per-frame OBSERVED signals: motion in start ROI, end ROI, whole frame,
    plus wrist trajectory (pose, if available)."""
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    prev, S, E, A, L = None, [], [], [], []
    pose = _POSE.Pose(model_complexity=1, min_detection_confidence=0.4, min_tracking_confidence=0.4) if (use_pose and _POSE) else None
    n = 0
    while True:
        ok, fr = cap.read()
        if not ok or (max_frames and n >= max_frames): break
        n += 1
        h, w = fr.shape[:2]
        g = cv2.GaussianBlur(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY), (5, 5), 0)
        d = np.zeros(g.shape, np.float32) if prev is None else cv2.absdiff(g, prev).astype(np.float32)
        prev = g
        def m(roi):
            x, y, rw, rh = _roi_px(roi, w, h); return float(d[y:y+rh, x:x+rw].mean())
        S.append(m(start_roi)); E.append(m(end_roi)); A.append(float(d.mean()))
        if pose:
            r = pose.process(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
            L.append([[p.x, p.y, p.visibility] for p in r.pose_landmarks.landmark] if r.pose_landmarks else None)
    cap.release()
    W = None
    if L:   # wrist track [lx,ly,rx,ry], gaps forward-filled
        W, last = [], [0.0]*4
        for p in L:
            if p: last = [p[15][0], p[15][1], p[16][0], p[16][1]]
            W.append(last)
        W = np.array(W)
    return dict(fps=fps, start=np.array(S), end=np.array(E), all=np.array(A), wrist=W, lm=L or None, n=n)

def _smooth(x, k=5):
    return np.convolve(x, np.ones(k)/k, mode="same") if len(x) >= k else x

def rising_edges(sig, fps, thr=None, refractory_s=0.5):
    s = _smooth(sig)
    thr = thr if thr is not None else s.mean() + 0.5*s.std()
    on = s > thr
    idx, last = [], -1e9
    for i in range(1, len(on)):
        if on[i] and not on[i-1] and (i-last)/fps >= refractory_s:
            idx.append(i); last = i
    return idx

def detect_cycles(sig, fps, start_thr=None, end_thr=None, min_cycle_s=1.0):
    """Cycle = start-ROI event followed by end-ROI event (not a single line)."""
    st = rising_edges(sig["start"], fps, start_thr)
    en = rising_edges(sig["end"], fps, end_thr)
    cycles = []
    for k, s in enumerate(st):
        nxt = st[k+1] if k+1 < len(st) else 10**9
        e = next((e for e in en if s < e < nxt), None)
        if e is not None and (e-s)/fps >= min_cycle_s:
            cycles.append(dict(start_f=s, end_f=e, duration_s=(e-s)/fps))
    return cycles

def dtw(a, b):
    """Dynamic Time Warping (Sakoe & Chiba, 1978); path-normalised distance."""
    a = np.asarray(a, float).reshape(len(a), -1); b = np.asarray(b, float).reshape(len(b), -1)
    n, m = len(a), len(b)
    D = np.full((n+1, m+1), np.inf); D[0, 0] = 0
    for i in range(1, n+1):
        c = np.linalg.norm(a[i-1] - b, axis=1)
        for j in range(1, m+1):
            D[i, j] = c[j-1] + min(D[i-1, j], D[i, j-1], D[i-1, j-1])
    return D[n, m] / (n+m)

def _z(x): return (x-x.mean())/(x.std()+1e-9)

def motion_similarity(ref_sig, ref_cyc, tst_sig, tst_cyc):
    """0-1 similarity of mean per-cycle motion profiles (speed-invariant via DTW)."""
    if not ref_cyc or not tst_cyc: return 0.0
    base = _motion_sim(ref_sig, ref_cyc, tst_sig, tst_cyc)
    if ref_sig.get("wrist") is not None and tst_sig.get("wrist") is not None:
        # wrist-path shape similarity (position-independent); 0.1 = 10% of frame width scale (assumption)
        def wp(sig, cyc):
            out = []
            for c in cyc:
                x = sig["wrist"][c["start_f"]:c["end_f"]]
                x = x - x.mean(axis=0)
                out.append(np.stack([np.interp(np.linspace(0, len(x)-1, 60), np.arange(len(x)), x[:, i]) for i in range(4)], 1))
            return np.mean(out, axis=0)
        wsim = float(np.exp(-dtw(wp(ref_sig, ref_cyc), wp(tst_sig, tst_cyc))/0.1))
        return 0.5*base + 0.5*wsim
    return base

def _motion_sim(ref_sig, ref_cyc, tst_sig, tst_cyc):
    def prof(sig, cyc):
        out = []
        for c in cyc:
            x = sig["all"][c["start_f"]:c["end_f"]]
            out.append(_z(np.interp(np.linspace(0, len(x)-1, 60), np.arange(len(x)), x)))
        return np.mean(out, axis=0)
    return float(np.exp(-dtw(prof(ref_sig, ref_cyc), prof(tst_sig, tst_cyc))))

def metrics(sig, cycles, idle_thr=None, target_per_hr=None, ref_sam_min=None, rating=1.0, allowance=0.15):
    T = sig["n"]/sig["fps"]
    d = np.array([c["duration_s"] for c in cycles]) if cycles else np.array([])
    s = _smooth(sig["all"]); thr = idle_thr if idle_thr is not None else 0.5*s.mean()
    productive = float((s > thr).sum()/sig["fps"])
    avg = float(d.mean()) if len(d) else None
    sam = avg*rating*(1+allowance)/60 if avg else None   # ESTIMATE only
    eff = (len(d)*ref_sam_min)/(T/60)*100 if (ref_sam_min and T) else None
    g = lambda f: float(f(d)) if len(d) else None
    return dict(cycles=len(d), avg_s=avg, median_s=g(np.median), min_s=g(np.min), max_s=g(np.max), std_s=g(np.std),
                observed_s=T, productive_s=productive, idle_s=T-productive,
                productive_pct=100*productive/T if T else 0, est_sam_min=sam,
                cycles_per_hr=3600/avg if avg else None, theoretical_cap_hr=60/sam if sam else None,
                efficiency_pct=eff, target_per_hr=target_per_hr)

def score(ref_m, tst_m, sim, w=(0.5, 0.3, 0.2), cap=1.5):
    """All terms equal 1.0 at benchmark. overall = w1*min(ratio,cap)+w2*sim+w3*completeness.
    Quality/safety gates are NOT automated: a human must confirm (see README)."""
    ratio = (ref_m["avg_s"]/tst_m["avg_s"]) if ref_m["avg_s"] and tst_m["avg_s"] else 0.0
    comp = min(1.0, tst_m["cycles"]/max(1, ref_m["cycles"])) if ref_m["cycles"] else 0.0
    return dict(cycle_time_ratio=ratio, motion_similarity=sim, completeness=comp,
                overall=w[0]*min(ratio, cap)+w[1]*sim+w[2]*comp)

def bottleneck(processes):
    """processes: dicts(name, cycle_s, workstations, target_per_hr?). Capacity = workstations*3600/cycle_s."""
    rows = [dict(p, capacity_hr=p["workstations"]*3600/p["cycle_s"]) for p in processes]
    low = min((r["capacity_hr"] for r in rows), default=None)
    for r in rows: r["bottleneck"] = r["capacity_hr"] == low
    return rows
