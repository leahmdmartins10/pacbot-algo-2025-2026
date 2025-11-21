@echo off
set iterations=10
set server_path=C:\dev\6ix-pac\server\pacbot_server.exe
set script_path=pacbotClient.py
set venv_activate=C:\dev\.venv\Scripts\activate.bat

for /l %%i in (1,1,%iterations%) do (
    echo Running iteration %%i
    call :RunIteration
)

echo All iterations completed
goto :eof

:RunIteration
call %venv_activate%
start %server_path%
call python %script_path%
call deactivate
goto :eof
