# Security policy

## Supported versions

Security fixes are applied to the latest released minor version of vertagus.
Older versions are not backported.

## Reporting a vulnerability

Please report vulnerabilities privately through
[GitHub Security Advisories](https://github.com/jdraines/vertagus/security/advisories/new),
or by email to johndanielraines@gmail.com. Please do not open a public issue for
an unfixed vulnerability.

Include, where you can: the version of vertagus, the configuration that triggers
the issue, and a minimal reproduction. You can expect an acknowledgement within a
week.

## Threat model

Vertagus reads a configuration file, reads version strings out of manifest files,
and runs `git` commands on the repository it is pointed at. It is designed to run
in CI, which means:

- **The configuration file is not trusted.** In a pull-request workflow the
  config is read from the contributor's branch, so any value in it -- remote
  name, tag prefix, target branch, manifest path -- may be chosen by someone with
  no write access to the repository.
- **Manifest contents are not trusted.** Version strings parsed out of a manifest
  end up in tag names and therefore on a git command line.
- **Command-line arguments are not trusted** for the same reason.

Every one of those values is validated before it reaches a `git` invocation; see
`src/vertagus/providers/scm/git_/validation.py`. Values that git would read as an
option (anything beginning with `-`) are rejected, as are control characters.
Git is invoked with an explicit argument vector and never through a shell.

Vertagus does not modify the configuration of the repository it operates on. The
committer identity used for tagging is supplied per-invocation with `git -c`.

## This repository's own CI

The same reasoning applies to the workflows in `.github/workflows`. Values that
originate outside the repository — `github.head_ref` above all, which on a fork
is the branch name chosen by someone with no write access, and which may contain
shell metacharacters — are passed to `run:` steps through `env:` rather than
interpolated into the script with `${{ }}`. An interpolated value is substituted
before the shell sees the line, so a branch named ``release/`id` `` would
otherwise execute. Workflow permissions are scoped per job, and third-party
actions holding `id-token: write` are pinned by commit SHA.
