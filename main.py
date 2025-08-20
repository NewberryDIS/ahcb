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
        Script(
            src="https://www.googletagmanager.com/gtag/js?id=G-VXBH4RD619", _async=True
        ),
        Script("""
            window.dataLayer = window.dataLayer || [];
            function gtag() {
              dataLayer.push(arguments);
            }
            gtag("js", new Date());
            gtag("config", "G-VXBH4RD619");

        """),
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
    *c,
    css=(),
    js=(),
    title="Atlas of Historical County Boundaries",
    content=(),
):
    menu_button = Button(
        Div(cls="line line1"),
        Div(cls="line line2"),
        Div(cls="line line3"),
        id="menu-button",
        # onclick="this.classList.toggle('show')",
    )
    return (
        Title(title),
        Head(css),
        Body(
            Div(cls="bg-overlay"),
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
                    Div(ft("dark-mode-toggle")(), cls="dmt-wrapper"),
                    Div(
                        menu_button,
                        Ul(
                            Li(A("About", href=f"/athf/about")),
                            Li(A("Downloads", href=f"/athf/download")),
                            Li(A("All states", href=f"/athf/maps")),
                            *[
                                Li(A(name, href=f"/athf/{code}"))
                                for code, name in STATE_NAMES.items()
                            ],
                        ),
                        cls="nav-menu",
                        id="nav-menu",
                    ),
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
        Script("""
let navMenu;
        """),
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


def lettr(l):
    return Span(l, cls="title-letter")


arrowSvg = """
<svg
   version="1.1"
   id="svg1"
   width="800"
   height="256.66666"
   viewBox="0 0 800 256.66666"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg"
  >
  <defs
     id="defs1" />
  <path
     d="m 251.6511,241.65199 -14.97206,-15.01465 39.32714,-39.3102 c 21.62993,-21.62061 39.32715,-39.76401 39.32715,-40.31867 0,-0.55467 -70.95,-1.00765 -157.66667,-1.00663 L -1.6534882e-8,146.00368 0.39699561,124.6685 0.79399121,103.33333 H 158.06366 c 86.49832,0 157.2692,-0.15 157.26863,-0.33334 -10e-4,-0.43806 -30.2249,-31.53102 -53.10754,-54.635291 L 244.09834,30.062734 259.04326,15.031367 273.98818,2.2105483e-8 336.66091,62.661504 l 62.67274,62.661506 -65.66178,65.67182 c -36.11397,36.1195 -65.97383,65.67182 -66.35524,65.67182 -0.38141,0 -7.43089,-6.75659 -15.66553,-15.01466 z"
     id="path2" />
</svg>
"""


def title_text(words, add_extra=False):
    list_of_words = list(words)
    for i, w in enumerate(list_of_words):
        if w == " ":
            list_of_words[i] = NotStr("&nbsp;")
    # print(f"list of words : {list_of_words}")
    if add_extra:
        # axxaxxa = Div(Div(cls="ax"), Div(cls="xax"), Div(cls="xa"), cls="axxaxxa")
        axxaxxa = Img(src="/athf/static/images/arrow.svg", cls="axxaxxa")
        redbox = (
            A(
                P(
                    Span("maps", cls="redbox-maps-text"),
                    Span("Go to the", cls="md-plus"),
                ),
                Div(cls="bg"),
                NotStr(arrowSvg),
                href="/athf/maps/",
                cls="redbox no-lines",
            ),
        )

        spans = Div(map(lettr, list_of_words), cls="mini-title-container")
        return Div(spans, redbox, cls="extra-title-container")
    else:
        return Div(map(lettr, list_of_words), cls="title-container")


# Home/Index page
@rt("/athf")
def home():
    page_title_text_1 = title_text("Atlas of")
    page_title_text_2 = title_text("Historical")
    page_title_text_3 = title_text("County ", True)
    page_title_text_4 = title_text("Boundaries")
    return BasePage(
        css=(
            # Link(rel="stylesheet", href="/athf/static/css/index.css"),
            Link(rel="stylesheet", href="/athf/static/css/jumbo_v2.css"),
        ),
        content=(
            Article(
                # Img(src="/athf/static/images/jumbo-textonly-rockwell.png"),
                page_title_text_1,
                page_title_text_2,
                page_title_text_3,
                page_title_text_4,
                id="jumbotron",
            ),
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
