# Снимки страниц мастера установки (GitHub Actions). Только для просмотра глазами, на результат сборки не влияет.
#   pwsh installer/wizard_shots.ps1 -Setup installer\build\out\ContentPipeline-Setup-0.1.0.exe
param([Parameter(Mandatory = $true)] [string]$Setup)
$ErrorActionPreference = "Continue"
$tmp = if ($env:RUNNER_TEMP) { $env:RUNNER_TEMP } else { $env:TEMP }
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public static class Win { [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); }
"@
function Shot($name) {
  $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  $bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
  $gr = [System.Drawing.Graphics]::FromImage($bmp)
  $gr.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size)
  $dir = Join-Path $tmp "shots"; New-Item -ItemType Directory -Force $dir | Out-Null
  $bmp.Save((Join-Path $dir "$name.png"), [System.Drawing.Imaging.ImageFormat]::Png); $gr.Dispose(); $bmp.Dispose()
}
$p = Start-Process -FilePath $Setup -ArgumentList @("/DIR=`"C:\Тест мастер`"") -PassThru
Start-Sleep -Seconds 6
$wiz = Get-Process | Where-Object { $_.ProcessName -like "ContentPipeline-Setup*" -and $_.MainWindowTitle } | Select-Object -First 1
if ($wiz) { [Win]::SetForegroundWindow($wiz.MainWindowHandle) | Out-Null; Write-Host "окно мастера: $($wiz.ProcessName) $($wiz.MainWindowTitle)" }
Shot "wizard-1-welcome"
foreach ($n in 2..3) {
  [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
  Start-Sleep -Seconds 2
  Shot ("wizard-{0}" -f $n)
}
# на странице компонентов: строка 2 — описание под списком
[System.Windows.Forms.SendKeys]::SendWait("{DOWN}")
Start-Sleep -Seconds 1
Shot "wizard-3-components-click"
Get-Process | Where-Object { $_.ProcessName -like "ContentPipeline-Setup*" } | Stop-Process -Force -ErrorAction SilentlyContinue
if (-not $p.HasExited) { $p.Kill() }
Write-Host "снимки: $tmp\shots"
