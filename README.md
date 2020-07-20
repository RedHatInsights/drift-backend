# drift-dev-setup

to run:

 * `docker login https://registry.redhat.io` (needed so you can pull base images during build process)
 * `bash build-images.sh`
 * `docker-compose -f full-stack.yml up -d`
 * confirm everything is up: `docker-compose -f full-stack.yml ps` and confirm everything is either "running" or "exit 0"
 * confirm that you see the archiver working (give it a minute to see output): `docker-compose -f full-stack.yml logs -f hsp-archiver`
 * go to http://ci.foo.redhat.com:1337 in the browser and confirm things look ok!
