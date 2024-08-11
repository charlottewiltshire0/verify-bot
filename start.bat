@echo off
cd /d "%~dp0"
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

where poetry >nul 2>nul
if %errorlevel% neq 0 (
    echo Poetry is not installed. Please install Poetry first.
    exit /b 1
)

set COMMAND=%1
shift

if "%COMMAND%"=="install" (
    echo Installing dependencies...
    poetry install
) else if "%COMMAND%"=="run" (
    echo Running the application...
    poetry run python ./main.py
) else if "%COMMAND%"=="shell" (
    echo Entering the Poetry shell...
    poetry shell
) else if "%COMMAND%"=="test" (
    echo Running tests...
    poetry run pytest
) else (
    echo Usage: poetry.bat [install|run|shell|test]
    exit /b 1
)

echo (%time%) Bot closed/crashed...
exit /b 0
pause