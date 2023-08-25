# Snippet Sharing API Backend 

Welcome to the Snippet Sharing project. This is a CRUD API backend with authentication implemented using FastAPI and Prisma ORM. If you're an authenticated user, you can share code snippets, edit them, and manage them. For developers and other services, there's a generated API key associated with each user to provide easy integration with other microservices.

## Features:

- User registration and authentication.
- CRUD operations for code snippets.
- API key generation for users.
- Integration capabilities with other microservices.

## Quick Start:

### 1. Setup Environment

Make sure you have Python 3.8+ and Prisma CLI installed on your machine.

```bash 
python3 -m venv fastapienv 
source fastapienv/bin/activate 
pip install -r requirements.txt 
prisma generate # generates from schema.prisma

```

### 2. Configuration

Configure github/google Oauth using their documentations: [Github](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#web-application-flow) and [Google](https://developers.google.com/identity/protocols/oauth2/web-server#prerequisites). Setup a .env file with the variables from .env.example. 


### 3. Start the Server

```bash
uvicorn main:app --reload --port 8000
```

Now, your server should be running at `http://localhost:8000/`. You can access the Swagger UI at `http://localhost:8000/docs` to test the API.



## Integrating with other Microservices

Use the API key generated for each user to authenticate and access other related microservices. Ensure you add this API key in the header of your request:

```bash
Authorization: Bearer YOUR_API_KEY
```


Thank you for checking out the Snippet Sharing project. Your feedback and contributions are welcomed!

