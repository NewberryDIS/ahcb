#!/usr/bin/env python3
"""
Historical Counties Data Processor

This script processes JSONP files containing historical county boundary data:
1. Converts JSONP to JSON
2. Removes redundant fields
3. Handles null values
4. Creates optimized preview files with date indexes
5. Splits full-resolution data into individual feature files
6. Organizes data by state using 2-letter abbreviations

Usage:
    python process_data.py --input-dir raw_data --output-dir data --preview-suffix _preview --full-suffix _full
"""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import hashlib

# US State name to abbreviation mapping
STATE_ABBREVIATIONS = {
    # "alabama": "al",
    "alaska": "ak",
    # "arizona": "az",
    # "arkansas": "ar",
    # "california": "ca",
    # "colorado": "co",
    # "connecticut": "ct",
    # "delaware": "de",
    # "florida": "fl",
    # "georgia": "ga",
    # "hawaii": "hi",
    # "idaho": "id",
    # "illinois": "il",
    # "indiana": "in",
    # "iowa": "ia",
    # "kansas": "ks",
    # "kentucky": "ky",
    # "louisiana": "la",
    # "maine": "me",
    # "maryland": "md",
    # "massachusetts": "ma",
    # "michigan": "mi",
    # "minnesota": "mn",
    # "mississippi": "ms",
    # "missouri": "mo",
    # "montana": "mt",
    # "nebraska": "ne",
    # "nevada": "nv",
    # "new hampshire": "nh",
    # "new jersey": "nj",
    # "new mexico": "nm",
    # "new york": "ny",
    # "north carolina": "nc",
    # "north dakota": "nd",
    # "ohio": "oh",
    # "oklahoma": "ok",
    # "oregon": "or",
    # "pennsylvania": "pa",
    # "rhode island": "ri",
    # "south carolina": "sc",
    # "south dakota": "sd",
    # "tennessee": "tn",
    # "texas": "tx",
    # "utah": "ut",
    # "vermont": "vt",
    # "virginia": "va",
    # "washington": "wa",
    # "west virginia": "wv",
    # "wisconsin": "wi",
    # "wyoming": "wy",
}


def get_state_abbreviation(filename):
    """Extract state abbreviation from filename"""
    # Try to match common patterns like "delaware_preview.jsonp" or "DE_full.jsonp"
    filename_lower = filename.lower()

    # First try direct state name match
    for state_name, abbrev in STATE_ABBREVIATIONS.items():
        if state_name in filename_lower:
            return abbrev

    # Try abbreviation match (case insensitive)
    for state_name, abbrev in STATE_ABBREVIATIONS.items():
        if abbrev in filename_lower:
            return abbrev

    # If no match found, try to extract from filename pattern
    # Look for 2-letter combinations that might be state codes
    parts = re.findall(r"[a-z]{2}", filename_lower)
    for part in parts:
        if part in STATE_ABBREVIATIONS.values():
            return part

    # Fallback: use first part of filename
    base_name = Path(filename).stem.split("_")[0].lower()
    return STATE_ABBREVIATIONS.get(base_name, base_name[:2])


def parse_jsonp(content):
    """Convert JSONP to JSON, handling JavaScript null values"""
    # Remove JSONP callback wrapper if present
    content = content.strip()

    # Look for common JSONP patterns like callback({...}) or var_name = {...}
    jsonp_patterns = [
        r"^[a-zA-Z_$][a-zA-Z0-9_$]*\s*\(\s*({.*})\s*\)\s*;?\s*$",  # callback({...})
        r"^[a-zA-Z_$][a-zA-Z0-9_$]*\s*=\s*({.*})\s*;?\s*$",  # var = {...}
        r"^({.*})$",  # Just JSON
    ]

    json_content = None
    for pattern in jsonp_patterns:
        match = re.match(pattern, content, re.DOTALL)
        if match:
            json_content = match.group(1)
            break

    if json_content is None:
        raise ValueError("Could not parse JSONP content")

    # Handle JavaScript null values by replacing with Python None equivalent
    # This is a bit tricky because we need to avoid replacing null inside strings
    json_content = re.sub(r"\bnull\b", "null", json_content)  # Ensure it's JSON null

    return json.loads(json_content)


def clean_feature_properties(properties):
    """Remove redundant fields and handle null values"""
    # Fields to remove (redundant data)
    redundant_fields = {"START_N", "END_N", "start", "end"}

    # Create cleaned properties dict
    cleaned = {}
    for key, value in properties.items():
        if key not in redundant_fields:
            # Convert JavaScript null to Python None, then to empty string for consistency
            if value is None:
                cleaned[key] = ""
            else:
                cleaned[key] = value

    return cleaned


def create_date_index(features):
    """Create an index for efficient date-based lookups"""
    county_index = defaultdict(list)
    date_range = {"min_date": None, "max_date": None}

    for i, feature in enumerate(features):
        props = feature["properties"]
        county_id = props["ID"]
        start_date = props["START_DATE"]
        end_date = props["END_DATE"]

        # Track date range for the entire dataset
        if date_range["min_date"] is None or start_date < date_range["min_date"]:
            date_range["min_date"] = start_date
        if date_range["max_date"] is None or end_date > date_range["max_date"]:
            date_range["max_date"] = end_date

        county_index[county_id].append(
            {
                "feature_index": i,
                "start_date": start_date,
                "end_date": end_date,
                "name": props["NAME"],
                "full_name": props.get("FULL_NAME", props["NAME"]),
            }
        )

    return dict(county_index), date_range


def generate_feature_id(feature):
    """Generate a unique ID for each feature based on its properties"""
    props = feature["properties"]
    # Create a hash based on county ID, start date, and end date
    id_string = f"{props['ID']}_{props['START_DATE']}_{props['END_DATE']}"
    return hashlib.md5(id_string.encode()).hexdigest()[:12]


def process_state_data(input_file, output_dir, is_preview=True):
    """Process a single state's data file"""
    print(f"Processing {input_file}...")

    # Read and parse JSONP file
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        data = parse_jsonp(content)
    except Exception as e:
        print(f"Error parsing {input_file}: {e}")
        return None

    # Get state abbreviation from filename
    state_abbrev = get_state_abbreviation(input_file.name)
    print(f"  Detected state: {state_abbrev}")

    # Create state directory
    state_dir = output_dir / state_abbrev
    state_dir.mkdir(parents=True, exist_ok=True)

    # Process features
    if "features" not in data:
        print(f"  Warning: No 'features' key found in {input_file}")
        return None

    processed_features = []
    feature_files = []

    for feature in data["features"]:
        # Clean properties
        cleaned_props = clean_feature_properties(feature["properties"])

        # Create processed feature
        processed_feature = {
            "type": feature["type"],
            "properties": cleaned_props,
            "geometry": feature["geometry"],
        }

        processed_features.append(processed_feature)

        # If processing full data, prepare individual feature files
        if not is_preview:
            feature_id = generate_feature_id(processed_feature)
            feature_files.append({"id": feature_id, "feature": processed_feature})

    if is_preview:
        # Create date index
        county_index, date_range = create_date_index(processed_features)

        # Save preview file with index
        preview_data = {
            "type": "FeatureCollection",
            "features": processed_features,
            "metadata": {
                "state": state_abbrev.upper(),
                "feature_count": len(processed_features),
                "date_range": date_range,
                "processed_at": datetime.now().isoformat(),
            },
            "county_index": county_index,
        }

        preview_file = state_dir / "preview.json"
        with open(preview_file, "w", encoding="utf-8") as f:
            json.dump(preview_data, f, separators=(",", ":"))

        print(f"  Created preview: {preview_file} ({len(processed_features)} features)")

    else:
        # Create features directory
        features_dir = state_dir / "features"
        features_dir.mkdir(exist_ok=True)

        # Save individual feature files
        feature_manifest = {
            "state": state_abbrev.upper(),
            "total_features": len(feature_files),
            "features": {},
        }

        for feature_data in feature_files:
            feature_id = feature_data["id"]
            feature = feature_data["feature"]

            # Save individual feature file
            feature_file = features_dir / f"{feature_id}.json"
            with open(feature_file, "w", encoding="utf-8") as f:
                json.dump(feature, f, separators=(",", ":"))

            # Add to manifest
            props = feature["properties"]
            feature_manifest["features"][feature_id] = {
                "county_id": props["ID"],
                "name": props["NAME"],
                "start_date": props["START_DATE"],
                "end_date": props["END_DATE"],
                "filename": f"{feature_id}.json",
            }

        # Save feature manifest
        manifest_file = state_dir / "features_manifest.json"
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(feature_manifest, f, indent=2)

        print(f"  Created {len(feature_files)} feature files in {features_dir}")
        print(f"  Created manifest: {manifest_file}")

    return state_abbrev


def main():
    parser = argparse.ArgumentParser(
        description="Process historical county boundary data"
    )
    parser.add_argument(
        "--input-dir", type=Path, required=True, help="Directory containing JSONP files"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data"),
        help="Output directory for processed data",
    )
    parser.add_argument(
        "--preview-suffix", default="_preview", help="Suffix for preview files"
    )
    parser.add_argument(
        "--full-suffix", default="_full", help="Suffix for full-resolution files"
    )

    args = parser.parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Find all JSONP files
    jsonp_files = list(args.input_dir.glob("*.jsonp"))
    if not jsonp_files:
        print(f"No JSONP files found in {args.input_dir}")
        return

    print(f"Found {len(jsonp_files)} JSONP files")

    # Separate preview and full files
    preview_files = [f for f in jsonp_files if args.preview_suffix in f.name]
    full_files = [f for f in jsonp_files if args.full_suffix in f.name]

    print(f"  Preview files: {len(preview_files)}")
    print(f"  Full files: {len(full_files)}")

    # Process preview files first
    processed_states = set()

    for preview_file in preview_files:
        state = process_state_data(preview_file, args.output_dir, is_preview=True)
        if state:
            processed_states.add(state)

    # Process full files
    for full_file in full_files:
        state = process_state_data(full_file, args.output_dir, is_preview=False)
        if state:
            processed_states.add(state)

    # Create summary
    summary = {
        "processed_at": datetime.now().isoformat(),
        "states_processed": sorted(list(processed_states)),
        "total_states": len(processed_states),
    }

    summary_file = args.output_dir / "processing_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nProcessing complete!")
    print(f"States processed: {', '.join(sorted(processed_states))}")
    print(f"Summary saved to: {summary_file}")


if __name__ == "__main__":
    main()
