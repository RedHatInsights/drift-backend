import unittest

from kerlescan import profile_parser

from kerlescan.exceptions import UnparsableNEVRAError


class PackageParserTests(unittest.TestCase):
    def test_package_parsing(self):
        tests = {
            "0:bluejeans-1.37.22-1": ("bluejeans", "1.37.22-1"),
            "0:brscan4-0.4.7-1": ("brscan4", "0.4.7-1"),
            "0:epel-release-7-11": ("epel-release", "7-11"),
            "0:gpg-pubkey-fd431d51-4ae0493b": ("gpg-pubkey", "fd431d51-4ae0493b"),
            "0:hll2395dwpdrv-4.0.0-1": ("hll2395dwpdrv", "4.0.0-1"),
            "0:skypeforlinux-8.34.0.78-1": ("skypeforlinux", "8.34.0.78-1"),
            "0:gpg-pubkey-f4a80eb5-53a7ff4b": ("gpg-pubkey", "f4a80eb5-53a7ff4b"),
            "7:squid-3.5.20-12.el7_6.1": ("squid", "3.5.20-12.el7_6.1"),
            "bluejeans-0:1.37.22-1": ("bluejeans", "1.37.22-1"),
            "brscan4-0:0.4.7-1": ("brscan4", "0.4.7-1"),
            "epel-release-0:7-11": ("epel-release", "7-11"),
            "gpg-pubkey-0:fd431d51-4ae0493b": ("gpg-pubkey", "fd431d51-4ae0493b"),
            "hll2395dwpdrv-0:4.0.0-1": ("hll2395dwpdrv", "4.0.0-1"),
            "skypeforlinux-0:8.34.0.78-1": ("skypeforlinux", "8.34.0.78-1"),
            "gpg-pubkey-0:f4a80eb5-53a7ff4b": ("gpg-pubkey", "f4a80eb5-53a7ff4b"),
            "xfsprogs-0:4.5.0-20.el7.x86_64": ("xfsprogs", "4.5.0-20.el7.x86_64"),
            "squid-7:3.5.20-12.el7_6.1": ("squid", "3.5.20-12.el7_6.1"),
            "no_epoch-1-1": ("no_epoch", "1-1"),
        }

        for pkg_string in tests:
            name, vra = profile_parser._get_name_vra_from_string(pkg_string)
            self.assertEqual((name, vra), tests[pkg_string])

    def test_bad_package_parsing(self):
        with self.assertRaises(UnparsableNEVRAError):
            profile_parser._get_name_vra_from_string("this-will_not_parse")


class IntegerParserTests(unittest.TestCase):
    def test_cores_per_socket_parsing(self):
        tests = {"id": "548f28c4-752d-11ea-b35c-54e1add9c7a0"}

        parsed_profiles = profile_parser.parse_profile(tests, "fake-name", None)
        self.assertEqual(parsed_profiles["cores_per_socket"], "N/A")
