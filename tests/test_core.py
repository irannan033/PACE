import pytest, numpy as np
from sewing_ai import core, db
from sewing_ai.synthetic import make_video, START_ROI, END_ROI

def _an(tmp_path, name, **kw):
    p = str(tmp_path/name); make_video(p, **kw)
    s = core.extract_signals(p, START_ROI, END_ROI); return s, core.detect_cycles(s, s["fps"])

def test_cycle_count_and_time(tmp_path):
    s, c = _an(tmp_path, "a.mp4", period_s=4.0, n_cycles=5)
    assert abs(len(c)-5) <= 1
    assert all(1.0 < x["duration_s"] < 4.0 for x in c)

def test_score_baseline_is_one(tmp_path):
    s, c = _an(tmp_path, "a.mp4", period_s=4.0, n_cycles=5)
    m = core.metrics(s, c); sim = core.motion_similarity(s, c, s, c); sc = core.score(m, m, sim)
    assert sc["cycle_time_ratio"] == pytest.approx(1.0) and sim == pytest.approx(1.0) and sc["overall"] == pytest.approx(1.0)

def test_slower_test_has_ratio_below_one(tmp_path):
    sr, cr = _an(tmp_path, "r.mp4", period_s=4.0, n_cycles=5); st, ct = _an(tmp_path, "t.mp4", period_s=6.0, n_cycles=5)
    assert core.score(core.metrics(sr, cr), core.metrics(st, ct), 1.0)["cycle_time_ratio"] < 1.0

def test_dtw_zero_for_identical():
    a = np.sin(np.linspace(0, 6, 50)); assert core.dtw(a, a) == pytest.approx(0)

def test_bottleneck_uses_parallelism():
    r = core.bottleneck([dict(name="A", cycle_s=60, workstations=2), dict(name="B", cycle_s=40, workstations=1)])
    assert [x["name"] for x in r if x["bottleneck"]] == ["B"]

def test_db_roundtrip():
    c = db.connect(":memory:"); info = dict(buyer="b", style="s", unit="u", line="1", process="p", operator="o", ref_video="r", test_video="t")
    m = dict(cycles=3, avg_s=4, est_sam_min=.08, cycles_per_hr=900, productive_pct=80)
    db.save_run(c, info, m, dict(cycle_time_ratio=1, motion_similarity=1, overall=1), {}); assert len(db.history(c, buyer="b")) == 1
