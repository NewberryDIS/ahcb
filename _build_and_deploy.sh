#!/bin/zsh
python generate_static.py --build-only && rsync -avz dist/athf/ $RSRVR51/domains/publications.newberry.org/athf/
