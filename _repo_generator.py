""" 
    Put this script in the root folder of your repo and it will
    zip up all addon folders, create a new zip in your zips folder
    and then update the md5 and addons.xml file
"""

import argparse
import os
import shutil
import hashlib
import subprocess
import tempfile
import zipfile
import html
from xml.etree import ElementTree

SCRIPT_VERSION = 1
KODI_VERSIONS = ["addons"]
TEXTURE_PACKER = os.environ.get(
    "TEXTURE_PACKER",
    os.path.expanduser("~/.local/bin/TexturePacker"),
)
IGNORE = [
    ".git",
    ".github",
    ".gitignore",
    ".DS_Store",
    "thumbs.db",
    ".idea",
    "venv",
]
# Preserve these upstream texture bundles instead of rebuilding them. Their XBTs
# contain runtime assets that are not available as loose files in the source
# trees, so replacing a bundle from only the loose files would discard assets.
PRESERVE_TEXTURE_BUNDLES = {
    "skin.arctic.fuse.2",
    "skin.arctic.zephyr.2.resurrection.mod",
    "skin.arctic.zephyr.mod",
    "skin.bingie",
    "skin.confluence",
}
# Preserved bundles do not contain newer p3i/VS10 and enhanced-PPI assets added
# as loose files, so these skins use hybrid packaging: retain the upstream XBT
# and include the newer loose media alongside it.
INCLUDE_LOOSE_MEDIA_WITH_TEXTURE_BUNDLE = {
    "skin.arctic.fuse.2",
    "skin.arctic.zephyr.2.resurrection.mod",
    "skin.arctic.zephyr.mod",
    "skin.bingie",
    "skin.confluence",
}


def _setup_colors():
    console = 0
    if os.name == 'nt':  # Only if we are running on Windows
        color = os.system("color")
        from ctypes import windll

        k = windll.kernel32
        console = k.SetConsoleMode(k.GetStdHandle(-11), 7)
        return color == 1 or console == 1
    return False


_COLOR_ESCAPE = "\x1b[{}m"
_COLORS = {
    "black": "30",
    "red": "31",
    "green": "4;32",
    "yellow": "3;33",
    "blue": "34",
    "magenta": "35",
    "cyan": "1;36",
    "grey": "37",
    "endc": "0",
}
_SUPPORTS_COLOR = _setup_colors()


def color_text(text, color):
    return (
        '{}{}{}'.format(
            _COLOR_ESCAPE.format(_COLORS[color]),
            text,
            _COLOR_ESCAPE.format(_COLORS["endc"]),
        )
        if _SUPPORTS_COLOR
        else text
    )


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


class Generator:
    """
    Generates a new addons.xml file from each addons addon.xml file
    and a new addons.xml.md5 hash file. Must be run from the root of
    the checked-out repo.
    """

    def __init__(self, release, folders=None):
        self.release_path = release
        self.zips_path = os.path.join(self.release_path, "zips")
        self.folders = self._resolve_folders(folders)
        addons_xml_path = os.path.join(self.zips_path, "addons.xml")
        md5_path = os.path.join(self.zips_path, "addons.xml.md5")

        if not os.path.exists(self.zips_path):
            os.makedirs(self.zips_path)

        self._remove_binaries()

        if self._generate_addons_file(addons_xml_path):
            print(
                "Successfully updated {}".format(color_text(addons_xml_path, 'yellow'))
            )

            if self._generate_md5_file(addons_xml_path, md5_path):
                print("Successfully updated {}".format(color_text(md5_path, 'yellow')))

    def _resolve_folders(self, folders):
        """Validate optional add-on folders while preserving their order."""

        if not folders:
            return None

        resolved = []
        release_prefix = self.release_path + os.sep
        for folder in folders:
            folder = os.path.normpath(folder)
            if folder.startswith(release_prefix):
                folder = folder[len(release_prefix):]

            addon_path = os.path.join(self.release_path, folder)
            if (
                os.path.isabs(folder)
                or os.path.dirname(folder)
                or not os.path.isdir(addon_path)
                or not os.path.exists(os.path.join(addon_path, "addon.xml"))
            ):
                raise ValueError("Invalid add-on folder: {}".format(folder))

            if folder not in resolved:
                resolved.append(folder)

        return resolved

    def _selected_paths(self, base_path):
        """Return selected paths, or the whole base path for a full build."""

        if self.folders is None:
            return [base_path]
        return [os.path.join(base_path, folder) for folder in self.folders]

    def _remove_binaries(self):
        """
        Removes any and all compiled Python files before operations.
        """

        for search_path in self._selected_paths(self.release_path):
            for parent, dirnames, filenames in os.walk(search_path):
                for fn in filenames:
                    if fn.lower().endswith("pyo") or fn.lower().endswith("pyc"):
                        compiled = os.path.join(parent, fn)
                        try:
                            os.remove(compiled)
                            print(
                                "Removed compiled python file: {}".format(
                                    color_text(compiled, 'green')
                                )
                            )
                        except OSError as error:
                            print(
                                "Failed to remove compiled python file {}: {}".format(
                                    color_text(compiled, 'red'), error
                                )
                            )
                for directory in dirnames:
                    if "pycache" in directory.lower():
                        compiled = os.path.join(parent, directory)
                        try:
                            shutil.rmtree(compiled)
                            print(
                                "Removed __pycache__ cache folder: {}".format(
                                    color_text(compiled, 'green')
                                )
                            )
                        except OSError as error:
                            print(
                                "Failed to remove __pycache__ cache folder {}: {}".format(
                                    color_text(compiled, 'red'), error
                                )
                            )

    def _ignore_media_pack_source(self, directory, names):
        """
        Ignore files that should not be fed back into TexturePacker.
        """
        ignored = set()
        for name in names:
            if name in IGNORE or name.lower().endswith(".xbt"):
                ignored.add(name)
        return ignored

    def _has_loose_media_files(self, media_path):
        """
        Return True when a media directory has files to pack.
        """
        for root, dirnames, filenames in os.walk(media_path):
            dirnames[:] = [d for d in dirnames if d not in IGNORE]
            for filename in filenames:
                if filename in IGNORE or filename.lower().endswith(".xbt"):
                    continue
                return True
        return False

    def _pack_media_assets(self, folder):
        """
        Pack loose media assets into Textures.xbt when an add-on has media files.
        Existing .xbt files are excluded from the pack source to avoid recursion.
        """
        addon_folder = os.path.join(self.release_path, folder)
        media_path = os.path.join(addon_folder, "media")
        if not os.path.isdir(media_path) or not self._has_loose_media_files(media_path):
            return

        if folder in PRESERVE_TEXTURE_BUNDLES:
            output_path = os.path.join(media_path, "Textures.xbt")
            if not os.path.isfile(output_path):
                raise FileNotFoundError(
                    "Preserved texture bundle not found at {}".format(output_path)
                )
            print(
                "Preserved texture bundle: {}".format(
                    color_text(output_path, 'green')
                )
            )
            return

        if not os.path.exists(TEXTURE_PACKER):
            raise FileNotFoundError(
                "TexturePacker not found at {}. Set TEXTURE_PACKER to override.".format(
                    TEXTURE_PACKER
                )
            )

        output_path = os.path.join(media_path, "Textures.xbt")
        with tempfile.TemporaryDirectory() as temp_dir:
            pack_source = os.path.join(temp_dir, "media")
            shutil.copytree(
                media_path,
                pack_source,
                ignore=self._ignore_media_pack_source,
            )
            result = subprocess.run(
                [
                    TEXTURE_PACKER,
                    "-input",
                    pack_source,
                    "-output",
                    output_path,
                    "-dupecheck",
                ],
                capture_output=True,
                text=True,
            )

        if result.returncode != 0:
            output = "\n".join(
                line for line in [result.stdout, result.stderr] if line
            ).strip()
            raise RuntimeError("TexturePacker failed for {}:\n{}".format(folder, output))

        warning_count = sum(
            1
            for line in (result.stdout + result.stderr).splitlines()
            if "warning" in line.lower()
        )
        message = "Packed media assets: {}".format(color_text(output_path, 'green'))
        if warning_count:
            message += " ({} warning{})".format(
                warning_count,
                "" if warning_count == 1 else "s",
            )
        print(message)

    def _should_zip_file(self, addon_folder, fullpath):
        """
        Skip loose media files once Textures.xbt has been generated.

        Add-ons configured for hybrid texture packaging retain their existing
        XBT, which may contain assets unavailable in the source tree, and also
        include loose media files that may be newer than that bundle.
        """
        relative_path = os.path.relpath(fullpath, addon_folder)
        path_parts = relative_path.split(os.sep)
        if path_parts[0] == "media":
            if (
                os.path.basename(addon_folder)
                in INCLUDE_LOOSE_MEDIA_WITH_TEXTURE_BUNDLE
            ):
                return True
            return os.path.basename(fullpath).lower().endswith(".xbt")
        return True

    def _create_zip(self, folder, addon_id, version):
        """
        Creates a zip file in the zips directory for the given addon.
        """
        addon_folder = os.path.join(self.release_path, folder)
        zip_folder = os.path.join(self.zips_path, addon_id)
        if not os.path.exists(zip_folder):
            os.makedirs(zip_folder)
        
        final_zip = os.path.join(zip_folder, "{0}-{1}.zip".format(addon_id, version))

        zip = zipfile.ZipFile(final_zip, "w", compression=zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(addon_folder):
            # remove any unneeded artifacts
            for i in IGNORE:
                if i in dirs:
                    try:
                        dirs.remove(i)
                    except:
                        pass
                files[:] = [f for f in files if not f.startswith(i)]

            for f in files:
                fullpath = os.path.join(root, f)
                if not self._should_zip_file(addon_folder, fullpath):
                    continue

                relative_name = os.path.relpath(fullpath, addon_folder)
                archive_name = os.path.join(addon_id, relative_name)
                zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)

        zip.close()
        self._remove_old_addon_zips(zip_folder, final_zip)
        size = convert_bytes(os.path.getsize(final_zip))
        print(
            "Zip created for {} ({}) - {}".format(
                color_text(addon_id, 'cyan'),
                color_text(version, 'green'),
                color_text(size, 'yellow'),
            )
        )
        return final_zip

    def _remove_old_addon_zips(self, zip_folder, current_zip):
        """Remove superseded packages after the replacement ZIP is complete."""

        current_zip = os.path.abspath(current_zip)
        for filename in os.listdir(zip_folder):
            old_zip = os.path.join(zip_folder, filename)
            if (
                not filename.lower().endswith(".zip")
                or os.path.abspath(old_zip) == current_zip
                or not os.path.isfile(old_zip)
            ):
                continue

            os.remove(old_zip)
            print(
                "Removed old ZIP: {}".format(
                    color_text(old_zip, 'green')
                )
            )
        
    def _copy_meta_files(self, addon_id, addon_folder):
        """
        Copy the addon.xml and relevant art files into the relevant folders in the repository.
        """

        tree = ElementTree.parse(os.path.join(self.release_path, addon_id, "addon.xml"))
        root = tree.getroot()

        copyfiles = ["addon.xml"]
        for ext in root.findall("extension"):
            if ext.get("point") in ["xbmc.addon.metadata", "kodi.addon.metadata"]:
                assets = ext.find("assets")
                if assets is None:
                    continue
                for art in [a for a in assets if a.text]:
                    copyfiles.append(os.path.normpath(art.text))

        src_folder = os.path.join(self.release_path, addon_id)
        for file in copyfiles:
            addon_path = os.path.join(src_folder, file)
            if not os.path.exists(addon_path):
                continue

            zips_path = os.path.join(addon_folder, file)
            asset_path = os.path.split(zips_path)[0]
            if not os.path.exists(asset_path):
                os.makedirs(asset_path)

            shutil.copy(addon_path, zips_path)

    def _copy_root_repository_zip(self, addon_root, zip_path, addon_id, version):
        """
        Copy repository installer zips to the project root.
        """
        if not any(
            ext.get("point") == "xbmc.addon.repository"
            for ext in addon_root.findall("extension")
        ):
            return

        root_path = os.path.dirname(os.path.abspath(self.release_path))
        root_zip = os.path.join(
            root_path, "{0}-{1}.zip".format(addon_id, version)
        )
        shutil.copy(zip_path, root_zip)
        self._write_root_repository_index(root_path)
        print(
            "Root repository ZIP updated: {}".format(
                color_text(root_zip, 'yellow')
            )
        )

    def _add_repository_metadata(self, addon_root, zip_path, addon_id):
        """
        Add generated repository package metadata to an addon entry.
        """
        metadata = None
        for ext in addon_root.findall("extension"):
            if ext.get("point") in ["xbmc.addon.metadata", "kodi.addon.metadata"]:
                metadata = ext
                break

        if metadata is None:
            return

        for tag in ["size", "path"]:
            for child in metadata.findall(tag):
                metadata.remove(child)

        size = ElementTree.Element("size")
        size.text = str(os.path.getsize(zip_path))
        metadata.append(size)

        path = ElementTree.Element("path")
        path.text = "{}/{}".format(addon_id, os.path.basename(zip_path))
        metadata.append(path)

    def _write_root_repository_index(self, root_path):
        """
        Write a simple root index of repository installer zips for Kodi file manager.
        """
        links = [
            f for f in sorted(os.listdir(root_path))
            if (
                f.startswith("repository.")
                and f.endswith(".zip")
                and ".test-" not in f
            )
        ]
        body = "\n".join(
            '<a href="{0}">{0}</a><br>'.format(html.escape(f, quote=True))
            for f in links
        )
        self._save_file(
            "<!DOCTYPE html>\n<html><body>\n{}\n</body></html>\n".format(body),
            file=os.path.join(root_path, "index.html")
        )

    def _generate_addons_file(self, addons_xml_path):
        """
        Generates a zip for each found addon, and updates the addons.xml file accordingly.
        """
        if not os.path.exists(addons_xml_path):
            addons_root = ElementTree.Element('addons')
            addons_xml = ElementTree.ElementTree(addons_root)
        else:
            addons_xml = ElementTree.parse(addons_xml_path)
            addons_root = addons_xml.getroot()

        folders = self.folders or [
            i
            for i in os.listdir(self.release_path)
            if os.path.isdir(os.path.join(self.release_path, i))
            and i != "zips"
            and not i.startswith(".")
            and os.path.exists(os.path.join(self.release_path, i, "addon.xml"))
        ]

        addon_xpath = "addon[@id='{}']"
        active_ids = set()
        changed = False
        for addon in folders:
            id = addon
            try:
                addon_xml_path = os.path.join(self.release_path, addon, "addon.xml")
                addon_xml = ElementTree.parse(addon_xml_path)
                addon_root = addon_xml.getroot()
                id = addon_root.get('id')
                version = addon_root.get('version')
                active_ids.add(id)

                self._pack_media_assets(addon)
                zip_path = self._create_zip(addon, id, version)
                self._copy_meta_files(addon, os.path.join(self.zips_path, id))
                self._copy_root_repository_zip(addon_root, zip_path, id, version)
                self._add_repository_metadata(addon_root, zip_path, id)

                addon_entry = addons_root.find(addon_xpath.format(id))
                if addon_entry is not None and (
                    addon_entry.get('version') != version
                    or ElementTree.tostring(addon_entry) != ElementTree.tostring(addon_root)
                ):
                    index = addons_root.findall('addon').index(addon_entry)
                    addons_root.remove(addon_entry)
                    addons_root.insert(index, addon_root)
                    changed = True
                elif addon_entry is None:
                    addons_root.append(addon_root)
                    changed = True

            except Exception as e:
                print(
                    "Excluding {}: {}".format(
                        color_text(id, 'yellow'), color_text(e, 'red')
                    )
                )

        if self.folders is None:
            for addon_entry in list(addons_root.findall('addon')):
                if addon_entry.get('id') not in active_ids:
                    addons_root.remove(addon_entry)
                    changed = True

        addons_root[:] = sorted(addons_root, key=lambda addon: addon.get('id'))
        try:
            ElementTree.indent(addons_xml, space="    ")
            addons_xml.write(
                addons_xml_path, encoding="utf-8", xml_declaration=True
            )

            return True
        except Exception as e:
            print(
                "An error occurred updating {}!\n{}".format(
                    color_text(addons_xml_path, 'yellow'), color_text(e, 'red')
                )
            )

    def _generate_md5_file(self, addons_xml_path, md5_path):
        """
        Generates a new addons.xml.md5 file.
        """
        try:
            m = hashlib.md5(
                open(addons_xml_path, "r", encoding="utf-8").read().encode("utf-8")
            ).hexdigest()
            self._save_file(m, file=md5_path)

            return True
        except Exception as e:
            print(
                "An error occurred updating {}!\n{}".format(
                    color_text(md5_path, 'yellow'), color_text(e, 'red')
                )
            )

    def _save_file(self, data, file):
        """
        Saves a file.
        """
        try:
            open(file, "w").write(data)
        except Exception as e:
            print(
                "An error occurred saving {}!\n{}".format(
                    color_text(file, 'yellow'), color_text(e, 'red')
                )
            )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build all add-ons, or only the specified add-on folders."
    )
    parser.add_argument(
        "folders",
        nargs="*",
        help="Optional add-on folders to build, in the requested order.",
    )
    args = parser.parse_args()

    try:
        for release in [r for r in KODI_VERSIONS if os.path.exists(r)]:
            print(release)
            Generator(release, args.folders)
    except ValueError as error:
        parser.error(str(error))
