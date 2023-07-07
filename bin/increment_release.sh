#!/usr/bin/env bash

# increment version number
export OLDVERSION="$(grep -m 1 version setup.py | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3)"
export VERSION="$(echo ${OLDVERSION} | awk -F. -v OFS=. '{$NF += 1 ; print}')"

if [ "$(uname)" == "Darwin" ]; then
    # Do something under Mac OS X platform 
    sed -i '' -e "s/$OLDVERSION/$VERSION/g" setup.py
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Do something under GNU/Linux platform
    sed -i "s/$OLDVERSION/$VERSION/g" setup.py
fi
