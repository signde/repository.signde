"""Build a minimal GitHub Pages artifact for the Kodi repository."""

import re
import shutil
import hashlib
import html
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent
SITE = ROOT / "_site"
# Omega keeps its established package URLs so installed repositories and cached
# indexes keep working. Only its feed moves; Piers has its own package namespace.
RELEASES = {"omega": Path("addons/zips"), "piers": Path("addons/piers")}
TEST_ZIP_PATTERN = re.compile(
    r"(?:-test-[0-9]+|~test[0-9]+|\.test-[0-9.]+)\.zip$"
)


def copy_file(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def repository_package_path(addon):
    for extension in addon.findall("extension"):
        if extension.get("point") not in (
            "xbmc.addon.metadata",
            "kodi.addon.metadata",
        ):
            continue

        package_path = extension.findtext("path")
        if package_path:
            return PurePosixPath(package_path)

    raise ValueError("Missing package path for {}".format(addon.get("id")))


def validate_package_path(addon_id, package_path):
    if (
        package_path.is_absolute()
        or ".." in package_path.parts
        or len(package_path.parts) != 2
        or package_path.parts[0] != addon_id
    ):
        raise ValueError(
            "Invalid package path for {}: {}".format(addon_id, package_path)
        )


def copy_addon_metadata(addon_id, zips, destination):
    source_dir = zips / addon_id
    if not source_dir.is_dir():
        raise FileNotFoundError("Missing metadata directory: {}".format(source_dir))

    for source in source_dir.rglob("*"):
        if source.is_file() and source.suffix.lower() != ".zip":
            copy_file(source, destination / source.relative_to(zips))


def build_feed(release, package_directory):
    zips = ROOT / "addons" / release
    feed = SITE / "addons" / release
    destination = SITE / package_directory
    index = zips / "addons.xml"
    checksum = (zips / "addons.xml.md5").read_text().strip()
    if hashlib.md5(index.read_bytes()).hexdigest() != checksum:
        raise ValueError("Invalid index checksum: {}".format(index))
    for filename in ("addons.xml", "addons.xml.md5"):
        copy_file(zips / filename, feed / filename)
        if release == "omega":
            # Repository 1.2 still reads this endpoint until it updates to 1.3.
            copy_file(zips / filename, destination / filename)

    addons = ElementTree.parse(index).getroot()
    links = []
    seen = set()
    for addon in addons.findall("addon"):
        addon_id = addon.get("id")
        if not addon_id or addon_id in seen:
            raise ValueError("Missing or duplicate add-on id in {}".format(index))
        seen.add(addon_id)
        package_path = repository_package_path(addon)
        validate_package_path(addon_id, package_path)
        if TEST_ZIP_PATTERN.search(package_path.name):
            raise ValueError("Test package in public feed: {}".format(package_path))
        source = zips.joinpath(*package_path.parts)
        if not source.is_file():
            raise FileNotFoundError("Missing referenced package: {}".format(source))
        copy_addon_metadata(addon_id, zips, destination)
        copy_file(source, destination / Path(*package_path.parts))
        href = "{}/{}".format("../zips" if release == "omega" else ".", package_path)
        links.append('<a href="{}">{}</a><br>'.format(
            html.escape(href, quote=True), html.escape(package_path.name)))
    (feed / "index.html").write_text(
        "<!DOCTYPE html>\n<html><body>\n<h1>{}</h1>\n{}\n</body></html>\n".format(
            release.title(), "\n".join(links)), encoding="utf-8")
    return len(seen)


def build_site():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)

    copy_file(ROOT / "index.html", SITE / "index.html")
    (SITE / ".nojekyll").touch()

    for installer in sorted(ROOT.glob("repository.*.zip")):
        if not TEST_ZIP_PATTERN.search(installer.name):
            copy_file(installer, SITE / installer.name)

    package_count = 0
    for release, destination in RELEASES.items():
        package_count += build_feed(release, destination)
    # Keep historical installer links valid, including clients with cached 1.2
    # repository metadata. Ordinary Omega package URLs were preserved above.
    for installer in ROOT.glob("repository.signde-*.zip"):
        if not TEST_ZIP_PATTERN.search(installer.name):
            copy_file(installer, SITE / "addons/zips/repository.signde" / installer.name)

    total_size = sum(path.stat().st_size for path in SITE.rglob("*") if path.is_file())
    print(
        "Built {} with {} packages ({:.1f} MiB)".format(
            SITE, package_count, total_size / (1024 * 1024)
        )
    )


if __name__ == "__main__":
    build_site()
