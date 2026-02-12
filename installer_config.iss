; Script per Inno Setup
; 🎓 DIDATTICA: Questo script crea l'installer professionale .exe con icone e disinstallazione.

[Setup]
AppId={{C15A7B8F-E2D4-4B9F-83C1-72D9B3877F92}
AppName=Lab Internet Control
AppVersion=0.3.17
AppPublisher=Alfonso Parisini
DefaultDirName={autopf}\LabInternetControl
DefaultGroupName=Lab Internet Control
; Richiesto per {commondesktop} (All Users)
PrivilegesRequired=admin
AllowNoIcons=yes
; Output file
OutputDir=.
OutputBaseFilename=LabInternetControl_Setup_v0.3.17
Compression=lzma
SolidCompression=yes
WizardStyle=modern
DisableDirPage=no
DisableProgramGroupPage=no
ShowComponentSizes=yes

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Prendiamo i file generati da PyInstaller nella cartella dist
Source: "dist\LabInternetControl\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Setup]
; ...
; Quando hai il file icona, mettilo in "assets\icon.ico" e decommenta questa riga:
SetupIconFile=assets\logo.ico

[Icons]
Name: "{group}\Lab Internet Control"; Filename: "{app}\LabInternetControl.exe"
; 🎓 DIDATTICA: Creiamo l'icona sul Desktop per TUTTI gli utenti ({commondesktop}).
; Il nome è abbreviato in "Lab Control" come richiesto.
; Non specifichiamo IconFilename: Windows userà automaticamente l'icona incorporata nell'EXE.
Name: "{commondesktop}\Lab Control"; Filename: "{app}\LabInternetControl.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\LabInternetControl.exe"; Description: "{cm:LaunchProgram,Lab Internet Control}"; Flags: nowait postinstall skipifsilent
