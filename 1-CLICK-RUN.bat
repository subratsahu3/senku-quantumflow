@echo off
title SENKU QUANTUMFLOW // LIVE VISUALIZER
cd /d "D:\Subrat\quantumflow"
cls
echo ======================================================================
echo   STARTING SENKU QUANTUMFLOW WEB VISUALIZER
echo   Opening browser to http://localhost:8080 ...
echo ======================================================================
echo.
python senku.py web
pause
