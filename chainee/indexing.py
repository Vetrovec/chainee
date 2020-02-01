import json
import os
import struct
from typing import Dict, Generic, List, Optional, TypeVar
from .block import Block
from .utils import validate_address

T = TypeVar('T')


class Index(Generic[T]):
    def __init__(self, parent: 'Optional[Index[T]]' = None):
        self._index: Dict[str, T] = {}
        self._parent = parent

    def keys(self) -> List[str]:
        return list(self._index.keys())

    def is_set(self, key: str) -> bool:
        return key in self._index

    def set(self, key: str, value: T) -> None:
        self._index[key] = value

    def get(self, key: str) -> Optional[T]:
        if self._parent is not None and not self.is_set(key):
            return self._parent.get(key)
        if not self.is_set(key):
            return None
        return self._index[key]

    def _serialize_key(self, key: str) -> bytes:
        return key.encode("ascii")

    def _serialize_value(self, value: T) -> bytes:
        return json.dumps(value, indent=0, separators=(',', ':')).encode("utf-8")

    def _deserialize_key(self, key: bytes) -> str:
        return key.decode("ascii")

    def _deserialize_value(self, value: bytes) -> T:
        return json.loads(value.decode("utf-8"))

    def save(self, file: str) -> None:
        os.makedirs(os.path.dirname(file), exist_ok=True)
        f = open(file, "wb")
        for key in self.keys():
            serialized_value = self._serialize_value(self.get(key))
            serialized_key = self._serialize_key(key)
            f.write(struct.pack("<BH", len(serialized_key), len(serialized_value)))
            f.write(serialized_key)
            f.write(serialized_value)
        f.close()

    def load(self, file: str, ignore: bool = True) -> None:
        f = open(file, "rb")
        line_header = f.read(3)
        while line_header != b"":
            (key_size, value_size) = struct.unpack("<BH", line_header)
            key = self._deserialize_key(f.read(key_size))
            value = self._deserialize_value(f.read(value_size))
            self.set(key, value)
            line_header = f.read(3)
        f.close()


class HexIndex(Index[str]):
    def __init__(self, parent: Optional[Index[str]] = None):
        Index.__init__(self, parent)

    def _serialize_key(self, key: str) -> bytes:
        return bytes.fromhex(key)

    def _serialize_value(self, value: str) -> bytes:
        return bytes.fromhex(value)

    def _deserialize_key(self, key: bytes) -> str:
        return key.hex()

    def _deserialize_value(self, value: bytes) -> str:
        return value.hex()


class BlockIndex(Index[Block]):
    def __init__(self, parent: Optional[Index[Block]] = None):
        Index.__init__(self, parent)

    def _serialize_key(self, key: str) -> bytes:
        return bytes.fromhex(key)

    def _serialize_value(self, value: Block) -> bytes:
        return value.serialize()

    def _deserialize_key(self, key: bytes) -> str:
        return key.hex()

    def _deserialize_value(self, value: bytes) -> Block:
        return Block.deserialize(value)


class BlockHashIndex(Index[str]):
    def __init__(self, parent: Optional[Index[str]] = None):
        Index.__init__(self, parent)

    def _serialize_key(self, key: str) -> bytes:
        return struct.pack("<L", int(key))

    def _serialize_value(self, value: str) -> bytes:
        return bytes.fromhex(value)

    def _deserialize_key(self, key: bytes) -> str:
        return str(struct.unpack("<L", key)[0])

    def _deserialize_value(self, value: bytes) -> str:
        return value.hex()


class StateIndex(Index[Dict[str, int]]):
    def __init__(self, parent: Optional[Index[Dict[str, int]]] = None):
        Index.__init__(self, parent)

    def set(self, key: str, value: Dict[str, int]) -> None:
        if not validate_address(key):
            raise Exception("Address not valid")
        Index.set(self, key, value)

    def init_account(self, address: str, balance: int = 0, nonce: int = 0) -> None:
        self.set(address, {
            "balance": balance,
            "nonce": nonce
        })

    def get_balance(self, address: str) -> int:
        account = self.get(address)
        if account is None:
            return 0
        return account["balance"]

    def get_nonce(self, address: str) -> int:
        account = self.get(address)
        if account is None:
            return 0
        return account["nonce"]

    def set_balance(self, address: str, balance: int) -> None:
        account = self.get(address)
        if account is None:
            self.init_account(address, balance)
            return
        account["balance"] = balance
        self.set(address, account)

    def set_nonce(self, address: str, nonce: int) -> None:
        account = self.get(address)
        if account is None:
            self.init_account(address, 0, nonce)
            return
        account["nonce"] = nonce
        self.set(address, account)

    def _serialize_key(self, key: str) -> bytes:
        return bytes.fromhex(key)

    def _serialize_value(self, value: Dict[str, int]) -> bytes:
        return struct.pack("<HQ", value["nonce"], value["balance"])

    def _deserialize_key(self, key: bytes) -> str:
        return key.hex()

    def _deserialize_value(self, value: bytes) -> Dict[str, int]:
        (nonce, balance) = struct.unpack("<HQ", value)
        return {
            "balance": balance,
            "nonce": nonce,
        }


def index_merge(base: Index[T], new: Index[T]) -> Index[T]:
    for key in new.keys():
        base.set(key, new.get(key))
    return base
