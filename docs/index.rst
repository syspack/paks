.. _manual-main:

====
Paks
====

.. image:: https://img.shields.io/github/stars/syspack/paks?style=social
    :alt: GitHub stars
    :target: https://github.com/syspack/paks/stargazers

Paks is a community framework for container interactions 📦️

Paks provides a core set of commands to help you manage your container state or 
get quick access to metadata without leaving your development environment.
It is similar to `syspack/pack <https://github.com/syspack/paks>`_, but implemented in a different
language, intentionally to allow for contribution from the larger scientific community that 
embraces Python. With Paks you can:

 - quickly ``#save`` your development container while you are shelled into it working.
 - develop or use custom recipes or actions for your containers.
 
You can see different recipes for interactions under the `pakages <https://github.com/pakages>`_ organization.

.. _main-goals:

-----
Goals
-----

If you are a developer, paks is a framework that makes it easy for you to develop with containers
without needing to leave your container.

To see the code, head over to the `repository <https://github.com/syspack/paks/>`_.

.. _main-getting-started:

-------------------------
Getting started with Paks
-------------------------

Paks can be installed from pypi or directly from the repository. See :ref:`getting_started-installation` for
installation, and then the :ref:`getting-started` section for using paks on the command line or 
from a provided base container.

.. _main-support:

-------
Support
-------

* For **bugs and feature requests**, please use the `issue tracker <https://github.com/syspack/paks/issues>`_.
* For **contributions**, visit Spliced on `Github <https://github.com/syspack/paks>`_.

---------
Resources
---------

`GitHub Repository <https://github.com/syspack/paks>`_
    The code on GitHub.


.. toctree::
   :caption: Getting started
   :name: getting_started
   :hidden:
   :maxdepth: 2

   getting_started/index
   getting_started/user-guide
   getting_started/developer-guide

.. toctree::
    :caption: API Reference
    :name: api-reference
    :hidden:
    :maxdepth: 1

    api_reference/paks
    api_reference/internal/modules
