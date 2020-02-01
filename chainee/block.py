from typing import Any, Dict, List
from struct import pack, unpack
from .transaction import Transaction
from .utils import sha3, merkle_tree_root


class Block:
    """
    Args:
        number (int): Index of block in blockchain
        parent_hash (str): Hash of parent block
        beneficiary (str): Address of creator of the block
        target (int): Not implemented
        timestamp (int): In seconds
        nonce (int): Artibtrary data to match target
        transactions: Block transactions
    """
    def __init__(self, number: int, parent_hash: str, beneficiary: str, target: int, timestamp: int, nonce: int, transactions: List[Transaction] = []):
        self.number = number
        self.parent_hash = parent_hash
        self.beneficiary = beneficiary
        self.target = target
        self.timestamp = timestamp
        self.nonce = nonce
        self.transactions: List[Transaction] = []
        for transaction in transactions:
            self.add_transaction(transaction)

    def hash(self) -> str:
        return sha3(self.serialize(False))

    def transactions_root(self) -> str:
        if len(self.transactions) < 1:
            return sha3("")
        hashes = list(map(lambda transaction: transaction.id(), self.transactions))
        hashes.sort()
        return merkle_tree_root(hashes)

    def add_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)

    def to_dict(self) -> Dict[str, Any]:
        dt = self.__dict__.copy()
        dt["hash"] = self.hash()
        dt["transactions"] = dt["transactions"][:]
        for i in range(len(dt["transactions"])):
            dt["transactions"][i] = dt["transactions"][i].to_dict()
        return dt

    def serialize(self, includeTransactions: bool = True) -> bytes:
        serialized = pack(
            "<I32s20s32sIII",
            self.number,
            bytes.fromhex(self.parent_hash),
            bytes.fromhex(self.beneficiary),
            bytes.fromhex(self.transactions_root()),
            self.target,
            self.timestamp,
            self.nonce
        )
        if not includeTransactions:
            return serialized
        serialized += pack("<H", len(self.transactions))
        for transaction in self.transactions:
            serialized_transaction = transaction.serialize()
            serialized += pack("<H", len(serialized_transaction)) + serialized_transaction
        return serialized

    @staticmethod
    def deserialize(data: bytes) -> 'Block':
        (number, parent_hash, beneficiary, transactions_root, target, timestamp, nonce) = unpack("<I32s20s32sIII", data[:100])
        parent_hash = parent_hash.hex()
        beneficiary = beneficiary.hex()
        transactions_root = transactions_root.hex()
        block = Block(number, parent_hash, beneficiary, target, timestamp, nonce)
        if len(data) == 100:
            return block
        # transaction_count = unpack("<H", data[100:102])[0]
        transaction_block = data[102:]
        pos = 0
        while pos < len(transaction_block):
            size = unpack("<H", transaction_block[pos:(pos + 2)])[0]
            pos += 2
            transaction = transaction_block[pos:(pos + size)]
            pos += size
            transaction = Transaction.deserialize(transaction)
            block.add_transaction(transaction)
        if transactions_root != block.transactions_root():
            raise Exception('Invalid root')
        return block
