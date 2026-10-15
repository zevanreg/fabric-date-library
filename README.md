# Fabric date library

A standalone, zero-runtime-dependency Python demo. It prints the current **UTC**
date and time to whole seconds, not the workstation's local time. Requires
Python 3.11 or newer.

```python
from demo_date import print_current_date

print_current_date()  # For example: 2026-10-09T14:30:45+00:00
```

`print_current_date()` prints `YYYY-MM-DDTHH:MM:SS+00:00` followed by a newline.
The `+00:00` offset denotes UTC; fractional seconds are omitted. Date-only
inputs print at midnight UTC (`00:00:00`).

`current_date()` still returns a `datetime.date`. Both functions accept an optional
`datetime` or `date` for deterministic demos and tests. Aware datetimes are
converted to UTC; naive datetimes are interpreted as UTC. For date-only text,
use `current_date().isoformat()`.

## Local build and validation (PowerShell)

```powershell
Set-Location C:\repos\fabric-date-library
python -m venv .venv
$python = (Resolve-Path .venv\Scripts\python.exe).Path
& $python -m pip install -r requirements-dev.txt
& $python -m build --wheel
& $python -m pip install --no-deps dist\demo_date-0.1.0-py3-none-any.whl
$tests = (Resolve-Path tests).Path
Push-Location ..
try {
    & $python -m unittest discover -s $tests -v
    & $python -c "from demo_date import print_current_date; print_current_date()"
} finally {
    Pop-Location
}
Get-FileHash dist\demo_date-0.1.0-py3-none-any.whl -Algorithm SHA256
```

Tests deliberately run outside the repository against the installed wheel.
The `src` layout avoids accidentally testing an uninstalled source package.
Development build tools are pinned; runtime dependencies are empty.

## GitHub CI and release

- `ci.yml`: pushes to `main`, pull requests, or manual dispatch build a wheel,
  install it, run standard-library `unittest` tests on Python 3.11, and retain
  the wheel as an Actions artifact.
- `release.yml`: a pushed `v*` tag must exactly match the version in
  `pyproject.toml` (initially `v0.1.0`). It builds once, installs and tests that
  wheel, then publishes it and `SHA256SUMS` to a GitHub Release. Only the release
  job has `contents: write`. Nothing is published to PyPI.
- After publication, an optional `notify-workloads` job dispatches the consuming
  repository's **Update library release pin** workflow, which verifies the assets
  and opens a reviewed pin-only PR to `dev`. It does not deploy or auto-merge.

After reviewing and committing the repository, configure a GitHub remote and
push `main`, then create and push the version tag. Those remote operations are
not performed by the local setup. For every new release, bump the metadata
version first, commit, and use a new tag. Do not move or reuse release tags.

Initial asset: **`demo_date-0.1.0-py3-none-any.whl`**.
The workflow does not overwrite existing releases or assets. Enable GitHub's
**immutable releases** repository setting before publishing for server-enforced
immutability; otherwise repository administrators can still edit/delete assets.
Protect release tags and restrict who can create them.

### Automatic consumer pin PR

Publish the consumer's `update-pin.yml` workflow on `main` and its updater on
`dev` before enabling notification. In this library repository, configure:

| Setting | Value |
| --- | --- |
| Repository variable `WORKLOADS_REPOSITORY` | `zevanreg/fabric-wheel-workloads` |
| Secret `WORKLOADS_DISPATCH_TOKEN` | Fine-grained PAT with consumer **Actions: read/write** access |

In the consumer, configure secret `PIN_PR_TOKEN` with **Contents: read/write**
and **Pull requests: read/write**, plus `GH_RELEASE_TOKEN` with library
**Contents: read** if this library is private. The separate PR token ensures
PR creation triggers the consumer's existing CI. Protect the consumer's `dev`
and `main` branches and keep human review required.

Without `WORKLOADS_REPOSITORY`, notification is skipped and release publication
is unchanged. When enabled, a notification failure fails that job but leaves
the published release intact. Retry by manually running the consumer's
**Update library release pin** workflow on `main` with the exact published tag;
do not recreate the release. This also bootstraps an already published `v0.1.0`.

## Downstream manual integration

Put this workflow in a consuming repository. Replace `YOUR_ORG` and pin the
repository variable `DEMO_DATE_WHEEL_SHA256` to the wheel hash from a trusted
release. Keep the tag, filename, and expected checksum pinned together when
upgrading; never select a mutable `latest` asset.

```yaml
name: Run date demo
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  demo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Download pinned release wheel
        env:
          GH_TOKEN: ${{ secrets.LIBRARY_READ_TOKEN || github.token }}
        run: |
          gh release download v0.1.0 --repo YOUR_ORG/fabric-date-library \
            --pattern demo_date-0.1.0-py3-none-any.whl
      - name: Verify trusted checksum and install
        env:
          EXPECTED_SHA256: ${{ vars.DEMO_DATE_WHEEL_SHA256 }}
        run: |
          test "${#EXPECTED_SHA256}" -eq 64
          printf '%s  %s\n' "$EXPECTED_SHA256" \
            demo_date-0.1.0-py3-none-any.whl | sha256sum --check --strict
          python -m pip install --no-deps demo_date-0.1.0-py3-none-any.whl
      - name: Print current UTC date and time
        run: python -c "from demo_date import print_current_date; print_current_date()"
```

For a private library repository, provide a narrowly scoped
`LIBRARY_READ_TOKEN` secret with read access to that repository's contents.
A consuming repository's default token normally cannot read another private
repository. Public library releases can use the default token.

For a Fabric notebook, first download and verify the same pinned wheel, upload
it through your approved Fabric library/environment mechanism, then run the
Python example above. This repository intentionally does not automate workspace
deployment or contain tenant credentials.

No license has been assigned; agree licensing before distributing beyond the
authorized customer demo.
