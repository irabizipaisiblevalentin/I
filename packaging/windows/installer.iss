; Inno Setup script for the I Studio IDE Windows desktop app.
; Compile with: ISCC.exe packaging\windows\installer.iss
; Expects a PyInstaller onedir build in dist\istudio-ide (build_windows.ps1).

#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif

#define MyAppName "I Studio IDE"
#define MyAppExeName "IStudioIDE.exe"
#define MyAppAssocName MyAppName + " Project"
#define MyAppPublisher "I Language"
#define MyAppURL "https://github.com/irabizipaisiblevalentin/I"
#define MyAppSourceDir "..\..\dist\istudio-ide"

[Setup]
AppId={{2E9B7C1A-8D4F-4E6B-9A3D-5C2F1E0B7A6D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\..\release
OutputBaseFilename=IStudioIDE-Setup-{#MyAppVersion}
SetupIconFile=app.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion={#MyAppVersion}
VersionInfoDescription={#MyAppName} Installer
VersionInfoCompany={#MyAppPublisher}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a {cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#MyAppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Classes\istudio-ide"; ValueType: string; ValueData: "URL:I Studio IDE Protocol"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\istudio-ide\shell\open\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Directory\shell\IStudioIDE"; ValueType: string; ValueData: "Open with I Studio"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\IStudioIDE\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" --app ""%1"""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\IStudioIDE"; ValueType: string; ValueData: "Open with I Studio"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\IStudioIDE\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" --app ""%V"""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueName: "Path"; ValueData: "{app}"; Flags: uninsdeletevalue

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
