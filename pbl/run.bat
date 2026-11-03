@echo off
title HealthPulse Lifetime System
echo ========================================================
echo        HEALTHPULSE - PATIENT HEALTH PROBLEMS TRACKER
echo             Registered: richitha132@gmail.com
echo ========================================================
echo  [1] Open HealthPulse in Browser (http://localhost:5000)
echo  [2] Start Lifetime Silent Background Service (Runs Forever)
echo  [3] Install Auto-Start on Windows Boot (True Lifetime)
echo  [4] Download Patient Health Report Directly
echo  [5] Stop Background Service
echo  [6] Exit
echo ========================================================
set /p opt="Select option (1-6): "

if "%opt%"=="1" (
    start http://localhost:5000/login
    python app.py
) else if "%opt%"=="2" (
    wscript.exe start_lifetime_service.vbs
    start http://localhost:5000/login
    echo HealthPulse is running silently in the background!
    timeout /t 3
) else if "%opt%"=="3" (
    call install_auto_start_on_boot.bat
) else if "%opt%"=="4" (
    start http://localhost:5000/report
) else if "%opt%"=="5" (
    call stop_service.bat
) else (
    exit
)
