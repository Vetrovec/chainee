from unittest import TestCase
from chainee.block import Block
from chainee.blockchain import Blockchain
from chainee.transaction import Transaction


class TestBlockchain(TestCase):

    def setUp(self):
        self.blockchain = Blockchain()
        address = "c70f4891d2ce22b1f62492605c1d5c2fc1a8ef47"
        timestamp = 1579861388
        self.genesis = Block(0, "0" * 64, address, 0, timestamp, 0)
        self.transaction = Transaction(0, {
            "0000000000000000000000000000000000000000": 5
        })
        self.transaction.sign(
            "685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe")
        self.block = Block(1, self.genesis.hash(), address,
                           0, timestamp + 60, 0, [self.transaction])
        self.blockchain.add_block(self.genesis)
        self.blockchain.add_block(self.block)

    def test_get_latest_block(self):
        self.assertEqual(
            self.block.hash(),
            self.blockchain.get_latest_block().hash()
        )

    def test_get_genesis_block(self):
        self.assertEqual(
            self.genesis.hash(),
            self.blockchain.get_genesis_block().hash()
        )

    def test_get_block(self):
        self.assertEqual(
            self.block.hash(),
            self.blockchain.get_block(self.block.hash()).hash()
        )

    def test_get_block_hash(self):
        self.assertEqual(
            self.block.hash(),
            self.blockchain.get_block_hash(1)
        )

    def test_get_transaction(self):
        self.assertEqual(
            self.transaction.id(),
            self.blockchain.get_block(self.block.hash()).transactions[0].id()
        )

    def test_get_balance(self):
        self.assertEqual(
            5,
            self.blockchain.get_balance("0000000000000000000000000000000000000000")
        )

    def test_get_nonce(self):
        self.assertEqual(
            1,
            self.blockchain.get_nonce("c70f4891d2ce22b1f62492605c1d5c2fc1a8ef47")
        )
