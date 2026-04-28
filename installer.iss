[Setup]
AppName=Sindlish
AppVersion=0.7.0
DefaultDirName={autopf}\Sindlish
DefaultGroupName=Sindlish
UninstallDisplayIcon={app}\sindlish.exe
SetupIconFile=tools\sindlish.ico
WizardImageFile=tools\wizard.bmp
WizardSmallImageFile=tools\wizard_small.bmp
Compression=lzma2
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=sindlish-installer-win64
ChangesEnvironment=yes

[Files]
Source: "dist\sindlish.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Sindlish"; Filename: "{app}\sindlish.exe"

[Registry]
; Add to PATH for the current user
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: NeedsAddPath(ExpandConstant('{app}'))

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  Result := Pos(Upper(Param), Upper(OrigPath)) = 0;
end;
