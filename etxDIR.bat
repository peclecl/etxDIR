@echo off
:: %~dp0 refers to the directory where this batch file is located.
:: This ensures it always finds the python script, no matter where you run the command from.
python "%~dp0etxDIR.py" %*