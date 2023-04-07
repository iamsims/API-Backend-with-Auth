#!/bin/bash
set -e # Exit with nonzero exit code if anything fails

prisma migrate deploy 
prisma generate
exec python3 -m uvicorn main:app --host 0.0.0.0 --port 8080
