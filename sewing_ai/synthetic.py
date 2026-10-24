import numpy as np, cv2
START_ROI, END_ROI = (0.05, 0.3, 0.3, 0.4), (0.65, 0.3, 0.3, 0.4)
def make_video(path, period_s=4.0, n_cycles=5, fps=25, size=(320, 240), jitter=0.0, seed=0):
    """Synthetic 'hand' works at START area, moves, works at END area, returns."""
    rng = np.random.default_rng(seed); w, h = size
    vw = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
    ps, pe = (int(.2*w), int(.5*h)), (int(.8*w), int(.5*h))
    for _ in range(n_cycles):
        N = int(period_s*(1+rng.uniform(-jitter, jitter))*fps)
        for i in range(N):
            ph = i/N; fr = np.full((h, w, 3), 40, np.uint8)
            if ph < .2: p = ps
            elif ph < .5: t = (ph-.2)/.3; p = (int(ps[0]+t*(pe[0]-ps[0])), ps[1])
            elif ph < .7: p = pe
            else: t = (ph-.7)/.3; p = (int(pe[0]-t*(pe[0]-ps[0])), ps[1])
            j = 6*np.sin(i*1.7)
            cv2.circle(fr, (int(p[0]+j), int(p[1]+j/2)), 14, (60, 200, 255), -1)
            vw.write(fr)
    vw.release()
