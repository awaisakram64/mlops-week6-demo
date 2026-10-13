#!/usr/bin/env bash
# Rebuilds class/loan-project in the exact state the slides expect at the START of a part,
# by running every slide command up to that point (Docker steps are replaced by plain Python).
#
#   bash scripts/jump_to.sh part2     start of Part 2 (Part 1 done)
#   bash scripts/jump_to.sh part3     start of Part 3 (Parts 1 and 2 done)
#   bash scripts/jump_to.sh part4     start of Part 4
#   bash scripts/jump_to.sh part5     start of Part 5
#   bash scripts/jump_to.sh end       the whole session, end to end (a full rehearsal)
#
# Use it in class if a live step goes wrong: jump, then carry on from the next slide.
# It DELETES the current class/ folder first.
set -e
TARGET="${1:-end}"
cd "$(dirname "$0")/.."
ROOT="$(pwd)"

bash scripts/fresh_start.sh > /dev/null
cd class/loan-project

run() { echo; echo "\$ $*"; eval "$@"; }
slide() { echo; echo "================ SLIDE $1"; }

# Git needs a name and email to commit. Set them here only if missing.
git config user.name  > /dev/null 2>&1 || git config --global user.name  "SEN 337 Demo"
git config user.email > /dev/null 2>&1 || git config --global user.email "demo@example.com"

# ------------------------------------------------------------------ PART 1
part1() {
  slide 21
  # The one-line edit made live on slide 21: print the row count after reading the CSV.
  python - <<'EOF'
p = "src/train.py"
s = open(p).read()
line = 'df = pd.read_csv("data/loans.csv")\n'
add = 'print(f"Training on {len(df):,} applicants")\n'
if add not in s:
    s = s.replace(line, line + add)
open(p, "w").write(s)
EOF
  slide "25 (Docker replaced by plain Python)"
  run python src/train.py
}

# ------------------------------------------------------------------ PART 2
part2() {
  slide 34
  run git init -b main
  run dvc init
  slide 35
  run mkdir ../dvc-remote
  run dvc remote add -d localremote ../dvc-remote
  run git add .gitignore .dockerignore Dockerfile requirements.txt src tools '*.py' .dvc/config
  run git commit -q -m '"Code, Dockerfile and DVC setup"'
  slide 36;  run dvc add data/loans.csv
  slide 37;  run cat data/loans.csv.dvc
  slide 38;  run cat data/.gitignore; run ls .dvc/cache/files/md5
  slide 39
  run git add data/loans.csv.dvc data/.gitignore
  run git commit -q -m '"Data v1: 5,000 applicants"'
  run git tag data-v1
  run dvc push
  slide 40;  run cp batches/loans_v2.csv data/loans.csv; run dvc status
  slide 41;  run dvc add data/loans.csv; run git diff
  slide 42;  run git commit -q -am '"Data v2: 6,000 applicants"'; run git tag data-v2; run dvc push
  slide 43
  run git checkout -q data-v1; run dvc checkout; run wc -l data/loans.csv
  run git checkout -q main;    run dvc checkout; run wc -l data/loans.csv
  slide 45;  run git log -n 2 data/loans.csv.dvc; run dvc diff data-v1 data-v2
  slide 46
  run git tag
  run ls ../dvc-remote/files/md5
  slide 48
  run rm -rf .dvc/cache data/loans.csv
  run ls data
  run dvc pull
  run wc -l data/loans.csv
  slide 50
  run dvc stage add -n train -d src/train.py -d data/loans.csv -o models/model.pkl -M metrics.json python src/train.py
  slide 51;  run cat dvc.yaml
  slide 52;  run dvc repro; run dvc repro
  slide 54;  run cat dvc.lock
  slide 55;  run dvc metrics show; run dvc dag
  slide 57
  run git add dvc.yaml dvc.lock metrics.json models/.gitignore
  run git commit -q -m '"Training pipeline"'
  run dvc push
  slide "58 (docker run replaced by plain Python)"
  run cd ..
  run git clone -q loan-project teammate-copy
  run cd teammate-copy
  run dvc pull
  run python src/train.py
  run cd ../loan-project
}

# ------------------------------------------------------------------ PART 3
part3() {
  slide 65
  run cp batches/loans_bad.csv data/loans.csv
  run dvc add data/loans.csv
  run dvc repro
  run python src/predict.py
  slide 66;  run python tools/peek.py data/loans.csv
  slide 70
  run git checkout HEAD data/loans.csv.dvc dvc.lock metrics.json
  run dvc checkout
  run dvc repro
  run python src/predict.py
}

# ------------------------------------------------------------------ PART 4
part4() {
  slide 78
  run python src/validate.py data/loans.csv schema || true
  run python src/validate.py batches/batch_renamed.csv schema || true
  run python src/validate.py batches/batch_string.csv schema || true
  slide 79;  run python src/validate.py batches/batch_nullzero.csv schema || true
  slide 80;  run python src/validate.py batches/batch_swapped.csv schema || true
  slide 82
  run python build_reference.py
  run cat reference.json
  run git add reference.json
  run git commit -q -m '"Reference profile from data v2"'
  slide 84;  run python src/validate.py batches/batch_monthly.csv || true
  slide 85;  run python src/validate.py batches/batch_swapped.csv || true
  slide 88;  run python src/validate.py batches/batch_stale.csv || true
  slide 89;  run python src/validate.py data/loans.csv 'batches/batch_*.csv' || true
}

# ------------------------------------------------------------------ PART 5
part5() {
  slide 96
  run dvc stage add -n validate -d src/validate.py -d data/loans.csv -d reference.json -o reports/validation.json python src/validate.py data/loans.csv
  run dvc stage add -f -n train -d src/train.py -d data/loans.csv -d reports/validation.json -o models/model.pkl -M metrics.json python src/train.py
  slide 98
  run cp batches/loans_bad.csv data/loans.csv
  run dvc add data/loans.csv
  run dvc repro || true
  run dvc metrics show
  slide 99
  run cp batches/loans_v3_good.csv data/loans.csv
  run dvc add data/loans.csv
  run dvc repro
  run git add dvc.yaml dvc.lock metrics.json reports/.gitignore data/loans.csv.dvc
  run git commit -q -m '"Validation gate, and data v3"'
  run dvc push
  slide 100; run python src/predict.py swapped nocheck
  slide 102; run python src/predict.py swapped || true; run python src/predict.py
}

case "$TARGET" in
  part2) part1 ;;
  part3) part1; part2 ;;
  part4) part1; part2; part3 ;;
  part5) part1; part2; part3; part4 ;;
  end)   part1; part2; part3; part4; part5 ;;
  *) echo "Use one of: part2 part3 part4 part5 end"; exit 1 ;;
esac

echo
echo "================ DONE. class/loan-project is at the start of: $TARGET"
echo "Now:  cd $ROOT/class/loan-project"
