from fasthtml.common import *
import json
from pathlib import Path
from typing import Dict, Optional

BASE_PATH = "/athf"
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


app, rt = fast_app(
    pico=False,
    hdrs=(
        MarkdownJS(),
        Meta(charset="utf-8"),
        Meta(name="viewport", content="width=device-width, initial-scale=1"),
        Link(rel="stylesheet", href="/athf/static/css/_base.css"),
        Link(rel="stylesheet", href="/athf/static/css/_newberry.css"),
        Link(rel="stylesheet", href="/athf/static/css/main.css"),
    ),
)


def load_state_data(state_code: str) -> Optional[Dict]:
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
    return STATE_NAMES.get(state_code.lower(), state_code.upper())


def BasePage(
    *c, css=(), js=(), title="Atlas of Historical County Boundaries", content=()
):
    return (
        Title(title),
        Head(css),
        Body(
            Header(
                ft("newberry-logo")(),
                H1(
                    A(
                        "Atlas of Historical County Boundaries",
                        href="/athf/",
                        cls="link-lines",
                    )
                ),
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
                        id="nav-menu",
                    ),
                    ft("dark-mode-toggle")(),
                    cls="header-right",
                ),
                cls="main-header",
            ),
            Main(
                content,
            ),
        ),
        Script(src="/athf/static/js/dark-mode-toggle.js"),
        Script(src="/athf/static/js/newberry-logo.js"),
        Script(src="/athf/static/js/main.js"),
        js,
    )


def head_assets(input=()):
    return ""


# Static file serving
@rt("/{fname:path}.{ext:static}")
def static_files(fname: str, ext: str):
    return FileResponse(f"static/{fname}.{ext}")


# Data file serving
@rt("/athf/data/{path:path}")
def data_files(path: str):
    return FileResponse(f"data/{path}")


# Home/Index page
@rt("/athf")
def home():
    return BasePage(
        css=(Link(rel="stylesheet", href="/athf/static/css/index.css"),),
        content=(
            Article(
                A(
                    H1(
                        "Atlas of Historical County Boundaries",
                        # Span("Atlas of"),
                        # Span("Historical"),
                        # Span("County"),
                        # Span("Boundaries"),
                        id="jumbo",
                    ),
                    href=f"{BASE_PATH}/maps",
                    cls=f"big no-lines",
                ),
                Section(
                    A(
                        H2("About the project"),
                        href=f"{BASE_PATH}/about",
                        cls="small no-lines",
                        id="aboutus",
                    ),
                    A(
                        H2("Download the data"),
                        href=f"{BASE_PATH}/download",
                        cls="small no-lines",
                        id="downloads",
                    ),
                    A(
                        H2("Go to the maps"),
                        href=f"{BASE_PATH}/maps",
                        cls="small no-lines",
                        id="maps",
                    ),
                    cls="smalls",
                ),
                cls="jumbotron",
            ),
            Script("""
                const jumbo = document.getElementById("jumbo");
                if ("undefined" !== jumbo) {
                  const bg = Math.random() - 0.5 > 0 ? "rock" : "styrene";
                  jumbo.classList.add(bg);
                }
            """),
        ),
    )


@rt("/athf/clear")
def clear_htmx_route():
    return ""


with open("./md/about.md") as file:
    aboutMd = file.read()

with open("./md/download.md") as file:
    downloadMd = file.read()


@rt("/athf/about")
def about():
    return BasePage(
        title="About the Atlas of Historical County Boundaries",
        content=(Article(aboutMd, cls="marked text-page")),
    )


@rt("/athf/download")
def download():
    return BasePage(
        title="Download the AHCB data",
        content=(Article(downloadMd, cls="marked text-page")),
    )


@rt("/athf/maps")
def all_maps_page():
    return BasePage(
        title="Atlas of Historical County Boundaries",
        css=(Link(rel="stylesheet", href="/athf/static/css/all-maps.css")),
        js=(
            Script(src="/athf/static/js/wander.js"),
            Script(src="/athf/static/js/main.js"),
        ),
        content=(
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
                        )
                        for code, name in STATE_NAMES.items()
                    ]
                ),
                cls="all-maps",
            )
        ),
    )


# Main state page route
@rt("/athf/{state_code}")
def state_page(state_code: str):
    """Display the map page for a specific state"""

    state_data = load_state_data(state_code.lower())
    state_name = get_state_name(state_code)

    return BasePage(
        title=f"{state_name} - Atlas of Historical County Boundaries",
        css=(
            Link(rel="stylesheet", href="/athf/static/css/leaflet.css"),
            Link(rel="stylesheet", href="/athf/static/css/leaflet-mods.css"),
            Link(rel="stylesheet", href="/athf/static/css/map-page.css"),
            Link(rel="stylesheet", href="/athf/static/css/download-modal.css"),
        ),
        js=(
            Script(f"""
                       // Initialize state variables 
                       const stateCode = '{state_code.lower()}';
                       const stateName = '{state_name}';
                       const previewData = {json.dumps(state_data["preview"])};
                       const manifestData = {json.dumps(state_data["manifest"])};
                       
                   """),
            Script(src="/athf/static/js/leaflet.js"),
            Script(src="/athf/static/js/leaflet.timeline.min.js"),
            Script(src="/athf/static/js/map.js"),
            Script("""
                       // Initialize the map when DOM is loaded
                       document.addEventListener('DOMContentLoaded', function() {{
                           initializeMap(stateCode, stateName, previewData, manifestData);
                       }});
                   """),
        ),
        content=(
            Div(
                # Map container
                Div(id="map", cls="map-container"),
                # Info sidebar
                Aside(
                    H2(state_name),
                    Div(
                        id="infotext",
                    ),
                    Button(
                        "Download data",
                        hx_get=download_state.to(state_code=state_code),
                        hx_target="body",
                        hx_swap="beforeend",
                        id="download-button",
                        cls="ui-button",
                    ),
                    Button(
                        Span("In", cls="inc"),
                        Span("De", cls="dec"),
                        "crease timeline size",
                        id="change-ui-size",
                        cls="ui-button",
                    ),
                    cls="info-sidebar",
                ),
                cls="main-content",
            ),
        ),
    )


@rt("/athf/dl/{state_code}")
def download_state(state_code: str):
    state_name = get_state_name(state_code)
    return (
        Title("Download state data"),
        Div(
            Section(
                H2(f"Download the data for {state_name} in the following formats:"),
                Ul(
                    Li(
                        A(
                            "GIS Files",
                            href=f"/ahcb/download/gis/{state_code.upper()}_AtlasHCB.zip",
                            target="_blank",
                            cls="link-lines",
                        )
                    ),
                    Li(
                        A(
                            "KMZ Files",
                            href=f"/ahcb/download/kmz/{state_code.upper()}_HistCountiesKMZ.zip",
                            target="_blank",
                            cls="link-lines",
                        )
                    ),
                    Li(
                        A(
                            "PDF Files",
                            href=f"/ahcb/download/pdf/{state_code.upper()}_HistCountiesPDF.zip",
                            target="_blank",
                            cls="link-lines",
                        )
                    ),
                ),
                P(
                    "See our",
                    A(
                        "download page",
                        href="/athf/download",
                        cls="link-lines in-text-link",
                    ),
                    "for more information and additional download options.",
                ),
                onclick="event.stopPropagation()",
            ),
            hx_get="/athf/clear",
            hx_swap="outerHTML",
            hx_target="#download-modal",
            id="download-modal",
            cls="download-modal",
        ),
    )


@rt("/")
def root():
    """Redirect root to atlas home"""
    return RedirectResponse("/athf", status_code=303)


# Handle 404s for invalid athf routes
# Since it's a static site, 404s will be handled by apache
@rt("/athf/{path:path}")
def athf_404(path: str):
    """Handle 404s for invalid ATHF routes"""
    return Titled(
        "Page Not Found",
        Div(f"'{path}' is not a valid state code", cls="error-message"),
    )


if __name__ == "__main__":
    serve()
