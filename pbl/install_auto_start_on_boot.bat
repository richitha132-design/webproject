@echo off
echo ==========================================================
echo    HealthPulse: Installing Lifetime Background Service
echo ==========================================================
set SCRIPT_PATH=%~dp0start_lifetime_service.vbs
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
copy "%SCRIPT_PATH%" "%STARTUP_DIR%\HealthPulse_Lifetime.vbs" /Y >nul
echo [OK] HealthPulse configured to start automatically on system boot!
echo [OK] Lifetime access enabled.
echo ==========================================================
echo Starting HealthPulse silent background service right now...
wscript.exe "%SCRIPT_PATH%"
echo HealthPulse is now running live at http://localhost:5000
timeout /t 3 >nul
start http://localhost:5000/login
exit

