#!/bin/bash

cd "$(dirname "$0")"
title="StarStudio"
copyright="Copyright 2023 StarStudio. All rights reserved."
clear

echo "(${date +%T})                                                      #             ##"
echo "(${date +%T})                                                                   #  #"
echo "(${date +%T})   #   #   ###   # ##    ###   #   #   ## #  # ##    ##     ###    #"
echo "(${date +%T})   #   #  #   #  ##  #  #   #   # #   #  #   ##  #    #    #   #  ####"
echo "(${date +%T})   # # #  #   #  #      #####    #     ##    #        #    #####   #"
echo "(${date +%T})   # # #  #   #  #      #       # #   #      #        #    #       #"
echo "(${date +%T})    # #    ###   #       ###   #   #   ###   #       ###    ###    #"
echo "(${date +%T})                                      #   #"
echo "(${date +%T})                                       ###"
echo "$copyright"

if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Please install Poetry first."
    exit 1
fi

command="$1"
shift

case "$command" in
    install)
        echo "Installing dependencies..."
        poetry install
        ;;
    run)
        echo "Running the application..."
        poetry run python ./main.py
        ;;
    shell)
        echo "Entering the Poetry shell..."
        poetry shell
        ;;
    test)
        echo "Running tests..."
        poetry run pytest
        ;;
    *)
        echo "Usage: $0 [install|run|shell|test]"
        exit 1
        ;;
esac

echo "(${date +%T}) Bot closed/crashed..."
exit 0