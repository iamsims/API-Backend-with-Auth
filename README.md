# Installation  
```bash 
python3 -m venv fastapienv 
source fastapienv/bin/activate 
pip install -r requirements.txt 
prisma generate # generates from schema.prisma

```

# Configuration 
Setup a .env file with the variables from .env.example

# Run
```bash
uvicorn main:app --reload --port 8000
```

# Swagger UI
http://localhost:8000/docs
