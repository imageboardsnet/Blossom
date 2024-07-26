# Blossom

This software is designed to provide an easy-to-navigate management list for imageboards.
 Built on a Flask stack, Blossom runs in a Docker container.
This project is dedicated to the website imageboards.net, but feel free to reuse it.

## Features

 - User-friendly Interface: Simplifies the management of imageboards.
 
 - Efficient Organization: Categorizes and arranges imageboards   
   effectively.
   
 - Secure & Scalable: Utilizes Docker for a secure environment.
 
 - Flask Backend: Offers a robust and flexible backend with Flask.

## Installation instruction

Pull the repo

    git pull https://github.com/imageboardsnet/Blossom.git

Run it with Docker

    docker compose build
    docker compose up -d
*Default port 7070*

Run it locally

    pip install -r requirements.txt
    python app.py
*Default port 5000*
