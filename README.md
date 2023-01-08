# Forum on django

**CSS is Without mobile adaptation**
<br>

**Install and run virtual environment**
> pipenv shell

**Install dependencies**
> pipenv install

**Redis** <br>
Install and run
> https://redis.io/docs/getting-started/

**Run celery** <br>
> celery -A project.celery worker -l info

Windows:
> celery -A project.celery worker -l info -P gevent

**Run celery beat**
> celery -A project.celery beat

****
### env Configuration
Create **.env** file in path with **manage.py**

**Add the following keys**
<details>
  <summary> → env Keys ←</summary>
  <p>SECRET_KEY</p>
  <p>DB_NAME</p>
  <p>DB_USER</p>
  <p>DB_PASSWORD</p>
  <p>DB_HOST</p>
  <p>DB_PORT</p>
  <p>EMAIL_HOST_USER</p>
  <p>EMAIL_HOST_PASSWORD</p>
  <p>REDIS_HOST</p>
  <p>REDIS_PORT</p>
</details>

****
## Tools used 
- Bootstrap
- Mysql
- Django
    - django-ckeditor
    - django-simple-captcha
    - django-debug-toolbar
- Django REST Framework
- Celery 
  - redis
- Jquery
