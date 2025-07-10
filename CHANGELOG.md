CHANGELOG
===

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
