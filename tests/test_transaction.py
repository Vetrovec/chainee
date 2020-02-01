from unittest import TestCase
from chainee.transaction import Transaction


class TestTransaction(TestCase):

    def setUp(self):
        private_key = "685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe"
        out = {
            "38fb65b08416b9870067b6cba63fa50a81bc78c8": 100
        }
        self.transaction = Transaction(1, out)
        self.transaction.sign(private_key)

    def test_id(self):
        self.assertEqual(
            self.transaction.id(),
            "d1ed0b9ab80eb6dcacb8d54cc164700e34a1950fbe0589a181b158568f7c4041"
        )

    def test_address(self):
        self.assertEqual(
            self.transaction.address(),
            "c70f4891d2ce22b1f62492605c1d5c2fc1a8ef47"
        )

    def test_value(self):
        self.assertEqual(self.transaction.value(), 100)

    def test_serialize(self):
        self.assertEqual(
            self.transaction.serialize().hex(),
            "01000138fb65b08416b9870067b6cba63fa50a81bc78c8640000000000000034c4ac66523f355dba984e99baff0d991096bcf52b64909201a604b78fb48433106b598de5a8a69a79655414338dc43f8f197ed0d607e29f12d6f67b6fb852a301"
        )

    def test_deserialize(self):
        serialized = self.transaction.serialize()
        temp_transaction = Transaction.deserialize(serialized)
        self.assertEqual(serialized, temp_transaction.serialize())
