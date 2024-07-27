# report_scanner

1) Place .env file right configurarions in it

2) create database in postgrase
    ```
    CREATE DATABASE Translaited;
    ```
3) setup alembic for migrations
    - setup 'sqlalchemy.url' inside alembic.ini
    - configure alembic/env.py
    
    ```      
    from config.database import engine, Base
    from models.model import Model
    target_metadata = Base.metadata
    ```
  
4) Setup alembic
    ```
    alembic init alembic
    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head
    ```

5) setup virtual envirnment
    ```
    virtualenv env/bin/python3 env
    source env/bin/activate
    python api.py
    ```
