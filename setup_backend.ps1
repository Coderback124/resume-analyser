mkdir backend
cd backend

mkdir app
mkdir app\routes

ni app\main.py
ni app\logger_config.py
ni app\config.py
ni app\__init__.py

ni app\routes\upload.py
ni app\routes\__init__.py

ni .env
ni .gitignore

python -m venv venv
.\venv\Scripts\activate

pip install fastapi uvicorn python-multipart python-dotenv

pip freeze > requirements.txt