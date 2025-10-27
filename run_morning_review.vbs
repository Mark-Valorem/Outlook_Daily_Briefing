' Valorem Smart Outlook Review - Morning Briefing (09:00)
' Double-click to run or use in Task Scheduler for morning briefing

Set objShell = CreateObject("WScript.Shell")

' Get script directory
strScriptPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Change to project directory
objShell.CurrentDirectory = strScriptPath

' Run Python script silently (hidden console window)
' Mode: morning (generates 08:00 briefing)
objShell.Run "python src\run_summary.py --config config\config.yaml --mode morning", 0, True

' Alternative: Uncomment line below to see console output for debugging
' objShell.Run "python src\run_summary.py --config config\config.yaml --mode morning", 1, True
