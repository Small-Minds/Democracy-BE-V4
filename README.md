# Democracy

[![CI](https://github.com/Small-Minds/Democracy-BE-V3/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/Small-Minds/Democracy-BE-V3/actions/workflows/ci.yml)

**SOURCE CODE COPYRIGHT (C) SMALL MINDS 2020**

This repository contains the services/backend component to the Democracy system.

The _Democracy_ project by _Small Minds_ is designed to:

1. Provide a secure and fair voting system for small elections.
1. Give election runners the ability to easily manage a set of open positions.
1. Give candidates a simple way to run for any given position.
1. Ensure election runners can restrict applicants by email domain.
1. Use simple email verification to ensure users are part of any given org.

Frontend: [Democracy-PWA-V3](https://github.com/Small-Minds/Democracy-PWA-V3)

## Contributing

When adding new features, please use the semantic commit style with these labels:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries such as documentation generation


## Development

No matter the OS, you can simply type these two commands to build, run (with hot reloading,) and unit test the system:

```shell
# Build
docker-compose build

# Start/Develop
docker-compose up

# Run Unit Tests
docker-compose run django pytest --looponfail
```

In development, an artificial mailbox can be found at <http://127.0.0.1:8025/>. All dev emails are directed here.


## Structure

```
User
  => First/Last Name
  =>
  => [Email Addresses]
  => Elections  (Elections the User owns.)

Election
  => [Email Domains]
  => Multiple_Applications: boolean
  => Application_Start_Time: date
  => Application_End_Time: date
  => Voting_Start_Time: date
  => Voting_End_Time: date
  => Positions: Position[]

Position
  => Title: string
  => Description: string
  => Candidates: Candidate[]

Candidate
  => User: User
  => Platform: string
```


## FUBAR

If nothing works, use `docker system prune --all --force --volumes` to kill everything.

## Heroku Access

To get to BASH in Heroku, download the CLI and use the following command:

```
heroku run -a sm-democracy-v1 bash
```

## Backup or Restore Database Dump

<https://devcenter.heroku.com/articles/heroku-postgres-import-export>

You'll need to paste the password from the docker compose configs when prompted.

```ps
PS C:\vc\sm\Democracy\backups\ieee_ess_2021>
pg_restore --verbose --clean --no-acl --no-owner -d localhost:5432 -U lyWseqTBCwaJmewskVjaSTukcQUkgoFf -d democracy .\latest.dump
```
