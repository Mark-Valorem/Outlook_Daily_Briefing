' Valorem Smart Outlook Review - Silent Launcher
' Double-click to run or use in Task Scheduler
' Auto mode: Determines morning/evening based on current time

Set objShell = CreateObject("WScript.Shell")

' Get script directory
strScriptPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Change to project directory
objShell.CurrentDirectory = strScriptPath

' Run Python script silently (hidden console window)
' Parameter 0 = Hidden, True = Wait for completion
objShell.Run "python src\run_summary.py --config config\config.yaml --mode auto", 0, True

' Alternative: Uncomment line below to see console output for debugging
' objShell.Run "python src\run_summary.py --config config\config.yaml --mode auto", 1, True
