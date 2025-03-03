# Docker Setup for Project

This `docker-compose.yml` file defines multiple services used in the project, including PostgreSQL, Redis, Backend Server, Mobile Client, and Web Client. It also manages their dependencies, environment variables, and networking.

## Overview

The Docker Compose setup is structured as follows:

- **PostgreSQL Database** (`postgres`)
- **Backend Server** (`server`)
- **Redis** (`redis`)
- **Mobile Client** (`client_mobile`)
- **Web Client** (`client_web`)

These services communicate with each other via a custom Docker network (`area_network`). They are orchestrated using Docker Compose, allowing for easy setup and management of the services.

## Services

### 1. **PostgreSQL Database (`postgres`)**

This service runs a PostgreSQL 15 database.

- **Image**: `postgres:15`
- **Container Name**: `postgres_container`
- **Environment Variables**:
  - `POSTGRES_USER`: PostgreSQL username.
  - `POSTGRES_PASSWORD`: PostgreSQL password.
  - `POSTGRES_DB`: Database name.
- **Ports**: Exposes port `5432` for connecting to the database.
- **Volumes**: 
  - Persists data in a volume called `postgres_data`.
- **Network**: Connected to the `area_network` for communication with other services.
- **Health Check**: Periodically checks if PostgreSQL is ready with `pg_isready`.

### 2. **Backend Server (`server`)**

This service builds and runs the backend server.

- **Build Context**: `./backend` (Dockerfile located at `deployment/Dockerfile`).
- **Ports**: Exposes port `8080` for communication with the web and mobile clients.
- **Depends On**: Waits for PostgreSQL to be healthy before starting.
- **Environment Variables**:  
  - Configures database connection settings with environment variables such as `POSTGRES__HOST`, `POSTGRES__USER`, `POSTGRES__PASSWORD`, `POSTGRES__DB`.
- **Network**: Connected to the `area_network`.

### 3. **Redis (`redis`)**

This service runs Redis.

- **Image**: `redis:7.0.10`
- **Ports**: Exposes Redis on port `6380` (localhost only).
- **Command**: Starts Redis with the `--requirepass` option, using the password from the environment variable.
- **Network**: Connected to the `area_network`.

### 4. **Mobile Client (`client_mobile`)**

This service builds and runs the mobile client.

- **Build Context**: `./frontend/area` (Dockerfile located at `Dockerfile.mobile`).
- **Volumes**: Mounts a `build_volume` to persist build artifacts at `/app/build`.
- **Network**: Connected to the `area_network`.

### 5. **Web Client (`client_web`)**

This service builds and runs the web client.

- **Build Context**: `./frontend/area` (Dockerfile located at `Dockerfile.web`).
- **Ports**: Exposes the web client on port `8081`.
- **Volumes**: Mounts a `build_volume` to persist build artifacts at `/app/build`.
- **Depends On**:  
  - Waits for the mobile client (`client_mobile`) and the server (`server`) to be ready.
- **Network**: Connected to the `area_network`.

## Volumes

- **`build_volume`**: A volume used by both the mobile and web client services to persist build artifacts.
- **`postgres_data`**: A volume used to persist PostgreSQL database data.

## Networks

- **`area_network`**: A custom bridge network allowing all services to communicate with each other.

## Environment Variables

You must define the following environment variables for proper configuration:

- `POSTGRES_USER`: PostgreSQL username.
- `POSTGRES_PASSWORD`: PostgreSQL password.
- `POSTGRES_DB`: PostgreSQL database name.
- `POSTGRES_HOST`: Host for PostgreSQL connection.
- `REDIS_PASSWORD`: Redis password.


### Example `.env` file:

```env
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydatabase
POSTGRES_HOST=postgres
REDIS_PASSWORD=myredispassword
```


# Usage

## Build and Start Services
Run the following command to build and start all services:

```bash
docker-compose up --build
```

This will:

- Build images for all services.
- Start the services defined in the docker-compose.yml file.

## Stopping Services
To stop and remove all running containers, networks, and volumes:

```bash
docker-compose down
```

## Viewing Logs
To view the logs of a specific service:

```bash
docker-compose logs <service_name>
```

For example:

```bash
docker-compose logs server
```

## Accessing Services
- **PostgreSQL**: Accessible on `localhost:5432`.
- **Backend Server**: Accessible on `localhost:8080`.
- **Redis**: Accessible on `localhost:6380` (only locally).
- **Web Client**: Accessible on `localhost:8081`.

## Health Check for PostgreSQL
PostgreSQL health check is configured to ensure the database is ready. The check runs every 10 seconds, with a timeout of 5 seconds, and retries 5 times before considering the service unhealthy.

```bash
pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}
```

## Docker Compose Syntax
- **depends_on**: Ensures services are started in the right order based on the health of their dependencies.
- **volumes**: Mounts directories or Docker-managed volumes inside containers to persist data.
- **environment**: Specifies environment variables to configure services.
- **networks**: Defines the networks that services are connected to.

