from secp256k1 import PrivateKey, PublicKey, ALL_FLAGS
from hashlib import sha3_256
from os import urandom
from time import time
from typing import List, Union

hexdigits = "0123456789abcdef"
# https://www.secg.org/sec2-v2.pdf
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def timestamp() -> int:
    return int(time())


def is_hex_string(input: str) -> bool:
    return all(c in hexdigits for c in input.lower())


# TODO: Not implemented
def unpack_target(packed_target: int) -> int:
    size = packed_target >> 24
    word = packed_target & 0x7FFFFF
    if size <= 3:
        return word >> 8 * (3 - size)
    return word << 8 * (size - 3)


# private key in string hex format without padding zeros is still considered valid
def validate_private_key(private_key: Union[str, int]) -> bool:
    if type(private_key) == str:
        if not is_hex_string(private_key):
            return False
        private_key = int(private_key, 16)
    return private_key > 0 and private_key < n


def validate_address(address: str) -> bool:
    return is_hex_string(address) and len(address) == 40


def sha3(input: Union[bytes, str], hex: bool = True) -> str:
    if type(input) == str and hex:
        input = bytes.fromhex(input)
    elif type(input) == str:
        input = input.encode("utf-8")
    hash = sha3_256()
    hash.update(input)
    return hash.hexdigest()


def merkle_tree_root(arr: List[str]) -> str:
    tree = list(map(lambda e: sha3(e, is_hex_string(e)), arr))
    if len(tree) % 2 == 1:
        tree.append(tree[-1])
    while len(tree) > 1:
        temp = []
        for i in range(0, len(tree), 2):
            temp.append(sha3(tree[i] + tree[i + 1]))
        tree = temp
    return tree[0]


def generate_private_key() -> str:
    """
    Returns:
        private_key (str): 32 bytes on secp256k1 curve encoded as hex string
    """
    rand = 0
    while not validate_private_key(rand):
        rand = int(urandom(32).hex(), 16)
    return hex(rand)[2:].rjust(64, '0')


def get_pub_key(private_key: str) -> str:
    """
    Returns:
        pub_key (str): Public key in uncompressed format without "04" prefix
    """
    private_key = private_key.rjust(64, '0')
    pub_key: str = PrivateKey(bytes.fromhex(private_key)).pubkey.serialize(False).hex()[2:]
    return pub_key


def address_from_public(pub_key: str) -> str:
    """
    Args:
        pub_key (str): Public key in uncompressed format without "04" prefix

    Returns:
        address (str): Address of the public key
    """
    return sha3(pub_key, True)[-40:]


def address_from_private(private_key: str) -> str:
    pub_key = get_pub_key(private_key)
    address = address_from_public(pub_key)
    return address


# returns recoverable signature with recovery bit appended at the end
def sign(message: Union[bytes, str], private_key: str, hex: bool = True) -> str:
    """Signs input data with provided private key

    Args:
        message (str): Data to sign
        private_key (str): Private key to sign the data with
        hex (bool): Hex string is provided as input message

    Returns:
        signature (str): Recoverable signature with appended recovery bit
    """
    if type(message) == str and hex:
        data = bytes.fromhex(message)
    elif type(message) == str:
        data = message.encode("utf-8")
    else:
        data = message
    private_key = PrivateKey(bytes.fromhex(private_key))
    signature = private_key.ecdsa_sign_recoverable(data, digest=sha3_256)
    (signature, recovery) = private_key.ecdsa_recoverable_serialize(signature)
    signature += bytes([recovery])
    return signature.hex()


# returns address
def recover(message: Union[bytes, str], signature: str, hex: bool = True) -> str:
    """Signs input data with provided private key

    Args:
        message (str): Message to recover address from
        signature (str): Signature with recovery bit
        hex (bool): Hex string is provided as input message

    Returns:
        signature (str): Recoverable signature with appended recovery bit
    """
    if type(message) == str and hex:
        data = bytes.fromhex(message)
    elif type(message) == str:
        data = message.encode("utf-8")
    else:
        data = message
    pub_key = PublicKey(flags=ALL_FLAGS)
    signature = bytes.fromhex(signature)
    signature = pub_key.ecdsa_recoverable_deserialize(signature[:-1], int.from_bytes(signature[-1:], "big"))
    pub_key = PublicKey(pub_key.ecdsa_recover(data, signature, digest=sha3_256))
    return address_from_public(pub_key.serialize(False).hex()[2:])
