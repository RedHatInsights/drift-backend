# kerlescan
shared service lib

## Required dependencies:
- poetry
- pre-commit

## Work with pre-commit hooks

```bash
# installs pre-commit hooks into the repo
pre-commit install --install-hooks

# run pre-commit hooks for staged files
pre-commit run

# run pre-commit hooks for all files in repo
pre-commit run --all-files

# bump versions of the pre-commit hooks automatically
pre-commit autoupdate

# bypass pre-commit check
git commit --no-verify
```

## To run tests
1. `poetry install --with dev sync`
2. `poetry run pytest`

## To run SonarQube:
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
