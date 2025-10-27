' Valorem Smart Outlook Review - Run Anytime (Force Mode)
' Double-click to run immediately, bypassing time window restrictions
' Useful for testing or manual execution outside scheduled times

Set objShell = CreateObject("WScript.Shell")

' Get script directory
strScriptPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Change to project directory
objShell.CurrentDirectory = strScriptPath

' Run Python script silently (hidden console window)
' Force mode: Bypasses time window checks, runs immediately
objShell.Run "python src\run_summary.py --config config\config.yaml --mode force", 0, True

' Alternative: Uncomment line below to see console output for debugging
' objShell.Run "python src\run_summary.py --config config\config.yaml --mode force", 1, True
