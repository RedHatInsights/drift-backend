import unittest
from mock import MagicMock

from kerlescan import profile_parser

from kerlescan.exceptions import UnparsableNEVRAError


class InfoParserTests(unittest.TestCase):
    def test_package_parsing(self):
        tests = {
            "0:bluejeans-1.37.22-1": ("bluejeans", "1.37.22-1"),
            "0:brscan4-0.4.7-1": ("brscan4", "0.4.7-1"),
            "0:epel-release-7-11": ("epel-release", "7-11"),
            "0:gpg-pubkey-fd431d51-4ae0493b": ("gpg-pubkey", "fd431d51-4ae0493b"),
            "0:hll2395dwpdrv-4.0.0-1": ("hll2395dwpdrv", "4.0.0-1"),
            "0:skypeforlinux-8.34.0.78-1": ("skypeforlinux", "8.34.0.78-1"),
            "0:gpg-pubkey-f4a80eb5-53a7ff4b": ("gpg-pubkey", "f4a80eb5-53a7ff4b"),
            "no_epoch-1-1": ("no_epoch", "1-1"),
        }

        for pkg_string in tests:
            name, vra = profile_parser._get_name_vra_from_string(pkg_string)
            self.assertEqual((name, vra), tests[pkg_string])

    def test_bad_package_parsing(self):
        with self.assertRaises(UnparsableNEVRAError):
            profile_parser._get_name_vra_from_string("this-will_not_parse")

    def test_running_process_parsing(self):
        profile = {"id": "1234", "running_processes": ["vim", "vim", "doom.exe"]}
        fake_plastic_tree = MagicMock()
        result = profile_parser.parse_profile(
            profile, "some_display_name", fake_plastic_tree
        )
        self.assertEqual(result["running_processes.vim"], "2")
        self.assertEqual(result["running_processes.doom.exe"], "1")

    def test_network_interface_parsing(self):
        profile = {
            "id": "1234",
            "network_interfaces": [
                {"mtu": 9876, "name": "fake-nic"},
                {"name": "no_mtu"},
            ],
        }
        fake_plastic_tree = MagicMock()
        result = profile_parser.parse_profile(
            profile, "some_display_name", fake_plastic_tree
        )
        self.assertEqual(result["network_interfaces.fake-nic.mtu"], "9876")
        self.assertEqual(result["network_interfaces.no_mtu.mtu"], "N/A")
