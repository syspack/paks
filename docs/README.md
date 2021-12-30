# Paks

Paks is a packaging framework that is optimized for community packages, meaning that
anyone can generate a simple repository with a package specification and then:

1. The repository automatically detects new versions of a package upstream and builds
2. Building is recommended to perform testing
3. A successful update, build, and test leads to a new release
4. The repository then serves metadata about the package via RESTful API
5. (Optionally) the repository can provide single containers

While we use Spack as the underlying manager for building, we have extended a Spack
spec and other concepts to be flexible to installing from a source like GitHub.

## Usage

### Install Paks

First, clone the repository:

```bash
$ git clone https://github.com/syspack/paks
$ cd paks
```

You'll need to init submodules - spack is "installed" as a submodule alongside it.

```bash
$ git submodule init
$ git submodule update
```

Note that spack is added as follows - and you can modify this logic if you want a different
branch, version, etc.

```bash
$ git submodule add git@github.com:spack/spack paks/spack
```

And then create a virtual environment

```bash
$ python -m venv env
$ source env/bin/activate
```

And install paks

```bash
$ pip install -e .
```

### GitHub Setup

If you want to push packages to your organization, you will need to go to Settings -> Packages
and ensure that the public box is checked. Otherwise, all packages will be private (and not seen by
the tool).

### Settings

Most defaults should work without changing. However, to change defaults you can either
edit the settings.yml file in the installation directory, or create a user-specific configuration
by doing:

```bash
$ paks config init
Created user settings file /home/vanessa/.paks/settings.yml
```

You can then change a setting, such as the username and email for your gpg key (used to sign
the build cache artifacts):

```bash
$ paks config set username:dinosaur
Updated username to be dinosaur
$ paks config set email:dinosaur@users.noreply.github.io
Updated email to be dinosaur@users.noreply.github.io
```

These user settings will over-ride the default installation ones.

### Commands

#### Install

Since paks is a wrapper to spack, you can install any list of packages that you would
install with spack, just using paks install (which is installable via pip so it can be on your path
more easily or in a Python environment).

```bash
$ paks install zlib
Preparing to install zlib
linux-ubuntu20.04-skylake
[+] /home/vanessa/Desktop/Code/syspack/paks/paks/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/zlib-1.2.11-3kmnsdv36qxm3slmcyrb326gkghsp6px
```

This is a traditional install, but it's also a little more! We generate a software
bill of materials to go alongside the install, and this will be uploaded to the package archive.
If you install, build, and push to a trusted Paks registry (the one in your settings) then this
registry will be used as a cache for future installs. We can use the manifest of the artifact to validate 
the checksum before installing it.

#### Shell

If you want a quick shell to interact with the Pak client and spack, you can do:

```bash
$ paks shell
Python 3.8.8 (default, Apr 13 2021, 19:58:26) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.30.1 -- An enhanced Interactive Python. Type '?' for help.

In [1]: client
Out[1]: [paks-client]
```

You can also import anything from spack in the shell.

#### Build

The main functionality of paks is (drumroll) to build `Pak`s that are then easy to install
in a container, or again into the spack install that comes with Pak. A basic build is going
to generate a build cache with one or more specs of interest. Here is how to build zlib:

```bash
$ paks build zlib
```

By default, a build cache will be created in a temporary directory and the Pak
saved there. This is recommended, as each pak is intended to be modular. If you want
to specify a custom cache (or one that is always used) you can add `--cache-dir`.
You also might want to set a specific gpg key hash to sign with `--key` (otherwise
we will default to the first one we find that is commented for Spack).
When you do a build, it will show you the location of the build cache.

```bash
$ paks build zlib
Preparing to install zlib
linux-ubuntu20.04-skylake
[+] /home/vanessa/Desktop/Code/syspack/paks/paks/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/zlib-1.2.11-3kmnsdv36qxm3slmcyrb326gkghsp6px
==> Pushing binary packages to file:///tmp/paks-tmp.1by0dclj/build_cache
gpg: using "DECA3181DA00313E633F963157BE6A82D830EA34" as default secret key for signing
```

#### Build and Push

If you add `--push` with a GitHub repository (or other OCI registry that supports oras) identifier, we will
use oras to upload there:

```bash
$ paks build zlib --push ghcr.io/syspack/paks
```

By default, the above with `--push` will build, push, and cleanup. You can disable cleanup:

```bash
$ paks build zlib --no-cleanup --push ghcr.io/syspack/paks
```

Or to use the default trusted registry from your settings, just do:

```bash
$ paks build zlib --pushd
```

If you have an existing build cache you want to push:

```bash
$ paks push /tmp/paks-tmp.nudv7k0u/ ghcr.io/syspack/paks
```

Or push and cleanup:

```bash
$ paks push --cleanup /tmp/paks-tmp.nudv7k0u/ ghcr.io/syspack/paks
```

#### Uninstall

You can also uninstall a package.

```bash
$ paks uninstall zlib
```

#### List

List installed packages as follows:

```bash
$ paks list
-- linux-ubuntu20.04-x86_64 / gcc@9.3.0 -------------------------
zlib@1.2.11
```

## TODO

 - create same GitHub actions to perform builds, and across a matrix of arches we will support
 - provide those container bases too
 - provide a paks container that can easily pull from the cache so it's ready to go!
 - from @alecbcs - add "trusted" packages repo (tested, signed, etc.)
 - There is eventually going to be a design flaw in installing this if the user doesn't have write to the install location because of spack. Ug.
 - Can we have a nightly run to compare sboms for package releases to clair?
 - create paks metadata spec for container labels? Also add spack labels to container

## Old Brainstorming

### Paks Organization

On a high level, Stack should be optimized to:

1. Install packages from the Github package caches. This ensures that installation is fast. And since we are optimizing for container installs, we will typically choose a core set of containers to provide binaries for. Since the installs are just downloading binaries, it should also be quick. This means we will need a similar logic / organization to a package install tree as is done with [spack](https://github.com/spack/spack), where packages are installed based on a hash of some kind under a common tree, and can be loaded as such.
2. Build containers.
3. Provide a community framework to empower individuals to build, test, and deploy. This should cut down on maintenance responsibility by some central team.

### stack Client

#### Building Packages

The stack client will be optimized to build packages from source, and this will be done
on GitHub (and likely with a GitHub action). When we are in a repository, that might look like:

```bash
$ stack build .
```

If we are on the command line and want to build a remote repository, that might look like:

```bash
$ stack build github.com/vanessa/salad
```

And then we would require the GitHub repository to provide some basic files for the install.
If we want to keep things in Go, likely it would be a module called package served at the repository:

```bash
package/
  package.go
```

and then a module named accordingly. E.g.,:

```bash
# go.mod
module github.com/username/packagename

go 1.16
```

I think this would be possible if each package was interacted with as a [plugin](https://github.com/vladimirvivien/go-plugin-example)
because then we could download the package to some known root, e.g.,:

```bash
/tmp/stack-install-xndfush
   packagename/
      go.mod
      go.sum
      package/
         package.go
```

And then via the plugin framework define the module as the path there, build an so, and then
load the package to then be built from source. Arguably this could also be done locally,
but it's more optimal to do in advance. There is a good example of using plugins [here](https://github.com/vladimirvivien/go-plugin-example/blob/b5d9c4134805a908c1b1320951cc3dd6d64d851c/greeter.go#L32).


##### Containers

The builds could be done in containers, and thus we would be controlling the architecture
and organization within the container. We could deploy a container, but we would be pushing GitHub
packages and adding them to a container.

1. Can we have a minimal filesystem / container base to install the tool?
2. Then can we grab packages (binaries) that the user wants to add (pre-built)
3. The container base would be akin to any other contianer base (e.g., ubuntu 16.04) and we may want to start with something that already exists
4. A user could easily build their own arch packages (maybe it's represented in the package metadata / arch name)

More abstractly, we want to have a package manager built around GitHub packages.
We can look at ones that already exist to get a better sense of how others do that.

#### Installing Packages

Installation would be straight forward - you would install via a GitHub repository URI:

```bash
$ stack install github.com/usernamename/packagename
```
And I'm thinking we could have an entire org that serves packages, and then they would be provided
in a registry known to stack. Then instead of packagename, if that repository is registered under packagename,
we would just do:

```bash
$ stack install packagename
```

And stack would:

1. Lookup the package in the registry
2. Run the same stack install with the full GitHub URI

During install, we would basically need to match the architecture of the package
to what is requested, and we would provide a reasonable set. This package manager is not 
intended for HPC, it would be intended for installing inside containers.
