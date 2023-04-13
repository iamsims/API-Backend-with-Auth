#!/bin/bash
set -e # Exit with nonzero exit code if anything fails

prisma migrate deploy 
exec python3 -m uvicorn --proxy-headers --forwarded-allow-ips="*"  main:app --host 0.0.0.0 --port 8080
