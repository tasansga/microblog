#!/bin/bash

# Convenience script to set up environment and start CLI

set -eo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if [ ! -d venv ]
then
    echo "Creating Python venv"
    python3 -m venv venv
fi

#shellcheck disable=SC1091
. venv/bin/activate

echo "Installing/updating requirements"
pip install -r requirements.txt > /dev/null

PYTHONPATH=$(realpath venv/lib/python3.10/site-packages):$(realpath "${SCRIPT_DIR}")
export PYTHONPATH

python3 microblog/cli.py "$@"
