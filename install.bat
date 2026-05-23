@echo off
echo ========================================
echo  FindMyCar - Installazione dipendenze
echo ========================================
echo.

echo [1/3] Installazione Kivy e KivyMD...
pip install kivy[base] kivymd
if %errorlevel% neq 0 (
    echo ERRORE: Fallita installazione Kivy/KivyMD
    pause
    exit /b 1
)

echo [2/3] Installazione dipendenze aggiuntive...
pip install pillow plyer requests numpy scipy
if %errorlevel% neq 0 (
    echo ERRORE: Fallita installazione dipendenze
    pause
    exit /b 1
)

echo [3/3] Generazione logo...
python generate_logo.py

echo.
echo ========================================
echo  Installazione completata!
echo.
echo  Per avviare l'app: python main.py
echo  Per compilare per Android: buildozer android debug
echo ========================================
pause
