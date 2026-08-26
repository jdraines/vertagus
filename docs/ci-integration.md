# CI Integration

Vertagus talks to source control by running the `git` executable. It makes no
API calls to GitHub, GitLab, or any other host, and reads no platform-specific
environment variables, so it runs anywhere a `git` binary and a working checkout
are available.

What differs between platforms is not vertagus but the checkout their CI systems
hand you. Two properties matter:

* **Can the job push?** `create-tag` and `create-aliases` write tags to the
  remote.
* **How much history was cloned?** The `semver` bumper reads commit messages
  since the last version tag.

## Push credentials

`vertagus create-tag` ends in a `git push` of the new tag to the configured
remote. The job therefore needs credentials with write access to the repository.

=== "GitLab CI"

    GitLab's default `CI_JOB_TOKEN` **cannot push to the repository** — it is
    scoped to reading the source and talking to the registry. The runner bakes
    that token into the `origin` URL, so a push fails with `403 Forbidden` even
    though the clone succeeded.

    Create a [project access token](https://docs.gitlab.com/user/project/settings/project_access_tokens/)
    with the `write_repository` scope and at least the Maintainer role, store it
    as a masked CI/CD variable, and point the remote at it:

    ```yaml
    tag:
      stage: release
      image: python:3.11
      variables:
        GIT_DEPTH: 0
      rules:
        - if: $CI_COMMIT_BRANCH =~ /^(release|hotfix)\//
      before_script:
        - pip install vertagus
        - git remote set-url origin
            "https://oauth2:${VERTAGUS_TOKEN}@${CI_SERVER_HOST}/${CI_PROJECT_PATH}.git"
      script:
        - vertagus create-tag -c vertagus.yaml -s prod
    ```

    If your tags match a [protected tag](https://docs.gitlab.com/user/project/protected_tags/)
    pattern — `v*` is a common default — the token's identity must also be
    allowed to create them, or the push is rejected regardless of scope.

=== "GitHub Actions"

    The default `GITHUB_TOKEN` can push once the job is granted write
    permission:

    ```yaml
    jobs:
      tag:
        runs-on: ubuntu-latest
        permissions:
          contents: write
        steps:
          - uses: actions/checkout@v4
            with:
              fetch-depth: 0
          - uses: actions/setup-python@v5
            with:
              python-version: '3.11'
          - run: pip install vertagus
          - run: vertagus create-tag -c vertagus.yaml -s prod
    ```

    Tag protection rules and required rulesets apply the same way GitLab's
    protected tags do.

When a push is rejected, vertagus reports git's own stderr alongside a reminder
of these causes, so a `403` in a pipeline log should point at the fix directly.

## Clone depth

CI checkouts are shallow by default — GitLab CI uses `GIT_DEPTH: 20`, and
`actions/checkout` fetches a single commit. Two vertagus behaviours depend on
history being present:

* `vertagus bump` with the `semver` bumper reads every commit message since the
  last version tag. On a truncated clone it sees only the commits that were
  fetched, and computes too small a bump — silently, because a short history is
  indistinguishable from a quiet release.
* The tag-based `version_strategy` finds the highest version by querying the
  remote, so it always sees every tag. If the tag it picks is older than the
  clone depth, vertagus fetches that one tag on demand rather than failing, but
  the commit range it then walks is still bounded by the clone.

**Set the depth to unlimited in any job that runs `bump`, or that runs
`create-tag` with a semver bumper:**

=== "GitLab CI"

    ```yaml
    variables:
      GIT_DEPTH: 0
    ```

=== "GitHub Actions"

    ```yaml
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    ```

Jobs that only run `validate` against a target branch do not need full history:
the branch-based `version_strategy` reads a single manifest file out of
`origin/<branch>`, which one `git fetch` satisfies.

## Detached HEAD

Both platforms check out a detached HEAD rather than a branch. Vertagus does not
depend on the current branch name — tags are created at an explicit commit, and
the branch used for validation comes from `--target-branch` / the `-b` flag. Pass
the platform's own variable:

=== "GitLab CI"

    ```yaml
    script:
      - vertagus validate -c vertagus.yaml -s dev -b "$CI_MERGE_REQUEST_TARGET_BRANCH_NAME"
    ```

=== "GitHub Actions"

    ```yaml
    - run: vertagus validate -c vertagus.yaml -s dev -b "${{ github.base_ref }}"
    ```

## Choosing a remote

Vertagus pushes to the remote named by `remote_name` in the `scm` block, which
defaults to `origin` — the name both platforms give the remote they configure.
Set it explicitly only if your job adds a second remote to push tags somewhere
other than where the code was cloned from.
