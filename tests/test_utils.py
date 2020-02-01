from unittest import TestCase
import chainee.utils as utils


class TestUtils(TestCase):

    def test_is_hex_string(self):
        self.assertTrue(utils.is_hex_string("AbCdeF1234567890"), "is hex")
        self.assertFalse(utils.is_hex_string("abcdefg"), "is not hex")

    def test_validate_private_key(self):
        self.assertTrue(
            utils.validate_private_key("685CF62751CEF607271ED7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe"),
            "is valid private key"
        )
        self.assertFalse(
            utils.validate_private_key("0000000000000000000000000000000000000000000000000000000000000000"),
            "is not valid private key"
        )
        self.assertFalse(
            utils.validate_private_key("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"),
            "is not valid private key"
        )

    def test_validate_address(self):
        self.assertTrue(
            utils.validate_address("0000000000000000000000000000000000000000"),
            "is valid address"
        )
        self.assertTrue(
            utils.validate_address("c70f4891d2ce22b1f62492605c1d5c2fc1a8ef47"),
            "is valid address"
        )
        self.assertFalse(
            utils.validate_address("1234567890"),
            "is not valid address"
        )
        self.assertFalse(
            utils.validate_address("abcdefghijklmnopqrstuvwxyzabcdefghijklmn"),
            "is not valid address"
        )

    def test_sha3(self):
        self.assertEqual(
            utils.sha3("abcdef"),
            "8b8a2a6bc589cd378fc57f47d5668c58b31167b2bf9e632696e5c2d50fc16002"
        )
        self.assertEqual(
            utils.sha3("test", False),
            "36f028580bb02cc8272a9a020f4200e346e276ae664e45ee80745574e2f5ab80"
        )

    def test_generate_private_key(self):
        self.assertTrue(
            utils.validate_private_key(utils.generate_private_key()),
            "should generate valid private key"
        )

    def test_get_pub_key(self):
        self.assertEqual(
            utils.get_pub_key("685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe"),
            "6b2cc423e68813a13b4f0b3c7666939d20f845a40104a3c85db2d8a3bcfd9517620075fac7de10a94073ab9a09a9a8dd28bb44adaaf24bf334a6c6258524dd08"
        )

    def test_address_from_public(self):
        self.assertEqual(
            utils.address_from_public("6b2cc423e68813a13b4f0b3c7666939d20f845a40104a3c85db2d8a3bcfd9517620075fac7de10a94073ab9a09a9a8dd28bb44adaaf24bf334a6c6258524dd08"),
            "c70f4891d2ce22b1f62492605c1d5c2fc1a8ef47"
        )

    def test_address_from_private(self):
        self.assertEqual(
            utils.address_from_private("685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe"),
            "c70f4891d2ce22b1f62492605c1d5c2fc1a8ef47"
        )

    def test_sign(self):
        self.assertEqual(
            utils.sign("abcdef", "685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe"),
            "b90e97baea96a2120a53d3ba34201705891e79beb8b86cfaf26a4e467264ac6e2481ffed9036a8403161d1d0bf7a7485f6e190d1ffdc1bccefd74fe6c547b30a01"
        )
        self.assertEqual(
            utils.sign("test", "685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe", False),
            "6f2dfa18ba808d126ef8d7664cbb5331a4464f6ab739f82981a179e47569550636daa57960b6bfeef2981ea61141ce34b2febe811394ce3b46ffde0ce121516101"
        )

    def test_recover(self):
        self.assertEqual(
            utils.recover("abcdef", "b90e97baea96a2120a53d3ba34201705891e79beb8b86cfaf26a4e467264ac6e2481ffed9036a8403161d1d0bf7a7485f6e190d1ffdc1bccefd74fe6c547b30a01"),
            "c70f4891d2ce22b1f62492605c1d5c2fc1a8ef47"
        )
        self.assertEqual(
            utils.recover("test", "6f2dfa18ba808d126ef8d7664cbb5331a4464f6ab739f82981a179e47569550636daa57960b6bfeef2981ea61141ce34b2febe811394ce3b46ffde0ce121516101", False),
            "c70f4891d2ce22b1f62492605c1d5c2fc1a8ef47"
        )
