#!/usr/bin/env python3
"""
County Boundary Simplification Script

This script takes JSONP files containing historical county boundary data
and creates simplified "preview" versions using Shapely's Douglas-Peucker algorithm.
"""

import json
import re
from pathlib import Path
from shapely.geometry import shape
from shapely.validation import make_valid
import argparse


def extract_jsonp_data(jsonp_content):
    """
    Extract JSON data from JSONP format.
    Assumes format: onLoadData({...json data...})
    """
    # Find the JSON part between the parentheses
    match = re.search(r"onLoadData\s*\(\s*({.*})\s*\)", jsonp_content, re.DOTALL)
    if not match:
        raise ValueError("Could not find JSON data in JSONP format")

    json_str = match.group(1)
    return json.loads(json_str)


def create_jsonp_output(data, callback_name="onLoadData"):
    """
    Wrap JSON data back into JSONP format.
    """
    json_str = json.dumps(data, indent=2)
    return f"{callback_name}({json_str})"


def simplify_geometry(geometry, tolerance=0.01):
    """
    Simplify a geometry using Shapely's simplify method.

    Args:
        geometry: Shapely geometry object
        tolerance: Simplification tolerance (higher = more simplified)

    Returns:
        Simplified geometry object
    """
    try:
        # Ensure the geometry is valid before simplification
        if not geometry.is_valid:
            print(f"Warning: Invalid geometry detected, attempting to fix...")
            geometry = make_valid(geometry)

        # Apply Douglas-Peucker simplification
        simplified = geometry.simplify(tolerance, preserve_topology=True)

        # Ensure the result is still valid
        if not simplified.is_valid:
            print(
                f"Warning: Simplification resulted in invalid geometry, using original..."
            )
            return geometry

        return simplified

    except Exception as e:
        print(f"Error simplifying geometry: {e}")
        return geometry


def calculate_size_reduction(original_coords, simplified_coords):
    """
    Calculate the percentage reduction in coordinate count.
    """

    def count_coordinates(coords):
        """Recursively count coordinates in nested structure."""
        if not isinstance(coords, list):
            return 0
        if len(coords) == 2 and all(isinstance(x, (int, float)) for x in coords):
            return 1  # This is a coordinate pair
        return sum(count_coordinates(item) for item in coords)

    original_count = count_coordinates(original_coords)
    simplified_count = count_coordinates(simplified_coords)

    if original_count == 0:
        return 0

    reduction = ((original_count - simplified_count) / original_count) * 100
    return reduction


def process_county_data(input_file, output_file, tolerance=0.01, verbose=True):
    """
    Process a county boundary file and create a simplified version.

    Args:
        input_file: Path to input JSONP file
        output_file: Path to output simplified JSONP file
        tolerance: Simplification tolerance
        verbose: Whether to print progress information
    """
    if verbose:
        print(f"Processing: {input_file}")
        print(f"Tolerance: {tolerance}")

    # Read input file
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {input_file}: {e}")
        return False

    # Extract JSON data from JSONP
    try:
        data = extract_jsonp_data(content)
    except Exception as e:
        print(f"Error parsing JSONP data: {e}")
        return False

    # Process each feature
    total_features = len(data.get("features", []))
    total_original_coords = 0
    total_simplified_coords = 0

    for i, feature in enumerate(data.get("features", [])):
        if verbose and total_features > 1:
            print(
                f"  Processing feature {i + 1}/{total_features}: {feature.get('properties', {}).get('FULL_NAME', 'Unknown')}"
            )

        try:
            # Convert GeoJSON geometry to Shapely object
            geometry = shape(feature["geometry"])

            # Count original coordinates
            original_coords = feature["geometry"]["coordinates"]
            original_count = (
                sum(1 for _ in str(original_coords).split(",")) // 2
            )  # Rough coordinate count
            total_original_coords += original_count

            # Simplify the geometry
            simplified_geometry = simplify_geometry(geometry, tolerance)

            # Convert back to GeoJSON format
            feature["geometry"] = simplified_geometry.__geo_interface__

            # Count simplified coordinates
            simplified_count = (
                sum(1 for _ in str(feature["geometry"]["coordinates"]).split(",")) // 2
            )
            total_simplified_coords += simplified_count

            if verbose and total_features > 1:
                reduction = calculate_size_reduction(
                    original_coords, feature["geometry"]["coordinates"]
                )
                print(f"    Coordinate reduction: {reduction:.1f}%")

        except Exception as e:
            print(f"Warning: Could not simplify feature {i}: {e}")
            continue

    # Calculate overall reduction
    if total_original_coords > 0:
        overall_reduction = (
            (total_original_coords - total_simplified_coords) / total_original_coords
        ) * 100
        if verbose:
            print(f"Overall coordinate reduction: {overall_reduction:.1f}%")
            print(f"Original coordinates: ~{total_original_coords:,}")
            print(f"Simplified coordinates: ~{total_simplified_coords:,}")

    # Save simplified data
    try:
        output_content = create_jsonp_output(data)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output_content)

        if verbose:
            print(f"Saved simplified data to: {output_file}")

        return True

    except Exception as e:
        print(f"Error saving file {output_file}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Simplify county boundary data for preview use"
    )
    parser.add_argument("input", help="Input JSONP file path")
    parser.add_argument(
        "-o", "--output", help="Output file path (default: adds _preview suffix)"
    )
    parser.add_argument(
        "-t",
        "--tolerance",
        type=float,
        default=0.01,
        help="Simplification tolerance (default: 0.01, higher = more simplified)",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress verbose output"
    )

    args = parser.parse_args()

    input_path = Path(args.input)

    # Generate output filename if not provided
    if args.output:
        output_path = Path(args.output)
    else:
        # Add _preview suffix before file extension
        output_path = (
            input_path.parent / f"{input_path.stem}_preview{input_path.suffix}"
        )

    # Process the file
    success = process_county_data(
        input_file=input_path,
        output_file=output_path,
        tolerance=args.tolerance,
        verbose=not args.quiet,
    )

    if success:
        print(f"\n✓ Successfully created preview file: {output_path}")
    else:
        print(f"\n✗ Failed to process {input_path}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
