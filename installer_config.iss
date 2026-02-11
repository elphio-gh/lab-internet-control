; Script per Inno Setup
; 🎓 DIDATTICA: Questo script crea l'installer professionale .exe con icone e disinstallazione.

[Setup]
AppId={{C15A7B8F-E2D4-4B9F-83C1-72D9B3877F92}
AppName=Lab Internet Control
AppVersion=0.3.1
AppPublisher=Alfonso Parisini
DefaultDirName={autopf}\LabInternetControl
DefaultGroupName=Lab Internet Control
AllowNoIcons=yes
; Output file
OutputDir=.
OutputBaseFilename=LabInternetControl_Setup_v0.3.1
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Prendiamo i file generati da PyInstaller nella cartella dist
Source: "dist\LabInternetControl\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Lab Internet Control"; Filename: "{app}\LabInternetControl.exe"
Name: "{autodesktop}\Lab Internet Control"; Filename: "{app}\LabInternetControl.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\LabInternetControl.exe"; Description: "{cm:LaunchProgram,Lab Internet Control}"; Flags: nowait postinstall skipifsilent
