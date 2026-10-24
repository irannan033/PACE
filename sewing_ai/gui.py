import sys, cv2, datetime, csv
import numpy as np
from PySide6 import QtWidgets as W, QtCore as C, QtGui as G
import pyqtgraph as pg
from . import core, db

def to_pix(fr):
    h, w = fr.shape[:2]; return G.QPixmap.fromImage(G.QImage(fr.data, w, h, 3*w, G.QImage.Format_BGR888).copy())

class Main(W.QMainWindow):
    FIELDS = ["buyer", "style", "unit", "line", "process", "operator", "operator_id", "shift"]
    REQ = ["buyer", "style", "unit", "line", "process", "operator"]
    def __init__(self):
        super().__init__(); self.setWindowTitle("Sewing AI – Cycle Time & Motion Analysis")
        self.conn = db.connect(); self.paths = {"ref": None, "test": None}
        self.rois = {"start": (0.05, .3, .3, .4), "end": (.65, .3, .3, .4)}; self.sig = {}; self.cyc = {}; self.caps = {}
        tabs = W.QTabWidget(); self.setCentralWidget(tabs)
        tabs.addTab(self._analysis_tab(), "Analysis"); tabs.addTab(self._history_tab(), "History"); self.resize(1250, 850)
        self.timer = C.QTimer(); self.timer.timeout.connect(self.tick); self.fno = 0
    def _analysis_tab(self):
        w = W.QWidget(); v = W.QVBoxLayout(w); form = W.QFormLayout(); self.ed = {}
        for f in self.FIELDS:
            self.ed[f] = W.QLineEdit(); form.addRow(f.replace("_", " ").title()+(" *" if f in self.REQ else ""), self.ed[f])
        ok = core.pose_available()
        self.pose = W.QCheckBox("Run pose estimation (slower, needed for skeleton)"); self.pose.setChecked(ok); self.pose.setEnabled(ok); form.addRow(self.pose)
        self.skel = W.QCheckBox("Show skeleton overlay"); self.skel.setChecked(True); form.addRow(self.skel)
        if not ok: form.addRow(W.QLabel("<font color='red'>MediaPipe not available: skeleton disabled. Use Python 3.11/3.12 and: pip install mediapipe==0.10.14</font>"))
        v.addLayout(form); bar = W.QHBoxLayout()
        for t, fn in [("Load Reference", lambda: self.load("ref")), ("Load Test", lambda: self.load("test")),
                      ("Draw START ROI", lambda: self.draw("start")), ("Draw END ROI", lambda: self.draw("end")),
                      ("Run Analysis", self.run), ("Play/Pause", self.toggle)]:
            b = W.QPushButton(t); b.clicked.connect(fn); bar.addWidget(b)
        v.addLayout(bar); pan = W.QHBoxLayout(); self.view = {}; self.info = {}
        for k, t in [("ref", "Reference"), ("test", "Test")]:
            col = W.QVBoxLayout(); col.addWidget(W.QLabel(f"<b>{t}</b>")); self.view[k] = W.QLabel(); self.view[k].setMinimumSize(480, 300)
            self.view[k].setStyleSheet("background:#222"); self.info[k] = W.QLabel("-"); col.addWidget(self.view[k]); col.addWidget(self.info[k]); pan.addLayout(col)
        v.addLayout(pan); self.cmp = W.QTextEdit(); self.cmp.setReadOnly(True); self.cmp.setMaximumHeight(170); v.addWidget(self.cmp)
        return w
    def _history_tab(self):
        w = W.QWidget(); v = W.QVBoxLayout(w); b = W.QPushButton("Refresh"); b.clicked.connect(self.refresh); e = W.QPushButton("Export CSV"); e.clicked.connect(self.export)
        self.tbl = W.QTableWidget(); self.plot = pg.PlotWidget(title="Overall score by run (1.0 = benchmark)"); self.plot.setMaximumHeight(200)
        for x in (b, e, self.tbl, self.plot): v.addWidget(x)
        return w
    def load(self, k):
        p, _ = W.QFileDialog.getOpenFileName(self, "Video", "", "Video (*.mp4 *.avi *.mov *.mkv)")
        if p: self.paths[k] = p; self.caps[k] = cv2.VideoCapture(p); self.show_frame(k)
    def draw(self, kind):
        p = self.paths["test"] or self.paths["ref"]
        if not p: return W.QMessageBox.warning(self, "No video", "Load a video first.")
        c = cv2.VideoCapture(p); ok, f = c.read(); c.release()
        r = cv2.selectROI(f"Draw {kind} ROI, press ENTER", f); cv2.destroyAllWindows(); h, w = f.shape[:2]
        if r[2] and r[3]: self.rois[kind] = (r[0]/w, r[1]/h, r[2]/w, r[3]/h)
    def validate(self):
        miss = [f for f in self.REQ if not self.ed[f].text().strip()]
        if miss: return f"Missing: {', '.join(miss)}"
        if not (self.paths["ref"] and self.paths["test"]): return "Load both videos."
    def run(self):
        err = self.validate()
        if err: return W.QMessageBox.warning(self, "Input", err)
        for k in ("ref", "test"):
            self.sig[k] = core.extract_signals(self.paths[k], self.rois["start"], self.rois["end"], self.pose.isChecked())
            self.cyc[k] = core.detect_cycles(self.sig[k], self.sig[k]["fps"])
        mr, mt = [core.metrics(self.sig[k], self.cyc[k]) for k in ("ref", "test")]
        sim = core.motion_similarity(self.sig["ref"], self.cyc["ref"], self.sig["test"], self.cyc["test"]); sc = core.score(mr, mt, sim)
        info = {f: self.ed[f].text().strip() for f in self.FIELDS}; info.update(date=str(datetime.date.today()), ref_video=self.paths["ref"], test_video=self.paths["test"])
        rid = db.save_run(self.conn, info, mt, sc, dict(ref=mr, test=mt, cycles_ref=self.cyc["ref"], cycles_test=self.cyc["test"]))
        f = lambda x: "n/a" if x is None else f"{x:.2f}"
        self.cmp.setHtml(f"<b>Run #{rid}</b> (OBSERVED = measured from video; ESTIMATE = assumption-based)<br>"
          f"Cycles ref/test (observed): {mr['cycles']}/{mt['cycles']} | Avg cycle s ref/test: {f(mr['avg_s'])}/{f(mt['avg_s'])}<br>"
          f"Productive % (test): {f(mt['productive_pct'])} | Idle s: {f(mt['idle_s'])} | Cycles/hr: {f(mt['cycles_per_hr'])}<br>"
          f"Est. SAM min (ESTIMATE; rating 1.0, 15% allowance): {f(mt['est_sam_min'])}<br>"
          f"<b>Cycle-time ratio {f(sc['cycle_time_ratio'])} | Motion similarity {f(sim)} | Completeness {f(sc['completeness'])} | Overall {f(sc['overall'])}</b> (1.0 = benchmark)<br>"
          "Faster is not automatically better; quality/safety must be verified by a person.")
        self.fno = 0
        for k in ("ref", "test"): self.caps[k] = cv2.VideoCapture(self.paths[k])
        self.timer.start(int(1000/self.sig["ref"]["fps"])); self.refresh()
    def toggle(self): self.timer.stop() if self.timer.isActive() else self.timer.start(40)
    def tick(self):
        for k in ("ref", "test"): self.show_frame(k)
        self.fno += 1
    def show_frame(self, k):
        c = self.caps.get(k)
        if not c: return
        ok, fr = c.read()
        if not ok: self.timer.stop(); return
        h, w = fr.shape[:2]
        for name, col in (("start", (0, 255, 0)), ("end", (0, 0, 255))):
            x, y, rw, rh = core._roi_px(self.rois[name], w, h); cv2.rectangle(fr, (x, y), (x+rw, y+rh), col, 2)
        lm = self.sig.get(k, {}).get("lm")
        if lm is not None and self.skel.isChecked() and self.fno < len(lm): self.draw_skeleton(fr, lm)
        cyc = self.cyc.get(k, []); n = sum(1 for q in cyc if q["end_f"] <= self.fno)
        cv2.putText(fr, f"cycles: {n}", (8, 22), cv2.FONT_HERSHEY_SIMPLEX, .7, (255, 255, 255), 2)
        if any(abs(q["start_f"]-self.fno) < 3 for q in cyc): cv2.putText(fr, "CYCLE START", (8, 48), 0, .6, (0, 255, 0), 2)
        if any(abs(q["end_f"]-self.fno) < 3 for q in cyc): cv2.putText(fr, "CYCLE END", (8, 74), 0, .6, (0, 0, 255), 2)
        self.view[k].setPixmap(to_pix(fr).scaled(self.view[k].size(), C.Qt.KeepAspectRatio))
        self.info[k].setText(f"cycles so far: {n} | total detected: {len(cyc)}")
    BONES = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16), (11, 23), (12, 24), (23, 24),
             (15, 17), (15, 19), (15, 21), (17, 19), (16, 18), (16, 20), (16, 22), (18, 20)]
    def draw_skeleton(self, fr, lm):
        h, w = fr.shape[:2]; pts = lm[self.fno]
        P = lambda q, i: (int(q[i][0]*w), int(q[i][1]*h))
        for t in range(max(0, self.fno-30), self.fno):          # wrist motion trails (last ~30 frames)
            a, b = lm[t], lm[t+1]
            if a and b:
                for i, col in ((15, (255, 0, 255)), (16, (0, 165, 255))):
                    if a[i][2] > .5 and b[i][2] > .5: cv2.line(fr, P(a, i), P(b, i), col, 2)
        if not pts: return cv2.putText(fr, "no pose", (8, h-10), 0, .5, (0, 0, 255), 1)
        for a, b in self.BONES:
            if pts[a][2] > .5 and pts[b][2] > .5: cv2.line(fr, P(pts, a), P(pts, b), (255, 200, 0), 2)
        for i in [0] + list(range(11, 25)):
            if pts[i][2] > .5: cv2.circle(fr, P(pts, i), 6 if i in (15, 16) else 4, (0, 255, 255), -1)
        conf = float(np.mean([pts[i][2] for i in (11, 12, 13, 14, 15, 16)]))
        cv2.putText(fr, f"pose conf {conf:.2f} (model estimate)", (8, h-10), 0, .5, (255, 255, 255), 1)
    def refresh(self):
        cur = self.conn.execute("select * from runs"); cols = [d[0] for d in cur.description]; rows = db.history(self.conn)
        self.tbl.setColumnCount(len(cols)); self.tbl.setHorizontalHeaderLabels(cols); self.tbl.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, v in enumerate(r): self.tbl.setItem(i, j, W.QTableWidgetItem(str(v)))
        self.plot.clear(); self.plot.plot([r[cols.index("overall")] or 0 for r in rows][::-1], pen="y", symbol="o")
    def export(self):
        p, _ = W.QFileDialog.getSaveFileName(self, "CSV", "report.csv", "CSV (*.csv)")
        if p:
            cols = [d[0] for d in self.conn.execute("select * from runs").description]
            with open(p, "w", newline="") as fh: wr = csv.writer(fh); wr.writerow(cols); wr.writerows(db.history(self.conn))

def main():
    app = W.QApplication(sys.argv); m = Main(); m.show(); sys.exit(app.exec())
