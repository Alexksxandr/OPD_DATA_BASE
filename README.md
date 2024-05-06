pip install -r requirements.txt

cd OPD_DATA_BASE

python manage.py makemigrations

python manage.py migrate

python manage.py runserver
