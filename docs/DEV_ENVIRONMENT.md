# Dev environment note
The build box has no Docker. FalkorDB was run by extracting `redis-server` and `falkordb.so` from the official
`falkordb/falkordb:latest` image layers (FalkorDB 4.22.1) and starting it with the image's own glibc loader. Judges: use `docker run falkordb/falkordb`.
