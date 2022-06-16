.. image:: https://badge.fury.io/py/web-youtube-dl.svg
    :target: https://badge.fury.io/py/web-youtube-dl
    :alt: PyPi Package

.. image:: https://img.shields.io/pypi/pyversions/web-youtube-dl
    :target: https://pypi.org/project/web-youtube-dl/
    :alt: Compatible Python Versions


About
=====

This is a project that builds on pytube to provide a simple web-interface 
for downloading audio from Youtube. It's primary purpose is to provide a LAN 
HTTP accessible method of saving audio to a local device.

This project is built using python's asyncio libraries and packages include 
FastAPI, janus, and uvicorn. It's also an example of how to work with pytube's 
python sdk and enable asynchronous downloads in the context of a web-app. 

Files are downloaded using an API endpoint and then retrived from the application's 
static files directory using Javascript's fetch API. Download progress is presented 
via a websocket connection.


Installation
============

.. code-block:: bash

    pip install web-youtube-dl


Running
=======

CLI
---

Installing this project will give you access to two CLI tools, each with a
separate purpose:

* | **web-youtube-dl-cli**
  | Useful for simply downloading the highest possible quality audio of a song. 
  | Simply provide the URL and an .mp3 will be downloaded to current working
  | directory or to the value of the *YT_DOWNLOAD_PATH* environment variable 

* | **web-youtube-dl-web**
  |  Useful for running the web service on the local machine. It will 
  |  listen to all local network connections on port 5000 (or whatever port is
  |  defined in the environment variable *YT_DOWNLOAD_PORT*).


Docker
------

This project can optionally be run and managed as a Docker container.

Build the Docker image
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    docker build . -t  web-youtube-dl:latest --force-rm

Or, using the project's Makefile

.. code-block:: bash

    make image

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

Or, using the project's Makefile

.. code-block:: bash

    make compose

Enhancements
^^^^^^^^^^^^
Track progress beyond YT download
- tie into ffmpeg
- tie into metadata extraction