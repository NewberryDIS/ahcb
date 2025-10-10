from fasthtml.common import *
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

BASE_PATH = "/ahcb"
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
        Link(rel="stylesheet", href="/ahcb/static/css/_base.css"),
        Link(rel="stylesheet", href="/ahcb/static/css/_newberry.css"),
        Link(rel="stylesheet", href="/ahcb/static/css/main.css"),
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

# cli = Client(app)


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
        Head(css, Title(title)),
        Body(
            Div(cls="bg-overlay"),
            Header(
                ft("newberry-logo")(),
                H1(
                    A(
                        "Atlas of Historical County Boundaries",
                        href="/ahcb/",
                        cls="link-lines",
                    )
                ),
                Div(
                    Div(ft("dark-mode-toggle")(), cls="dmt-wrapper"),
                    Div(
                        menu_button,
                        Ul(
                            Li(A("About", href=f"/ahcb/about")),
                            Li(A("Downloads", href=f"/ahcb/download")),
                            Li(A("All states", href=f"/ahcb/maps")),
                            *[
                                Li(A(name, href=f"/ahcb/{code}"))
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
        Script(src="/ahcb/static/js/dark-mode-toggle.js"),
        Script(src="/ahcb/static/js/newberry-logo.js"),
        Script(src="/ahcb/static/js/main.js"),
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
@rt("/ahcb/data/{path:path}")
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
        axxaxxa = Img(src="/ahcb/static/images/arrow.svg", cls="axxaxxa")
        redbox = (
            A(
                P(
                    Span("maps", cls="redbox-maps-text"),
                    Span("Go to the", cls="md-plus"),
                ),
                Div(cls="bg"),
                NotStr(arrowSvg),
                href="/ahcb/maps/",
                cls="redbox no-lines",
            ),
        )

        spans = Div(map(lettr, list_of_words), cls="mini-title-container")
        return Div(spans, redbox, cls="extra-title-container")
    else:
        return Div(map(lettr, list_of_words), cls="title-container")


# Home/Index page
@rt("/ahcb")
def home():
    page_title_text_1 = title_text("Atlas of")
    page_title_text_2 = title_text("Historical")
    page_title_text_3 = title_text("County ", True)
    page_title_text_4 = title_text("Boundaries")
    return BasePage(
        css=(
            # Link(rel="stylesheet", href="/athf/static/css/index.css"),
            Link(rel="stylesheet", href="/ahcb/static/css/jumbo_v2.css"),
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


@rt("/ahcb/clear")
def clear_htmx_route():
    return ""


with open("./md/about.md") as file:
    aboutMd = file.read()

with open("./md/download.md") as file:
    downloadMd = file.read()


@rt("/ahcb/about")
def about():
    return BasePage(
        title="About the Atlas of Historical County Boundaries",
        content=(Article(aboutMd, cls="marked text-page")),
    )


@rt("/ahcb/download")
def download():
    return BasePage(
        title="Download the AHCB data",
        content=(Article(downloadMd, cls="marked text-page")),
    )


videos = [
    {
        "video": "9KDJzkqCyIo",
        "title": "US Historical State & Territorial Boundaries, 1783-2000 (3:00)",
        "img": "us-states-territories-1783-2000-3min.webp",
        "alt": "US Historical State & Territorial Boundaries, 1783-2000 (0:30) [graphic]",
    },
    {
        "video": "7-0lM1g9iSs",
        "title": "US Historical County Boundaries, 1629-2000 (0:30)",
        "img": "us-counties-1629-2000.webp",
        "alt": "US Historical County Boundaries, 1629-2000 [graphic]",
    },
    {
        "video": "jJ-0HzEgOd0",
        "title": "US Historical County Boundaries, 1629-2000 (3:00)",
        "img": "us-counties-1629-2000-3min.webp",
        "alt": "US Historical County Boundaries, 1629-2000 (3:00) [graphic]",
    },
    {
        "video": "QEdDU3ho1oE",
        "title": "US Historical County Boundaries (1629-2000), with State/Territorial boundaries (1783-2000) (0:30)",
        "img": "us-counties-territories-1629-2000.webp",
        "alt": "US Historical County Boundaries (1629-2000), with State/Territorial boundaries (1783-2000) (0:30) [graphic]",
    },
    {
        "video": "X7WzKaqCaV4",
        "title": "US Historical County Boundaries (1629-2000), with State/Territorial boundaries (1783-2000) (3:00)",
        "img": "us-counties-territories-1629-2000-3min.webp",
        "alt": "US Historical County Boundaries (1629-2000), with State/Territorial boundaries (1783-2000) (3:00) [graphic]",
    },
    {
        "video": "g5_j2UaOVDM",
        "title": "US Historical State & Territorial Boundaries, 1783-2000 (0:30)",
        "img": "us-states-territories-1783-2000.webp",
        "alt": "US Historical State & Territorial Boundaries, 1783-2000 (0:30) [graphic]",
    },
    {
        "video": "9KDJzkqCyIo",
        "title": "US Historical State & Territorial Boundaries, 1783-2000 (3:00)",
        "img": "us-states-territories-1783-2000-3min.webp",
        "alt": "US Historical State & Territorial Boundaries, 1783-2000 (0:30) [graphic]",
    },
    {
        "video": "7-0lM1g9iSs",
        "title": "US Historical County Boundaries, 1629-2000 (0:30)",
        "img": "us-counties-1629-2000.webp",
        "alt": "US Historical County Boundaries, 1629-2000 [graphic]",
    },
]

# @router.get("/animation/{idx}", response_class=HTMLResponse)
# async def get_animation_li(
#     request: Request,
#     idx: Optional[int] = 0,
# ):
#     video = videos[idx]
#     return get_template_response(
#         "animations.html",
#         {
#             "request": request,
#             "video": video,
#         })
# template = """
# <li class="animation-li" style="--video-img: url({{video.image}});" onclick=??? >{{video.title}}</li>
# """


@rt("/ahcb/animation/{idx}")
def get_animation_li(idx: int = 0):
    video = videos[idx]
    return (
        Title("Atlas of Historical County Boundaries"),
        Div(
            Img(
                src=f"/ahcb/static/images/usanimations/{video['img']}",
                cls="us-img",
            ),
            P(video["title"], cls="us-text"),
            cls="link-wrapper animation-li",
            hx_get=f"/ahcb/animation/{idx}/modal",
            hx_target="#modal-container",
            hx_swap="innerHTML",
            role="button",
            tabindex="0",
        ),
    )


@rt("/ahcb/animation/{idx}/modal")
def get_animation_modal(idx: int):
    video = videos[idx]
    if video:
        return (
            Title("Atlas of Historical County Boundaries"),
            Div(
                Div(
                    hx_get="/ahcb/clear",
                    hx_target="#modal-container",
                    hx_swap="innerHTML",
                    cls="modal-backdrop",
                ),
                Div(
                    Button(
                        "×",
                        hx_get="/ahcb/clear",
                        hx_target="#modal-container",
                        hx_swap="innerHTML",
                        cls="close-btn",
                    ),
                    H2(video["title"]),
                    Iframe(
                        width="560",
                        height="315",
                        src=f"https://www.youtube.com/embed/{video['video']}",
                        frameborder="0",
                        allowfullscreen="",
                    ),
                    cls="modal-content",
                ),
                id="video-modal",
                cls="modal",
            ),
        )


def video_index_button(i):
    return Li(
        Button(
            i + 1,
            cls="video-idx-btn",
            id=f"video-idx-{i}",
            hx_get=f"/ahcb/animation/{i}",
            hx_target="#anim-li",
        )
    )


@rt("/ahcb/maps")
def all_maps_page():
    return BasePage(
        title="Atlas of Historical County Boundaries Maps",
        css=(
            Link(rel="stylesheet", href="/ahcb/static/css/all-maps.css"),
            Link(rel="stylesheet", href="/ahcb/static/css/leaflet.css"),
        ),
        js=(
            Script(src="/ahcb/static/js/leaflet.js"),
            Script(f"""
                const stateLookup = {json.dumps(STATE_NAMES)};
            """),
            Script(src="/ahcb/static/js/map-nav.js"),
        ),
        content=(
            Section(
                Div(id="usa-map"),
                Div(
                    A(
                        # H3("", cls="state-name", id="ex-tt-title"),
                        Img(
                            src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
                            cls="card-img",
                            id="ex-tt-img-1",
                        ),
                        # Img(
                        #     src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
                        #     cls="card-img-name",
                        #     id="ex-tt-img-2",
                        # ),
                        href="#",
                        id="ex-tt-link",
                    ),
                    id="ex-tt",
                    cls="state-postcard",
                ),
                cls="map-nav",
            ),
            Article(
                Section(
                    A(
                        I("Download national data"),
                        Div(
                            Img(
                                src="/ahcb/static/images/usmap.svg",
                                cls="us-img us-dl-img",
                            ),
                            P(
                                "Data for the entire nation is available on the download page.  Historical commentary and metadata are also available.",
                                cls="us-dl-caption",
                            ),
                            cls="link-wrapper",
                        ),
                        href="/ahcb/download#us-dl",
                        cls="us-dl-link all-us-link",
                    ),
                    Div(
                        I("View animations of national data"),
                        Div(
                            hx_get="/ahcb/animation/0",
                            hx_trigger="load",
                            id="anim-li",
                        ),
                        Ul(map(video_index_button, range(6)), cls="anim-ul"),
                        cls="all-us-link",
                    ),
                    cls="all-us-links",
                ),
                Div(id="modal-container"),
                Ul(
                    *[
                        Li(
                            A(
                                H3(name, cls="state-name"),
                                Img(
                                    src=f"/ahcb/static/images/pcards/{code}_postcard_bg.webp",
                                    cls="card-img",
                                ),
                                Img(
                                    src=f"/ahcb/static/images/pcards/{code}_postcard_fg.webp",
                                    cls="card-img-name",
                                ),
                                href=f"/ahcb/{code}",
                            ),
                            id=f"state-{code}",  # More specific ID
                            cls="state-postcard",
                        )
                        for code, name in STATE_NAMES.items()
                    ]
                ),
                cls="all-maps",
            ),
        ),
    )


no_commentary = [
    "Alaska",
    "Arizona",
    "Arkansas",
    "Colorado",
    "Connecticut",
    "Delaware",
    "District of Columbia",
    "Hawaii",
    "Idaho",
    "Kansas",
    "Louisiana",
    "Maine",
    "Maryland",
    "Mississippi",
    "Missouri",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "Oklahoma",
    "Oregon",
    "Rhode Island",
    "Texas",
    "Utah",
    "Vermont",
    "Washington",
]


# Main state page route
@rt("/ahcb/{state_code}")
def state_page(state_code: str):
    """Display the map page for a specific state"""
    state_data = load_state_data(state_code.lower())
    state_name = get_state_name(state_code)

    def date_linker(date_str):
        # print(f"date in datelinker: {date_str}")
        return Option(
            date_str,
            value=f"/ahcb/{state_code.lower()}?date={date_str}",
            id=f"date-option-{date_str}",
        )

    date_list = []
    manifest = state_data["manifest"]
    for id, feature in manifest["features"].items():
        start_date = feature["start_date"]
        if start_date not in date_list:
            date_list.append(start_date)
            # link_list.append(
            #     Li(A(start_date, href=f"/athf/{state_code.lower()}?date={start_date}"))
            # )
    date_list = list(set(date_list))
    date_list = sorted(date_list, key=lambda x: datetime.strptime(x, "%Y-%m-%d"))
    # link_dropdown = Ul(*link_list, cls="link-dropdown", onclick="toggleDateDropdown")
    # print(f"date list: {date_list}")
    if state_name not in no_commentary:
        commentary = state_code.upper()
    else:
        commentary = "No"

    return BasePage(
        title=f"{state_name} - Atlas of Historical County Boundaries",
        css=(
            Link(rel="stylesheet", href="/ahcb/static/css/leaflet.css"),
            Link(rel="stylesheet", href="/ahcb/static/css/leaflet-mods.css"),
            Link(rel="stylesheet", href="/ahcb/static/css/map-page.css"),
            Link(rel="stylesheet", href="/ahcb/static/css/download-modal.css"),
        ),
        js=(
            Script(f"""
                       const stateCode = '{state_code.lower()}';
                       const stateName = '{state_name}';
                       const previewData = {json.dumps(state_data["preview"])};
                       const manifestData = {json.dumps(manifest)};
                       const urlParams = new URLSearchParams(window.location.search);
                       window.dateParam = urlParams.get("date");
                       
                   """),
            Script("""
                       function openOption(el){
                            console.log("open option fn value", el.value)
                           let target = "_blank";
                           if (el.value.indexOf("?") > -1 ){
                                target="_self";
                           }
                           window.open(el.value, target);
                       }

            """),
            Script(src="/ahcb/static/js/leaflet.js"),
            Script(src="/ahcb/static/js/leaflet.timeline.min.js"),
            Script(src="/ahcb/static/js/map.js"),
            Script("""
                       // Initialize the map when DOM is loaded
                       document.addEventListener('DOMContentLoaded', function() {
                          initializeMap(stateCode, stateName, previewData, manifestData);
                          if(window.dateParam){
                            const selectedDate = document.getElementById(`date-option-${window.dateParam}`)
                            selectedDate.selected = true
                          } else {
                            const allOptions = document.querySelectorAll('#link-select option')
                            allOptions[4].selected = true;
                          }
                       });

                   """),
        ),
        content=(
            Div(
                # Map container
                Div(id="map", cls="map-container"),
                # Info sidebar
                Aside(
                    H2(state_name),
                    Select(
                        Option(
                            "All Changes",
                            value=f"/ahcb/documents/{state_code.upper()}_Consolidated_Chronology.htm",
                            cls="link-lines",
                            target="_blank",
                        ),
                        Option(
                            "Changes by County",
                            value=f"/ahcb/documents/{state_code.upper()}_Individual_County_Chronologies.htm",
                            cls="link-lines",
                            target="_blank",
                        ),
                        Option(
                            f"{state_name} Bibliography",
                            value=f"/ahcb/documents/{state_code.upper()}_Bibliography.htm",
                            cls="link-lines",
                            target="_blank",
                        ),
                        Option(
                            "Commentary",
                            value=f"/ahcb/documents/{commentary}_Commentary.htm",
                            cls="link-lines",
                            target="_blank",
                        ),
                        *map(date_linker, date_list),
                        onchange="openOption(this)",
                        id="link-select",
                    ),
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


@rt("/ahcb/dl/{state_code}")
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
                        href="/ahcb/download",
                        cls="link-lines in-text-link",
                    ),
                    "for more information and additional download options.",
                ),
                onclick="event.stopPropagation()",
            ),
            hx_get="/ahcb/clear",
            hx_swap="outerHTML",
            hx_target="#download-modal",
            id="download-modal",
            cls="download-modal",
        ),
    )


def static_usa_map():
    map_script = Script(
        """
            // Initialize map with interactions disabled
            const map = L.map('usa-map', {
                zoomControl: false,        // Remove zoom buttons
                scrollWheelZoom: false,    // Disable scroll zoom
                doubleClickZoom: false,    // Disable double-click zoom
                boxZoom: false,            // Disable box zoom
                keyboard: false,           // Disable keyboard navigation
                dragging: false,           // Disable panning/dragging
                tap: false,                // Disable tap (mobile)
                touchZoom: false,          // Disable pinch zoom
                attributionControl: false  // Remove attribution
            }).setView([39.8283, -98.5795], 4);
            
            // Simple base layer (you could even skip this for pure vector)
            // L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            //     attribution: ''
            // }).addTo(map);
            
            // Load and display states
            fetch('/ahcb/static/us-states-albers.json' )
                .then(response => response.json())
                .then(statesData => {
                    L.geoJSON(statesData, {

                        style: { 
                            fillColor: 'var(--fg-color)',
                            color: 'var(--bg-color)',
                            weight: 1,
                            fillOpacity: 0.8 
                        },
                        onEachFeature: function(feature, layer) {
                            layer.on({
                                mouseover: function(e) {
                                    e.target.setStyle({
                                        fillColor: '#fff',
                                        fillOpacity: 0.9,
                                        weight: 2
                                    });
                                    const externalTT = document.getElementById('ex-tt');
                                    externalTT.innerText = feature.properties.NAME;
                                },
                                mouseout: function(e) {
                                    e.target.setStyle({
                                        fillColor: 'var(--fg-color)', 
                                        fillOpacity: 0.8,
                                        weight: 1
                                    });
                                },
                                click: function(e) {
                                    const stateName = feature.properties.NAME.toLowerCase().replace(/\s+/g, '-');
                                    htmx.ajax('GET', `/state/${stateName}`, {target: 'body'});
                                }
                            });
                            
                            // Add tooltip with state name
                            layer.bindTooltip(feature.properties.NAME, {
                                permanent: false,
                                anchor: '#usa-map',
                                 direction: 'center',
                                className: 'state-tooltip'
                            });
                        }
                    }).addTo(map);
                    
                    // Optional: fit map to show all states perfectly
                    map.fitBounds(L.geoJSON(statesData).getBounds(), {padding: [10, 10]});
                });
    """,
        type="module",
    )

    return Div(Div(id="usa-map"), map_script)


@rt("/")
def root():
    """Redirect root to atlas home"""
    return RedirectResponse("/ahcb", status_code=303)


# Handle 404s for invalid athf routes
# Since it's a static site, 404s will be handled by apache
@rt("/ahcb/{path:path}")
def ahcb_404(path: str):
    """Handle 404s for invalid AHCB routes"""
    return Titled(
        "Page Not Found",
        Div(f"'{path}' is not a valid state code", cls="error-message"),
    )


if __name__ == "__main__":
    serve()
