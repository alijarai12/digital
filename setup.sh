#!/bin/bash

: <<'COMMENT'
-- author   Naxa
-- detail   This script prepares project for local development and production environment.
COMMENT

echo "============================================================================================="
echo "||                             I am lazy today. Setup manually!                            ||"
echo "============================================================================================="

# FASTAPI_PROD_COMPOSE=$(cat <<EOF
#   fastapi:
#     env_file:
#       - .env
#     build:
#       context: .
#       dockerfile: Dockerfile
#     restart: always
#     volumes:
#       - .:/code
#       - ./logs/:/logs/
#     depends_on:
#       - db
#       - mongo
#     ports:
#       - \${FASTAPI_APP_PORT}:8000
#     entrypoint: sh fastapi-entrypoint.sh
#     networks:
#       - \${PROJECT_NAME}_nw
#     deploy:
#       resources:
#         limits:
#           cpus: "0.5"
#           memory: "500M"

#   mongo:
#     image: mongo:6.0.2
#     restart: always
#     volumes:
#       - ./mongodb_data:/data/db
#     # ports:
#     #   - 27017:27017
#     env_file:
#       - .db_env
#     networks:
#       - \${PROJECT_NAME}_nw
#     deploy:
#       resources:
#         limits:
#           cpus: "0.3"
#           memory: "300M"
# EOF
# )

# FASTAPI_DEV_COMPOSE=$(cat <<EOF
#   fastapi:
#     env_file: .env
#     build:
#       context: .
#       dockerfile: Dockerfile
#     restart: always
#     volumes:
#       - .:/code
#     depends_on:
#       - db
#       - mongo
#     ports:
#       - \${FASTAPI_APP_PORT}:8000
#     entrypoint: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

#   mongo:
#     image: mongo:6.0.2
#     volumes:
#       - ./mongodb_data:/data/db
#     # ports:
#     #   - 27017:27017
#     env_file:
#       - .db_env
# EOF
# )

# function createEntrypoint {
#     echo "Enter port for Web App:"
#     read WEB_APP_PORT
#     export WEB_APP_PORT=$WEB_APP_PORT
#     export PROJECT_NAME=$PROJECT_NAME
#     if [ $NEED_FASTAPI = 'y' ]; then
#       echo "Enter port for FastApi App:"
#       read FASTAPI_APP_PORT
#       export FASTAPI_APP_PORT=$FASTAPI_APP_PORT
#     fi
#     echo ""
#     if [ $DEPLOY_TYPE -eq 2 ]; then
#         if [ $NEED_FASTAPI = 'y' ]; then
#           export FASTAPI_COMPOSE=`echo "$FASTAPI_PROD_COMPOSE" | envsubst`
#         fi
#         cp -p docker/docker-compose.prod.yml docker-compose.yml
#         cat docker-compose.yml | envsubst | tee docker-compose.yml
#         cp -p docker/docker-entrypoint.prod.sh entrypoint.sh
#         cat entrypoint.sh | envsubst | tee entrypoint.sh
#         cp -p uwsgi.ini uwsgi.$PROJECT_NAME.ini
#     else
#         if [ $NEED_FASTAPI = 'y' ]; then
#           export FASTAPI_COMPOSE=`echo "$FASTAPI_DEV_COMPOSE" | envsubst`
#         fi
#         cp -p docker/docker-compose.local.yml docker-compose.yml
#         cp -p docker/docker-entrypoint.local.sh entrypoint.sh
#         cat docker-compose.yml | envsubst | tee docker-compose.yml
#     fi
# }

# function makeProject {
#     if [ $DEPLOY_TYPE -eq 2 ]; then
#         cp -rp docker/Dockerfile.prod Dockerfile
#     else
#         cp -rp docker/Dockerfile.dev Dockerfile
#     fi
#     cp -rp env_sample .env
#     cp -rp pg_env_sample .db_env
#     createEntrypoint
# }

# function makeGISProject {
#     cp -rp dependencies/requirements_gis.txt requirements.txt
#     cp -rp dependencies/apt_requirements_gis.txt apt_requirements.txt
#     makeProject
# }

# function makeNonGISProject {
#     cp -rp dependencies/requirements_nongis.txt requirements.txt
#     cp -rp dependencies/apt_requirements_nongis.txt apt_requirements.txt
#     makeProject
# }

# function readDeploymentType {
#     echo "Please Choose the deployment type:"
#     echo "   [1] Local"
#     echo "   [2] Production"
#     read DEPLOY_TYPE

#     if [ $DEPLOY_TYPE -eq 1 ]; then
#         echo "Preparing project for local development"
#     elif [ $DEPLOY_TYPE -eq 2 ]; then
#         echo "Preparing project for Production"
#     else
#         echo "Bad deployment type input please choose 1 or 2."
#         exit 1
#     fi
#     echo ""
# }

# function readProjectType {
#     echo "Please Choose the project type:"
#     echo "   [1] GIS"
#     echo "   [2] NON-GIS"
#     read PROJECT_TYPE

#     if [ $PROJECT_TYPE -eq 1 ]; then
#         echo "Preparing project as GIS"
#         echo ""
#         makeGISProject
#     elif [ $PROJECT_TYPE -eq 2 ]; then
#         echo "Preparing project as Non-GIS"
#         echo ""
#         makeNonGISProject
#     else
#         echo "Bad project type input please choose 1 or 2."
#         exit 1
#     fi
#     echo ""
# }

# function readProjectName {
#     echo "Please give project a name:"
#     read PROJECT_NAME
#     echo ""
# }

# function readFastAPIIntegration {
#     echo "Do you want FastAPI integration [y/n]?"
#     read NEED_FASTAPI
#     echo ""
# }

# readProjectName
# readDeploymentType
# readFastAPIIntegration
# readProjectType

# echo "Boilerplate files generated. Please review following files:"
# echo "  1. .env"
# echo "  2. .pg_env"
# echo "  3. docker-compose.yml"
# echo "  4. entrypoint.sh"

# echo 'Then run `docker compose up -d`'
