@echo off

REM Cria a virtualenv
python -m venv venv

REM Ativa a virtualenv e instala as dependências em um único comando
venv\Scripts\activate && pip install -r requirements.txt && deactivate