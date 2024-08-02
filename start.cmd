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
:runScript
poetry run python ./run.py
echo (%time%) Bot closed/crashed... restarting!
goto runScript
pause