#!/usr/bin/env bash -l

export > /tmp/exports

say running

cd "$PWD"
ls > /tmp/dirlisting

PYTHON="/usr/local/bin/python3"

if hash $PYTHON 2>/dev/null; then
    if ! $PYTHON -u update.py | tee /tmp/InvestoscopUpdate.log 2> /tmp/InvestoscopUpdateErr.log; then
        echo "Resource Directory Listing"
        ls
        echo "Exports"
        export

        echo "ALERT:Error|Something didn't go right - check the log!"
    fi

    rm /tmp/InvestoscopUpdate.log
    rm /tmp/InvestoscopUpdateErr.log
else
    echo "ALERT:Error|You don't have python3 in folder /usr/local/bin!"
fi
