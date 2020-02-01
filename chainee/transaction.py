from typing import Any, Dict, Optional
from struct import pack, unpack
from .utils import sign, recover, validate_address, sha3


class Transaction:
    """
    Args:
        nonce (int): Account transaction nonce
        out (Dict[str, int]): Outputs of the transaction
    """
    def __init__(self, nonce: int, out: Dict[str, int]):
        self.nonce = nonce
        self.out: Dict[str, int] = {}
        self.signature: Optional[bytes] = None
        for (address, amount) in out.items():
            self.set_out(address, amount)

    def id(self) -> str:
        return sha3(self.serialize())

    def address(self) -> Optional[str]:
        if self.signature is None:
            return None
        serialized = self.serialize(False).hex()
        return recover(serialized, self.signature.hex())

    def value(self) -> int:
        value = 0
        for (_, amount) in self.out.items():
            value += amount
        return value

    def set_out(self, address: str, amount: int) -> None:
        if not validate_address(address):
            raise Exception("Address not valid")
        if amount < 1:
            raise Exception("Amount not valid")
        self.out[address] = amount

    def sign(self, private_key: str) -> None:
        serialized = self.serialize(False).hex()
        self.signature = bytes.fromhex(sign(serialized, private_key))

    def to_dict(self) -> Dict[str, Any]:
        dt = self.__dict__.copy()
        dt["id"] = self.id()
        if dt["signature"] is not None:
            dt["address"] = self.address()
            dt["signature"] = dt["signature"].hex()
        return dt

    def serialize(self, include_signature: bool = True) -> bytes:
        outLen = len(self.out)
        serialized = pack("<Hb", self.nonce, outLen)
        for (address, amount) in self.out.items():
            serialized += pack("<20sQ", bytes.fromhex(address), amount)
        if include_signature and self.signature is not None:
            serialized += self.signature
        return serialized

    @staticmethod
    def deserialize(data: bytes) -> 'Transaction':
        (nonce, outLen) = unpack("<Hb", data[:3])
        out: Dict[str, int] = {}
        i = 3
        while i < (28 * outLen + 3):
            temp = data[i:(i + 28)]
            (address, amount) = unpack("<20sQ", temp)
            out[address.hex()] = amount
            i += 28
        signature = None
        if len(data) > i:
            signature = data[i:]
        transaction = Transaction(nonce, out)
        transaction.signature = signature
        return transaction
