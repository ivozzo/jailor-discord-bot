#!/bin/bash

version=1.1.0

docker build --build-arg version=${version} . -t ivozzo/jailor-bot:${version}
