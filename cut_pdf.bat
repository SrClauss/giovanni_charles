@echo off

rem Ativar a venv
call venv\Scripts\activate

rem Executar o script ui.py
python cut_pdf.py

rem Desativar a venv
deactivate