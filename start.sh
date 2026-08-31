#!/bin/bash
# Launch project

docker compose up --build -d

echo "------------------------------------------------"
echo " Project successfully started in Docker! "
echo " Use 'docker compose logs -f' to see logs. "
echo "------------------------------------------------"
