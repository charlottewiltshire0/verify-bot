@echo off
title StarStudio
set copyright=Copyright 2023 StarStudio. All rights reserved.
cls
echo (%time%)                                                      #             ##
echo (%time%)                                                                   #  #
echo (%time%)   #   #   ###   # ##    ###   #   #   ## #  # ##    ##     ###    #
echo (%time%)   #   #  #   #  ##  #  #   #   # #   #  #   ##  #    #    #   #  ####
echo (%time%)   # # #  #   #  #      #####    #     ##    #        #    #####   #
echo (%time%)   # # #  #   #  #      #       # #   #      #        #    #       #
echo (%time%)    # #    ###   #       ###   #   #   ###   #       ###    ###    #
echo (%time%)                                      #   #
echo (%time%)                                       ###
echo %copyright%
del ./poetry.lock
python ./installer.py
:runScript
poetry run python ./main.py
echo (%time%) Bot closed/crashed... restarting!
goto runScript
pause