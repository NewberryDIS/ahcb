#!/usr/bin/env python3
"""
Static site generator with incremental file copying and development server
Generates a static version of the FastHTML site with efficient file management
"""

import os
import sys
import shutil
import time
import json
import subprocess
import threading
import http.server
import socketserver
from pathlib import Path
from typing import Dict, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class IncrementalCopy:
    """Handles efficient copying of files with modification time tracking"""

    def __init__(self, manifest_path: Path = Path("dist/.copy_manifest.json")):
        self.manifest_path = manifest_path
        self.manifest = self.load_manifest()

    def load_manifest(self) -> Dict[str, float]:
        """Load the copy manifest tracking file modification times"""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {}

    def save_manifest(self):
        """Save the copy manifest"""
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_path, "w") as f:
            json.dump(self.manifest, f, indent=2)

    def should_copy(self, src: Path, dest: Path) -> bool:
        """Check if file should be copied based on modification time"""
        if not dest.exists():
            return True

        src_mtime = src.stat().st_mtime
        src_str = str(src)

        # Check if we have this file in our manifest and if it's been modified
        if src_str in self.manifest:
            return src_mtime > self.manifest[src_str]

        return True

    def copy_file(self, src: Path, dest: Path):
        """Copy a single file and update manifest"""
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)  # copy2 preserves metadata
        self.manifest[str(src)] = src.stat().st_mtime

    def sync_directory(
        self, src_dir: Path, dest_dir: Path, extensions: Set[str] = None
    ) -> int:
        """Sync directory with incremental copying"""
        copied_count = 0

        for src_file in src_dir.rglob("*"):
            if src_file.is_file():
                # Filter by extensions if specified
                if extensions and src_file.suffix.lower() not in extensions:
                    continue

                # Calculate destination path
                rel_path = src_file.relative_to(src_dir)
                dest_file = dest_dir / rel_path

                # Only copy if needed
                if self.should_copy(src_file, dest_file):
                    self.copy_file(src_file, dest_file)
                    copied_count += 1

        return copied_count


class StaticSiteGenerator:
    """Main static site generator"""

    def __init__(self, output_dir: str = "dist"):
        self.output_dir = Path(output_dir)
        self.copier = IncrementalCopy()

    def clean_output_dir(self, full_clean: bool = False):
        """Clean output directory"""
        if full_clean and self.output_dir.exists():
            shutil.rmtree(self.output_dir)
            print(f"🗑️  Cleaned output directory: {self.output_dir}")

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def copy_static_files(self) -> int:
        """Copy static assets with incremental sync"""
        total_copied = 0

        # Copy static directory
        if Path("static").exists():
            copied = self.copier.sync_directory(
                Path("static"), self.output_dir / "athf" / "static"
            )
            total_copied += copied
            if copied > 0:
                print(f"📁 Copied {copied} static files")

        # Copy data directory (this is the big one with 17k+ files)
        if Path("data").exists():
            copied = self.copier.sync_directory(
                Path("data"),
                self.output_dir / "athf" / "data",
                extensions={".json"},  # Only copy JSON files from data
            )
            total_copied += copied
            if copied > 0:
                print(f"📊 Copied {copied} data files")

        return total_copied

    def generate_html_pages(self):
        """Generate HTML pages using FastHTML app"""
        print("🔨 Generating HTML pages...")

        # Import/reload the FastHTML app to pick up changes
        sys.path.insert(0, ".")

        # Force reload the main module to pick up changes
        import importlib

        if "main" in sys.modules:
            importlib.reload(sys.modules["main"])

        from main import app, STATE_NAMES
        from starlette.testclient import TestClient

        client = TestClient(app)

        # Generate pages
        pages_generated = 0

        try:
            # Home page
            response = client.get("/athf")
            if response.status_code == 200:
                self.save_page("athf/index.html", response.text)
                pages_generated += 1

            # All maps page
            response = client.get("/athf/maps")
            if response.status_code == 200:
                self.save_page("athf/maps/index.html", response.text)
                pages_generated += 1

            # Individual state pages
            for state_code in STATE_NAMES.keys():
                try:
                    response = client.get(f"/athf/{state_code}")
                    if response.status_code == 200:
                        self.save_page(f"athf/{state_code}/index.html", response.text)
                        pages_generated += 1
                    else:
                        print(
                            f"⚠️  Skipped {state_code} (status {response.status_code})"
                        )
                except Exception as e:
                    print(f"⚠️  Error generating {state_code}: {e}")

            print(f"📄 Generated {pages_generated} HTML pages")

        except Exception as e:
            print(f"❌ Error generating pages: {e}")
            return False

        return True

    def save_page(self, path: str, content: str):
        """Save a page to the output directory"""
        file_path = self.output_dir / path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def create_redirects(self):
        """Create redirect files for compatibility"""
        # Root redirect to /athf
        root_html = """<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url=/athf/">
    <title>Redirecting...</title>
</head>
<body>
    <p>If you are not redirected automatically, <a href="/athf/">click here</a>.</p>
</body>
</html>"""

        with open(self.output_dir / "index.html", "w") as f:
            f.write(root_html)

        print("🔗 Created redirect files")

    def build(self, full_clean: bool = False) -> bool:
        """Full build process"""
        start_time = time.time()

        # Clean output directory
        self.clean_output_dir(full_clean)

        # Copy static files (incremental)
        files_copied = self.copy_static_files()

        # Generate HTML pages
        if not self.generate_html_pages():
            return False

        # Create redirects
        self.create_redirects()

        # Save copy manifest
        self.copier.save_manifest()

        build_time = time.time() - start_time
        print(f"✅ Build completed in {build_time:.2f}s")
        if files_copied > 0:
            print(f"   📁 {files_copied} files copied")

        return True


class DevRebuildHandler(FileSystemEventHandler):
    """File watcher for development rebuilds"""

    def __init__(self, generator: StaticSiteGenerator):
        self.generator = generator
        self.last_build = 0
        self.build_lock = threading.Lock()
        # Track which files should trigger rebuilds
        self.rebuild_extensions = {".py", ".css", ".js", ".md"}
        self.static_extensions = {
            ".css",
            ".js",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".ico",
        }

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Ignore build artifacts and hidden files
        if any(part.startswith(".") for part in file_path.parts):
            return

        if file_path.suffix in self.rebuild_extensions:
            self.rebuild()
        elif file_path.suffix in self.static_extensions and file_path.is_relative_to(
            Path("static")
        ):
            self.rebuild_static_only()

    def rebuild(self):
        """Full rebuild"""
        current_time = time.time()
        if current_time - self.last_build < 1:  # Debounce
            return

        with self.build_lock:
            self.last_build = current_time
            print(f"\n🔄 Files changed, rebuilding...")
            self.generator.build()

    def rebuild_static_only(self):
        """Rebuild only static files"""
        current_time = time.time()
        if current_time - self.last_build < 0.5:  # Shorter debounce for static files
            return

        with self.build_lock:
            self.last_build = current_time
            print(f"\n📁 Static file changed, copying...")
            files_copied = self.generator.copy_static_files()
            if files_copied > 0:
                print(f"✅ Copied {files_copied} files")


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler for serving the static site"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="dist", **kwargs)

    def end_headers(self):
        # Add headers to prevent caching during development
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, format, *args):
        # Only log errors and important requests
        if "40" in str(args[1]) or "50" in str(args[1]):
            super().log_message(format, *args)


def run_server(port: int = 8000):
    """Run the development server"""
    try:
        with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
            print(f"🌐 Development server running at http://localhost:{port}")
            print(f"🌐 Atlas available at http://localhost:{port}/athf/")
            print("📁 Serving from 'dist' directory")
            print("💡 Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {port} is already in use")
            return False
        else:
            print(f"❌ Server error: {e}")
            return False
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Static site generator and dev server")
    parser.add_argument(
        "--port", "-p", type=int, default=8000, help="Dev server port (default: 8000)"
    )
    parser.add_argument(
        "--build-only", action="store_true", help="Build once and exit (no dev server)"
    )
    parser.add_argument("--no-watch", action="store_true", help="Disable file watching")
    parser.add_argument(
        "--clean", action="store_true", help="Clean build (remove all output first)"
    )
    parser.add_argument(
        "--output", "-o", default="dist", help="Output directory (default: dist)"
    )

    args = parser.parse_args()

    # Check requirements
    if not Path("main.py").exists():
        print("❌ main.py not found in current directory")
        sys.exit(1)

    # Create generator
    generator = StaticSiteGenerator(args.output)

    # Initial build
    print("🔨 Building static site...")
    if not generator.build(full_clean=args.clean):
        print("❌ Build failed")
        sys.exit(1)

    if args.build_only:
        print("✅ Build complete")
        return

    # Set up file watching
    observer = None
    if not args.no_watch:
        event_handler = DevRebuildHandler(generator)
        observer = Observer()

        # Watch relevant directories
        watch_paths = [".", "static", "data"]
        for path in watch_paths:
            if Path(path).exists():
                observer.schedule(event_handler, path, recursive=True)
                print(f"👀 Watching {path}/ for changes")

        observer.start()
        print("🔄 Auto-rebuild enabled")

    # Run development server
    try:
        run_server(args.port)
    except KeyboardInterrupt:
        pass
    finally:
        if observer:
            observer.stop()
            observer.join()
        print("\n👋 Development session ended")


if __name__ == "__main__":
    main()
