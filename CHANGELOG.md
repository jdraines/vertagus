CHANGELOG
===

0.5.0
---

**Breaking changes.**

* **Rules are now configured as a flat list.** The `rules` block is no longer split into `current`, `increment`, and `manifest_comparisons` sub-keys. List every rule directly under `rules`; vertagus infers from the rule class whether it validates a single version or compares versions. A 0.4.x-style mapping is detected and raises an error explaining the migration.

  ```yaml
  # 0.4.x                       # 0.5.0
  rules:                        rules:
    current:                      - not_empty
      - not_empty                 - any_increment
    increment:
      - any_increment
  ```

* **`manifests_comparison` is now an ordinary, configurable rule.** Instead of the `manifest_comparisons` sub-key, list it like any other configurable rule with a `manifests` config naming the manifests to compare. Omitting `manifests` now raises a descriptive error instead of a `KeyError`.
* **Minimum supported Python is now 3.11** (was 3.9). The test matrix covers 3.11 through 3.14. TOML parsing moved from the `tomli` dependency to the stdlib `tomllib`, dropping a runtime dependency.
* **Rule base classes were consolidated.** `VersionComparisonRule` is now `ComparisonRule`, and `ConfigurableSingleVersionRule` is folded into `SingleVersionRule` — every rule now takes an optional `config` dict and validates as an instance. `SingleVersionRuleType`, `SingleVersionRuleProtocol`, `is_single_version_rule_type`, and `is_configurable_single_version_rule` are removed. This only affects code importing vertagus rule internals.
* `vertagus list-rules` now reports a `Type` column (`single_version` / `comparison`) in place of the old `Config Usage` column, and includes `manifests_comparison`.
* Rules are now deduplicated by class *and* config, so the same rule type can be listed at both project and stage level with different configurations.
* **Configuration errors are now reported as plain CLI errors** rather than tracebacks. A new `vertagus.errors.ConfigurationError` covers the 0.4.x migration message, unknown rule names, malformed rule entries, and `manifests_comparison` misconfiguration; the CLI catches it, prints the message, and exits 1.
* A `manifests_comparison` rule that names a manifest which isn't defined now reports exactly which name didn't resolve and lists the known manifests, instead of failing later with a confusing "only one version to compare" error.

0.4.0
---

* Add a `vertagus init` command that runs a wizard to create a vertagus configuration file.
- Expand the capabilities of the single-version rule type that is used to evaluate whether the current version matches some criteria (e.g. regex) so that rules can now accept configuration by users. There is currently one rule that utilizes this feature, `custom_regex`, allowing a user to specify a custom regex expression that the current version should match.
- Added the `custom_regex` rule that can be configured in the vertagus config to provide user-defined regex validation.
- Added `uv` as the package/project management tool.

0.3.1
---

* Fix the way `SemanticCommitBumper` is handling the `BREAKING CHANGES` substring. In `0.3.0`, this substring was handled as a semantic commit type, but from now on, is handled in keeping with Conventional Commit documentation, so that if it appears anywhere in the commit message, the bump should be major.

0.3.0
---

* **Semantic Commit auto version bumping support** A new `SemanticCommmitBumper` class uses commit messages that follow the semantic commit conventions to determin the level of semver bump that should be applied.

0.2.5
---

* **Version bumping kwargs** The `Bumper` class' `.bump()` method now accepts `**kwargs` and calling operations (e.g., `vertagus.operations.bump_version`) now inject only kwargs. The CLI expects key-values, so `vertagus bump level=minor` would be the new usage. However, to maintain backwards compatibility with `0.2.4`, a single bumper argument without an `=` sign will be handled as the equivalent of `level={arg}`.


0.2.4
---

* **Version bumping** A new primitive, `Bumper` has been added, providing some sort of logic to bump a version via a `.bump(version, *args)` method. Currently only implemented for semver, expecting the argument `level` to be one of `major`, `minor`, or `patch`. See README for fuller description.

0.2.3
---

* **Bugfix in GitScm** A parameter validation check was checking to see if _either_ `branch` was `None` _or_ if `self.target_branch` was None and was failing on both conditions. It should only be failing if the `and` condition is true. This was fixed.

0.2.2
---

* **Consistent & flexible manifest `loc` declaration** Manifest locs can now be declared as either a string with dot notation or as a list of str. Previously, it was ambiguous in the code and documentation as to which could be used in various places. The parsing is now consistent in all places and flexible to support both declaration types.
* **Bug in GitScm** When configured for `branch` version strategy, the GitScm provider was not passing a configured `manifest_loc` value to the function extracting the version from the branch's manifest. For providers like `toml`, `yaml`, and `json` where version is extracted via some configured `loc` path, this was problematic. For manifest providers like `setuptools_pyproject`, this did not create any issues, since that provider specifies a static loc on as a class attribute.


0.2.1
---

* **Git client rollback** changes to the git client relating to deleting tags produced their own new issues and were rolled back.

0.2.0
---

* **Branch-based versioning** - vertagus now supports using a manifest file on a target branch as the source of truth for the highest previous version, rather than needing to rely on tags.
* **Semver pre-release-tag separators** - For separating the tag (e.g. `dev`, `b`) from the rest of the version, you can now use no space, a dash, or a dot. Previously, only no space or a dash was supported.
* **Git client bugfix** - The git client was previously falling back on a subprocess git command most of the time for tag deletion. This was because of incorrect use of the provider library's API. The use has been updated to match the API.
* **Config type checking** - Type checking in the config file parsing was incomplete and could potentially pass a `None` value in places where collections were expected if the underlying config had declared `null` for that field rather than omitting it. This was fixed.
