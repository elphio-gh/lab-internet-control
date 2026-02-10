@echo off

REM --- FASE 1: TERMINAZIONE PROCESSI BROWSER ---
taskkill /F /IM chrome.exe /T >nul 2>&1
taskkill /F /IM msedge.exe /T >nul 2>&1
taskkill /F /IM firefox.exe /T >nul 2>&1
taskkill /F /IM brave.exe /T >nul 2>&1
taskkill /F /IM opera.exe /T >nul 2>&1
taskkill /F /IM vivaldi.exe /T >nul 2>&1
taskkill /F /IM iexplore.exe /T >nul 2>&1

REM --- FASE 2: CONFIGURAZIONE RESTRIZIONI DI RETE ---
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /t REG_SZ /d "127.0.0.1:6666" /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v AutoDetect /t REG_DWORD /d 0 /f >nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v AutoConfigURL /f >nul 2>&1

REM --- FASE 3: AGGIORNAMENTO PARAMETRI DI SISTEMA ---
RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters 1, True

REM --- FASE 4: CONFIGURAZIONE RIPRISTINO AL RIAVVIO ---
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce" /v SbloccoEmergenza /t REG_SZ /d "cmd /c reg add \"HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\" /v ProxyEnable /t REG_DWORD /d 0 /f" /f >nul

REM --- FASE 5: AUTODISTRUZIONE (Sicura per Master) ---
REM Si elimina solo se NON è in C:\ per proteggere la copia del docente
if /I NOT "%~dp0"=="C:\" (goto) 2>nul & del "%~f0"