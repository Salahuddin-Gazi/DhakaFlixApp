@echo off
echo Building DhakaFlix Streamer for Windows...
echo Ensure you have Python installed and 'pip install -r requirements.txt'

:: Install pyinstaller if missing
pip install pyinstaller

:: Run build
pyinstaller build.spec --clean --noconfirm

echo.
echo Build Complete! Check the 'dist' folder.
echo You must copy 'libmpv-2.dll' to the 'dist' folder for it to work!
pause
