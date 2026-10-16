#!/bin/bash
# Local FalkorDB. Preferred: docker run -p 6379:6379 falkordb/falkordb:latest
# (this dev box has no docker; the image's own binaries were extracted - see docs/DEV_ENVIRONMENT.md)
docker run -d --name aftershock-falkordb -p 6379:6379 falkordb/falkordb:latest
