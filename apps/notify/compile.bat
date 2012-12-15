@echo off

set compiler="C:\Program Files\IronPython 2.7"
set root="C:\Documents and Settings\happz\Desktop\settlers-notify\"

rem Compile
%compiler%\ipy.exe %compiler%\Tools\Scripts\pyc.py /out:settlers-notify /target:winexe /main:settlers-notify.py /platform:x86

rem Copy resource files
del /s /q %root%\dist
mkdir %root%\dist
copy /Y %root%\res\*.* %root%\dist

rem Copy newly compiled binaries
move settlers-notify.exe %root%\dist
move settlers-notify.dll %root%\dist
