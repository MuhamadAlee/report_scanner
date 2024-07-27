# report_scanner

make a readme.md having following content
1) create database in postgrase
    CREATE DATABASE Translaited;
2) setup alembic for migrations
    i) setup 'sqlalchemy.url' inside alembic.ini
    ii) configure alembic/env.py
    
    ```      
    from config.database import engine, Base
    from models.model import Model
    target_metadata = Base.metadata
    ```
  
3) Setup alembic
    ```
    alembic init alembic
    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head
    ```

3) setup virtual envirnment
    ```
    virtualenv env/bin/python3 env
    source env/bin/activate
    python api.py
    ```
