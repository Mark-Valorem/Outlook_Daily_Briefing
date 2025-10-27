' Valorem Smart Outlook Review - Run Anytime (Force Mode)
' Double-click to run immediately, bypassing time window restrictions
' Useful for testing or manual execution outside scheduled times

Set objShell = CreateObject("WScript.Shell")

' Get script directory
strScriptPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Change to project directory
objShell.CurrentDirectory = strScriptPath

' Run Python script with visible console window for debugging
' Force mode: Bypasses time window checks, runs immediately (including weekends)
' Window parameter: 1 = Visible (for debugging), 0 = Hidden (for production)
objShell.Run "python src\run_summary.py --config config\config.yaml --mode force", 1, True
