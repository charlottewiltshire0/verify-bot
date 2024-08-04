#!/bin/bash
echo "StarStudio"
copyright="Copyright 2023 StarStudio. All rights reserved."
clear
echo "($time)"
echo "($time)"
echo "($time)   #   #   ###   # ##    ###   #   #   ## #  # ##    ##     ###    #"
echo "($time)   #   #  #   #  ##  #  #   #   # #   #  #   ##  #    #    #   #  ####"
echo "($time)   # # #  #   #  #      #####    #     ##    #        #    #####   #"
echo "($time)   # # #  #   #  #      #       # #   #      #        #    #       #"
echo "($time)    # #    ###   #       ###   #   #   ###   #       ###    ###    #"
echo "($time)                                      #   #"
echo "($time)                                       ###"
echo "$copyright"
rm ./poetry.lock
python3 ./installer.py
while true; do
    poetry run python ./main.py
    echo "($time) Bot closed/crashed... restarting!"
done
