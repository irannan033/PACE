from sewing_ai.synthetic import make_video
make_video("data/ref.mp4", period_s=4.0, n_cycles=6)
make_video("data/test.mp4", period_s=5.5, n_cycles=5, jitter=0.1, seed=1)
print("Wrote data/ref.mp4, data/test.mp4 (START ROI left, END ROI right)")
