# Смоук-тест установщика на Windows (GitHub Actions, windows-latest). Не входит в установку.
#   pwsh installer/smoke.ps1 -Setup installer\build\out\ContentPipeline-Setup-0.1.0.exe -Dir C:\cp-test
# Проверяет: тихую установку с компонентами без видеокарты, встроенные программы, ярлыки, tkinter,
# компонентный установщик (--headless), сервер (GET /, API, повторный запуск, heartbeat, выход, stop.request,
# запуск через pythonw как у ярлыка), check_env.py без системных программ в PATH, тихое удаление.
param(
  [Parameter(Mandatory = $true)] [string]$Setup,
  [Parameter(Mandatory = $true)] [string]$Dir,
  [string]$Components = "base,text,stress,edgetts",
  [switch]$ExpectNonAscii,
  [int]$Port = 8790
)
$ErrorActionPreference = "Continue"   # ошибки считаем сами (Ok), stderr программ не должен прерывать скрипт
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$script:failed = @()

function Ok($cond, $msg) {
  if ($cond) { Write-Host "OK   $msg" } else { Write-Host "::error::FAIL $msg"; $script:failed += $msg }
}
function Group($name) { Write-Host "::group::$name" }
function EndGroup { Write-Host "::endgroup::" }

$tmp = if ($env:RUNNER_TEMP) { $env:RUNNER_TEMP } else { $env:TEMP }
$log = Join-Path $tmp ("setup-" + [guid]::NewGuid().ToString("N") + ".log")
$py = Join-Path $Dir "tools\python\python.exe"
$pyw = Join-Path $Dir "tools\python\pythonw.exe"
$extra = ($Components -split "," | Where-Object { $_ -ne "base" }) -join ","
$tag = if ($ExpectNonAscii) { "cyr" } else { "lat" }

function Shot($name) {
  # снимок экрана для artifact «screenshots» (проверка окон глазами)
  try {
    Add-Type -AssemblyName System.Windows.Forms, System.Drawing
    $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
    $gr = [System.Drawing.Graphics]::FromImage($bmp)
    $gr.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size)
    $dir = Join-Path $tmp "shots"
    New-Item -ItemType Directory -Force $dir | Out-Null
    $bmp.Save((Join-Path $dir "$name.png"), [System.Drawing.Imaging.ImageFormat]::Png)
    $gr.Dispose(); $bmp.Dispose()
  } catch { Write-Host "скриншот $name не снят: $_" }
}

# ---------- 1. тихая установка ----------
Group "Установка в $Dir"
$t0 = Get-Date
$p = Start-Process -FilePath $Setup -ArgumentList @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/DIR=`"$Dir`"", "/COMPONENTS=$Components", "/LOG=`"$log`"") -Wait -PassThru
Write-Host ("Установка заняла {0:N0} с, код {1}" -f ((Get-Date) - $t0).TotalSeconds, $p.ExitCode)
Ok ($p.ExitCode -eq 0) "установщик завершился с кодом 0"
if (Test-Path $log) { Get-Content $log -Encoding UTF8 | Select-Object -Last 60 | ForEach-Object { Write-Host "  | $_" } }
EndGroup

if ($ExpectNonAscii) {
  Ok ([bool](Select-String -Path $log -Pattern "non-ASCII" -SimpleMatch -Quiet)) "в логе есть предупреждение о русских буквах в пути"
}

Group "Файлы и ярлыки"
foreach ($f in @("tools\python\python.exe", "tools\python\pythonw.exe", "tools\ffmpeg\bin\ffmpeg.exe", "tools\ffmpeg\bin\ffprobe.exe",
                 "tools\node\node.exe", "tools\node\npm.cmd", "tools\node\npx.cmd", "tools\mingit\cmd\git.exe",
                 "tools\auto-editor\auto-editor.exe", "app\server.py", "app\setup\components.py", "app\setup\icon.ico",
                 "installed.json", "licenses\README.txt", "licenses\ffmpeg", "licenses\python", "unins000.exe", "skills\kp-bench\scripts\check_env.py")) {
  Ok (Test-Path (Join-Path $Dir $f)) "есть $f"
}
Ok (-not (Test-Path (Join-Path $Dir "tools\ffmpeg\bin\ffplay.exe"))) "ffplay не включён"
Ok (-not (Test-Path (Join-Path $Dir ".git"))) "установленная копия — не git-клон"
$desk = Join-Path ([Environment]::GetFolderPath("Desktop")) "Конвейер контента.lnk"
$menu = Join-Path ([Environment]::GetFolderPath("Programs")) "Конвейер контента\Конвейер контента.lnk"
Ok (Test-Path $desk) "ярлык на рабочем столе"
Ok (Test-Path $menu) "ярлык в меню «Пуск»"
if (Test-Path $desk) {
  # .lnk хранит путь цели в LinkInfo/IDList, кодировка зависит от пути — проверяем запуском (ниже) и печатаем строки
  $bytes = [System.IO.File]::ReadAllBytes($desk)
  $u = [System.Text.Encoding]::Unicode.GetString($bytes) -replace "[^\u0020-\u04FF]", " " -replace "\s{2,}", " | "
  Write-Host "  строки ярлыка: $u"
  Ok ([System.Text.Encoding]::Latin1.GetString($bytes).Contains("pythonw.exe") -or $u.Contains("pythonw.exe")) "ярлык указывает на pythonw.exe"
}
EndGroup

# ---------- 2. встроенные программы ----------
Group "Встроенные программы"
$checks = @(
  @("tools\python\python.exe", @("--version")),
  @("tools\ffmpeg\bin\ffmpeg.exe", @("-hide_banner", "-version")),
  @("tools\ffmpeg\bin\ffprobe.exe", @("-hide_banner", "-version")),
  @("tools\node\node.exe", @("--version")),
  @("tools\mingit\cmd\git.exe", @("--version")),
  @("tools\auto-editor\auto-editor.exe", @("--version"))
)
foreach ($c in $checks) {
  $exe = Join-Path $Dir $c[0]
  $all = & $exe @($c[1]) 2>&1
  $code = $LASTEXITCODE
  $out = ($all | Select-Object -First 1)
  Ok ($code -eq 0) "$($c[0]) $($c[1] -join ' '): $out"
}
$out = & $py -c "import tkinter, venv, ensurepip, ssl, sqlite3; print('tk', tkinter.Tcl().eval('info patchlevel'), ssl.OPENSSL_VERSION)" 2>&1
Ok ($LASTEXITCODE -eq 0) "tkinter, venv, ssl в встроенном Python: $out"
EndGroup

# ---------- 3. компоненты ----------
Group "Компоненты (повторный запуск: ожидается «уже было»)"
$clog = Join-Path $Dir "data\logs\components.log"
if (Test-Path $clog) {
  $cl = Get-Content $clog -Encoding UTF8
  $cl | Where-Object { $_ -match "^\[|^  \S|Скачиваю|%$" } | Select-Object -First 80 | ForEach-Object { Write-Host "  | $_" }
  Write-Host ("  строк прогресса скачивания (pip --progress-bar raw): {0}" -f @($cl | Where-Object { $_ -match "^\s+\d+%$" }).Count)
}
if ($extra) {
  & $py (Join-Path $Dir "app\setup\components.py") --headless --components $extra
  Ok ($LASTEXITCODE -eq 0) "components.py --headless --components $extra"
  $last = Get-Content (Join-Path $Dir "data\setup\last.json") -Encoding UTF8 -Raw | ConvertFrom-Json
  foreach ($r in $last.results) { Ok ($r.status -in @("ok", "already")) "компонент $($r.id): $($r.status) $($r.error)" }
  Ok (Test-Path (Join-Path $Dir "data\venv\asr\Scripts\python.exe")) "окружение data\venv\asr"
}
Group "Окно компонентов: pythonw + tkinter, без установки (--dry-run)"
$g = Start-Process -FilePath $pyw -ArgumentList @("`"$(Join-Path $Dir 'app\setup\components.py')`"", "--dry-run", "--close-when-done", "6", "--components", "all") -WorkingDirectory $Dir -PassThru
Start-Sleep -Seconds 4
Shot "components-$tag-running"
Start-Sleep -Seconds 10
Shot "components-$tag-done"
$exited = $g.WaitForExit(90000)
if (-not $exited) { $g.Kill() }
Ok ($exited -and $g.ExitCode -eq 0) "окно компонентов открылось, прошло план и закрылось (код $($g.ExitCode))"
Ok (-not (Test-Path (Join-Path $Dir "data\setup\pending.json"))) "окно — tkinter (запасной путь через браузер не понадобился)"
EndGroup

& $py (Join-Path $Dir "app\setup\components.py") --list
& $py (Join-Path $Dir "app\setup\components.py") --headless --dry-run --components all
Ok ($LASTEXITCODE -eq 0) "components.py --dry-run --components all"
EndGroup

# ---------- 4. check_env.py только со встроенными программами ----------
Group "check_env.py без системных программ в PATH"
$savedPath = $env:PATH
$env:PATH = "$env:SystemRoot\System32;$env:SystemRoot"
Push-Location $Dir   # корень для bench\env ищется от текущей папки
$out = & $py (Join-Path $Dir "skills\kp-bench\scripts\check_env.py") --tester ci-bundled 2>&1
Pop-Location
$env:PATH = $savedPath
$out | ForEach-Object { Write-Host "  | $_" }
$text = $out -join "`n"
foreach ($k in @("node", "ffmpeg", "git")) { Ok ($text -match "OK\s+$k") "check_env видит $k" }
Ok ($text -match "OK\s+auto-editor") "check_env видит auto-editor"
$envJson = Get-Content (Join-Path $Dir "bench\env\ci-bundled.json") -Encoding UTF8 -Raw | ConvertFrom-Json
Ok ($envJson.installed -eq $true) "bench\env\ci-bundled.json: installed = true"
EndGroup

# ---------- 5. сервер ----------
function Wait-Lock($timeoutSec) {
  $lockPath = Join-Path $Dir "data\server.lock"
  for ($i = 0; $i -lt $timeoutSec * 4; $i++) {
    if (Test-Path $lockPath) { try { return (Get-Content $lockPath -Raw | ConvertFrom-Json) } catch { } }
    Start-Sleep -Milliseconds 250
  }
  return $null
}
function Wait-NoLock($timeoutSec) {
  $lockPath = Join-Path $Dir "data\server.lock"
  for ($i = 0; $i -lt $timeoutSec * 4; $i++) { if (-not (Test-Path $lockPath)) { return $true }; Start-Sleep -Milliseconds 250 }
  return $false
}

Group "Сервер: python.exe app\server.py --no-browser"
$srvOut = Join-Path $tmp "server-out.txt"
$srv = Start-Process -FilePath $py -ArgumentList @("`"$(Join-Path $Dir 'app\server.py')`"", "--no-browser", "--port", "$Port") -WorkingDirectory $Dir -PassThru -RedirectStandardOutput $srvOut -RedirectStandardError "$srvOut.err"
$lock = Wait-Lock 30
Ok ($null -ne $lock) "data\server.lock появился"
if ($lock) {
  $base = "http://127.0.0.1:$($lock.port)"
  $hdr = @{ "X-Bench-Token" = $lock.token }
  $r = Invoke-WebRequest "$base/" -UseBasicParsing
  Ok ($r.StatusCode -eq 200 -and $r.Content -match "Конвейер контента") "GET / → 200"
  $meta = Invoke-RestMethod "$base/api/meta"
  Ok ($meta.installed -eq $true) "api/meta: installed = true"
  Ok ($meta.git_repo -eq $false) "api/meta: git_repo = false (кнопка git скрыта)"
  Ok (@($meta.sections.id) -contains "setup") "api/meta: есть раздел «Установка»"
  $tools = Invoke-RestMethod "$base/api/tools"
  foreach ($t in $tools.tools) { Ok ($t.found -and $t.bundled) "api/tools: $($t.id) встроенный — $($t.path) $($t.version)" }
  $comp = Invoke-RestMethod "$base/api/setup/components"
  foreach ($id in ($extra -split "," | Where-Object { $_ })) {
    Ok ((@($comp.components) | Where-Object { $_.id -eq $id }).installed) "api/setup/components: $id установлен"
  }
  $hb = Invoke-RestMethod "$base/api/heartbeat" -Method Post -Headers $hdr -Body "{}" -ContentType "application/json"
  Ok ($hb.ok) "POST /api/heartbeat"
  # задачи через API: проверка среды и humanizer-ru из data\venv
  foreach ($job in @(@{ action = "bench.check_env"; params = @{ tester = "ci" } },
                     @{ action = "bench.textcheck"; params = @{ tester = "ci"; variant = "humanizer-ru" } })) {
    if ($job.action -eq "bench.textcheck" -and -not (($extra -split ",") -contains "text")) { continue }
    $res = Invoke-RestMethod "$base/api/run" -Method Post -Headers $hdr -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes(($job | ConvertTo-Json -Compress)))
    $st = $null
    for ($i = 0; $i -lt 120; $i++) { $st = Invoke-RestMethod "$base/api/job/$($res.job)"; if ($st.state -notin @("running", "queued")) { break }; Start-Sleep 1 }
    $st.tail | Select-Object -Last 15 | ForEach-Object { Write-Host "  | $_" }
    Ok ($st.state -eq "done") "задача $($job.action): $($st.state) $($st.error)"
  }
  # повторный запуск: второй сервер не поднимается
  $second = Start-Process -FilePath $py -ArgumentList @("`"$(Join-Path $Dir 'app\server.py')`"", "--no-browser") -WorkingDirectory $Dir -PassThru -RedirectStandardOutput "$srvOut.2" -RedirectStandardError "$srvOut.2.err"
  $exited = $second.WaitForExit(20000)
  if (-not $exited) { $second.Kill() }
  Ok ($exited -and $second.ExitCode -eq 0) "повторный запуск завершился сразу (код $($second.ExitCode))"
  Ok ((Get-Content "$srvOut.2" -Raw -Encoding UTF8) -match "уже запущен") "повторный запуск сообщил «уже запущен»"
  $sd = Invoke-RestMethod "$base/api/shutdown" -Method Post -Headers $hdr -Body "{}" -ContentType "application/json"
  Ok ($srv.WaitForExit(20000)) "POST /api/shutdown остановил сервер"
  Ok (Wait-NoLock 10) "lock-файл удалён после выхода"
}
Get-Content $srvOut, "$srvOut.err" -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "  | $_" }
EndGroup

Group "Сервер как у ярлыка: pythonw.exe, остановка через data\stop.request"
$w = Start-Process -FilePath $pyw -ArgumentList @("`"$(Join-Path $Dir 'app\server.py')`"", "--no-browser", "--port", "$($Port + 5)") -WorkingDirectory $Dir -PassThru
$lock = Wait-Lock 30
Ok ($null -ne $lock) "pythonw: сервер запустился"
if ($lock) {
  $r = Invoke-WebRequest "http://127.0.0.1:$($lock.port)/" -UseBasicParsing
  Ok ($r.StatusCode -eq 200) "pythonw: GET / → 200"
  Set-Content -Path (Join-Path $Dir "data\stop.request") -Value "stop"
  Ok ($w.WaitForExit(20000)) "pythonw: остановился по data\stop.request"
}
$sl = Join-Path $Dir "data\logs\server.log"
Ok (Test-Path $sl) "pythonw: вывод сервера в data\logs\server.log"
if (Test-Path $sl) { Get-Content $sl -Encoding UTF8 | Select-Object -Last 10 | ForEach-Object { Write-Host "  | $_" } }
EndGroup

Group "Запуск ярлыком с рабочего стола (как у пользователя)"
if (Test-Path $desk) {
  Start-Process -FilePath $desk
  $lock = Wait-Lock 40
  Ok ($null -ne $lock) "ярлык запустил сервер (lock-файл появился)"
  if ($lock) {
    $r = Invoke-WebRequest "http://127.0.0.1:$($lock.port)/" -UseBasicParsing
    Ok ($r.StatusCode -eq 200) "ярлык: интерфейс отвечает, GET / → 200"
    $sp = Get-Process -Id $lock.pid -ErrorAction SilentlyContinue
    Ok ($sp -and $sp.ProcessName -eq "pythonw") "ярлык: сервер работает под pythonw.exe (без окна консоли)"
    Start-Sleep -Seconds 3
    Shot "shortcut-$tag-browser"
    Set-Content -Path (Join-Path $Dir "data\stop.request") -Value "stop"
    Ok (Wait-NoLock 20) "ярлык: сервер остановлен через data\stop.request"
  }
  Get-Process msedge, chrome -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}
EndGroup

# ---------- 6. удаление ----------
Group "Тихое удаление"
$u = Start-Process -FilePath (Join-Path $Dir "unins000.exe") -ArgumentList @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART") -Wait -PassThru
for ($i = 0; $i -lt 120 -and (Test-Path (Join-Path $Dir "app\server.py")); $i++) { Start-Sleep -Milliseconds 500 }
Ok ($u.ExitCode -eq 0) "деинсталлятор: код 0"
Ok (-not (Test-Path (Join-Path $Dir "app\server.py"))) "программа удалена"
Ok (-not (Test-Path (Join-Path $Dir "tools"))) "папка tools удалена"
Ok (-not (Test-Path $desk)) "ярлык с рабочего стола удалён"
if (Test-Path $Dir) { Get-ChildItem $Dir -Force | ForEach-Object { Write-Host "  осталось: $($_.Name)" } }
EndGroup

if ($script:failed.Count) {
  Write-Host "::error::Смоук: $($script:failed.Count) проверок не прошло"
  $script:failed | ForEach-Object { Write-Host "  - $_" }
  exit 1
}
Write-Host "Смоук: все проверки прошли ($Dir)"
