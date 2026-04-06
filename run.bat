@echo off
setlocal

:: Get the current directory of the batch file
set "ROOT_DIR=%~dp0"

echo Launching Development Environment...

:: Launch windows terminal with two tabs (backend and frontend)
wt -w 0 nt -d "%ROOT_DIR%backend" --title "Backend" cmd /k "python -m uvicorn api.api:app --reload" ; ^
nt -d "%ROOT_DIR%frontend" --title "Frontend" cmd /k "npm run dev"

:: Wait a few seconds for servers to initialize
echo Waiting for servers...
timeout /t 3 /nobreak > nul


start http://localhost:5173
:: start http://localhost:8000/docs

echo Environment is ready!