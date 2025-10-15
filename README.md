# Realest
Real Estate app that collects properties on sale and provide a rating


### Start the application
./run.sh

### Or manually:
podman-compose -f podman-compose.yml up --build -d

### Check services
podman-compose -f podman-compose.yml ps

#### Check services env
podman-compose -f podman-compose.yml exec web env

### Stop services
podman-compose -f podman-compose.yml down
