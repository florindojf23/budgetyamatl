@echo off
echo Starting Django server...

REM Activate Conda environment
call C:\Users\%USERNAME%\anaconda3\Scripts\activate.bat djangoenv

REM Go to project folder
cd /d D:\Django_Projects\archival

REM Run Django
python manage.py runserver

pause
