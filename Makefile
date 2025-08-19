makemigrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

create_user:
	python manage.py createsuperuser

run:
	python manage.py runserver 0.0.0.0:8000