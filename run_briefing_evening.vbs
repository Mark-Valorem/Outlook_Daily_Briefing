' Run Outlook Daily Briefing - EVENING MODE
' This script sends the actual evening briefing email via Outlook
' Use this for Windows Task Scheduler or manual execution

Dim objShell, scriptDir
Set objShell = CreateObject("WScript.Shell")

' Get the directory where this VBS script is located (project root)
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Change to project directory
objShell.CurrentDirectory = scriptDir

' Run the Python script with virtual environment in EVENING mode
' Parameters: 0 = hide console window, False = don't wait (run async)
objShell.Run """" & scriptDir & "\.venv\Scripts\python.exe"" """ & scriptDir & "\src\run_summary.py"" --config """ & scriptDir & "\config\config.yaml"" --mode evening", 0, False

Set objShell = Nothing
