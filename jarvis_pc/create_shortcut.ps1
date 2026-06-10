$ws = New-Object -ComObject WScript.Shell
$desktop = $ws.SpecialFolders("Desktop")
$shortcutPath = Join-Path $desktop "JARVIS.lnk"
$shortcut = $ws.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "C:\Users\balup\.codex\BaluAI\jarvis_pc\jarvis.bat"
$shortcut.WorkingDirectory = "C:\Users\balup\.codex\BaluAI\jarvis_pc"
$shortcut.Description = "Launch JARVIS AI Assistant"
$shortcut.Save()
Write-Host "JARVIS shortcut created on Desktop!"
