.. image:: https://badge.fury.io/py/web-youtube-dl.svg
    :target: https://badge.fury.io/py/web-youtube-dl
    :alt: PyPi Package

.. image:: https://img.shields.io/pypi/pyversions/web-youtube-dl
    :target: https://pypi.org/project/web-youtube-dl/
    :alt: Compatible Python Versions


Issues
======

Backend issues if a single user hits submit multiple times
  - "raise RuntimeError("Response content longer than Content-Length")"

Installation
============

.. code-block:: bash

    pip install <>


Running
=======

CLI
---

Installing this project will give you access to two CLI tools, each with a separate 
purpose:

* | **web-youtube-dl-cli**
  |  Useful for simply downloading the highest possible quality 
  | audio of a song. Simply provide the URL and an .mp3 will be downloaded to that 
  | same directory

* | **web-youtube-dl**
  |  Useful for running the web service on the local machine. It will 
  |  listen to all local network connections on port 5000 (or whatever port is defined 
  |  in the environment variable *YT_DOWNLOAD_PORT*).


Docker
------

This project can optionally be run and managed as a Docker container.

Build the Docker image
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    docker build . -t  web-youtube-dl:latest --force-rm

Run the service
^^^^^^^^^^^^^^^

When running the service via Docker, you can configure where it stores downloaded 
songs by default and the port the service listens on by setting the appropriate 
environment variables.

To configure the port, set the environment variable *YT_DOWNLOAD_PORT* to some 
other numerical value.

To configure the download path, set the environment variable *YT_DOWNLOAD_PATH* 
to some other filesystem path. Note that an unprivileged user must have access 
to writing to this location. By default, this is set to *tmp* and does not 
really need to be changed.

.. code-block:: bash

    docker-compose up -d