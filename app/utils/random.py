import secrets
import base64

def generate_random_string(value=48):
    random_bytes = secrets.token_bytes(value)
    api_key = base64.b64encode(random_bytes).decode('utf-8')
    api_key = api_key.replace("=","")
    api_key = api_key.replace("+","")
    api_key = api_key.replace("/","")  
    return api_key    

