#!/usr/bin/env bash
# Creates a clean class/loan-project from kit/, with freshly generated data.
# DELETES any previous class/ folder (the project, the DVC remote, the teammate copy).
#
#   bash scripts/fresh_start.sh
#
# Run it the day before class, and again to reset after a rehearsal.
set -e
cd "$(dirname "$0")/.."

rm -rf class
mkdir class
cp -r kit class/loan-project

cd class/loan-project
python 00_make_data.py
python 04_make_batches.py

# The "clean machine" for slide 10: pandas only, no scikit-learn.
# Lives outside class/ so resets do not delete it. Created once.
if [ ! -d ../../clean-env ]; then
  echo "Creating clean-env (pandas only) for slide 10..."
  python -m venv ../../clean-env
  if [ -f ../../clean-env/Scripts/activate ]; then
    ../../clean-env/Scripts/python -m pip install -q pandas
  else
    ../../clean-env/bin/python -m pip install -q pandas
  fi
fi

echo
echo "Ready. Now:  cd class/loan-project"
