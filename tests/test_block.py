from unittest import TestCase
from chainee.block import Block


class TestBlock(TestCase):

    def setUp(self):
        address = "c70f4891d2ce22b1f62492605c1d5c2fc1a8ef47"
        timestamp = 1579861388
        self.block = Block(0, "0" * 64, address, 0, timestamp, 0)

    def test_hash(self):
        self.assertEqual(
            self.block.hash(),
            "075869850a068c32c4e8aca47218c3a65fa3a0de83b529af335c56a3d3c5df62"
        )

    def test_serialize(self):
        self.assertEqual(
            self.block.serialize(False).hex(),
            "000000000000000000000000000000000000000000000000000000000000000000000000c70f4891d2ce22b1f62492605c1d5c2fc1a8ef47a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a000000008cc52a5e00000000"
        )

    def test_deserialize(self):
        serialized = self.block.serialize(False)
        temp_block = Block.deserialize(serialized)
        self.assertEqual(serialized, temp_block.serialize(False))
