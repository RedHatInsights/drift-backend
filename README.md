# historical-system-profiles-backend
A service to return older system profile records


### dev setup
(need to fill this in)
 * make sure you have `libpq-devel` installed

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
