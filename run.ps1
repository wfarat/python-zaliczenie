& .\.venv\Scripts\Activate.ps1

pip install .\llama_cpp_python-0.3.31-py3-none-win_amd64.whl

pip install -r requirements.txt

streamlit run app.py