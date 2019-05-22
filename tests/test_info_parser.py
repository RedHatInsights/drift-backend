import unittest

from drift import info_parser

from drift.exceptions import UnparsableNEVRAError


class InfoParserTests(unittest.TestCase):

    def test_package_parsing(self):
        tests = {"epoch:name-version-release.arch": ('name', 'version-release.arch'),
                 "0:bluejeans-1.37.22-1": ('bluejeans', '1.37.22-1'),
                 "0:brscan4-0.4.7-1": ('brscan4', '0.4.7-1'),
                 "0:epel-release-7-11": ('epel-release', '7-11'),
                 "0:gpg-pubkey-fd431d51-4ae0493b": ('gpg-pubkey', 'fd431d51-4ae0493b'),
                 "0:hll2395dwpdrv-4.0.0-1": ('hll2395dwpdrv', '4.0.0-1'),
                 "0:skypeforlinux-8.34.0.78-1": ('skypeforlinux', '8.34.0.78-1'),
                 "0:gpg-pubkey-f4a80eb5-53a7ff4b": ('gpg-pubkey', 'f4a80eb5-53a7ff4b'),
                 "no_epoch-1-1": ('no_epoch', '1-1')}

        for pkg_string in tests:
            name, vra = info_parser._get_name_vra_from_string(pkg_string)
            self.assertEqual((name, vra), tests[pkg_string])

    def test_bad_package_parsing(self):
        with self.assertRaises(UnparsableNEVRAError):
            info_parser._get_name_vra_from_string("this-will_not_parse")
