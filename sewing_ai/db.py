import sqlite3, json
SCHEMA = """
CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, ts TEXT DEFAULT CURRENT_TIMESTAMP,
 buyer TEXT, style TEXT, unit TEXT, line TEXT, process TEXT, operator TEXT, operator_id TEXT,
 run_date TEXT, shift TEXT, workstation TEXT, ref_video TEXT, test_video TEXT,
 cycles INT, avg_cycle_s REAL, est_sam_min REAL, cycles_per_hr REAL, productive_pct REAL,
 ratio REAL, similarity REAL, overall REAL, details TEXT);
CREATE TABLE IF NOT EXISTS corrections(id INTEGER PRIMARY KEY, run_id INT, kind TEXT,
 frame INT, label TEXT, ts TEXT DEFAULT CURRENT_TIMESTAMP);
"""
def connect(path="data/sewing.db"):
    c = sqlite3.connect(path); c.executescript(SCHEMA); return c
def save_run(c, info, m, sc, details):
    cur = c.execute("""INSERT INTO runs(buyer,style,unit,line,process,operator,operator_id,run_date,shift,
     workstation,ref_video,test_video,cycles,avg_cycle_s,est_sam_min,cycles_per_hr,productive_pct,
     ratio,similarity,overall,details) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
     (info["buyer"], info["style"], info["unit"], info["line"], info["process"], info["operator"],
      info.get("operator_id"), info.get("date"), info.get("shift"), info.get("workstation"),
      info["ref_video"], info["test_video"], m["cycles"], m["avg_s"], m["est_sam_min"],
      m["cycles_per_hr"], m["productive_pct"], sc["cycle_time_ratio"], sc["motion_similarity"],
      sc["overall"], json.dumps(details, default=float)))
    c.commit(); return cur.lastrowid
def history(c, **f):
    q, a = "SELECT * FROM runs WHERE 1=1", []
    for k, v in f.items():
        if v: q += f" AND {k}=?"; a.append(v)
    return c.execute(q+" ORDER BY id DESC", a).fetchall()
def add_correction(c, run_id, kind, frame, label=""):
    c.execute("INSERT INTO corrections(run_id,kind,frame,label) VALUES(?,?,?,?)", (run_id, kind, frame, label)); c.commit()
