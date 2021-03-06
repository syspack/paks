.. _getting_started-settings:

========
Settings
========

Most defaults should work without changing, however you will likely want to customize 
settings in the case that you are a developer.

Updating Settings
=================

To change defaults you can either edit the settings.yml file in the installation directory
at ``paks/settings.yml`` or create a user-specific configuration by doing:


.. code-block:: console

    $ paks config init
    Created user settings file /home/vanessa/.paks/settings.yml


You can then change a setting, such as the username and email for your gpg key (used to sign
the build cache artifacts):


.. code-block:: console

    $ paks config set username=dinosaur
    Updated username to be dinosaur
    $ paks config set email=dinosaur@users.noreply.github.io
    Updated email to be dinosaur@users.noreply.github.io


These user settings will over-ride the default installation ones.

Settings Table
==============

The following variables can be configured in your user settings:

.. list-table:: Title
   :widths: 25 65 10
   :header-rows: 1

   * - Name
     - Description
     - Default
   * - container_tech
     - The container technology to use (docker or podman)
     - Defaults to ``docker``
   * - username
     - A username to use to sign packages (only required when using build)
     - Defaults to your ``$USER``
   * - email
     - An email to use to sign packages (only required when using build)
     - Defaults to ``$USER@users.noreply.spack.io``
   * - trusted_packages_org
     - The trusted packages GitHub organization to install from
     - pakages
   * - trusted_packages_registry
     - The default trusted packages GitHub organization to push to. If no push registries are provided, we fallback to push here.
     - ghcr.io/pakages
   * - trusted_pull_registries
     - One or more registries to pull from.
     - [ghcr.io/pakages]
   * - cache_dir
     - A default cache directory to use - will only be cleaned up for build using ``--force``
     - unset
   * - default_tag
     - The default tag to use to push artifacts.
     - latest
   * - content_type
     - The default content type for the spack package (not recommended to change)
     - application/vnd.spack.package

