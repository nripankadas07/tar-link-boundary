# tar-link-boundary

Trace ordered TAR symlink/hardlink boundary hazards without extracting files.

**Alpha, offline diagnostic.** Built for a developer reviewing a downloaded source/archive before choosing an extractor.
Original implementation with AI assistance; no competitor code or prose copied.
No production impact, adoption or performance advantage is claimed.

## Install and get a useful result

Python 3.10+. Clone this repository, then:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install .
python example.py
```

The bundled fixture is synthetic. `example.py` only creates its own temporary
fixture when present. Exit 0 means a report was produced with no CLI-level failure;
exit 1 explicitly reports hazards/uncovered hosts; exit 2 reports invalid or unsupported input.
Read the report limits before taking action.

## Input

```bash
tar-link-boundary downloaded.tar
```

Only an uncompressed TAR is accepted. stdout is the JSON report; exit 1 means
one or more boundary/unsupported hazards, and exit 2 means invalid input.
The archive digest is computed from the same bytes inspected. This tool does
not extract the archive. A zero result only describes the documented virtual
model, and must not authorize an unsafe extraction in a real destination.

## Capability and limits

Reads only uncompressed TAR metadata, at most 64 MiB and 10,000 members. Models an empty POSIX root with ordered virtual symlink traversal before parent segments; hardlinks must point to an earlier regular file. Duplicate/overwrite and special members are conservatively flagged. Retains outward link declarations virtually so later writes have a chain witness. No extraction or filesystem node creation occurs. A within-model result does not prove a particular extractor is safe: existing destinations, permissions, races, Windows semantics, sparse metadata, compression and extractor-specific overwrite policies are outside scope.

## Acceptance criteria

A symlink a→.. followed by a/secret produces two hazards and an explicit link chain; inward links resolve; parent segments are applied after link traversal; cycles terminate; hardlink forward references, duplicate names, non-directory parents and special/platform paths are flagged; malformed TAR fails without extracting.

## Checks and evidence

```bash
python -m unittest -v
python -m compileall -q .
```

[Validation](VALIDATION.md) documents the prepared checks and failure cases.
[Research and alternatives](RESEARCH.md) records dated observations, competing
workflows and a bounded inferred need. The [CI workflow](.github/workflows/test.yml)
builds wheels and tests installed commands outside the checkout on Linux Python
3.10/3.12/3.14. Check the actual current Actions result before relying on it.

[Contributing](CONTRIBUTING.md) · [Support](SUPPORT.md) ·
[Security](SECURITY.md) · [MIT license](LICENSE)
