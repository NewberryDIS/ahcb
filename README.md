# Historical County Boundaries Website

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
│   ├── dc/                    # Washington DC data
│   │   └── ...
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

Create a `requirements.txt` file:

```txt
fasthtml>=0.6.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
requests>=2.31.0
```

Install dependencies:

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

Copy the CSS and JavaScript code from the artifacts into:

- `static/css/main.css`
- `static/js/map.js`

### 4. Run the Development Server

```bash
python main.py
```

The application will be available at `http://localhost:5001`

Access state pages at: `http://localhost:5001/ahcb/{state_code}`

For example:

- Arizona: `http://localhost:5001/ahcb/az`
- Washington DC: `http://localhost:5001/ahcb/dc`

### 5. Generate Static Site

To create a static version of the site:

```bash
python generate_static.py
```

This will create a `dist/` directory with the complete static site.

Options:

- `--output DIR` - Specify output directory (default: dist)
- `--base-url URL` - Base URL for the app (default: http://localhost:5001)

## Features

### Interactive Map

- **Leaflet.js** integration for map display
- **Leaflet Timeline** for temporal navigation
- Click counties to view detailed information
- Responsive design for mobile and desktop

### Timeline Controls

- Previous/Next buttons for stepping through time
- Play button for animated timeline
- Scrubber bar for direct date selection
- Current date display

### County Information Panel

- Displays county metadata when clicked
- Shows start/end dates, changes, citations
- Responsive sidebar layout

### API Endpoints

- `/api/feature/{state_code}/{feature_id}` - Get detailed feature data
- Serves individual county detail files

## Customization

### Styling

- Modify `static/css/main.css` for visual customization
- Colors, fonts, and layout can be easily adjusted
- Responsive breakpoints included

### Map Behavior

- Edit `static/js/map.js` to modify map interactions
- County coloring algorithm can be customized
- Timeline behavior is configurable

### Data Processing

- The app expects GeoJSON format with specific properties
- Required properties: `START_DATE`, `END_DATE`, `NAME`, `ID`
- Optional properties: `FIPS`, `AREA_SQMI`, `CHANGE`, `CITATION`

## Deployment

### Static Site Deployment

After running the static generator, the `dist/` directory contains a complete static site that can be deployed to:

- GitHub Pages
- Netlify
- Vercel
- Any static file hosting service

### Dynamic Deployment

The FastHTML app can be deployed to platforms supporting Python/ASGI:

- Railway
- Heroku
- DigitalOcean App Platform
- AWS/GCP/Azure

## Browser Support

- Modern browsers with ES6+ support
- Leaflet.js compatibility
- Responsive design for mobile devices

## Performance Considerations

- Preview files are loaded initially for fast rendering
- Detailed county data is loaded on-demand via API
- Timeline processing is optimized for large datasets
- Static generation eliminates server-side processing

## Troubleshooting

### Common Issues

1. **Map not displaying**: Check that Leaflet CSS/JS are loading correctly
2. **Timeline not working**: Ensure Leaflet Timeline extension is loaded
3. **Data not loading**: Verify data file structure and paths
4. **Static generation fails**: Ensure all states have required data files

### Debug Mode

Set `debug=True` in the FastHTML app initialization for detailed error messages.

### Data Validation

Ensure all GeoJSON files are valid and contain required properties. The app will skip states with missing or invalid data files.
