' Run Outlook Daily Briefing (DRY RUN mode)
' This script uses the virtual environment Python to run the briefing
' Double-click to test the briefing without sending emails

Dim objShell, scriptDir
Set objShell = CreateObject("WScript.Shell")

' Get the directory where this VBS script is located (project root)
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Change to project directory
objShell.CurrentDirectory = scriptDir

' Run the Python script with virtual environment in DRY RUN mode
' Parameters: 0 = hide console window, True = wait for completion
objShell.Run """" & scriptDir & "\.venv\Scripts\python.exe"" """ & scriptDir & "\src\run_summary.py"" --config """ & scriptDir & "\config\config.yaml"" --dry-run --mode morning", 0, True

Set objShell = Nothing

' Show completion message
MsgBox "Briefing dry run completed! Check docs\samples\example-summary.html for the report.", vbInformation, "Outlook Briefing"
