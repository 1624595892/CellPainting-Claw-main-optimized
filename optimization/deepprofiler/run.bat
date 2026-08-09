@echo off
chcp 65001 >nul
setlocal

REM ================================================================
REM DeepProfiler optimized pipeline — matches before-optimization output
REM ================================================================
set "PYTHON=D:\MINICONDA\envs\cellpainting-claw\python.exe"
set "PYTHONPATH=D:\CellPainting-Claw-main2\DeepProfiler-master\DeepProfiler-master"
set "SCRIPT=D:\CellPainting-Claw-main2\CellPainting-Claw-main\optimization\deepprofiler\pipeline.py"
set "DATA_DIR=D:\CellPainting-Claw-main2\CellPainting-Claw-main\demo\workspace\reference_data\BR00117035"
set "OUTPUT_DIR=D:\CellPainting-Claw-main2\CellPainting-Claw-main\demo\workspace\outputs\deepprofiler_pipeline"

echo.
echo ================================================================
echo  DeepProfiler Optimized Pipeline
echo ================================================================
echo  Start: %time%
echo  Data:  BR00117035 (A01, real data)
echo ================================================================
echo.

REM Clean old pipeline output
if exist "%OUTPUT_DIR%" (
    echo [Clean] Removing old pipeline output...
    rmdir /s /q "%OUTPUT_DIR%"
)

REM Run
"%PYTHON%" "%SCRIPT%" --data-dir "%DATA_DIR%"

echo.
echo ================================================================
echo  End:   %time%
echo  Output: %OUTPUT_DIR%
echo ================================================================

REM Show output files
if exist "%OUTPUT_DIR%" (
    echo.
    echo Output files:
    dir /s /b "%OUTPUT_DIR%\*.npz" 2>nul
    dir /s /b "%OUTPUT_DIR%\*.parquet" 2>nul
    dir /s /b "%OUTPUT_DIR%\*.csv.gz" 2>nul
)
pause
