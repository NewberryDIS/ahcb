#!/usr/bin/env python3
"""
Static Site Generator for Historical County Boundaries

This script "cooks down" the FastHTML application into a static site
by pre-generating all the HTML pages and copying necessary assets.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import requests
from urllib.parse import urljoin

# Import the FastHTML app
from main import app, US_STATES, load_state_data, get_state_name


class StaticSiteGenerator:
    def __init__(
        self, output_dir: str = "dist", base_url: str = "http://localhost:5001"
    ):
        self.output_dir = Path(output_dir)
        self.base_url = base_url
        self.static_dir = self.output_dir / "static"

    def generate(self):
        """Generate the complete static site"""
        print("Starting static site generation...")

        # Clean and create output directory
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Copy static assets
        self.copy_static_assets()

        # Copy data files
        self.copy_data_files()

        # Generate state pages
        self.generate_state_pages()

        # Generate index redirect
        self.generate_index()

        # Generate 404 page
        self.generate_404()

        print(f"Static site generated successfully in '{self.output_dir}'")

    def copy_static_assets(self):
        """Copy CSS, JS, and other static assets"""
        print("Copying static assets...")

        source_static = Path("static")
        if source_static.exists():
            shutil.copytree(source_static, self.static_dir, dirs_exist_ok=True)
        else:
            # Create directories if they don't exist
            (self.static_dir / "css").mkdir(parents=True, exist_ok=True)
            (self.static_dir / "js").mkdir(parents=True, exist_ok=True)

            # Copy CSS and JS files from artifacts if they exist
            # In a real scenario, you would have these files in your static directory
            print(
                "Note: Create static/css/main.css and static/js/map.js from the artifacts"
            )

    def copy_data_files(self):
        """Copy data files to output directory"""
        print("Copying data files...")

        data_source = Path("data")
        data_dest = self.output_dir / "data"

        if data_source.exists():
            shutil.copytree(data_source, data_dest, dirs_exist_ok=True)
        else:
            print("Warning: data directory not found")

    def generate_state_pages(self):
        """Generate HTML pages for each state"""
        print("Generating state pages...")

        # Create ahcb directory
        ahcb_dir = self.output_dir / "ahcb"
        ahcb_dir.mkdir(exist_ok=True)

        for state_code in US_STATES:
            state_data = load_state_data(state_code)
            if state_data:
                self.generate_state_page(state_code, state_data, ahcb_dir)
            else:
                print(f"Warning: No data found for state {state_code}")

    def generate_state_page(self, state_code: str, state_data: Dict, ahcb_dir: Path):
        """Generate HTML page for a specific state"""
        state_name = get_state_name(state_code)
        print(f"Generating page for {state_name} ({state_code})")

        # Create the HTML content
        html_content = self.create_static_html(state_code, state_name, state_data)

        # Write to file
        output_file = ahcb_dir / f"{state_code}.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

    def create_static_html(
        self, state_code: str, state_name: str, state_data: Dict
    ) -> str:
        """Create static HTML content for a state page"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Historical County Boundaries - {state_name}</title>
    
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="../static/css/leaflet.css">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="../static/css/main.css">
</head>
<body>
    <header class="main-header">
        <h1>{state_name} Historical County Boundaries</h1>
    </header>
    
    <main>
        <div class="main-content">
            <!-- Map container -->
            <div id="map" class="map-container"></div>
            
            <!-- Info sidebar -->
            <aside class="info-sidebar">
                <h2>County Information</h2>
                <div id="infotext">
                    <p class="placeholder-text">Click on a county to view details</p>
                </div>
            </aside>
        </div>
        
        <!-- Timeline controls container -->
        <div class="timeline-container">
            <div id="timeline-controls" class="timeline-controls"></div>
        </div>
    </main>
    
    <!-- JavaScript files -->
    <script src="../static/js/leaflet.js"></script>
    <script src="../static/js/leaflet.timeline.js"></script>
    <script src="../static/js/map.js"></script>
    
    <!-- Initialize map with state data -->
    <script>
        // State data
        const stateCode = '{state_code}';
        const stateName = '{state_name}';
        const previewData = {json.dumps(state_data["preview"])};
        const manifestData = {json.dumps(state_data["manifest"])};
        
        // API endpoint for detailed features (static version)
        async function loadDetailedFeature(featureId) {{
            const manifestFeature = manifestData.features[featureId];
            if (!manifestFeature) return;
            
            try {{
                const response = await fetch(`../data/${{stateCode}}/features/${{manifestFeature.filename}}`);
                if (response.ok) {{
                    const detailedData = await response.json();
                    console.log('Loaded detailed feature data:', detailedData);
                    return detailedData;
                }}
            }} catch (error) {{
                console.error('Error loading detailed feature data:', error);
            }}
            return null;
        }}
        
        // Initialize the map when DOM is loaded
        document.addEventListener('DOMContentLoaded', function() {{
            initializeMap(stateCode, stateName, previewData, manifestData);
        }});
    </script>
</body>
</html>"""

    def generate_index(self):
        """Generate index.html that redirects to Arizona"""
        index_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="0; url=ahcb/az.html">
    <title>Historical County Boundaries - Redirecting...</title>
</head>
<body>
    <p>Redirecting to <a href="ahcb/az.html">Arizona Historical County Boundaries</a>...</p>
    <script>
        window.location.href = 'ahcb/az.html';
    </script>
</body>
</html>"""

        with open(self.output_dir / "index.html", "w") as f:
            f.write(index_content)

    def generate_404(self):
        """Generate 404 error page"""
        error_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Page Not Found - Historical County Boundaries</title>
    <link rel="stylesheet" href="static/css/main.css">
</head>
<body>
    <header class="main-header">
        <h1>Historical County Boundaries</h1>
    </header>
    
    <main style="padding: 2rem;">
        <div class="error-message">
            <h2>Page Not Found</h2>
            <p>The page you're looking for doesn't exist.</p>
            <p><a href="ahcb/az.html" style="color: white; text-decoration: underline;">Return to Arizona</a></p>
        </div>
    </main>
</body>
</html>"""

        with open(self.output_dir / "404.html", "w") as f:
            f.write(error_content)

    def create_state_list_page(self):
        """Create a page listing all available states (optional)"""
        states_with_data = []
        for state_code in US_STATES:
            if Path(f"data/{state_code}").exists():
                states_with_data.append((state_code, get_state_name(state_code)))

        states_html = ""
        for state_code, state_name in sorted(states_with_data, key=lambda x: x[1]):
            states_html += (
                f'<li><a href="ahcb/{state_code}.html">{state_name}</a></li>\n'
            )

        list_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Historical County Boundaries - State List</title>
    <link rel="stylesheet" href="static/css/main.css">
</head>
<body>
    <header class="main-header">
        <h1>Historical County Boundaries</h1>
    </header>
    
    <main style="padding: 2rem;">
        <h2>Available States</h2>
        <ul style="columns: 3; list-style: none; padding: 0;">
            {states_html}
        </ul>
    </main>
</body>
</html>"""

        with open(self.output_dir / "states.html", "w") as f:
            f.write(list_content)


def main():
    """Main function to run the static site generator"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate static site from FastHTML app"
    )
    parser.add_argument(
        "--output", "-o", default="dist", help="Output directory (default: dist)"
    )
    parser.add_argument(
        "--base-url", default="http://localhost:5001", help="Base URL for the app"
    )

    args = parser.parse_args()

    generator = StaticSiteGenerator(args.output, args.base_url)
    generator.generate()


if __name__ == "__main__":
    main()
