@echo off
echo Uruchamianie srodowiska wirtualnego...
call .venv\Scripts\activate.bat

echo Instalacja lokalnej biblioteki llama-cpp...
pip install .\llama_cpp_python-0.3.31-py3-none-win_amd64.whl

echo Instalowanie reszty zaleznosci...
pip install -r requirements.txt

echo Odpalanie aplikacji Streamlit...
streamlit run app.py

pause