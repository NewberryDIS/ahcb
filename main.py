from fasthtml.common import *
import json
from pathlib import Path
from typing import Dict, Optional

# State names mapping (now the single source of truth)
STATE_NAMES = {
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

# Create FastHTML app without Pico CSS
app, rt = fast_app(
    pico=False,
    hdrs=(
        # Leaflet CSS
        Link(rel="stylesheet", href="/athf/static/css/leaflet.css"),
        # Custom CSS
        Link(rel="stylesheet", href="/athf/static/css/main.css"),
        Link(rel="stylesheet", href="/athf/static/css/map-page.css"),
        Link(rel="stylesheet", href="/athf/static/css/leaflet.mods.css"),
        # High-resolution loading CSS
        Link(rel="stylesheet", href="/athf/static/css/highres-loading.css"),
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


def get_state_name(state_code: str) -> str:
    """Convert state code to full state name"""
    return STATE_NAMES.get(state_code.lower(), state_code.upper())


# Static file serving
@rt("/{fname:path}.{ext:static}")
def static_files(fname: str, ext: str):
    return FileResponse(f"static/{fname}.{ext}")


# Data file serving
@rt("/athf/data/{path:path}")
def data_files(path: str):
    """Serve data files for the atlas"""
    return FileResponse(f"data/{path}")


global_header = (
    Header(
        ft("newberry-logo")(),
        H1(A("Atlas of Historical County Boundaries", href="/athf/", cls="link-lines")),
        Div(
            Div(
                "Go to...",
                Ul(
                    *[
                        Li(A(name, href=f"/athf/{code}"))
                        for code, name in STATE_NAMES.items()
                    ]
                ),
                cls="nav-menu",
            ),
            ft("dark-mode-toggle")(),
            cls="header-right",
        ),
        cls="main-header",
    ),
)


# Home/Index page
@rt("/athf")
def home():
    """Simple home page for the atlas"""
    return Title("Atlas of Historical County Boundaries"), Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Link(rel="stylesheet", href="/athf/static/css/_base.css"),
            Link(rel="stylesheet", href="/athf/static/css/_newberry.css"),
            Link(rel="stylesheet", href="/athf/static/css/main.css"),
        ),
        Body(
            global_header,
            Main(
                Article(
                    H2("Welcome to the Atlas of Historical County Boundaries"),
                    P(
                        "This digital atlas presents the changing boundaries of counties in the United States from their creation to the present day."
                    ),
                    P(A("Browse all state maps", href="/athf/maps", cls="button-link")),
                    cls="home-content",
                )
            ),
            Script(src="/athf/static/js/dark-mode-toggle.js"),
            Script(src="/athf/static/js/newberry-logo.js"),
        ),
    )


@rt("/athf/maps")
def all_maps_page():
    """Display all available state maps"""
    return Title("Atlas of Historical County Boundaries"), Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Link(rel="stylesheet", href="/athf/static/css/leaflet.css"),
            Link(rel="stylesheet", href="/athf/static/css/_base.css"),
            Link(rel="stylesheet", href="/athf/static/css/_newberry.css"),
            Link(rel="stylesheet", href="/athf/static/css/main.css"),
            Link(rel="stylesheet", href="/athf/static/css/all-maps.css"),
        ),
        Body(
            global_header,
            Main(
                Article(
                    Ul(
                        *[
                            Li(
                                A(
                                    H3(name, cls="state-name"),
                                    Img(
                                        src=f"/athf/static/images/pcards/{code}_postcard_bg.webp",
                                        cls="card-img",
                                    ),
                                    Img(
                                        src=f"/athf/static/images/pcards/{code}_postcard_fg.webp",
                                        cls="card-img-name",
                                    ),
                                    href=f"/athf/{code}",
                                ),
                                id=f"state-{code}",  # More specific ID
                                cls="state-postcard",
                                **{"data-state": code},
                            )
                            for code, name in STATE_NAMES.items()
                        ]
                    ),
                    cls="all-maps",
                )
            ),
            Script(src="/athf/static/js/wander.js"),
            Script(src="/athf/static/js/dark-mode-toggle.js"),
            Script(src="/athf/static/js/newberry-logo.js"),
        ),
    )


# Main state page route
@rt("/athf/{state_code}")
def state_page(state_code: str):
    """Display the map page for a specific state"""
    if state_code.lower() not in STATE_NAMES:
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
    return Title(f"{state_name} - Atlas of Historical County Boundaries"), Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Link(rel="stylesheet", href="/athf/static/css/leaflet.css"),
            Link(rel="stylesheet", href="/athf/static/css/_base.css"),
            Link(rel="stylesheet", href="/athf/static/css/_newberry.css"),
            Link(rel="stylesheet", href="/athf/static/css/leaflet-mods.css"),
            Link(rel="stylesheet", href="/athf/static/css/main.css"),
            Link(rel="stylesheet", href="/athf/static/css/map-page.css"),
        ),
        Body(
            global_header,
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
            Script(src="/athf/static/js/dark-mode-toggle.js"),
            Script(src="/athf/static/js/newberry-logo.js"),
            Script(src="/athf/static/js/leaflet.js"),
            Script(src="/athf/static/js/leaflet.timeline.min.js"),
            Script(src="/athf/static/js/map.js"),
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


# Root redirect to atlas home
@rt("/")
def root():
    """Redirect root to atlas home"""
    return RedirectResponse("/athf", status_code=303)


# Handle 404s for invalid athf routes
@rt("/athf/{path:path}")
def athf_404(path: str):
    """Handle 404s for invalid ATHF routes"""
    return Titled(
        "Page Not Found",
        Div(f"'{path}' is not a valid state code", cls="error-message"),
    )


if __name__ == "__main__":
    serve()
