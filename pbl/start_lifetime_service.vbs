Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\Richitha\OneDrive\Desktop\pbl"
WshShell.Run "pythonw app.py", 0, False

