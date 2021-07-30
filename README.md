Fyyur
-----

## Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

## Overview

This project provides a fully functioning site that is capable of doing the following things using a PostgreSQL database:

* creating new venues, artists, and creating new shows.
* avoid duplicated or nonsensical creation.
* searching for venues and artists.
* learning more about a specific artist or venue.

## Tech Stack (Dependencies)

### 1. Backend Dependencies
Our tech stack will include the following:
 * **virtualenv** as a tool to create isolated Python environments
 * **SQLAlchemy ORM** to be our ORM library of choice
 * **PostgreSQL** as our database of choice
 * **Python3** and **Flask** as our server language and server framework
 * **Flask-Migrate** for creating and running schema migrations


### 2. Frontend Dependencies
You must have the **HTML**, **CSS**, and **Javascript** with [Bootstrap 3](https://getbootstrap.com/docs/3.4/customize/) for our website's frontend. Bootstrap can only be installed by Node Package Manager (NPM). Therefore, if not already, download and install the [Node.js](https://nodejs.org/en/download/). Windows users must run the executable as an Administrator, and restart the computer after installation. After successfully installing the Node, verify the installation as shown below.
```
node -v
npm -v
```
Install [Bootstrap 3](https://getbootstrap.com/docs/3.3/getting-started/) for the website's frontend:
```
npm init -y
npm install bootstrap@3
```


## Main Files: Project Structure

  ```sh
  ├── README.md
  ├── error.log
  ├── run.py  *** "python app.py" to run the project 
                  after installing dependencies
  ├── config.py *** Database URLs, CSRF generation, etc
  ├── requirements.txt *** The dependencies we need to install with 
                        "pip3 install -r requirements.txt"
  ├── fyyur
        ├── __init.py__
        ├── models.py  *** sqlalchemy models
        ├── forms.py  *** forms used to create artists, shows and venues
        ├── enums.py  *** enum class of genre and state choices
        ├── migrations  *** data schema migration
        ├── routes  *** routes and handlers
        |   ├── __init__.py
        │   ├── general.py
        │   ├── venue.py
        │   ├── artist.py
        │   └── show.py
        ├── static  *** frontend built static assets
        │   ├── css 
        │   ├── font
        │   ├── ico
        │   ├── img
        │   └── js
        └── templates  *** templates render views based on data
            ├── errors
            ├── forms
            ├── layouts
            └── pages
  ```

## Run

1. **Initialize and activate a virtualenv using:**
```
$ pip install virtualenv
$ python -m virtualenv env
$ source env/bin/activate
```
>**Note** - In Windows, the `env` does not have a `bin` directory. Therefore, you'd use the analogous command shown below:
```
$ source env/Scripts/activate
```
> If you'd want to close virtual env, use the command shown below:
```
(env) $ deactivate
```

2. **Download and install the dependencies:**

```
(env) $ pip install SQLAlchemy
(env) $ pip install postgres
(env) $ pip install Flask
(env) $ pip install Flask-Migrate
(env) $ pip install -r requirements.txt
```
> **Note** - If we do not mention the specific version of a package, then the default latest stable package will be installed. 


3. **Run the development server:**
```
(env) $ python3 run.py
```

4. **Verify on the Browser**

Navigate to project homepage [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

