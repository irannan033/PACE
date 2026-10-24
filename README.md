# Sewing AI – Phase 1 test build (offline, local, CPU)
All processing is local; no video leaves the machine.

## Windows setup
```
py -3.11 -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python make_samples.py     # synthetic ref/test videos
pytest -q                  # unit tests
python run.py              # desktop app
```
Optional pose: `pip install mediapipe` then tick "Use MediaPipe pose".

## Try it
Fill required fields (*), Load Reference = data/ref.mp4, Load Test = data/test.mp4, Run Analysis. Use "Draw START/END ROI" (drag, ENTER) for real videos. History tab shows saved runs, chart, CSV export.

## Status
| Feature | State |
|---|---|
| Data entry + process-compatibility check | Implemented |
| Side-by-side synced playback, ROI + cycle overlays | Implemented |
| ROI-based cycle detection (start event → end event) | Implemented (motion-energy thresholds; needs tuning on real footage) |
| DTW motion similarity, 1.0-baseline scoring | Implemented (profiles = whole-frame motion; wrist features extracted when MediaPipe present but NOT yet used in DTW) |
| Metrics, SAM *estimate*, SQLite, history, CSV | Implemented (efficiency needs ref SAM passed to `metrics`; not yet in GUI) |
| Line bottleneck function (parallelism-aware) | Implemented as function + test; no line dashboard UI yet |
| Skeleton overlay, excess/missing movement detection, boundary correction UI | NOT yet (corrections table exists) |
| Training/eval utilities, model versioning | NOT yet; needs annotated videos |
| Real-time cameras | Phase 2: feed `cv2.VideoCapture(index)` frames into `core` with a rolling buffer; one worker thread per camera |

## Score
overall = 0.5·min(ratio,1.5) + 0.3·similarity + 0.2·completeness; ratio = ref cycle / test cycle. Weights are assumptions. Quality/safety gates require human review. No learning is claimed: nothing is trained yet.

## References (verify DOIs before citing)
- Sakoe & Chiba (1978), Dynamic programming algorithm optimization for spoken word recognition, IEEE TASSP, doi:10.1109/TASSP.1978.1163055 – DTW.
- Cao et al. (2019), OpenPose, IEEE TPAMI, doi:10.1109/TPAMI.2019.2929257 – multi-person pose.
- Bazarevsky et al. (2020), BlazePose, arXiv:2006.10204 – MediaPipe pose basis.
- Lugaresi et al. (2019), MediaPipe, arXiv:1906.08172 – pipeline framework.
None were validated on garment sewing by this project; evaluation per spec §12 is still to do.


Just Run

```
 py -3.12 -m venv .venv   
 .\.venv\Scripts\Activate.ps1    # activate virtual environment
 python run.py   # desktop app

```