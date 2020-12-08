#!/bin/bash

set -exu -o pipefail

pip install -U pip setuptools wheel

python setup.py sdist --formats=zip
pip install dist/*.zip

# ${FOO:-} means "$FOO if defined, else empty string"
if [ "${DOC_BUILD:-}" = "1" ]; then
    pip install -U sphinx
    pip install -U -r ci/rtd-requirements.txt
    cd docs
    sphinx-build -nW -b html source build
else
    # Actual tests

    pip install -Ur test-requirements.txt
    if [ -n "${OLD_CRYPTOGRAPHY:-}" ]; then
        pip install cryptography=="${OLD_CRYPTOGRAPHY}"
    fi
    mkdir empty
    pushd empty
    INSTALLDIR=$(python -c "import os, trustme; print(os.path.dirname(trustme.__file__))")
    pytest -c ../pytest.ini ../tests --cov="$INSTALLDIR" --cov=../tests --cov-config="../.coveragerc"

    pip install codecov
    codecov -F $(uname | tr A-Z a-z)
fi
