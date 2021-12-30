# Paks Actions

The following actions are provided for Paks:

 - [*build with paks*](#build): Build and optionally release a package

If you need a base container with paks, it's recommended to use the provided [container bases](https://github.com/syspack/paks/pkgs/container/paks-ubuntu-18.04).

## Build

This action will allow for:

 - build of a package in spack (will eventually support a local repository / package.py file)
 - release to GitHub packages as a binary artifact

Given the above, we could have repos that build and provide their own package binaries,
and then an addition to spack to allow installing from here. This means that a single repository
could package an existing spack package, or provide a new package. 
An example workflow might look like:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      packages: write
    name: Build Package Binaries
    steps:
      - name: Checkout
        uses: actions/checkout@v2
      - name: Build Packages
        uses: syspack/paks/action/build@main
        with:
          package: zlib
          token: ${{ secrets.GITHUB_TOKEN }}
          deploy: ${{ github.event_name != 'pull_request' }}
          user: ${{ github.actor }}
```

This action is provided in [build](build). Once a package is released, if it's your
trusted package registry you can use it to install with paks.
