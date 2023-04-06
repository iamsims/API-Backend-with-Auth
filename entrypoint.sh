#!/bin/bash
set -e # Exit with nonzero exit code if anything fails

exec python3 -m prisma migrate deploy 
exec python3 -m prisma generate
exec python3 -m uvicorn main:app --host 0.0.0.0 --port 8080
