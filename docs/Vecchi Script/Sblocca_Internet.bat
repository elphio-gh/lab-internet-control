@echo off

REM --- FASE 1: TERMINAZIONE PROCESSI BROWSER ---
taskkill /F /IM chrome.exe /T >nul 2>&1
taskkill /F /IM msedge.exe /T >nul 2>&1
taskkill /F /IM firefox.exe /T >nul 2>&1
taskkill /F /IM brave.exe /T >nul 2>&1
taskkill /F /IM opera.exe /T >nul 2>&1
taskkill /F /IM vivaldi.exe /T >nul 2>&1
taskkill /F /IM iexplore.exe /T >nul 2>&1

timeout /t 1 /nobreak >nul

REM --- FASE 2: RIPRISTINO IMPOSTAZIONI DI RETE ---
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /t REG_SZ /d "" /f >nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v AutoDetect /t REG_DWORD /d 1 /f >nul

REM --- FASE 3: AGGIORNAMENTO AMBIENTE E CACHE ---
RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters 1, True
ipconfig /flushdns >nul

REM --- FASE 4: RIMOZIONE PERSISTENZA RIAVVIO ---
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce" /v SbloccoEmergenza /f >nul 2>&1

REM --- FASE 5: AUTODISTRUZIONE (Sicura per Master) ---
if /I NOT "%~dp0"=="C:\" (goto) 2>nul & del "%~f0"