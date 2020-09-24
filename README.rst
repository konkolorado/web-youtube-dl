TODO
==== 

what happens if a user hits submit multiple times??
    multiple downloads for same url results in "raise RuntimeError("Response content longer than Content-Length")"

Need a couple of ways to detect if youtubedl will download anything
Need to make sure requests to /download/{filename} get sanitized


Running
=======

CLI

Docker
^^^^^^

This project can optionally be run and managed as a Docker container.

Build the Docker image
^^^^^^^^^^^^^^^^^^^^^^

docker build . -t  web-youtube-dl:latest --force-rm

Run the service
^^^^^^^^^^^^^^^

docker-compose up -d