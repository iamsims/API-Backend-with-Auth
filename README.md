# Installation  
```bash 
python3 -m venv fastapienv 
source fastapienv/bin/activate 
pip install -r requirements.txt 
uvicorn main:app --reload
```

# API Documentation 

## Authentication Endpoints
<br/>

### Login

#### `GET /login/{provider}`

Initiates the authentication process with the specified provider.

##### Request Parameters

- `provider` - The name of the provider to use for authentication. Currently supported providers are `google` and `github`.

##### Response

If successful, this endpoint returns a redirect to the provider's authentication page. If the provider is not recognized or an error occurs, an error response is returned.


<br/>

### Token 



#### `GET /token/{provider}`

Returns an access token for the specified provider. This endpoint is redirected by the endpoint `/login/{provider} `

##### Request 
Handled by the provider itself. 

- Path Parameters:
    - provider (string): the provider for the access token (either "google" or "github")
- Query Parameters:
    - code (string): the authorization code for the provider

##### Response

If successful, this endpoint returns a JSON object containing the access token for the authenticated user.

- Status Code: 201 Created
- Body:
    - result (boolean): whether the operation succeeded
    - access_token (string): the JWT access token for the user
    - token_type (string): the type of the token (must be "bearer")

 If an error occurs, an error response is returned.

<br/>

### Sign Up

#### `POST /signup`

Creates a new user account with the given credentials.

##### Request Body

- `username` - The username for the new account.
- `password` - The password for the new account.

##### Response

If successful, this endpoint returns a JSON object containing the access token for the new user account. 
- Status Code: 201 Created
- Body:
    - result (boolean): whether the operation succeeded
    - access_token (string): the JWT access token for the user
    - token_type (string): the type of the token (must be "bearer")

If the username is already taken or an error occurs, an error response is returned.

<br/>

### Login using Username/Password

#### `POST /token`

Authenticates the user with the given credentials and returns an access token.

##### Request Body

- `username` - The username for the account to authenticate.
- `password` - The password for the account to authenticate.

##### Response

If successful, this endpoint returns a JSON object containing the access token for the authenticated user. 
- Status Code: 200 OK
- Body:
    - result (boolean): whether the operation succeeded
    - access_token (string): the JWT access token for the user
    - token_type (string): the type of the token (must be "bearer")


If the credentials are invalid or an error occurs, an error response is returned.

<br/>

## Logout

#### `GET /logout`

Logs out the user by blacklisting their JWT access token.

#### Request

- Headers:
    - Authorization (string): the user's JWT access token (must be in the format "Bearer <access token>")

#### Response

If successful, this endpoint returns a JSON object: 
- Status Code: 200 OK
- Body:
    - result (boolean): whether the operation succeeded

If an error occurs, an error response is returned.


<br/>

## Reverse Proxy 

#### `GET POST /{endpoint:path}`

Proxies requests to the specified endpoint on behalf of the authenticated user.

##### Request 

- Path Parameters:
    - endpoint (string): the endpoint on the backend server to forward the request to
- Headers:
    - Authorization (string): the user's JWT access token (must be in the format "Bearer <access token>")
    - Other headers as needed for the request being forwarded

##### Response

If successful, this endpoint returns the response from the proxied endpoint. If an error occurs, an error response is returned.





<br/>
<br/>

# TODO 

- [ ] Write tests
- [ ] Extract from users_view to controllers
