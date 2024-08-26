# Django Template in Docker

Table of Contents
=================
<!--ts-->
   * [Notes before starting](#notes-before-starting)
   * [Setting up project](#setting-up-project)
      * [Git](#git)
      * [Docker](#docker)
      * [Django](#django)
      * [Postgresql](#postgresql)
   * [Status and Logs](#status-and-logs)
   * [Using Custom Model Fields for S3 Storage Support](#using-custom-model-fields-for-s3-storage-support)
   * [How to Read Files of S3 with Libraries That Don't Support URL as pandas](#how-to-read-files-of-s3-with-libraries-that-dont-support-url-as-pandas)
   * [Management Commands](#management-commands)
      * [Folder Structure](#folder-structure)
      * [Execute Management Commands](#execute-management-commands)
    * [Tests](#tests)
<!--te-->

## Notes before starting

### Place core features of the application in core app and build APIs in the same app's viewsets and serializers files.

### If the application is large divide it into smaller apps (Add according to you need.)

### Pre-commit

We use pre-commit to enforce strict clean code convention.

**Setting up Pre-commit**

**1. Install on your system**

```bash
$ pip install pre-commit
```

**2. After installing on host machine you need to install hooks on your project**

```bash
$ pre-commit install-hooks
$ pre-commit run --all-files --all

```

**3. Updating pre-commit hooks**

```bash
$ pre-commit autoupdate
```

**4. Installing pre-commit hooks on so git uses them**

```bash
$ pre-commit install
```

**5. Steps to validate commit with pre-commit**

```bash
$ git status # review changes
$ git diff # review crucial changes
$ git add . # stage changes
$ pre-commit run --all-files --all ## This will modify files in your code if pre-commit test fails (EX: black fixing code indentions) and you need to stage code again
#=====Optional Steps if pre-commit fails START=====#
$ git status # review changes made by pre-commit
$ git add . # Re stage changes made by pre-commit
#=====Optional Steps if pre-commit fails END=====#
$ git commit
$ git push origin <BRANCH>
```

> _Reference:_ https://wiki.naxa.com.np/en/git/pre-commit

> **Note** Your project must pass pre-commit hook and it will be validated on github too via Actions.

### Setting up project
=================


You can build the repository according to your needs.

# Setup Process
=================


## Git
----------------

Clone this repository

```sh
$ git clone https://github.com/naxa-developers/naxa-backend-template --depth=1
```

If yours is a gis project, that needs playing with large gis data or uses libraries like geoserver, gcc.

```sh
$ cp dependencies/apt_requirements_gis.txt apt_requirements.txt
$ cp dependencies/requirements_gis.txt requirements.txt
```

If yours is a non-gis project. i.e. Does not have whole lot of gis data, or does not use libraries like geoserver, gcc etc.
Even if you need simple gis db fields like PointField from django.contrib.gis.db, you can build this version. This version also includes GDAL.

```sh
$ cp dependencies/apt_requirements_nongis.txt apt_requirements.txt
$ cp dependencies/requirements_nongis.txt requirements.txt
```

## Docker
----------------


Install [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/) in your system.
Create a local copy of `docker-compose.local.yml` on your machine.

```bash
$ cp docker/docker-compose.local.yml docker-compose.yml
```

Similarly create `entrypoint.sh` by copying the sample entrypoint script.

```bash
$ cp docker/docker-entrypoint.local.sh entrypoint.sh
```

Also make a copy of `env_sample` to `.env` and use it for setting environment variables for your project.

```bash
$ cp env_sample .env
$ nano .env			    # Edit .env and set environment variables for django project
```

If you are using geoserver, create env for the same

```bash
$ cp geoserver_env_sample.txt geoserver_env.txt
$ nano geoserver_env.txt	# Edit geoserver_env.txt and set environment variables for geoserver
```

Then start the containers from main compose file

```bash
$ docker compose up -d			#  Will create all necessary services
  Starting db ... done
  Starting web   ... done
  .....
  .....
  Starting worker  ... done
```

Go to the postgres database container if you are using one and create database according to credential provided in env file.
You project should be running now

To stop all running containers

```bash
$ docker compose stop			# Will stop all running services
    Stopping db ... done
    Stopping web   ... done
    Stopping worker  ... done
```

## Django
----------------


Once you have created all necessary services. You may want to perform some tasks on Django server like `migrations`, `collectstatic` & `createsuperuser`.
Use these commands respectively.

```bash
$ docker exec -it <CONTAINER_NAME> bash		# Get a shell on container from docker
$ docker compose exec web bash		# Get a shell on container from docker compose
root@<container>$ python3 manage.py collectstatic 	# Collecting static files
root@<container>$ python3 manage.py migrate		# Database migrate
root@<container>$ python3 manage.py createsuperuser	# Creating a superuser for login.
```

Now you should be able to access your django server on http://localhost:8000.

## Postgresql
----------------


In case if you want to use a local postgresql server instead on running a docker container.
First verify if `postgresql` is installed.

```bash
     $ psql -V
     psql (PostgreSQL) <PostgreSQL_Version>
```

Edit `postgresql.conf` file to allow listening to other IP address.

```bash
    $ sudo nano /etc/postgresql/<PostgreSQL_Version>/main/postgresql.conf
    listen_addresses = '*'          # what IP address(es) to listen on;
```

Now you will need to allow authentication to `postgresql` server by editing `pg_hba.conf`.

```bash
$ sudo nano /etc/postgresql/<PostgreSQL_Version>/main/pg_hba.conf
```

Find `host all all 127.0.0.1/32 md5` and change it to `host all all 0.0.0.0/0 md5` \
_It can be `sha` on new version of PostgreSQL_

Restart your postgresql server.

```bash
$ sudo systemctl restart postgresql.service
```

You will now need to set environment `POSTGRES_HOST` your private IP address like following.

```
    POSTGRES_HOST=192.168.1.22 				# my local postgresql server ip address
```

For creating a postgresql `role` , `database` & enabling `extensions`.

```bash
    $ sudo su - postgres
    $ psql
    psql> CREATE DATABASE myproject;
    psql> CREATE USER myprojectuser WITH PASSWORD 'password';
    psql> GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;
    psql> CREATE EXTENSION postgis;
```

## Status and Logs
=================


For viewing status of your docker container.

```bash
    $ docker-compose ps
    Name               Command               State           Ports
    ------------------------------------------------------------------------
    nginx    /docker-entrypoint.sh ngin ...   Up      0.0.0.0:80->80/tcp
    web      sh entrypoint.sh                 Up      0.0.0.0:8001->8001/tcp
    worker   celery -A project worker - ...   Up
```

For viewing logs of your docker services.

```bash
    $ docker-compose logs -f  --tail 1000 web
     Apply all migrations: account, admin, auth, authtoken, contenttypes, core, sessions, sites, socialaccount, user
    Running migrations:
      Applying contenttypes.0001_initial... OK
      Applying contenttypes.0002_remove_content_type_name... OK
      Applying auth.0001_initial... OK
```

## Using Custom Model Fields for S3 storage support
=================


```python
from django.db import models
from project.storage_backends import S3PrivateMediaStorage, S3PublicMediaStorage
from django.conf import settings
from django.utils.translation import gettext_lazy as _


# Create your models here.
class UserUploadModel(models.Model):
    upload_files = models.FileField(
        storage=S3PrivateMediaStorage() if settings.USE_S3 else None,
        null=True,
        blank=True
    )
    upload_public_files = models.FileField(
        storage=S3PublicMediaStorage() if settings.USE_S3 else None,
        null=True,
        blank=True
    )
    name = models.CharField(_("Name"), max_length=50)
```

## How to read files of S3 with libraries that don't support URL as pandas
=================


```python
import boto3
import pandas as pd
s3 = boto3.client('s3', region_name='your_region')
s3.download_file('your_bucket_name', 'path/to/your/file.csv', 'local_file_name.csv')
df = pd.read_csv('local_file_name.csv')
os.remove('local_file_name.csv')
```

> **Warning**
> Don't forget to delete the downloaded file once work is complete. It can cause unwanted storage usage on server.

```

```

Management Commands
=================

Folder Structure
----------------
In Django, management commands are typically created within a "management" directory inside an app.

Execute Management Commands
---------------------------
### Create default groups:

```sh
$ ./manage.py create_groups
```
Running this command will create default django groups.

### Assign ward numbers
```sh
$ ./manage.py assign_ward_numbers
```
Running this command will assign ward numbers to buildings based on their spatial relationship.

### Populate building choices
```sh
$ ./manage.py building_choices_populate
```
Running this command will populate the BuildingCategoryModel with type and its respective choices.

### Populate road choices
```sh
$ ./manage.py road_choices_populate
```
Running this command will populate the RoadCategoryModel with type and its respective choices.




Tests
=================
