$ws = New-Object -ComObject WScript.Shell
$startup = $ws.SpecialFolders("Startup")
$shortcutPath = Join-Path $startup "JARVIS.lnk"
$shortcut = $ws.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "C:\Users\balup\.codex\BaluAI\jarvis_pc\jarvis.bat"
$shortcut.WorkingDirectory = "C:\Users\balup\.codex\BaluAI\jarvis_pc"
$shortcut.WindowStyle = 7  # Minimized
$shortcut.Description = "JARVIS AI Auto-Start"
$shortcut.Save()
Write-Host "JARVIS added to Windows Startup folder!"
Write-Host "Location: $shortcutPath"
Write-Host ""
Write-Host "Now every time you turn on your PC, JARVIS will start automatically."
Write-Host "Just say 'Hey Jarvis' anytime!"
