#!/bin/bash

# Convenience script to set up environment and run tests

set -eo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if [ ! -d venv ]
then
    python3 -m venv venv
fi

#shellcheck disable=SC1091
. venv/bin/activate

echo "Installing/updating requirements"
pip install -r requirements.txt --upgrade > /dev/null

echo "Linting Bash scripts"
find . -name '*.sh' -exec shellcheck {} +

echo "Checking code formatting"
black --check .

PYTHONPATH=$(realpath "${SCRIPT_DIR}")
export PYTHONPATH

echo "Running Python linter"
pylint "$(realpath microblog)"

for file in tests/test_*.py ; do
    echo "Testing ${file}..."
    SQLITE_PATH=$(mktemp --suffix "microblog.sqlite")
    export SQLITE_PATH
    python3 -m unittest "$(echo "$file" | sed 's/\//./g' | sed 's/.py//g')"
done

unset PYTHONPATH
unset SQLITE_PATH
