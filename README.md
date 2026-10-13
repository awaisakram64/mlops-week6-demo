# SEN 337 · Week 6 · Demo Runbook

**From "works on my machine" to "refuses bad data": Docker, DVC and data validation**

This runbook follows the deck slide by slide. Every command on a slide is here in the same order, with the output you should see. Outputs were produced by a full rehearsal of this kit (DVC 3.67, scikit-learn 1.5.2). Git hashes, timestamps and build times will differ on your machine; everything else should match.

Students see the slides. They never see this file, `scripts/`, or `00_make_data.py` / `04_make_batches.py`.

---

## What is in this folder

| Path | Purpose |
|---|---|
| `kit/` | The pristine project. **Never edit or run anything in here.** |
| `kit/src/train.py` | Trains the model, writes `models/model.pkl` and `metrics.json` |
| `kit/src/predict.py` | Scores one applicant; checks it against `reference.json` once that exists |
| `kit/src/validate.py` | The data contract: schema, distribution, freshness |
| `kit/build_reference.py` | Writes `reference.json` (what good data looks like) |
| `kit/tools/peek.py` | One-screen look at the income column (Part 3) |
| `kit/tools/validate_pandera.py` | Overflow X1: the schema rules in pandera |
| `kit/00_make_data.py` | Generates data v1, v2, v3 (dates relative to today) |
| `kit/04_make_batches.py` | Generates the seven bad batches |
| `kit/Dockerfile`, `.dockerignore`, `requirements.txt`, `.gitignore` | As shown on slides 13, 16 and 22 |
| `scripts/fresh_start.sh` | Creates a clean `class/loan-project` with new data. **Deletes `class/`.** |
| `scripts/jump_to.sh` | Rebuilds the project at the start of any part by replaying every slide command |
| `class/` | Created by the scripts. This is where you demo. Safe to delete. |
| `clean-env/` | Created once by `fresh_start.sh`: pandas only, for slide 10 |

Everything you run in class happens inside `class/loan-project`. The DVC remote is created at `class/dvc-remote` and the teammate clone at `class/teammate-copy`.

---

## Setup: the day before, not the morning of

### 1. Software on the instructor laptop

| Need | Check with |
|---|---|
| Python 3.11 to 3.13 | `python -V` |
| Git | `git version` |
| Docker Desktop, running | `docker version` (both Client and Server must answer) |
| A bash shell | macOS/Linux terminal, or **Git Bash** on Windows |

**Windows:** run every command in Git Bash, not PowerShell or CMD. The two exceptions are noted where they apply (activating a venv, and Docker volume paths).

```bash
cd week6-demo/kit
pip install -r requirements.txt dvc pandera
git config --global user.name  "Your Name"         # only if not already set
git config --global user.email "you@example.com"
```

### 2. Generate the class project

```bash
cd week6-demo
bash scripts/fresh_start.sh
```

Expected:

```
data/loans.csv                5,000 rows   default rate 41%
batches/loans_v2.csv          6,000 rows   default rate 41%
batches/loans_v3_good.csv     7,000 rows   default rate 41%
batches/batch_new.csv         1,000 rows   default rate 42%
batches/batch_renamed.csv     1,000 rows
...
batches/loans_bad.csv         7,000 rows
Ready. Now:  cd class/loan-project
```

**Do this the day before.** The freshness check compares dates with today. Data generated more than about two weeks before class will fail freshness on the good files.

### 3. The broken environment for slide 10

`fresh_start.sh` creates it for you the first time, at `week6-demo/clean-env`: a virtual environment with pandas and **no scikit-learn**. It sits outside `class/`, so resets do not delete it. From inside `class/loan-project` it is `../../clean-env`.

### 4. Pull the base image while the internet is good

```bash
docker pull python:3.11-slim
```

Build once to confirm it works, then remove only your image (keep the base) so the live build is real:

```bash
cd week6-demo/class/loan-project
docker build -t loan-train:1.0 .
docker rmi loan-train:1.0
```

### 5. Docker Hub login (only if you keep slide 27)

```bash
docker login
```

### 6. Full rehearsal

```bash
cd week6-demo
bash scripts/jump_to.sh end
```

This runs every non-Docker command in the session, in order, printing a `SLIDE n` marker before each group. It should finish with `DONE`. Then reset for class:

```bash
bash scripts/fresh_start.sh
```

### 7. Record the demo

Screen-record one full run. If Docker, the projector or the network fails in class, play it and narrate over it.

### 8. Two terminals open before class starts

- **Terminal A:** `cd week6-demo/class/loan-project`, working environment active. All demos run here.
- **Terminal B:** `cd week6-demo`, for `jump_to.sh` if a step goes wrong.

Set a large font (at least 20 pt) in both.

---

## If a live step goes wrong

Do not debug in front of the class for more than a minute. Jump instead:

```bash
# in Terminal B
bash scripts/jump_to.sh part3        # or part2, part4, part5
```

Then in Terminal A: `cd ../loan-project` (the folder was recreated; your shell needs to re-enter it), and continue from the first slide of that part. The jump replaces Docker runs with plain `python src/train.py`, so it works even if Docker is down.

| Problem | Do this |
|---|---|
| `docker build` stalls on pip (network) | Play the recording for slides 19 to 21, then continue. Or build at home and `docker save loan-train:1.1 -o loan-train.tar`; in class `docker load -i loan-train.tar` |
| `docker: Cannot connect to the Docker daemon` | Docker Desktop is not running. Start it; it takes about 30 s |
| Volume mount fails on Windows Git Bash (path looks like `C:/Program Files/Git/app/data`) | Prefix the command: `MSYS_NO_PATHCONV=1 docker run -v "$(pwd)/data:/app/data" ...` |
| `dvc stage add` says an output is already tracked or exists | `rm models/model.pkl` and run the stage add again |
| `dvc repro` reruns when you expected a skip | Something changed. Run `dvc status` and show students why. It is a good moment |
| `dvc checkout` says `Checkout failed ... Is your cache up to date?` | That version is not in the local cache. Run `dvc pull` instead |
| Git asks for a name and email | Step 1 of setup was skipped. Set them and rerun |
| On Linux, `dvc repro` cannot overwrite `models/model.pkl` after Docker wrote it | Docker wrote it as root: `sudo chown $USER models/model.pkl` (does not happen on Docker Desktop) |
| Running long | Follow the cut order in the lesson plan. Parts 3 to 5 carry Week 6's own content and must be reached |

---

# The session, slide by slide

Opening, slides 1 to 7. No commands until slide 7.

### Slide 7 · Watch Docker, type along for DVC and validation

Students who want to type along:

```bash
pip install -r requirements.txt dvc
```

They need the project folder too: share `week6-demo` (zip or repo) before class and have them run `bash scripts/fresh_start.sh`.

---

## Part 1 · Package it: Docker (slides 8 to 30)

All commands in Terminal A, inside `class/loan-project`.

### Slide 10 · Same file, clean machine, no sklearn

```bash
source ../../clean-env/bin/activate     # Windows Git Bash: source ../../clean-env/Scripts/activate
python src/train.py
```

```
Traceback (most recent call last):
  ...
ModuleNotFoundError: No module named 'sklearn'
```

```bash
deactivate
```

Say "Week 1, Failure 1". Do not re-teach.

### Slide 11 · "Install sklearn" does not say which one

```bash
pip show scikit-learn
```

```
Name: scikit-learn
Version: 1.5.2
```

### Slide 13 · requirements.txt, pinned

```bash
cat requirements.txt
```

```
pandas==2.2.3
numpy==2.1.3
scikit-learn==1.5.2
```

### Slide 15 · The container cannot see your Desktop

Open `src/train.py` and point to line 11 (`data/loans.csv`, a relative path) and line 15 (`random_state=42`).

### Slides 16 and 17 · The Dockerfile

```bash
cat Dockerfile
```

```
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["python", "src/train.py"]
```

### Slide 19 · docker build turns the file into an image

```bash
docker build -t loan-train:1.0 .
```

```
[+] Building 52.3s (10/10) FINISHED
 => [1/5] FROM docker.io/library/python:3.11-slim
 => [2/5] WORKDIR /app
 => [3/5] COPY requirements.txt .
 => [4/5] RUN pip install -r requirements.txt          (about 25 to 60 s)
 => [5/5] COPY src/ ./src/
 => exporting to image
 => => naming to docker.io/library/loan-train:1.0
```

Talk over the pip step. It is the only slow one.

### Slide 20 · You can see every layer and its size (EXTRA)

```bash
docker images loan-train
docker history loan-train:1.0
```

The `RUN pip install` layer is roughly 440 MB, nearly all of the image above the base. Sizes vary by platform.

### Slide 21 · Change the code, the install layer is reused

Open `src/train.py` and add this line directly under `df = pd.read_csv("data/loans.csv")`:

```python
print(f"Training on {len(df):,} applicants")
```

Save, then:

```bash
docker build -t loan-train:1.1 .
```

```
 => [1/5] FROM docker.io/library/python:3.11-slim
 => CACHED [2/5] WORKDIR /app
 => CACHED [3/5] COPY requirements.txt .
 => CACHED [4/5] RUN pip install -r requirements.txt
 => [5/5] COPY src/ ./src/
 => => naming to docker.io/library/loan-train:1.1
```

Finishes in about 2 s. Point at the three `CACHED` lines.

### Slide 22 · Data does not belong inside the image

```bash
cat .dockerignore
docker run loan-train:1.1
```

```
Traceback (most recent call last):
  File "/app/src/train.py", line 11, in <module>
    df = pd.read_csv("data/loans.csv")
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'data/loans.csv'
```

Note `/app/src/train.py` in the traceback: the code is running inside the container. Say: "Good. The data is not in the image, on purpose. The next slide gives it in from outside."

### Slide 25 · docker run, with data and models mounted

```bash
docker run -v "$(pwd)/data:/app/data" -v "$(pwd)/models:/app/models" loan-train:1.1
```

```
Training on 5,000 applicants
Accuracy: 91.6 %
```

```bash
ls models/
```

```
model.pkl
```

Windows PowerShell instead of Git Bash: replace `$(pwd)` with `${PWD}`.

### Slide 26 · Three runs, one number

Press up-arrow and Enter three times.

```
Accuracy: 91.6 %
Accuracy: 91.6 %
Accuracy: 91.6 %
```

Week 1 printed 88.3, 92.8 and 85.6.

### Slide 27 · The image is the thing you hand over (EXTRA)

```bash
docker tag loan-train:1.1 <your-dockerhub-user>/loan-train:1.1
docker push <your-dockerhub-user>/loan-train:1.1
```

On another machine: `docker pull <your-dockerhub-user>/loan-train:1.1`. Skip the push if the network is slow; show the commands only.

### Slide 29 · Discussion 1 (answers in slide notes)

---

## Part 2 · Version it: DVC (slides 31 to 61)

### Slide 34 · Step 1: two init commands

```bash
git init -b main
dvc init
```

```
Initialized empty Git repository in .../loan-project/.git/
Initialized DVC repository.

You can now commit the changes to git.
```

DVC also prints an analytics notice and links. Ignore them.

### Slide 35 · Step 1b: storage first, then the first commit

```bash
mkdir ../dvc-remote
dvc remote add -d localremote ../dvc-remote
git add .gitignore .dockerignore Dockerfile requirements.txt src tools *.py .dvc/config
git commit -m "Code, Dockerfile and DVC setup"
```

```
Setting 'localremote' as a default remote.
[main (root-commit) 4e0acd1] Code, Dockerfile and DVC setup
```

**Why the remote comes first:** DVC reads the remote address from the commit you push from. A version committed before the remote existed cannot be pushed later with a simple `dvc push`. Set up storage first, then push every version as you commit it.

**Why not `git add .`:** `data/loans.csv` is not ignored yet. `git add .` would put the CSV into Git, which is exactly what DVC exists to avoid.

### Slide 36 · Step 2: dvc add hashes the file

```bash
dvc add data/loans.csv
```

```
To track the changes with git, run:

	git add data/.gitignore data/loans.csv.dvc
```

### Slide 37 · Inside the pointer file

```bash
cat data/loans.csv.dvc
```

```
outs:
- md5: 8eea76d36565560067bc0e552f1e39c9
  size: 150262
  hash: md5
  path: loans.csv
```

Your md5 differs (the dates in the data depend on the day you generated it).

### Slide 38 · The real file moved into the cache

```bash
cat data/.gitignore
ls .dvc/cache/files/md5
```

```
/loans.csv
8e
```

### Slide 39 · Step 3: commit the pointer, tag it, push it

```bash
git add data/loans.csv.dvc data/.gitignore
git commit -m "Data v1: 5,000 applicants"
git tag data-v1
dvc push
```

```
1 file pushed
```

### Slide 40 · A new batch of applicants arrives

```bash
cp batches/loans_v2.csv data/loans.csv
dvc status
```

```
data/loans.csv.dvc:
	changed outs:
		modified:           data/loans.csv
```

### Slide 41 · Git sees two changed lines, DVC holds the new file

```bash
dvc add data/loans.csv
git diff
```

```
-- md5: 8eea76d36565560067bc0e552f1e39c9
-  size: 150262
+- md5: c4f434d4d2dc82ce569d7c0b5ed9c877
+  size: 180278
```

The leading minus and plus are Git's diff markers.

### Slide 42 · Commit, tag and push version 2

```bash
git commit -am "Data v2: 6,000 applicants"
git tag data-v2
dvc push
```

```
1 file pushed
```

### Slide 43 · Two commands move code and data together

```bash
git checkout data-v1
dvc checkout
wc -l data/loans.csv
```

```
M       data/loans.csv
5001 data/loans.csv
```

Git prints a "detached HEAD" warning on the first command. Say: "that is Git telling you we are visiting the past". 5,001 lines = 5,000 applicants plus the header.

```bash
git checkout main
dvc checkout
wc -l data/loans.csv
```

```
M       data/loans.csv
6001 data/loans.csv
```

### Slide 44 · Forget dvc checkout and they disagree (EXTRA)

Spoken, or run it: `git checkout data-v1`, then `dvc status` shows `modified`. Then `git checkout main` and `dvc checkout` to return.

### Slide 45 · Now we can answer "what changed?"

```bash
git log -n 2 data/loans.csv.dvc
dvc diff data-v1 data-v2
```

```
commit 5c5c02d...   Data v2: 6,000 applicants
commit 1e56614...   Data v1: 5,000 applicants

Modified:
    data/loans.csv

files summary: 1 modified
```

The real `git log` shows author and date on separate lines. Point at them: who, when, why.

### Slide 46 · Every version is already in the remote

```bash
git tag
ls ../dvc-remote/files/md5
```

```
data-v1
data-v2
8e
c4
```

Two tags, two folders: one per version. The `8e` and `c4` are the first two characters of each version's hash (slide 37 and 41).

### Slide 48 · Delete everything, pull it back

```bash
rm -rf .dvc/cache data/loans.csv
ls data
```

```
loans.csv.dvc
```

```bash
dvc pull
wc -l data/loans.csv
```

```
A       data/loans.csv
1 file fetched and 1 file added
6001 data/loans.csv
```

### Slide 50 · Step 8: training becomes a stage

```bash
dvc stage add -n train \
  -d src/train.py -d data/loans.csv \
  -o models/model.pkl -M metrics.json \
  python src/train.py
```

```
Added stage 'train' in 'dvc.yaml'
```

### Slide 51 · dvc.yaml, line by line

```bash
cat dvc.yaml
```

```
stages:
  train:
    cmd: python src/train.py
    deps:
    - data/loans.csv
    - src/train.py
    outs:
    - models/model.pkl
    metrics:
    - metrics.json:
        cache: false
```

### Slide 52 · DVC reruns only what changed

```bash
dvc repro
```

```
Running stage 'train':
> python src/train.py
Training on 6,000 applicants
Accuracy: 93.1 %
Generating lock file 'dvc.lock'
```

```bash
dvc repro
```

```
Stage 'train' didn't change, skipping
Data and pipelines are up to date.
```

### Slide 54 · The receipt for the model

```bash
cat dvc.lock
```

Points to show: the `data/loans.csv` md5 is `c4f434d4...`, the same hash as version 2 on slide 41. The model's md5 sits under `outs`.

### Slide 55 · Metrics and the graph, from the terminal (EXTRA)

```bash
dvc metrics show
dvc dag
```

```
Path          accuracy
metrics.json  0.931

+--------------------+
| data/loans.csv.dvc |
+--------------------+
           *
           *
           *
      +-------+
      | train |
      +-------+
```

`dvc dag` shows only DVC-tracked inputs, so `src/train.py` does not appear as a box even though the stage depends on it. Diagram D6 on slide 56 shows both.

### Slide 57 · Commit the pipeline, push the model

```bash
git add dvc.yaml dvc.lock metrics.json models/.gitignore
git commit -m "Training pipeline"
dvc push
```

```
1 file pushed
```

The one file is the model. Data v2 was already in the remote.

### Slide 58 · Three commands rebuild the project anywhere

```bash
cd .. && git clone loan-project teammate-copy && cd teammate-copy
dvc pull
```

```
A       data/loans.csv
A       models/model.pkl
2 files fetched and 2 files added
```

```bash
docker run -v "$(pwd)/data:/app/data" -v "$(pwd)/models:/app/models" loan-train:1.1
```

```
Training on 6,000 applicants
Accuracy: 93.1 %
```

```bash
cd ../loan-project
```

**Do not forget the last `cd`.** Everything after this runs in `loan-project`, not in the teammate copy.

### Slide 59 · Discussion 2 (answers in slide notes)

### Slide 62 · Break

During the break, check `git status` is clean and `dvc status` says up to date in `loan-project`.

---

## Part 3 · Why validation (slides 63 to 71)

### Slide 65 · The bad batch trains without a single error

```bash
cp batches/loans_bad.csv data/loans.csv
dvc add data/loans.csv
dvc repro
```

```
Running stage 'train':
> python src/train.py
Training on 7,000 applicants
Accuracy: 91.1 %
Updating lock file 'dvc.lock'
```

```bash
python src/predict.py
```

```
Prediction:  WILL DEFAULT
Confidence:  57.0%
```

Say: "Accuracy 91.1. Looks fine. But the same applicant who was a 99 percent default (you will see that number on slide 70) is now a coin flip."

### Slide 66 · The numbers were wrong before training started

```bash
python tools/peek.py data/loans.csv
```

```
rows           7,000
mean           3,693
min                0
max           20,533
zeros            312
```

Data v2's mean income was 46,230. Monthly, not yearly. And 312 zeros where nulls used to be.

### Slide 70 · DVC lets us undo it

```bash
git checkout HEAD data/loans.csv.dvc dvc.lock metrics.json
dvc checkout
```

```
Updated 3 paths from c238e07
M       data/loans.csv
M       models/model.pkl
```

```bash
dvc repro
python src/predict.py
```

```
Data and pipelines are up to date.
Prediction:  WILL DEFAULT
Confidence:  99.0%
```

Both the good data and the good model came back from the cache. Nothing retrained.

---

## Part 4 · Write the contract (slides 72 to 91)

Open `src/validate.py` on screen for slides 77, 83 and 88. It is the same code as the slides.

### Slide 78 · Renamed column and wrong type, both caught

```bash
python src/validate.py data/loans.csv schema
python src/validate.py batches/batch_renamed.csv schema
python src/validate.py batches/batch_string.csv schema
```

```
SCHEMA        PASS
SCHEMA        FAIL  missing column: loan_amount
SCHEMA        FAIL  credit_score: expected a number, got object
```

`batch_string` has 40 credit scores written as `unknown`, so pandas reads the whole column as text.

### Slide 79 · Zeros where nulls used to be, caught by range

```bash
python src/validate.py batches/batch_nullzero.csv schema
```

```
SCHEMA        FAIL  income: 50 rows outside 1 to 10,000,000
```

### Slide 80 · Discussion 3: will the swapped batch pass?

Take predictions first, then:

```bash
python src/validate.py batches/batch_swapped.csv schema
```

```
SCHEMA        PASS
```

### Slide 82 · The reference profile is built once, from good data

```bash
python build_reference.py
cat reference.json
git add reference.json
git commit -m "Reference profile from data v2"
```

```
reference.json written from 6,000 rows of data/loans.csv
{
  "income": {"mean": 46229.7, "null_rate": 0.0, "min": 12000, "max": 246400},
  "loan_amount": {"mean": 402650.5, "null_rate": 0.0, "min": 26000, "max": 2500000},
  "credit_score": {"mean": 649.3, "null_rate": 0.0, "min": 393, "max": 850}
}
```

(The real file is indented over 20 lines; the values are what matter.)

### Slide 84 · Right type, right range, wrong units

```bash
python src/validate.py batches/batch_monthly.csv
```

```
SCHEMA        PASS
DISTRIBUTION  FAIL  income: mean 3,862 vs reference 46,230
FRESHNESS     PASS
```

### Slide 85 · The swapped batch fails on distribution

```bash
python src/validate.py batches/batch_swapped.csv
```

```
SCHEMA        PASS
DISTRIBUTION  FAIL  income: mean 412,411 vs reference 46,230
                    loan_amount: mean 46,343 vs reference 402,650
FRESHNESS     PASS
```

### Slide 88 · Yesterday's file, sent again

```bash
python src/validate.py batches/batch_stale.csv
```

```
SCHEMA        PASS
DISTRIBUTION  PASS
FRESHNESS     FAIL  newest row is 94 days old, limit 30
```

If you generated the data a day or two before class, the number may read 95 or 96. That is correct: it is counted from today.

### Slide 89 · Six batches, three checks

```bash
python src/validate.py data/loans.csv batches/batch_*.csv
```

```
FILE                     SCHEMA   DISTRIBUTION   FRESHNESS
loans.csv                PASS     PASS           PASS
batch_monthly.csv        PASS     FAIL           PASS
batch_new.csv            PASS     PASS           PASS
batch_nullzero.csv       FAIL     not run        not run
batch_renamed.csv        FAIL     not run        not run
batch_stale.csv          PASS     PASS           FAIL
batch_string.csv         FAIL     not run        not run
batch_swapped.csv        PASS     FAIL           PASS
```

`batch_new` is a correct batch. It is there so that one batch passes everything.

### Slide 90 · Discussion 4 (answers in slide notes)

---

## Part 5 · Place the gate (slides 92 to 105)

### Slide 96 · validate becomes a stage before train

```bash
dvc stage add -n validate \
  -d src/validate.py -d data/loans.csv -d reference.json \
  -o reports/validation.json \
  python src/validate.py data/loans.csv

dvc stage add -f -n train \
  -d src/train.py -d data/loans.csv -d reports/validation.json \
  -o models/model.pkl -M metrics.json \
  python src/train.py
```

```
Added stage 'validate' in 'dvc.yaml'
Added stage 'train' in 'dvc.yaml'
```

`-f` replaces the existing `train` stage. The only change is the new dependency, `reports/validation.json`, and that is what forces `validate` to run first.

### Slide 98 · The bad batch never reaches the model

```bash
cp batches/loans_bad.csv data/loans.csv
dvc add data/loans.csv
dvc repro
```

```
Running stage 'validate':
> python src/validate.py data/loans.csv
SCHEMA        FAIL  income: 312 rows outside 1 to 10,000,000
DISTRIBUTION  not run (schema failed)
FRESHNESS     not run (schema failed)
ERROR: failed to reproduce 'validate': failed to run: python src/validate.py data/loans.csv, exited with 1
```

```bash
dvc metrics show
```

```
Path          accuracy
metrics.json  0.931
```

0.931 is still the model trained on data v2. `train` never ran.

### Slide 99 · A corrected export walks straight through

```bash
cp batches/loans_v3_good.csv data/loans.csv
dvc add data/loans.csv
dvc repro
```

```
Running stage 'validate':
> python src/validate.py data/loans.csv
SCHEMA        PASS
DISTRIBUTION  PASS
FRESHNESS     PASS
Running stage 'train':
> python src/train.py
Training on 7,000 applicants
Accuracy: 91.8 %
```

```bash
git add dvc.yaml dvc.lock metrics.json reports/.gitignore data/loans.csv.dvc
git commit -m "Validation gate, and data v3"
dvc push
```

```
3 files pushed
```

(Data v3, the new model, and the validation report.)

### Slide 100 · Week 1: the swapped applicant was approved

```bash
python src/predict.py swapped nocheck
```

```
Prediction:  will repay
Confidence:  30.0%
```

### Slide 102 · The swapped applicant is now rejected

```bash
python src/predict.py swapped
```

```
REJECTED:    income=420,000 is outside the training range 12,000 to 246,400
```

```bash
python src/predict.py
```

```
Prediction:  WILL DEFAULT
Confidence:  100.0%
```

The correct applicant still gets through.

---

## Overflow slides with commands

### X1 · The same contract in pandera

```bash
python tools/validate_pandera.py batches/batch_nullzero.csv
```

```
SCHEMA        FAIL
column                 check  failure_case
income in_range(1, 10000000)             0
...
```

### X2 · Validation inside the container

```bash
docker build -t loan-train:1.2 .
docker run -v "$(pwd)/data:/app/data" -v "$(pwd)/reference.json:/app/reference.json" loan-train:1.2 python src/validate.py data/loans.csv
```

```
SCHEMA        PASS
DISTRIBUTION  PASS
FRESHNESS     PASS
```

Rebuild first so the image has the current `src/`. A command after the image name replaces the Dockerfile's `CMD`.

### X4 · Cleaning the cache

```bash
dvc gc -w
```

Asks for confirmation, then deletes every cached version the current workspace does not use. The remote still has them; `dvc pull` brings any back.

### X7 · A serving container

Uses the Week 5 `flask-docker-demo` folder:

```bash
cd ../../flask-docker-demo        # wherever you keep it
docker build -t flask-demo .
docker run -d -p 5000:5000 flask-demo
curl http://localhost:5000/health
```

---

## After class

```bash
cd week6-demo
bash scripts/fresh_start.sh        # resets everything for the next section
```
