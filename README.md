# fpgas.online-docs

Documentation for [fpgas.online](https://fpgas.online), published at
<https://docs.fpgas.online>.

Sphinx, configured for Markdown via [MyST](https://myst-parser.readthedocs.io/).
Pages are `.md`; reStructuredText still works if a page ever needs it.

## Build locally

```console
$ python3 -m venv .venv && . .venv/bin/activate
$ pip install -r docs/requirements.txt
$ sphinx-build -b html docs docs/_build/html
$ python3 -m http.server -d docs/_build/html
```

CI and Read the Docs both build with warnings as errors, so a clean local build
is the bar.

## Layout

```
docs/
  conf.py           Sphinx configuration (MyST, furo theme)
  requirements.txt  pinned build dependencies
  index.md          landing page
  sites/            per-site hardware documentation
  packages.md       the APT repository and how packages reach it
  contributing.md   how to write and build these pages
.readthedocs.yaml   Read the Docs build configuration
```

## Read the Docs

The project builds from `.readthedocs.yaml`. `docs.fpgas.online` is a CNAME to
`readthedocs.io`; Read the Docs routes on the `Host` header, so the domain also
has to be registered as a custom domain on the project itself.

## Writing

See [contributing](docs/contributing.md). In short: document the surprise, not
the syntax, and date any measurement you record.

## Licence

Apache 2.0. See [LICENSE](LICENSE).
