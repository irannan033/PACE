# Project Title
**PACE- Precision AI Capacity Evaluation**
**AI-Powered Garment Sewing Line Capacity, Cycle-Time Measurement, and Motion Analysis System**

## 1. Project Objective

Develop a complete, locally running AI/ML-based application for garment manufacturing that automates sewing operation time studies, cycle counting, operator motion analysis, production capacity measurement, and efficiency monitoring by using GSD (General Sewing Data).

The system will initially analyze prerecorded sewing-operation videos and later transition to real-time camera feeds after the model has been developed and validated.

The application must use computer vision, machine learning, human pose or gesture estimation, motion analysis, and data analytics to compare an operator's performance against a predefined reference video. It must calculate cycle time, cycle count, productive and idle time, estimated SAM, efficiency, hourly capacity, and bottlenecks at both process and sewing-line levels.

All video processing, model inference, and data storage must run locally on the computer. No video may be uploaded to a cloud platform or web-based AI service.

Use published scientific journals and research papers as references for selecting suitable algorithms, designing the methodology, and evaluating the model.

## 2. Project Architecture: Two Development Phases

### Phase 1: Offline Video-Based Analysis

Develop a desktop application that allows the user to upload a fixed reference video and a test video for comparison.

The reference video represents the benchmark sewing operation. The test video represents the actual performance of an operator performing the same process.

The application must support the following workflow:

1. Launch the application through a desktop interface.
2. Enter the production and process information.
3. Select the fixed reference video or use a previously configured reference video.
4. Upload the test video.
5. Define the process cycle's start and end regions by drawing boxes, lines, or regions of interest on the video.
6. Run both videos simultaneously in a synchronized, side-by-side video player.
7. Apply the selected AI/ML models to both videos.
8. Display motion tracking, gesture or pose analysis, cycle detection, cycle time, and motion counts while the videos are playing.
9. Calculate the performance score of the test operator relative to the reference operator.
10. Save the analysis results in a local database.
11. Open a dashboard containing the latest results and historical production analytics.

### Phase 2: Real-Time Sewing-Line Monitoring

Extend the validated Phase 1 system to support live video feeds from cameras installed at sewing workstations.

The application should process live video locally, identify operation cycles, measure active and idle time, calculate production performance, and update the dashboard continuously.

The system should support multiple processes and eventually multiple workstations and sewing lines, subject to available computing resources.

Design the software architecture from the beginning so that offline video processing and real-time video processing can share the same analysis engine.

## 3. Production Data Entry

Before starting an analysis, the user must enter the following information.

**Production and process information:**
- Buyer name
- Style number
- Unit number
- Sewing line number
- Process or operation name
- Reference video
- Test video

**Operator information:**
- Operator name
- Operator ID, if available
- Date and shift
- Optional workstation or machine number

The reference video should be reusable for the same buyer, style, process, and applicable operating method. The user must be able to replace or update the reference video when necessary.

Validate the input fields and prevent comparisons between incompatible processes unless the user explicitly permits them.

## 4. Reference and Test Video Comparison Interface

Create a professional desktop interface with two video panels displayed side by side.

**Left panel — Reference Video**
- Reference operator's video
- Reference cycle count
- Reference cycle time
- Reference motion count
- Detected body keypoints or pose landmarks
- Hand, arm, and upper-body movement tracking where supported
- Detected cycle start and end events

**Right panel — Test Video**
- Test operator's video
- Test cycle count
- Test cycle time
- Test motion count
- Detected body keypoints or pose landmarks
- Hand, arm, and upper-body movement tracking where supported
- Detected cycle start and end events

The videos should run in parallel, with synchronized playback controls where feasible. Account for differences in frame rate, video duration, and cycle duration.

The interface must make the AI/ML gesture and movement analysis visibly understandable. Display pose skeletons, keypoints, motion trajectories, movement segments, cycle boundaries, event markers, and relevant model confidence values as overlays.

Include a comparison panel that updates during playback and displays:

- Reference cycle duration versus test cycle duration
- Reference motion sequence versus test motion sequence
- Cycle count and completed cycles per minute
- Excess, missing, or repeated movements
- Idle intervals and productive intervals
- Motion similarity score
- Overall performance score
- Detected process anomalies and possible improvement opportunities

Clearly distinguish directly observed measurements from model predictions or estimates.

## 5. AI/ML and Computer Vision Requirements

Build a modular AI/ML pipeline that can be improved as more labeled videos become available.

Investigate and evaluate suitable methods for the following tasks:

### A. Human Pose and Gesture Estimation
Use an appropriate computer vision model to identify and track relevant body landmarks, particularly the hands, wrists, elbows, shoulders, and upper body.

Evaluate suitable approaches such as MediaPipe Pose or Hand Landmarker, and YOLO-based pose estimation where compatible with the hardware and application requirements.

### B. Motion and Action Analysis
Extract temporal features from body keypoints, motion trajectories, and relevant image regions.

Investigate suitable methods such as:
- Keypoint-based motion features
- Optical flow
- Dynamic Time Warping (DTW)
- Temporal action segmentation
- Lightweight temporal neural networks
- Sequence models for recognizing sewing-operation stages

The selected methods must be appropriate for repetitive, fine-grained sewing operations, including fabric handling, alignment, stitching, trimming, and material transfer.

### C. Cycle Detection
Detect the beginning and completion of each operation cycle using configurable start/end regions, visual events, motion patterns, or a combination of these methods.

The user must be able to draw and configure the cycle start and end regions manually. Do not assume that crossing a single line always defines a complete sewing cycle.

Allow users to correct detected cycle boundaries and use those corrections as labeled training examples.

### D. Reference-Based Movement Comparison
Compare the test operator's movement sequence against the reference sequence.

The system should account for differences in execution speed and minor spatial variations. Compare movement order, duration, motion frequency, and task-relevant gestures.

Identify:
- Unnecessary or repeated movements
- Delays between operation stages
- Excessive reaching or repositioning
- Missing or inconsistent movements
- Differences in cycle duration
- Potential opportunities for motion and method improvement

Do not automatically classify a shorter movement sequence as better. Determine whether a movement is necessary for product quality, safety, and correct task execution.

### E. Learning and Model Improvement
Implement a human-in-the-loop learning workflow.

The application should save corrected cycle boundaries, verified movement labels, and user feedback. Use these data for subsequent model training or calibration.

Investigate reinforcement learning only if an appropriate reward function, environment, and action-selection problem can be defined. For the initial version, prioritize supervised learning, sequence alignment, threshold calibration, and incremental model improvement where technically justified.

The application must not claim to learn autonomously unless the training and model-update process is actually implemented.

## 6. Performance Rating and Benchmarking

Create a reference-based performance score with a normalized baseline of 1.0.

Interpret the score as follows:

- Below 1.0: performance is below the defined benchmark.
- Equal to 1.0: performance matches the defined benchmark.
- Above 1.0: performance exceeds the benchmark according to the selected metric.

Calculate separate scores for cycle-time performance, motion similarity, and overall task performance.

For example, a cycle-time ratio may be calculated as:

Performance ratio = Reference cycle time / Test cycle time

A ratio above 1 indicates a faster test cycle, but it must not be interpreted as overall efficiency or quality without additional checks.

Display the motion similarity score separately, using a normalized scale such as 0–1.

The overall score must account for cycle time, movement quality, process completeness, and applicable quality or safety constraints. Clearly document its formula, weights, assumptions, and limitations.

## 7. Time Study and Production Metrics

Calculate and store the following metrics for every process and operator:

- Total detected cycle count
- Average cycle time
- Median cycle time
- Minimum and maximum cycle time
- Cycle-time variability
- Completed cycles per hour
- Productive time
- Idle time
- Productive-time percentage
- Estimated SAM
- Hourly production capacity
- Actual output
- Target versus actual production
- Efficiency percentage
- Reference-versus-test performance ratio
- Motion count and movement similarity
- Model confidence and cycle-detection accuracy, where measurable

Provide clear definitions for all calculations.

For example:

Average cycle time = Total measured cycle duration / Number of valid completed cycles

Productive-time percentage = Productive time / Total observed time × 100

Operator efficiency = Earned standard minutes / Actual working minutes × 100

Estimated SAM must be clearly labeled as an estimate unless a validated standard time is available. Do not assume that the reference video alone establishes an authoritative SAM.

Calculate hourly capacity from the applicable standard time and working conditions. Distinguish theoretical capacity from observed production.

The system must handle breaks, machine downtime, waiting for materials, quality interruptions, and other nonproductive intervals where they can be identified reliably.

## 8. Sewing-Line Capacity and Bottleneck Analysis

Extend the analysis from a single operation to a complete sewing line.

The system should aggregate measurements across processes and lines using the buyer, style, unit, line, process, operator, date, and shift fields.

The dashboard must identify:
- Processes with the longest cycle times
- Processes with low output relative to their targets
- Capacity differences between consecutive operations
- Accumulating work-in-progress, where data is available
- Processes with high idle time
- Operators or workstations with inconsistent cycle times
- Potential line bottlenecks
- Estimated line capacity and required production rate

Do not identify a bottleneck solely by selecting the process with the longest individual cycle time. Consider workstation parallelism, operator allocation, machine availability, process dependencies, and work-in-progress.

## 9. Dashboard Requirements

After each analysis, open a dashboard that supports both current-session results and historical analysis.

Include the following views:

**A. Process Dashboard**
- Cycle count
- Average cycle time
- Hourly output
- Productive time and idle time
- Estimated SAM
- Efficiency
- Reference-versus-test comparison
- Motion analysis

**B. Line Dashboard**
- Total line output
- Line efficiency
- Target versus actual production
- Process-wise capacity
- Bottleneck indicators
- Work-in-progress information, where available
- Hourly production trend

**C. Historical Dashboard**
Allow filtering by:
- Buyer
- Style
- Unit
- Sewing line
- Process
- Operator
- Date range
- Shift

Display hourly, daily, weekly, and monthly trends. Support historical comparisons between operators, processes, styles, and production periods where the data is comparable.

Provide useful charts, tables, summary cards, and export options for reports.

## 10. Local Software Architecture

Develop a fully functional desktop application. Do not make the core video-processing workflow dependent on a web browser, cloud API, or internet connection.

Use an appropriate technology stack, such as:

- Python for the application and AI/ML pipeline
- OpenCV for video processing
- MediaPipe or a suitable pose-estimation model
- NumPy and pandas for numerical analysis
- A suitable sequence-alignment or temporal-analysis method
- SQLite for local storage
- PySide6 or another suitable desktop GUI framework
- PyQtGraph, Matplotlib, or an appropriate plotting library for analytics
- PyTorch or another suitable framework if a trainable model is required

Select dependencies based on compatibility with the target hardware, including CPU-only systems. GPU acceleration may be supported as an optional enhancement.

Keep the architecture modular, separating:
1. Desktop user interface
2. Video ingestion and playback
3. Pose and movement analysis
4. Cycle detection
5. Reference-to-test comparison
6. Metrics and capacity calculations
7. Local database and historical records
8. Dashboard and reporting
9. Model training, evaluation, and version management
10. Real-time camera integration

## 11. Research and Scientific Validation

Use published journal articles and reputable conference papers to guide the implementation.

Research relevant work in:
- Human pose estimation
- Fine-grained action recognition
- Human motion similarity and sequence alignment
- Cycle-time measurement in manufacturing
- Industrial video analytics
- Human-in-the-loop machine learning
- Reinforcement learning for production optimization, where applicable
- Time-study methods and predetermined motion-time systems

Provide verifiable paper titles, authors, publication years, DOI links where available, and a short explanation of how each reference supports the proposed system.

Do not invent citations or claim that an algorithm has been validated for garment sewing if the cited study did not test that application.

## 12. Testing and Model Evaluation

Build an evaluation process using manually annotated videos as the ground truth.

Measure:
- Cycle-count precision, recall, and F1-score
- Cycle-boundary timing error
- Cycle-time measurement error
- Pose or keypoint accuracy where suitable annotations are available
- Motion-sequence similarity
- Processing speed and frames per second
- CPU and memory consumption
- Performance across different operators, camera angles, lighting conditions, and sewing processes

Separate training and test data by recording session or operator where feasible to reduce data leakage.

Provide a method to compare the automated results against manual stopwatch time studies and verified production records.

## 13. Required Deliverables

Provide a complete, runnable source-code project rather than isolated code snippets.

Include:
- Full project directory structure
- All application source files
- Dependency and environment configuration
- Database schema and initialization scripts
- Desktop GUI
- Video upload and playback functionality
- Reference and test video comparison
- Visible pose, gesture, and motion analysis
- Configurable cycle start/end regions
- Cycle detection and measurement
- Reference-based performance scoring
- Process and line-level metrics
- Historical dashboard
- Model training and evaluation utilities
- Sample configuration and synthetic test data where appropriate
- Unit tests and integration tests
- Setup instructions for Windows
- A README with clear installation and execution commands
- A roadmap for integrating real-time cameras in Phase 2

If a reference project repository or source archive is provided, inspect its existing files first. Reuse suitable components, preserve working functionality, identify missing features, and integrate the new implementation without unnecessarily rebuilding everything.

## 14. Development Instructions

Develop the project incrementally, ensuring each major feature runs before moving to the next.

First inspect the supplied reference project and available hardware. Then establish the project architecture, implement the desktop interface and local video pipeline, and validate basic cycle measurement before developing advanced motion models.

Prioritize a working CPU-compatible prototype over an unnecessarily complex model. Clearly identify which features are fully implemented, which require additional training data, and which are planned for Phase 2.

The final deliverable must be a reproducible, maintainable, research-informed desktop application suitable for further development into a real-time sewing-line monitoring system.
