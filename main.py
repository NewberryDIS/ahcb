from fasthtml.common import *
import json
from pathlib import Path
from typing import Dict, List, Optional

# US state codes for validation
US_STATES = {
    "al",
    "ak",
    "az",
    "ar",
    "ca",
    "co",
    "ct",
    "de",
    "dt",
    "fl",
    "ga",
    "hi",
    "id",
    "il",
    "in",
    "ia",
    "ks",
    "ky",
    "la",
    "me",
    "md",
    "ma",
    "mi",
    "mn",
    "ms",
    "mo",
    "mt",
    "ne",
    "nv",
    "nh",
    "nj",
    "nm",
    "ny",
    "nc",
    "nd",
    "oh",
    "ok",
    "or",
    "pa",
    "ri",
    "sc",
    "sd",
    "tn",
    "tx",
    "ut",
    "vt",
    "va",
    "wa",
    "wv",
    "wi",
    "wy",
    "dc",
}

# Create FastHTML app without Pico CSS
app, rt = fast_app(
    pico=False,
    hdrs=(
        # Leaflet CSS
        Link(rel="stylesheet", href="/static/css/leaflet.css"),
        # Custom CSS
        Link(rel="stylesheet", href="/static/css/main.css"),
        Link(rel="stylesheet", href="/static/css/leaflet.mods.css"),
        # High-resolution loading CSS
        Link(rel="stylesheet", href="/static/css/highres-loading.css"),
    ),
)


def load_state_data(state_code: str) -> Optional[Dict]:
    """Load state data from JSON files"""
    data_dir = Path(f"data/{state_code}")

    if not data_dir.exists():
        return None

    try:
        # Load preview data
        with open(data_dir / "preview.json", "r") as f:
            preview_data = json.load(f)

        # Load features manifest
        with open(data_dir / "features_manifest.json", "r") as f:
            manifest = json.load(f)

        return {
            "preview": preview_data,
            "manifest": manifest,
            "state_code": state_code.upper(),
        }
    except (FileNotFoundError, json.JSONDecodeError):
        return None


state_names = {
    "al": "Alabama",
    "ak": "Alaska",
    "az": "Arizona",
    "ar": "Arkansas",
    "ca": "California",
    "co": "Colorado",
    "ct": "Connecticut",
    "de": "Delaware",
    "dt": "Dakota Territory",
    "fl": "Florida",
    "ga": "Georgia",
    "hi": "Hawaii",
    "id": "Idaho",
    "il": "Illinois",
    "in": "Indiana",
    "ia": "Iowa",
    "ks": "Kansas",
    "ky": "Kentucky",
    "la": "Louisiana",
    "me": "Maine",
    "md": "Maryland",
    "ma": "Massachusetts",
    "mi": "Michigan",
    "mn": "Minnesota",
    "ms": "Mississippi",
    "mo": "Missouri",
    "mt": "Montana",
    "ne": "Nebraska",
    "nv": "Nevada",
    "nh": "New Hampshire",
    "nj": "New Jersey",
    "nm": "New Mexico",
    "ny": "New York",
    "nc": "North Carolina",
    "nd": "North Dakota",
    "oh": "Ohio",
    "ok": "Oklahoma",
    "or": "Oregon",
    "pa": "Pennsylvania",
    "ri": "Rhode Island",
    "sc": "South Carolina",
    "sd": "South Dakota",
    "tn": "Tennessee",
    "tx": "Texas",
    "ut": "Utah",
    "vt": "Vermont",
    "va": "Virginia",
    "wa": "Washington",
    "wv": "West Virginia",
    "wi": "Wisconsin",
    "wy": "Wyoming",
    "dc": "District of Columbia",
}


def get_state_name(state_code: str) -> str:
    """Convert state code to full state name"""
    return state_names.get(state_code.lower(), state_code.upper())


# Static file serving
@rt("/{fname:path}.{ext:static}")
def static_files(fname: str, ext: str):
    return FileResponse(f"static/{fname}.{ext}")


# API endpoint for feature details
@rt("/api/feature/{state_code}/{feature_id}")
def get_feature_detail(state_code: str, feature_id: str):
    """API endpoint to get detailed feature data"""
    if state_code.lower() not in US_STATES:
        return JSONResponse({"error": "Invalid state code"}, status_code=404)

    feature_path = Path(f"data/{state_code.lower()}/features/{feature_id}.json")

    if not feature_path.exists():
        return JSONResponse({"error": "Feature not found"}, status_code=404)

    try:
        with open(feature_path, "r") as f:
            feature_data = json.load(f)
        return JSONResponse(feature_data)
    except json.JSONDecodeError:
        return JSONResponse({"error": "Invalid feature data"}, status_code=500)


# API endpoint to get multiple features at once (for high-res loading optimization)
@rt("/api/features/{state_code}/batch", methods=["POST"])
async def get_features_batch(state_code: str, request):
    """API endpoint to get multiple feature details in one request"""
    if state_code.lower() not in US_STATES:
        return JSONResponse({"error": "Invalid state code"}, status_code=404)

    try:
        body = await request.json()
        feature_ids = body.get("feature_ids", [])

        if not feature_ids or len(feature_ids) > 50:  # Limit batch size
            return JSONResponse(
                {"error": "Invalid feature_ids list (max 50)"}, status_code=400
            )

        features = {}
        for feature_id in feature_ids:
            feature_path = Path(f"data/{state_code.lower()}/features/{feature_id}.json")
            if feature_path.exists():
                try:
                    with open(feature_path, "r") as f:
                        features[feature_id] = json.load(f)
                except json.JSONDecodeError:
                    continue  # Skip invalid files

        return JSONResponse({"features": features})

    except Exception as e:
        return JSONResponse({"error": "Invalid request"}, status_code=400)


@rt("/ahcb/maps")
def all_maps_page():
    # Create the page structure
    return Title("Altas of Historical County Boundaries"), Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Link(rel="stylesheet", href="/static/css/leaflet.css"),
            Link(rel="stylesheet", href="/static/css/_base.css"),
            Link(rel="stylesheet", href="/static/css/_newberry.css"),
            Link(rel="stylesheet", href="/static/css/main.css"),
            Link(rel="stylesheet", href="/static/css/all-maps.css"),
        ),
        Body(
            Header(
                ft("newberry-logo")(),
                H1("Atlas of Historical County Boundaries"),
                Div(
                    Div(
                        Span("Go to..."),
                        Ul(
                            *[
                                Li(A(name, href=f"/ahcb/{code}"))
                                for code, name in state_names.items()
                            ]
                        ),
                        cls="nav-menu",
                    ),
                    ft("dark-mode-toggle")(),
                    cls="header-right",
                ),
                cls="main-header",
            ),
            Main(
                Article(
                    Ul(
                        *[
                            Li(
                                A(
                                    H3(name, cls="state-name"),
                                    Img(
                                        src=f"/static/images/pcards/{code}_postcard.jpg",
                                        cls="card-img",
                                    ),
                                    Img(
                                        src=f"/static/images/pcards/{code}_postcard.png",
                                        cls="card-img-name",
                                    ),
                                    href=f"/ahcb/{code}",
                                ),
                                cls="state-postcard",
                            )
                            for code, name in state_names.items()
                        ]
                    ),
                    cls="all-maps",
                )
            ),
            Script(src="/static/js/dark-mode-toggle.js"),
            Script(src="/static/js/newberry-logo.js"),
        ),
    )


# Main state page route
@rt("/ahcb/{state_code}")
def state_page(state_code: str):
    """Display the map page for a specific state"""
    if state_code.lower() not in US_STATES:
        return Titled("Page Not Found", Div("State not found", cls="error-message"))

    state_data = load_state_data(state_code.lower())
    if not state_data:
        return Titled(
            "Data Not Found",
            Div(
                f"No data available for {get_state_name(state_code)}",
                cls="error-message",
            ),
        )

    state_name = get_state_name(state_code)

    # Create the page structure
    return Title(f"{state_name} - Altas of Historical County Boundaries"), Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Link(rel="stylesheet", href="/static/css/leaflet.css"),
            Link(rel="stylesheet", href="/static/css/_base.css"),
            Link(rel="stylesheet", href="/static/css/_newberry.css"),
            Link(rel="stylesheet", href="/static/css/leaflet-mods.css"),
            Link(rel="stylesheet", href="/static/css/main.css"),
            Link(rel="stylesheet", href="/static/css/map-page.css"),
            Link(rel="stylesheet", href="/static/css/highres-loading.css"),
        ),
        Body(
            Header(
                ft("newberry-logo")(),
                H1("Atlas of Historical County Boundaries"),
                Div(
                    Div(
                        "Go to...",
                        Ul(
                            *[
                                Li(A(name, href=f"/ahcb/{code}"))
                                for code, name in state_names.items()
                            ]
                        ),
                        cls="nav-menu",
                    ),
                    ft("dark-mode-toggle")(),
                    cls="header-right",
                ),
                cls="main-header",
            ),
            Main(
                Div(
                    # Map container
                    Div(id="map", cls="map-container"),
                    # Info sidebar
                    Aside(
                        H2(state_name),
                        Div(
                            id="infotext",
                        ),
                        cls="info-sidebar",
                    ),
                    cls="main-content",
                ),
                # Timeline controls container
            ),
            # JavaScript files and initialization
            Script(src="/static/js/dark-mode-toggle.js"),
            Script(src="/static/js/newberry-logo.js"),
            Script(src="/static/js/leaflet.js"),
            Script(src="/static/js/leaflet.timeline.min.js"),
            Script(src="/static/js/map.js"),
            Script(f"""
                       // Initialize map with state data
                       const stateCode = '{state_code.lower()}';
                       const stateName = '{state_name}';
                       const previewData = {json.dumps(state_data["preview"])};
                       const manifestData = {json.dumps(state_data["manifest"])};
                       
                       // Initialize the map when DOM is loaded
                       document.addEventListener('DOMContentLoaded', function() {{
                           initializeMap(stateCode, stateName, previewData, manifestData);
                       }});
                   """),
        ),
    )


# Root redirect
@rt("/")
def home():
    """Redirect root to a default state or show state list"""
    return RedirectResponse("/ahcb/maps", status_code=303)


# Handle 404s for invalid ahcb routes
@rt("/ahcb/{path:path}")
def ahcb_404(path: str):
    """Handle 404s for invalid AHCB routes"""
    return Titled(
        "Page Not Found",
        Div(f"'{path}' is not a valid state code", cls="error-message"),
    )


if __name__ == "__main__":
    serve()
