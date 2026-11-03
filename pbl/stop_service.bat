@echo off
echo Stopping HealthPulse background service...
taskkill /f /im pythonw.exe >nul 2>&1
echo [OK] HealthPulse background service stopped.
pause

