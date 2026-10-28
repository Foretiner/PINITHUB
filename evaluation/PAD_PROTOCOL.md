# Research PAD evaluation protocol

This protocol is for non-commercial research only. The current CelebA-Spoof-derived baseline is not cleared for commercial or production use. Do not switch on account enrollment or authentication based on these results. The planned small attack exercise uses only the consenting project owner's own face and devices; do not recruit or test anyone else for it.

## Before collecting results

1. Get informed consent from every participant and approval required by the school/organization. Explain camera capture, purpose, who can access results, retention/deletion date, and that participation is optional. Do not test minors without appropriate guardian consent and institutional approval.
2. Use a local test environment. Do not send face images to Supabase, GitHub, analytics, or this CSV. Keep any recorded images encrypted, access-limited, and delete them on the documented schedule. Prefer recording only per-session outcomes.
3. Assign random `sample_id` values. Do not put participant names, emails, phone numbers, or face images in the results file. Keep the mapping to participants separately only if the approved protocol requires it.
4. Freeze the model/checksums and thresholds before the evaluation run. Record code commit, model hashes, browser, camera, lighting, and date in the study notes. Do not tune and report on the same sessions as an unbiased evaluation.

## Collection matrix

Capture at least 20 separate sessions for each attack type: `print_photo`, `phone_screen`, `laptop_screen`, and `replay`, all using the participant's own face and their own print/screens/recording. Also capture bona-fide sessions for BPCER context. Use the same intended camera distance, lighting range, and app flow; randomize attack order where practical. Record one final system outcome per session, not each frame. Keep retries and technical failures in separate notes and report them; do not silently discard them. This is a small internal exercise, not a general performance claim or certification.

Never use an unsuspecting person's image or attempt an attack on a real account. Use only consenting participants, your own devices, and a non-production instance. The current application is fail-closed and must remain so.

## Capture and analyse one session

The evaluation helper opens the default local webcam, randomly selects one of the three challenge sequences, and saves 10 ordered JPEG frames in the ignored `evaluation/data/` directory. Keep a neutral pose for the first 3 frames so the detector can establish a baseline, then perform the challenge. Run a bona-fide sample with:

```powershell
.\.venv\Scripts\python.exe evaluation\capture_pad_session.py --label bona_fide
```

For each attack medium, arrange it in front of the camera first and run the matching command, for example:

```powershell
.\.venv\Scripts\python.exe evaluation\capture_pad_session.py --label attack --attack-type print_photo
```

Repeat the matching command until 20 distinct sessions have been captured for each of `print_photo`, `phone_screen`, `laptop_screen`, and `replay`. The utility displays a randomly selected challenge; perform the sequence during capture. The capture tool writes only to the local ignored data folder. Do not upload those images to GitHub or Supabase. Use only your own face on the print, screens, and replay video.

Start the local face service in another PowerShell window. From the project root, set its token from the ignored `.env` file, then run Uvicorn:

```powershell
$tokenLine = Get-Content .env | Where-Object { $_.StartsWith('FACE_SERVICE_TOKEN=') } | Select-Object -First 1
$env:FACE_SERVICE_TOKEN = $tokenLine.Substring('FACE_SERVICE_TOKEN='.Length)
Set-Location services\face
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Use the capture utility's printed session folder and challenge key to submit the sample from a separate PowerShell window. Set the same token there:

```powershell
Set-Location C:\path\to\bio-identity
$tokenLine = Get-Content .env | Where-Object { $_.StartsWith('FACE_SERVICE_TOKEN=') } | Select-Object -First 1
$env:FACE_SERVICE_TOKEN = $tokenLine.Substring('FACE_SERVICE_TOKEN='.Length)
.\.venv\Scripts\python.exe evaluation\submit_pad_session.py evaluation\data\SESSION_FOLDER --label attack --attack-type print_photo --challenge turn_left_then_blink
```

Replace `SESSION_FOLDER`, label, attack type, and challenge with the values printed for that capture. For bona-fide sessions use `--label bona_fide` and omit `--attack-type`. The helper sends frames only to localhost, then appends a row to the ignored `evaluation/runs/pad_results.csv`. It saves no frame copies. A `RETRY` is counted as a non-acceptance for BPCER/APCER and is also reported separately as a retry; inspect the reason and report retries rather than treating them as successful live detections. Delete the captured frame folder after the approved retention period.

## Calculate and report

Copy `pad_results_template.csv` and fill it with one row per session:

- `sample_id`: random unique code
- `label`: `bona_fide` or `attack`
- `prediction`: `live` for `LIVE`, or `spoof` for a non-accepting `RETRY` decision
- `attack_type`: blank for bona-fide; one of the four attack categories above for attacks
- `challenge`, `system_decision`, `reason`: preserve the challenge and raw service outcome; these fields are filled by the helper

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe evaluation\pad_eval.py evaluation\runs\pad_results.csv
```

The script reports APCER by attack type and BPCER, each with a 95% Wilson interval and count. These intervals treat session rows as independent; if a participant contributes multiple sessions, the intervals may be too narrow. For a formal result, use a participant-clustered bootstrap or one independent session per participant per condition, and report participant counts and protocol deviations. Results from this small internal test are not certification or evidence of general performance.

## Status

No human or presentation-attack trials are recorded in this repository yet. The requested target is at least 20 of each of the four attack types against the consenting owner's own face. Do not invent or populate results with synthetic examples.
