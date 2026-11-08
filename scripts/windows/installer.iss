; GridPlayer Alabaster has its own AppId, install folder and Start menu
; group, so it installs next to upstream GridPlayer (vzhd1701/gridplayer)
; instead of over it, and its uninstaller never removes upstream's copy.
; Never set AppId back to upstream's. The executable inside is still
; {APP_NAME}.exe; only the folder separates the two.
[Setup]
AppId={{5E9EFBF1-5CB1-4898-BF59-6CA87176891D}
AppName={APP_DISP_NAME}
AppVersion={APP_VERSION}
AppVerName={APP_DISP_NAME} {APP_VERSION}
AppPublisher={APP_AUTHOR}
AppPublisherURL={APP_URL}
WizardStyle=classic
DefaultDirName={autopf}\GridPlayer Alabaster
DefaultGroupName=GridPlayer Alabaster
UninstallDisplayName={APP_DISP_NAME}
UninstallDisplayIcon={app}\{APP_NAME}.exe
Compression=lzma2
LZMAUseSeparateProcess=yes
SolidCompression=yes
ShowLanguageDialog=no
VersionInfoVersion={APP_VERSION_NUMERIC}
VersionInfoCompany={APP_AUTHOR}
VersionInfoCopyright=(c) 2021 {APP_AUTHOR}
VersionInfoProductName={APP_DISP_NAME}
VersionInfoProductVersion={APP_VERSION_NUMERIC}
VersionInfoProductTextVersion={APP_VERSION}
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
SourceDir={APP_SRC}
ChangesAssociations=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "*"; DestDir: "{app}"; Flags: recursesubdirs;

[Icons]
Name: "{group}\{APP_DISP_NAME}"; Filename: "{app}\{APP_NAME}.exe"; AppUserModelID: "{APP_ID}"
Name: "{group}\{cm:UninstallProgram,{APP_DISP_NAME}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{APP_DISP_NAME}"; Filename: "{app}\{APP_NAME}.exe"; AppUserModelID: "{APP_ID}"; Tasks: desktopicon

[Run]
Filename: "{app}\{APP_NAME}.exe"; Flags: nowait postinstall skipifsilent 64bit; Description: "{cm:LaunchProgram,{APP_DISP_NAME}}"

[Registry]
{APP_FILE_ASSOCIATIONS}
Root: HKCR; SubKey: "Local Settings\Software\Microsoft\Windows\Shell\MuiCache"; ValueType: string; ValueName: "{app}\{APP_NAME}.exe.FriendlyAppName"; ValueData: "{APP_DISP_NAME}"; Flags: uninsdeletevalue
Root: HKCR; SubKey: "Local Settings\Software\Microsoft\Windows\Shell\MuiCache"; ValueType: string; ValueName: "{app}\{APP_NAME}.exe.ApplicationCompany"; ValueData: "{APP_AUTHOR}"; Flags: uninsdeletevalue
