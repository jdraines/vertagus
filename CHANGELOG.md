CHANGELOG
===

0.2.0
---

* **Branch-based versioning** - vertagus now supports using a manifest file on a target branch as the source of truth for the highest previous version, rather than needing to rely on tags.
* **Semver tag separators** - For separating the tag (e.g. `dev`, `b`) from the rest of the version, you can now use no space, a dash, or a dot. Previously, only no space or a dash was supported.
* **Git client bugfix** - The git client was previously falling back on a subprocess git command most of the time for tag deletion. This was because of incorrect use of the provider library's API. The use has been updated to match the API.
* **Config type checking** - Type checking in the config file parsing was incomplete and could potentially pass a `None` value in places where collections were expected if the underlying config had declared `null` for that field rather than omitting it. This was fixed.
