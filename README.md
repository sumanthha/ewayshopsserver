## eWayShops Backend
Django rest framework

### Installation 
First ensure you have python globally installed in your computer. If not, you can get python [here](https://python.org).

### Install IDE
Install VisualStudio Code in your computer. Use the [this](https://code.visualstudio.com/download) link to install VisualStudio Code.

### Setup

After doing this, confirm that you have installed virtualenv globally as well. If not, run this:

    $ pip install virtualenv
Then, Git clone this repo to your PC

    $ git clone https://dhinesh1310@bitbucket.org/W2SAdmin/ewayshops_api.git
    $ cd ewayshop
    
Create a virtual environment

    $ virtualenv .venv && source .venv/bin/activate
Install dependancies

    $ pip install -r requirements.txt
Make migrations & migrate

    $ python manage.py makemigrations && python manage.py migrate
Create Super user
    
    $ python manage.py createsuperuser

### Launching the app
    $ python manage.py runserver

### Run Tests
    $ python manage.py test
