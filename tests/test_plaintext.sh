#!/usr/bin/env bash
# registers a user and prints the stored Mongo document
set -e
BASE="http://localhost:8000"
EMAIL="pocuser@test"
PASS="PlainPass123"

echo "[1] Registering user..."
curl -s -X POST "$BASE/auth/register" -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\",\"full_name\":\"PoC User\",\"role\":\"teacher\"}" >/dev/null

echo "[2] Querying Mongo (requires mongo reachable at localhost:27017)"
python - <<PY
from pymongo import MongoClient
c = MongoClient("mongodb://localhost:27017/schoolify")
doc = c.schoolify.users.find_one({"email":"$EMAIL"})
print(doc)
PY