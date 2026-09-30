"""Publication and migration checks without building or modifying real add-ons."""
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

import _build_pages as pages
from _repo_generator import Generator, release_folders, sync_repository_addon


class RepositoryPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.site = self.root / '_site'
        for name, value in [('ROOT', self.root), ('SITE', self.site)]:
            p = patch.object(pages, name, value)
            p.start()
            self.addCleanup(p.stop)
        (self.root / 'index.html').write_text('<html></html>')
        (self.root / 'repository.signde-1.2.zip').write_bytes(b'legacy installer')
        self.make_feed('omega', [('repository.signde', '1.3'), ('skin.example', '21.1')])
        self.make_feed('piers', [('skin.example', '22.1')])
        sync_repository_addon(self.root)

    def make_feed(self, release, addons):
        zips = self.root / 'addons' / release
        zips.mkdir(parents=True, exist_ok=True)
        root = ET.Element('addons')
        for addon_id, version in addons:
            addon = ET.SubElement(root, 'addon', id=addon_id, version=version)
            ext = ET.SubElement(addon, 'extension', point='xbmc.addon.metadata')
            path = f'{addon_id}/{addon_id}-{version}.zip'
            ET.SubElement(ext, 'path').text = path
            folder = zips / addon_id
            folder.mkdir(parents=True, exist_ok=True)
            (folder / 'addon.xml').write_bytes(ET.tostring(addon))
            (folder / 'icon.png').write_bytes(b'artwork')
            with zipfile.ZipFile(zips / path, 'w') as package:
                package.writestr(f'{addon_id}/addon.xml', ET.tostring(addon))
        ET.ElementTree(root).write(zips / 'addons.xml', encoding='utf-8')
        self.checksum(release)

    def checksum(self, release):
        p = self.root / 'addons' / release / 'addons.xml'
        p.with_suffix('.xml.md5').write_text(hashlib.md5(p.read_bytes()).hexdigest())

    def test_legacy_index_packages_and_installer_remain_available(self):
        pages.build_site()
        self.assertEqual((self.site/'addons/omega/addons.xml').read_bytes(),
                         (self.site/'addons/zips/addons.xml').read_bytes())
        for suffix in ['addons.xml.md5', 'skin.example/skin.example-21.1.zip',
                       'skin.example/icon.png']:
            self.assertEqual((self.site/'addons/zips'/suffix).read_bytes(),
                             (self.root/'addons/omega'/suffix).read_bytes())
        self.assertEqual((self.site/'addons/zips/repository.signde/repository.signde-1.2.zip').read_bytes(),
                         (self.root/'repository.signde-1.2.zip').read_bytes())
        # No duplicate copy of all Omega packages in the versioned feed folder.
        self.assertFalse((self.site/'addons/omega/skin.example').exists())

    def test_same_addon_id_has_isolated_versions(self):
        pages.build_site()
        for release, expected in [('omega', '21.1'), ('piers', '22.1')]:
            root = ET.parse(self.site/'addons'/release/'addons.xml').getroot()
            self.assertEqual(root.find("addon[@id='skin.example']").get('version'), expected)
        self.assertTrue((self.site/'addons/piers/skin.example/skin.example-22.1.zip').exists())
        self.assertFalse((self.site/'addons/piers/skin.example/skin.example-21.1.zip').exists())
        self.assertFalse((self.site/'addons/zips/skin.example/skin.example-22.1.zip').exists())

    def test_shared_installer_does_not_copy_other_omega_addons(self):
        self.make_feed('piers', [])
        sync_repository_addon(self.root)
        root = ET.parse(self.root/'addons/piers/addons.xml').getroot()
        self.assertEqual([a.get('id') for a in root], ['repository.signde'])
        self.assertEqual(root[0].get('version'), '1.3')

    def test_missing_package_stops_publication(self):
        (self.root/'addons/omega/skin.example/skin.example-21.1.zip').unlink()
        with self.assertRaises(FileNotFoundError):
            pages.build_site()

    def test_bad_checksum_stops_publication(self):
        (self.root/'addons/omega/addons.xml.md5').write_text('wrong')
        with self.assertRaisesRegex(ValueError, 'checksum'):
            pages.build_site()

    def test_test_package_stops_publication(self):
        self.make_feed('omega', [('skin.example', '21.1~test2')])
        with self.assertRaisesRegex(ValueError, 'Test package'):
            pages.build_site()

    def test_package_path_cannot_escape_addon_directory(self):
        for path in ('../secret.zip', '/secret.zip', 'other/file.zip'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                pages.validate_package_path('skin.example', pages.PurePosixPath(path))

    def test_installer_version_ranges_follow_addon_api(self):
        manifest = Path(__file__).resolve().parents[1]/'addons/repository.signde/addon.xml'
        dirs = ET.parse(manifest).findall('extension/dir')
        version = lambda s: tuple(int(v) for v in s.split('.'))
        # Repository.cpp compares xbmc.addon, whose API is 21.90.x during
        # Kodi 22 development (21.90.802 for the current CoreELEC Beta 2).
        cases = [('21.0.0', 'omega'), ('21.3.0', 'omega'),
                 ('21.89.999', 'omega'), ('21.90.0', 'piers'),
                 ('21.90.700', 'piers'), ('21.90.802', 'piers'),
                 ('21.90.900', 'piers'), ('22.0.0', 'piers'),
                 ('22.3.0', 'piers'), ('22.89.999', 'piers'),
                 ('20.5.0', None), ('22.90.0', None), ('23.0.0', None)]
        for api_version, expected in cases:
            with self.subTest(api_version=api_version):
                matches = [d.findtext('info') for d in dirs
                           if version(d.get('minversion')) <= version(api_version)
                           <= version(d.get('maxversion'))]
                self.assertEqual(len(matches), 0 if expected is None else 1)
                if expected is not None:
                    self.assertIn('/'+expected+'/', matches[0])

    def make_source(self, folder, version):
        source = self.root/'addons'/folder
        source.mkdir(parents=True, exist_ok=True)
        (source/'addon.xml').write_text(
            '<addon id="skin.example" version="{}">'
            '<extension point="xbmc.addon.metadata"/></addon>'.format(version))
        return source

    def test_flat_source_build_writes_only_selected_release(self):
        self.make_source('skin.example', '21.2')
        piers = (self.root/'addons/piers/addons.xml').read_bytes()
        Generator(self.root/'addons', ['skin.example'], self.root/'addons/omega')
        self.assertTrue((self.root/'addons/omega/skin.example/skin.example-21.2.zip').exists())
        self.assertEqual((self.root/'addons/piers/addons.xml').read_bytes(), piers)
        self.assertFalse((self.root/'addons/skin.example/zips').exists())
        # A different checkout folder can publish the same ID to Piers.
        self.make_source('skin.example-piers', '22.2')
        omega = (self.root/'addons/omega/addons.xml').read_bytes()
        Generator(self.root/'addons', ['skin.example-piers'], self.root/'addons/piers')
        self.assertTrue((self.root/'addons/piers/skin.example/skin.example-22.2.zip').exists())
        self.assertEqual((self.root/'addons/omega/addons.xml').read_bytes(), omega)

    def test_empty_target_list_never_builds_all_sources(self):
        self.make_source('skin.example', '21.2')
        Generator(self.root/'addons', [], self.root/'addons/piers', prune=True)
        self.assertEqual(len(ET.parse(self.root/'addons/piers/addons.xml').getroot()), 0)
        sync_repository_addon(self.root)
        root = ET.parse(self.root/'addons/piers/addons.xml').getroot()
        self.assertEqual([a.get('id') for a in root], ['repository.signde'])
        self.assertFalse((self.root/'addons/piers/skin.example/skin.example-21.2.zip').exists())

    def test_generated_folders_are_never_sources(self):
        self.make_source('skin.example', '21.2')
        self.make_source('omega', '99.0')
        generated_cache = self.root/'addons/omega/generated.pyc'
        generated_cache.write_bytes(b'untouched')
        Generator(self.root/'addons', output_path=self.root/'addons/piers')
        self.assertEqual(generated_cache.read_bytes(), b'untouched')
        with self.assertRaises(ValueError):
            Generator(self.root/'addons', ['omega'], self.root/'addons/piers')

    def test_release_assignments_require_explicit_opt_in(self):
        (self.root/'_repo_targets.json').write_text(json.dumps({
            'omega': ['skin.example'], 'piers': []}))
        self.assertEqual(release_folders(self.root, 'piers'), [])
        self.assertEqual(release_folders(self.root, 'omega', ['addons/skin.example']), ['skin.example'])
        with self.assertRaises(ValueError):
            release_folders(self.root, 'piers', ['skin.example'])


if __name__ == '__main__':
    unittest.main()
