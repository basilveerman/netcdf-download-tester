#!/bin/bash

BEAKER_SESSION_ID=4161d82baf164d3090c6dfc6580f6be2

echo "Data saved in `pwd`/"

while read line
do
    ARR=(${line//\// })
    LENGTH=${#ARR[@]}
    LAST_POSITION=$((LENGTH - 1))
    FNAME=${ARR[${LAST_POSITION}]} # strip out url base
    FNAME=${FNAME//.nc} # remove all .nc
    FNAME=${FNAME//&} # remove &

    # replace all funny chars with '-'
    FNAME=${FNAME//"?"/"-"}
    FNAME=${FNAME//"["/"-"}
    FNAME=${FNAME//"]"/"-"}
    FNAME=${FNAME//":"/"-"}
    
    if [ ${FNAME::-1} -eq "-" ]; then
        FNAME=${FNAME::-1} # remove last '-'
    fi

    FNAME="data/${FNAME}.nc"

    if [ ! -e "$FNAME" ]; then
        echo "Downloaded: ${FNAME}"
        wget --output-document="${FNAME}" --header "Cookie: beaker.session.id=$BEAKER_SESSION_ID" $line
    else
        echo "File already exists: ${FNAME}"
    fi
done
