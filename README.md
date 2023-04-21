# Installation  
```bash 
python3 -m venv fastapienv 
source fastapienv/bin/activate 
pip install -r requirements.txt 
prisma generate # generates from schema.prisma
uvicorn main:app --reload
```




# Data Migration

Create
```bash
prisma migrate dev --name `name` --create-only #requires DB_URL be set in the environment, performed during development 
```

Sync is performed by the code, during startup, using db config from secret file. 
