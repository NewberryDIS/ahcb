├── data                                  # data used for development
│   ├── ak
│   │   ├── features
│   │   │   └── ...data files...
│   │   ├── preview_manifest.json
│   │   └── preview.json
│   ├── al
│   │   ├── features
│   │   │   └── ...data files...
│   │   ├── preview_manifest.json
│   │   └── preview.json
│   ├── ...etc 
├── dist                                # output files
│   ├── athf                            # most output is here, since we deploy to a directory 
│   │   ├── about                       # outputs in the "folder/index.html" structure
│   │   │   └── index.html
│   │   ├── ak
│   │   │   └── index.html
│   │   ├── al
│   │   │   └── index.html
│   │   ├── ...etc                      # all the states 
│   │   ├── clear
│   │   │   └── index.html              # HTMX route to delete nodes
│   │   ├── data                        # duplicate of data folder
│   │   │   ├── ak
│   │   │   ├── al
│   │   │   └── ...etc
│   │   ├── dl                          # HTMX routes for download modals
│   │   │   ├── ak
│   │   │   │   └── index.html
│   │   │   ├── al
│   │   │   │   └── index.html
│   │   │   └── ...etc
│   │   ├── download                    # download page
│   │   │   └── index.html
│   │   ├── index.html                  # the real index
│   │   ├── maps                        # all maps list, the one with the postcards
│   │   │   └── index.html
│   │   └── static                      # duplicate of static folder
│   │       ├── css
│   │       ├── fonts
│   │       ├── images
│   │       └── js
│   └── index.html                      # not a real index; just redirects to /athf because I kept going to localhost and forgetting the path
├── generate_static.py                  # I use this for development, but main is fine too
├── main.py
├── md                                  # add more simple pages here
│   ├── about.md
│   └── download.md
├── original_data                       # the data as I received it 
│   ├── AL_full.jsonp                   # files as I got them
│   ├── AL_preview.jsonp                # output files from `simplify_boundaries.py`
│   └── ...etc 
├── README.md
├── requirements.txt
├── simplify_boundaries.py
└── static
    ├── css
    ├── fonts
    ├── images
    │   ├── pcards/
    │   └── ...etc.jpg
    └── js

