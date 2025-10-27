' Valorem Smart Outlook Review - Evening Briefing (17:00)
' Double-click to run or use in Task Scheduler for evening briefing

Set objShell = CreateObject("WScript.Shell")

' Get script directory
strScriptPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Change to project directory
objShell.CurrentDirectory = strScriptPath

' Run Python script silently (hidden console window)
' Mode: evening (generates 16:30 briefing)
objShell.Run "python src\run_summary.py --config config\config.yaml --mode evening", 0, True

' Alternative: Uncomment line below to see console output for debugging
' objShell.Run "python src\run_summary.py --config config\config.yaml --mode evening", 1, True
