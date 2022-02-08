.. _getting_started-user-guide:

==========
User Guide
==========

Paks provides basic functionality to run interactive commands in container environments.
If you haven't installed Paks yet you should read :ref:`getting_started-installation` first. If you want to tweak
settings, read :ref:`getting_started-settings`.

Quick Start
===========

After installation, if you want user-level control over Paks settings (discussed next) you should create your own copy of the config file.

.. code-block:: console

    # Init your user config
    $ paks config init

This will create a ``$HOME/.paks/settings.yml`` that you can customize to override
the defaults. To quickly edit:

.. code-block:: console

    $ paks config edit

The settings will let you choose your container technology and other features of paks.
Browse :ref:`getting_started-settings` and ensure the settings are to your liking before continuing.
If you are looking to develop your own container interactions to share with others, see
the :ref:`getting_started-developer-guide`.


Commands
========

Paks provides the following commands via the ``paks`` command line client.

Run
---

The most basic functionality is to run a container with paks, meaning that you get an interactive
environment with Paks commands supported. That looks like this:

.. code-block:: console
    
    $ paks run ubuntu


By default, we will use the shell defined in your config, but you can one-off this
if needed:

.. code-block:: console
    
    $ paks run --shell /bin/sh busybox


Or the container backend:

.. code-block:: console
    
    $ paks run --container-tech podman busybox


This will take you into a shell where you can interact! For example, here is a save:

.. code-block:: console

    / # #save
    Saving container...
    sha256:d82aaa268feb59344cf31a757ce7f5c0caa6a6bbd10b8d0af1d55cdbc50b609b 
    [+] Building 0.2s (5/5) FINISHED                                                                            
    ...
    => => writing image sha256:f58ae524d8644400b33c078f19612cba7849ef8f3ea158e2291ac697a4129080
    => => naming to docker.io/library/busybox-saved
    Untagged: dockerio-busybox-joyous-hippo-3922-gloopy-peanut-9044:latest
    Deleted: sha256:d82aaa268feb59344cf31a757ce7f5c0caa6a6bbd10b8d0af1d55cdbc50b609b
    Deleted: sha256:f58ae524d8644400b33c078f19612cba7849ef8f3ea158e2291ac697a4129080
    Successfully saved container! ⭐️
    #save

The main issue now is that tab and arrows won't work, I haven't found a solution that works well
for this yet. The only promising one was pynput but I couldn't control logging to a single terminal
window (e.g., it's going to keylog you everywhere!)
