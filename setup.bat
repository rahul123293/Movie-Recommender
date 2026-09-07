@echo off
REM ============================================================
REM  Movie Browser & Recommender - one-command setup (Windows)
REM  Runs fully OFFLINE: no API key and no network required.
REM ============================================================
setlocal

echo(
echo === Movie Browser ^& Recommender - setup ===
echo(

REM --- pick a Python launcher (py preferred, then python) ---
set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY (
    where python >nul 2>&1 && set "PY=python"
)
if not defined PY (
    echo [ERROR] Python was not found on PATH. Install Python 3.10 or 3.11 from python.org and re-run.
    goto :error
)
echo Using Python launcher: %PY%

REM --- create virtual environment ---
if not exist venv (
    echo Creating virtual environment...
    %PY% -m venv venv || goto :error
)

REM --- activate ---
call venv\Scripts\activate.bat || goto :error

REM --- install dependencies ---
echo Upgrading pip...
python -m pip install --upgrade pip || goto :error
echo Installing dependencies (this can take a few minutes)...
pip install -r requirements.txt || goto :error

REM --- create tables + seed demo data (idempotent) ---
echo Seeding demo data (tables, demo users, sample reviews)...
python seed_demo.py || goto :error

echo(
echo ============================================================
echo  Setup complete - starting the app.
echo(
echo  Open:  http://127.0.0.1:5000
echo(
echo  OFFLINE DEMO MODE is ON by default: the catalogue, search
echo  and recommendations all load from the bundled dataset
echo  (data\movies.json) - no API key or internet needed.
echo(
echo  Demo logins (sign in with the EMAIL address):
echo     admin@example.com / admin123
echo     demo@example.com  / demo12345
echo(
echo  To use LIVE TMDB data instead, get a free key at
echo  https://www.themoviedb.org/settings/api and set it before
echo  launching:   set MOVIE_API_KEY=your_key_here
echo(
echo  Press CTRL+C to stop the server.
echo ============================================================
echo(

python manage.py runserver -h 127.0.0.1 -p 5000
goto :eof

:error
echo(
echo [ERROR] Setup failed. Scroll up to see the first error message.
echo         Make sure Python 3.10 or 3.11 is installed and on PATH.
exit /b 1
