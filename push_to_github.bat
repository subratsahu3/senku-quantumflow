@echo off
echo ========================================================
echo   Pushing SENKU QUANTUMFLOW to GitHub (subrat-sahu444)
echo ========================================================
cd /d "D:\Subrat\quantumflow"
git branch -M main
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Code pushed successfully to https://github.com/subrat-sahu444/senku-quantumflow
) else (
    echo [NOTE] If you saw 'Repository not found', please create the repository first:
    echo        https://github.com/new?name=senku-quantumflow
    echo        Then run this script again!
)
pause
