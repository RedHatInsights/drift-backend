# historical-system-profiles-backend
A service to return older system profile records


### dev setup
(need to fill this in)
 * make sure you have `libpq-devel` installed

## db changes and migration

The db schema is defined by the objects defined in models.py.  When a change is made to these model objects, a database migration needs to be created.  This migration will be applied automatically when an updated image is spun up in a pod.  The steps to create the database migration are below:

* make changes to model objects in models.py
* in the historical-system-profiles-backend source directory, run `pipenv shell`
* spin up the dev database with `docker-compose -f dev.yml up -d`
* run flask to upgrade the dev database to its current state with the command `FLASK_APP=historical_system_profiles.app:get_flask_app_with_migration flask db upgrade`
* now run flask to create migration with the command `FLASK_APP=historical_system_profiles.app:get_flask_app_with_migration flask db migrate -m "migration message"`
* be sure to include the newly created migration file in migrations/versions/ in your pull request

### To run SonarQube:
1. Make sure that you have SonarQube scanner installed.
2. Duplicate the `sonar-scanner.properties.sample` config file.
```
  cp sonar-scanner.properties.sample sonar-scanner.properties
```
3. Update `sonar.host.url`, `sonar.login` in `sonar-scanner.properties`.
4. Run the following command
```
java -jar /path/to/sonar-scanner-cli-4.6.0.2311.jar -D project.settings=sonar-scanner.properties
```
5. Review the results in your SonarQube web instance.
