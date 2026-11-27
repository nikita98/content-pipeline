; Установщик «Конвейер контента» для Windows (Inno Setup 6).
; Сборка: python installer/build.py --version 0.1.0 (готовит build\stage и build\components*.iss, затем ISCC).
; Ставится для текущего пользователя, без прав администратора. Внутри — переносные Python, ffmpeg, Node, MinGit,
; auto-editor (installer/deps.json). Установщик и ярлыки запускают только файлы из папки установки.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#ifndef NumVersion
  #define NumVersion "0.0.0.0"
#endif
#define AppName "Конвейер контента"

[Setup]
AppId={{6B0E7C1A-3F2D-4E5B-9A8C-1D2E3F4A5B6C}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppName}
AppPublisherURL=https://github.com/nikita98/content-pipeline
VersionInfoVersion={#NumVersion}
VersionInfoProductName={#AppName}
VersionInfoDescription=Установка {#AppName}
DefaultDirName={userpf}\ContentPipeline
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
DisableWelcomePage=no
UsePreviousAppDir=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputBaseFilename=ContentPipeline-Setup-{#AppVersion}
SetupIconFile=build\stage\app\setup\icon.ico
UninstallDisplayIcon={app}\app\setup\icon.ico
UninstallDisplayName={#AppName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
SetupLogging=yes
ShowLanguageDialog=no

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Messages]
WelcomeLabel2=Программа установит «Конвейер контента» — страницу в браузере для подготовки роликов: проверка текстов, озвучка, распознавание речи, монтаж.%n%nВсё нужное уже внутри: Python, ffmpeg, Git, Node.js и auto-editor. Отдельно ничего ставить не надо, права администратора не нужны.%n%nДальше можно выбрать папку и дополнительные компоненты. Для компонентов нужен интернет.
SelectDirBrowseLabel=Нажмите «Далее», чтобы установить в эту папку. Чтобы выбрать другую — «Обзор». Лучше путь латиницей, например D:\ContentPipeline.
SelectComponentsLabel2=Отметьте, что поставить. Нажмите на строку, чтобы прочитать описание ниже. Не выбранное можно доставить позже в интерфейсе: раздел «Установка».
FinishedLabel=Готово. На рабочем столе появился ярлык «Конвейер контента» — он открывает интерфейс в браузере.

[Types]
Name: "custom"; Description: "Выбранные компоненты"; Flags: iscustom

#include "build\components.iss"

[Files]
Source: "build\stage\*"; DestDir: "{app}"; Components: base; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\data"

[Icons]
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\tools\python\pythonw.exe"; Parameters: """{app}\app\server.py"""; WorkingDir: "{app}"; IconFilename: "{app}\app\setup\icon.ico"; Comment: "Открыть интерфейс в браузере"
Name: "{autoprograms}\{#AppName}\{#AppName}"; Filename: "{app}\tools\python\pythonw.exe"; Parameters: """{app}\app\server.py"""; WorkingDir: "{app}"; IconFilename: "{app}\app\setup\icon.ico"; Comment: "Открыть интерфейс в браузере"
Name: "{autoprograms}\{#AppName}\Удалить {#AppName}"; Filename: "{uninstallexe}"

[Run]
; окно «Установка компонентов» (tkinter из встроенного Python, без консоли)
Filename: "{app}\tools\python\pythonw.exe"; Parameters: """{app}\app\setup\components.py"" --components {code:ExtraComponents}"; WorkingDir: "{app}"; StatusMsg: "Установка компонентов…"; Flags: waituntilterminated; Check: RunComponentsGui
; тихая установка (/VERYSILENT): то же без окна, лог — data\logs\components.log
Filename: "{app}\tools\python\python.exe"; Parameters: """{app}\app\setup\components.py"" --headless --components {code:ExtraComponents}"; WorkingDir: "{app}"; StatusMsg: "Установка компонентов…"; Flags: runhidden waituntilterminated; Check: RunComponentsSilent
Filename: "{app}\tools\python\pythonw.exe"; Parameters: """{app}\app\server.py"""; WorkingDir: "{app}"; Description: "Открыть «{#AppName}»"; Flags: postinstall nowait skipifsilent; Check: NotOpenedYet

[UninstallDelete]
Type: filesandordirs; Name: "{app}\app"
Type: filesandordirs; Name: "{app}\tools"
Type: filesandordirs; Name: "{app}\skills"
Type: filesandordirs; Name: "{app}\site"
Type: filesandordirs; Name: "{app}\licenses"
Type: filesandordirs; Name: "{app}\data\logs"
Type: filesandordirs; Name: "{app}\data\setup"
Type: files; Name: "{app}\data\server.lock"
Type: files; Name: "{app}\data\stop.request"
Type: dirifempty; Name: "{app}\data"
Type: dirifempty; Name: "{app}"

[Code]
#include "build\components_code.iss"

var
  SpaceLabel: TNewStaticText;
  CompDescLabel: TNewStaticText;
  NvidiaChecked: Boolean;

function HasNvidia: Boolean;
begin
  Result := FileExists(ExpandConstant('{sys}\nvidia-smi.exe')) or
            FileExists(ExpandConstant('{commonpf64}\NVIDIA Corporation\NVSMI\nvidia-smi.exe'));
end;

function IsAsciiPath(const S: String): Boolean;
var
  I: Integer;
begin
  Result := True;
  for I := 1 to Length(S) do
    if Ord(S[I]) > 127 then
    begin
      Result := False;
      Exit;
    end;
end;

function ExtraComponents(Param: String): String;
var
  I: Integer;
  Id: String;
begin
  Result := '';
  for I := 0 to CompCount - 1 do
  begin
    Id := CompIdAt(I);
    if (Id <> 'base') and WizardIsComponentSelected(Id) then
    begin
      if Result <> '' then
        Result := Result + ',';
      Result := Result + Id;
    end;
  end;
end;

function RunComponentsGui: Boolean;
begin
  Result := (not WizardSilent) and (ExtraComponents('') <> '');
end;

function RunComponentsSilent: Boolean;
begin
  Result := WizardSilent and (ExtraComponents('') <> '');
end;

function NotOpenedYet: Boolean;
begin
  Result := not FileExists(ExpandConstant('{app}\data\setup\opened.flag'));
end;

{ Остановить уже работающий интерфейс: сервер следит за файлом data\stop.request и удаляет data\server.lock. }
procedure StopServer(const AppDir: String);
var
  Lock: String;
  I: Integer;
begin
  Lock := AppDir + '\data\server.lock';
  if not FileExists(Lock) then
    Exit;
  Log('Server lock found, requesting stop');
  SaveStringToFile(AppDir + '\data\stop.request', 'stop', False);
  for I := 1 to 60 do
  begin
    if not FileExists(Lock) then
      Break;
    Sleep(250);
  end;
  if FileExists(Lock) then
  begin
    Log('Server did not stop in 15 s, lock is stale or server hangs');
    DeleteFile(Lock);
  end;
  DeleteFile(AppDir + '\data\stop.request');
end;

procedure UpdateSpace(Sender: TObject);
var
  Drive, Msg: String;
  FreeB, TotalB: Int64;
begin
  Drive := ExtractFileDrive(WizardForm.DirEdit.Text);
  Msg := '';
  if (Drive <> '') and GetSpaceOnDisk64(AddBackslash(Drive), FreeB, TotalB) then
    Msg := 'Свободно на диске ' + Drive + ' — ' + IntToStr(FreeB div 1073741824) + ' ГБ. '
  else if Drive = '' then
    Msg := 'Укажите полный путь, например D:\ContentPipeline. ';
  Msg := Msg + 'Окружения Python и модели тоже будут в этой папке (data). Для распознавания и озвучки с моделями нужно от 20 ГБ.';
  if not IsAsciiPath(WizardForm.DirEdit.Text) then
    Msg := Msg + #13#10#13#10 + 'Внимание: в пути есть русские буквы. Некоторые библиотеки с такими путями работают плохо. Лучше выбрать путь латиницей.';
  SpaceLabel.Caption := Msg;
end;

procedure CompClick(Sender: TObject);
var
  I: Integer;
begin
  I := WizardForm.ComponentsList.ItemIndex;
  if I >= 0 then
    CompDescLabel.Caption := CompDescription(I);
end;

procedure InitializeWizard;
begin
  SpaceLabel := TNewStaticText.Create(WizardForm);
  SpaceLabel.Parent := WizardForm.SelectDirPage;
  SpaceLabel.Left := WizardForm.DirEdit.Left;
  SpaceLabel.Top := WizardForm.DirEdit.Top + WizardForm.DirEdit.Height + ScaleY(14);
  SpaceLabel.Width := WizardForm.SelectDirPage.Width - SpaceLabel.Left;
  SpaceLabel.AutoSize := False;
  SpaceLabel.WordWrap := True;
  SpaceLabel.Height := ScaleY(96);
  WizardForm.DirEdit.OnChange := @UpdateSpace;

  WizardForm.ComponentsList.Height := WizardForm.ComponentsList.Height - ScaleY(56);
  CompDescLabel := TNewStaticText.Create(WizardForm);
  CompDescLabel.Parent := WizardForm.SelectComponentsPage;
  CompDescLabel.Left := WizardForm.ComponentsList.Left;
  CompDescLabel.Top := WizardForm.ComponentsList.Top + WizardForm.ComponentsList.Height + ScaleY(6);
  CompDescLabel.Width := WizardForm.ComponentsList.Width;
  CompDescLabel.AutoSize := False;
  CompDescLabel.WordWrap := True;
  CompDescLabel.Height := ScaleY(50);
  CompDescLabel.Caption := 'Нажмите на строку, чтобы прочитать описание.';
  WizardForm.ComponentsList.OnClick := @CompClick;
end;

procedure CurPageChanged(CurPageID: Integer);
var
  I: Integer;
begin
  if CurPageID = wpSelectDir then
    UpdateSpace(nil);
  if (CurPageID = wpSelectComponents) and not NvidiaChecked then
  begin
    NvidiaChecked := True;
    if not HasNvidia then
      for I := 0 to CompCount - 1 do
        if CompIsNvidiaOnly(I) then
        begin
          WizardForm.ComponentsList.Checked[I] := False;
          WizardForm.ComponentsList.ItemEnabled[I] := False;
          WizardForm.ComponentsList.ItemCaption[I] := WizardForm.ComponentsList.ItemCaption[I] + ' — видеокарта NVIDIA не найдена';
        end;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if (CurPageID = wpSelectDir) and not IsAsciiPath(WizardDirValue) then
  begin
    Log('Warning: install path contains non-ASCII characters');
    if SuppressibleMsgBox('В пути установки есть русские буквы:' + #13#10 + WizardDirValue + #13#10#13#10 +
         'Некоторые библиотеки распознавания и озвучки с такими путями работают плохо. ' +
         'Лучше выбрать путь латиницей, например D:\ContentPipeline.' + #13#10#13#10 +
         'Продолжить с этим путём?', mbConfirmation, MB_YESNO, IDYES) = IDNO then
      Result := False;
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  StopServer(WizardDirValue);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    if not IsAsciiPath(WizardDirValue) then
      Log('Warning: install path contains non-ASCII characters');
    if not HasNvidia then
      Log('NVIDIA: nvidia-smi not found')
    else
      Log('NVIDIA: nvidia-smi found');
    DeleteFile(WizardDirValue + '\data\setup\opened.flag');
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDir: String;
begin
  if CurUninstallStep = usUninstall then
  begin
    AppDir := ExpandConstant('{app}');
    StopServer(AppDir);
    if DirExists(AppDir + '\data\venv') or DirExists(AppDir + '\data\models') or DirExists(AppDir + '\data\cache') then
      if SuppressibleMsgBox('Удалить и окружения Python со скачанными моделями (папка data, может занимать гигабайты)?' + #13#10#13#10 +
           'Если оставить — при повторной установке в эту же папку их не придётся скачивать заново.' + #13#10 +
           'Ваши записи и результаты тестов (папка bench) останутся в любом случае.',
           mbConfirmation, MB_YESNO, IDNO) = IDYES then
      begin
        DelTree(AppDir + '\data', True, True, True);
        DelTree(AppDir + '\bench\tools', True, True, True);
      end;
  end;
end;
