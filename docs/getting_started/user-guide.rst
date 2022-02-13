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


And if you want to change a setting on the fly, you can add as many as you need with ``-s``.
For example, we retrieve history assuming a particular user (default is root) and history file (``/root/.bash_history``)
and this might not be the case for your container. This would be using the defaults (no change):

.. code-block:: console
    
    $ paks run -s user=root -s history_file:/root/.bash_history ubuntu 

Notice that we define a separate ``-s`` group for each.
This will take you into a shell where you can interact, and issue Paks commands,
discussed in the next section "Paks Commands."

Env
---

Named environments are stored in ``~/.paks/envs``, and they can be added to and loaded in containers.
but also on the host. You can use the paks command line tool to do this:


.. code-block:: console
    
    # Add GITHUB_TOKEN to the named environment github
    $ paks env add GITHUB_TOKEN=xxxxxxxxxxx github
    GITHUB_TOKEN was added to environment github

    # Remove GITHUB_TOKEN to the named environment github
    $ paks env rm GITHUB_TOKEN=xxxxxxxxxxx github
    GITHUB_TOKEN was removed from environment github

This would create an environment file ``~/.paks/envs/github`` that you could also
manually open up to tweak, or ask paks to open up your editor to tweak:

.. code-block:: console

    $ paks env edit github

You can also quickly show an environment:

.. code-block:: console

    $ paks env show github
    GITHUB_TOKEN=xxxxxxxxxxx


Note that envars can also be added on the fly in containers,
discussed in the next section.


Paks Commands
=============

The following commands can be run from inside a container, e.g., after doing a 
``paks run <container>``. Some of them interact with the host but they don't necessarily
need to.

.. warning::

    Paks commands work by way of ensuring that history is written to file upon container init 
    using ``history -a``. If your container OS doesn't support this you will still be able to run
    Paks commands, but likely not via history (pressing up or down). To retrieve history
    we also assume the history file to be at ``~/root/bash_history`` so if this is
    different for your container, make sure to set ``-s history_file=/path/.history``
    when you paks run.


Save
----

The most useful thing (I think) as a developer that I sometimes want to do is
save my container. This obviously doesn't include mounted volumes, but it does
include changes I've made the filesystem. A save comes down to:

1. Committing the current state
2. Squashing layers to not be in danger of going over the limit.
3. Saving the container with a suffix (e.g., ``-saved``).

So let's say that we do a paks run, and then attempt a save. That might
look like this:

.. code-block:: console

    $ paks run ubuntu
    # touch PANCAKES
    # #save
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


And then you can see that there is an ubuntu-saved container!

.. code-block:: console

    $ docker images | grep ubuntu
    ubuntu-saved                                      latest    93e336d994de   2 minutes ago   72.8MB
    ubuntu                                            latest    54c9d81cbb44   7 days ago      72.8MB

We could change the suffix of the thing saved too, because paks commands accept different kinds of arguments
and key word arguments (kwargs). In this case, the suffix is a keyword:

.. code-block:: console

    $ paks run ubuntu
    # touch PANCAKES
    # #save suffix=-pancakes
    ...
    #5 writing image sha256:6d3b5b27d0b15054eada3159a14c8c1a7fb251e6553adeddc37f54f0cfc9cc33 done
    #5 naming to docker.io/library/ubuntu-pancakes done
    #5 DONE 0.0s

    Untagged: dockerio-ubuntu-rugged-leg-4547-whispering-nunchucks-1604:latest
    Deleted: sha256:e6609a04affa74dd17fc931f1217503207f1b5030d82edaf657d30627511d53c
    Successfully saved container! ⭐️


.. warning::

    Your bash history will be written to ~/.bash_history. This (along with other likely
    precautions) we will need to think about carefully and write up the documentation here.
    For now you should assume that this is for your development purposes only and
    the tool should only be run by a trusted user in an environment he or she owns.


Inspect
-------

If you are forgetting labels or environment, inspect can help! The basic inspect will
dump the entire json to the terminal:

.. code-block:: console

    $ paks run ubuntu
    root@bdda5c133e23:/# #inspect
    Inspecting Container...
    [
        {
            "Id": "bdda5c133e230c70112899c0d9a800d68487884380b441fbd4ce2874b3c91696",
            "Created": "2022-02-10T20:48:51.114405695Z",
            "Path": "/bin/bash",
            "Args": [],
            "State": {
                "Status": "running",
                "Running": true,
                ...
]


That gives you the entire inspection (config, networking, mounts, drivers, etc.) however
you can also ask to see a specific section in entirety:

.. code-block:: console

    $ paks run ubuntu
    root@bdda5c133e23:/# #inspect config

Load
----

**Not implemented yet**

Given a custom set of paks commands (from an external repo or provided as modules in paks) you can load
them into your shell as follows:

.. code-block:: console

    $ paks run ubuntu
    root@bdda5c133e23:/# #load commandgroup


Environment
-----------

Paks will have a suite of commands intended to load, save, and otherwise interact with the environment.
(not implemented yet!). For example, let's say you are in a container and want to save an envar to a named
environment. This will export AND save the environment:

.. code-block:: console

    $ paks run ubuntu
    root@9ec6c3d43591:/# #envsave github GITHUB_USER=dinosaur
    Saving environment variable...
    Successfully added and exported environment variables.
                                                  
    root@9ec6c3d43591:/#  export GITHUB_USER=dinosaur

The above will save your GITHUB_USER to the named environment ``github``, which you can then
load on demand in the same (or another) container. How do you load an environment? Like this:
Notice that the export is written in plain site for you to verify.
Now let's try loading. We originally just had a token, so now we should have
the username "dinosaur" too:

.. code-block:: console

    root@9ec6c3d43591:/# #envload github
    Loading environment...
    Successfully loaded environment github
                                       
    root@9ec6c3d43591:/#  export GITHUB_TOKEN=xxxxxxxxx 
    root@9ec6c3d43591:/#  export GITHUB_USER=dinosaur

Let's now verify the envars are exported to the environment!

.. code-block:: console

    root@9ec6c3d43591:/# env | grep GITHUB
    GITHUB_USER=dinosaur
    GITHUB_TOKEN=xxxxxxxxx

If there is an envar exported in your host environment that you forgot to include?
You can grab it.

.. code-block:: console

    $ export PANCAKES=thebest
    $ paks run ubuntu
    root@71d6d3e92249:/# #envhost PANCAKES
    Getting host environment variable...
    Successfully loaded environment variables.

    root@71d6d3e92249:/# export PANCAKES=thebest
    root@71d6d3e92249:/# env | grep PANCAKES
    PANCAKES=thebest


More coming soon!

 - saving of sboms outside of the container (custom container)
 - and probably more!
