# drift-dev-setup

to run:

 * `bash build-images.sh`
 * `docker-compose -f full-stack.yml up -d`
 * confirm everything is up: `docker-compose -f full-stack.yml ps` and confirm everything is either "running" or "exit 0"
 * confirm that you see the archiver working (give it a minute to see output): `docker-compose -f full-stack.yml logs -f hsp-archiver`
 * run insights-proxy with the `api.js` spandx conf
