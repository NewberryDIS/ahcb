# Atlas of Historical County Boundaries

A FastHTML application for displaying interactive maps of historical county boundaries for US states.

## Project Structure

```
project/
├── main.py                     # Main FastHTML application
├── generate_static.py          # Static site generator script
├── requirements.txt            # Python dependencies
├── static/                     # Static assets
│   ├── css/
│   │   └── main.css           # Main stylesheet
│   └── js/
│       └── map.js             # Map functionality JavaScript
├── data/                       # County boundary data
│   ├── az/                    # Arizona data
│   │   ├── preview.json
│   │   ├── features_manifest.json
│   │   └── features/
│   │       ├── {feature_id}.json
│   │       └── ...
│   └── ...                    # Other states
└── dist/                      # Generated static site (created by generator)
    ├── index.html
    ├── 404.html
    ├── states.html
    ├── ahcb/
    │   ├── az.html
    │   ├── dc.html
    │   └── ...
    ├── static/
    │   ├── css/
    │   └── js/
    └── data/
        └── ...
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Data Files

Ensure your data directory structure matches the expected format:

- Each state should have a folder named with its 2-letter code (lowercase)
- Each state folder should contain:
  - `preview.json` - Simplified county boundaries for initial display
  - `features_manifest.json` - Mapping of features to detailed files
  - `features/` directory with individual county detail files

### 3. Create Static Assets

Create the directory structure:

```bash
mkdir -p static/css static/js
```

### 4. Run the Development Server

```bash
python main.py
```

The application will be available at `http://localhost:5001`

### 5. Generate Static Site

To create a static version of the site:

```bash
python generate_static.py
```

This will create a `dist/` directory with the complete static site.

Options:

- `--clean` - Delete all contents of output directory and copy fresh (default: False)
- `--build-only` - Build the site to the output directory but do not run server afterwards (default: False)
- `--output DIR` - Specify output directory (default: dist)
- `--base-url URL` - Base URL for the app (default: <http://localhost:5001>)

## Additional Scripts

- `simplify_boundaries.py`
  - Creates the "\_preview" versions of the files. Takes jsonp as input but you can change that.
- `data-cleaner.py`
  - Expects files similar to the output of `simplify_boundaries.py` and:
    - removes fields not used by the site
    - creates individual "feature" files for all high-resolution features for each state
    - creates a mapping file since the original data does not have unique ids for layers
- `_build_and_deploy.sh`
  - Builds and rsyncs the output to our server.

## Features

### Interactive Map

- **Leaflet.js** integration for map display
- **Leaflet Timeline** for temporal navigation
- Click counties to view detailed information

### Timeline Controls

- Previous/Next buttons for stepping through time
- Play button for animated timeline
- Scrubber bar for direct date selection
- URL query parameter handling: use ?date=YYYY-MM-DD to link directly to a date

### County Information Panel

- Displays county metadata when clicked
- Shows start/end dates, changes, citations

## Customization

### Map Behavior

- Edit `static/js/map.js` to modify map interactions
- Standard Leaflet and Leaflet.Timeline options are accessible
- Feature colors are set in JavaScript using CSS variables

### Data Processing

- The app expects GeoJSON format with specific properties
- Required properties: `START_DATE`, `END_DATE`, `NAME`, `ID`

## Deployment

### Static Site Deployment

After running the static generator, the `dist/` directory contains a complete static site that can be deployed wherever you might normally do so.

## Browser Support

- All modern browsers with ES6+ are supported
- Requires Leaflet.js compatibility

## Performance Considerations

- Preview files are loaded initially for fast rendering
- Detailed county data is loaded on-demand via API
- Timeline processing is optimized for large datasets
- Static generation eliminates server-side processing

## Troubleshooting

### Debug Mode

Set `debug=True` in the FastHTML app initialization for detailed error messages.

### Data Validation

Ensure all GeoJSON files are valid and contain required properties. The app will skip states with missing or invalid data files.
