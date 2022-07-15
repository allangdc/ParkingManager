# ParkingManager

## 1. Setup project

Create a ".env" file at the root of the project with the project settings, similar to the example below:

```bash
SECRET_KEY = "django_secret_key"
DBUSER = "user"
DBPASSWORD = "password"
DBNAME = "dbname"
```

If you choose to use Docker.

```bash
docker-compose build --no-cache
docker-compose up
```