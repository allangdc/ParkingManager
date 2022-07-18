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

Running tests

```bash
 docker-compose exec web python manage.py test
```

If you want to run the Coverage: (after this test check the file <i>htmlcov/index.html</i>)

```bash
 docker-compose exec web coverage run manage.py test

docker-compose exec web coverage html
```

## 2. Valid Routes

Register a car in the parking.

```
POST /api/v1/parking/
{ "plate": "ZZZ-0000" }
```

Register payment.

```
PUT /api/v1/parking/:id/pay/
```

Records the vehicle's exit

```
PUT /api/v1/parking/:id/out/
```

Search registration by the plate number.

```
GET /api/v1/parking/:plate
```
