from os import path
from typing import Optional
from .block import Block
from .transaction import Transaction
from .indexing import BlockIndex, BlockHashIndex, HexIndex, StateIndex, index_merge


class Blockchain:
    def __init__(self, config={}):
        self.config = config
        self.block_count = 0
        self.block_index = BlockIndex()
        self.block_hash_index = BlockHashIndex()
        self.state_index = StateIndex()
        self.transaction_index = HexIndex()

    def get_latest_block(self) -> Block:
        hash = self.get_block_hash(self.block_count - 1)
        return self.get_block(hash)

    def get_genesis_block(self) -> Block:
        hash = self.get_block_hash(0)
        return self.get_block(hash)

    def add_block(self, block: Block) -> None:
        self.validate_block_header(block)
        next_state = self.calculate_next_state(block)
        self.block_index.set(block.hash(), block)
        self.block_hash_index.set(str(block.number), block.hash())
        for transaction in block.transactions:
            self.transaction_index.set(transaction.id(), block.hash())
        index_merge(self.state_index, next_state)
        self.block_count += 1

    def validate_transaction(self, transaction: Transaction, state: StateIndex = None) -> None:
        if state is None:
            state = self.state_index
        for (address, value) in transaction.out.items():
            if address == transaction.address():
                raise Exception("Receiver same as sender")
        if transaction.value() > state.get_balance(transaction.address()):
            raise Exception("Insufficient balance")
        if transaction.nonce < state.get_nonce(transaction.address()):
            raise Exception("Previously used nonce")

    def validate_block_header(self, block: Block) -> None:
        next_number = 0
        parent_hash = "".rjust(64, '0')
        latest = self.get_latest_block()
        if latest is not None:
            next_number = latest.number + 1
            parent_hash = latest.hash()
        if next_number != block.number:
            raise Exception("Invalid number")
        if parent_hash != block.parent_hash:
            raise Exception("Invalid parent hash")

    def calculate_next_state(self, block: Block) -> StateIndex:
        state = StateIndex(self.state_index)
        for transaction in block.transactions:
            self.validate_transaction(transaction, state)
            nonce = state.get_nonce(transaction.address())
            for (address, value) in transaction.out.items():
                receiver_balance = state.get_balance(address) + value
                state.set_balance(address, receiver_balance)
            sender_balance = state.get_balance(transaction.address()) - transaction.value()
            state.set_balance(transaction.address(), sender_balance)
            state.set_nonce(transaction.address(), nonce + 1)
        beneficiary_balance = state.get_balance(block.beneficiary)
        self.state_index.set_balance(block.beneficiary, beneficiary_balance + 10)
        return state

    def get_block(self, hash: str) -> Optional[Block]:
        return self.block_index.get(hash)

    def get_block_hash(self, number: int) -> Optional[str]:
        return self.block_hash_index.get(str(number))

    def get_transaction(self, id: str) -> Optional[Transaction]:
        block_hash = self.transaction_index.get(id)
        if block_hash is None:
            return None
        block = self.get_block(block_hash)
        for transaction in block.transactions:
            if transaction.id() == id:
                return transaction
        return None

    def get_balance(self, address: str) -> int:
        return self.state_index.get_balance(address)

    def get_nonce(self, address: str) -> int:
        return self.state_index.get_nonce(address)

    def save(self) -> None:
        basedir = path.join(self.config["datadir"], "data")
        self.block_index.save(path.join(basedir, "blocks.dat"))

    def load(self) -> None:
        basedir = path.join(self.config["datadir"], "data")
        if path.exists(path.join(basedir, "blocks.dat")):
            block_index = BlockIndex()
            block_index.load(path.join(basedir, "blocks.dat"))
            for block_hash in block_index.keys():
                self.add_block(block_index.get(block_hash))
