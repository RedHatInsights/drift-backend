# drift-dev-setup

If running on Fedora 32, docker is no longer supported out of the box. Check this article about getting docker running: https://fedoramagazine.org/docker-and-fedora-32/. Symptoms include...
 * error during build-images.sh step include something about the version of runc not supporting cgroups
 * failure starting containers because TCP networking not working correctly

The article above has steps to get docker running on Fedora 32.
NOTE: In the firewall-cmd section, I had to add masquerade to the "default" zone, not the "FedoraWorkstation" zone, because the "default" zone is what my system was using. Likely this is a remnant of upgrading Fedora over several versions and not a fresh Fedora 32 install.

Update 5/13/21: Docker support for Fedora 32 and beyond:
 * https://docs.docker.com/engine/install/fedora/

---

## Run All Components

 * add this to your `/etc/hosts`:
```
127.0.0.1 prod.foo.redhat.com
127.0.0.1 stage.foo.redhat.com
127.0.0.1 qa.foo.redhat.com
127.0.0.1 ci.foo.redhat.com
```

 * `docker login https://registry.redhat.io` (needed so you can pull base images during build process)
 * `docker login https://quay.io` (needed so you can pull base images during build process)
 * if you need to remove all images run `docker rmi -f $(docker images -a -q)`
 * `bash build-images.sh`
 * `docker-compose -f full-stack.yml up -d`
 * confirm everything is up: `docker-compose -f full-stack.yml ps` and confirm everything is either "running" or "exit 0"
 * confirm that you see the archiver working (give it a minute to see output): `docker-compose -f full-stack.yml logs -f hsp-archiver`
 * go to https://ci.foo.redhat.com:1337/insights/drift in the browser and confirm things look ok!

## Run All Components Using Local kerlescan Code

If you are developing kerlescan code and want to run the components using the code you are developing, use `full-stack-local-kerlescan.yml` instead of `full-stack.yml` in the docker-compose command.
* `docker-compose -f full-stack-local-kerlescan.yml up -d`

This yml file assumes your kerlescan repo is checked out in the same parent directory as this drift-dev-setup repo is checked out. The `full-stack-local-kerlescan.yml` file mounts your local kerlescan source directory in place of the kerlescan code in the image running in each container.
