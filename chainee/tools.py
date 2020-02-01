from argparse import ArgumentParser
import json
import sys
from chainee.block import Block
from chainee.transaction import Transaction
from chainee.utils import sha3, generate_private_key, get_pub_key, sign, recover, address_from_public, timestamp

help_message = """chainee-tools <command> [<args>]

List of commands:
createblock             Creates serialized block
createtransaction       Creates signed serialized transaction
decodeblock             Decodes serialized block
decodetransaction       Decodes serialized transaction
generateaddress         Generates new address
recover                 Recovers address from signature
sha3                    Calculates sha3 hash
sign                    Signs message
"""


def create_block_handler():
    parser = ArgumentParser(description="Creates block object")
    parser.add_argument("-number", type=int, required=True)
    parser.add_argument("-parent", type=str, required=True)
    parser.add_argument("-beneficiary", type=str, required=True)
    parser.add_argument("-target", type=int, required=True)
    parser.add_argument("-timestamp", type=int, required=False)
    parser.add_argument("-nonce", type=int, required=True)
    parser.add_argument('transactions', type=str, nargs='*')
    args = parser.parse_args(sys.argv[2:])
    block_timestamp = args.timestamp
    if block_timestamp is None:
        block_timestamp = timestamp()
    block = Block(args.number, args.parent, args.beneficiary, args.target, block_timestamp, args.nonce)
    for serialized in args.transactions:
        block.add_transaction(Transaction.deserialize(bytes.fromhex(serialized)))
    print(block.serialize().hex())


def create_transaction_handler():
    parser = ArgumentParser(description="Creates transaction object")
    parser.add_argument("-nonce", type=int, required=True)
    parser.add_argument("-out", type=str, help="{\\\"address\\\":amount,...}", required=True)
    parser.add_argument("-private_key", type=str, required=True)
    args = parser.parse_args(sys.argv[2:])
    transaction = Transaction(args.nonce, json.loads(args.out))
    transaction.sign(args.private_key)
    print(transaction.serialize().hex())


def decode_block_handler():
    parser = ArgumentParser(description="Decodes transaction object")
    parser.add_argument("data", type=str)
    args = parser.parse_args(sys.argv[2:])
    block = Block.deserialize(bytes.fromhex(args.data))
    print(json.dumps(block.to_dict(), indent=4))


def decode_transaction_handler():
    parser = ArgumentParser(description="Decodes transaction object")
    parser.add_argument("data", type=str)
    args = parser.parse_args(sys.argv[2:])
    transaction = Transaction.deserialize(bytes.fromhex(args.data))
    print(json.dumps(transaction.to_dict(), indent=4))


def generate_address_handler():
    parser = ArgumentParser(description="Generates new address")
    parser.add_argument("-seed", type=str)
    args = parser.parse_args(sys.argv[2:])
    if args.seed is not None:
        private_key = sha3(args.seed, False)
    else:
        private_key = generate_private_key()
    pub_key = get_pub_key(private_key)
    address = address_from_public(pub_key)
    print(json.dumps({
        "address": address,
        "private_key": private_key,
        "pub_key": pub_key,
    }, indent=4))


def recover_handler():
    parser = ArgumentParser(description="Recovers address from signature and original message")
    parser.add_argument("message", type=str)
    parser.add_argument("signature", type=str)
    parser.add_argument("--hex", nargs="?", const=True, default=False)
    args = parser.parse_args(sys.argv[2:])
    print(recover(args.message, args.signature, args.hex))


def sha3_handler():
    parser = ArgumentParser(description="Calculates sha3")
    parser.add_argument("input", type=str)
    parser.add_argument("--hex", nargs="?", const=True, default=False)
    args = parser.parse_args(sys.argv[2:])
    print(sha3(args.input, args.hex))


def sign_handler():
    parser = ArgumentParser(description="Calculates signature")
    parser.add_argument("message", type=str)
    parser.add_argument("-private_key", type=str, required=True)
    parser.add_argument("--hex", nargs="?", const=True, default=False)
    args = parser.parse_args(sys.argv[2:])
    print(sign(args.message, args.private_key, args.hex))


handlers = {
    "createblock": create_block_handler,
    "createtransaction": create_transaction_handler,
    "decodeblock": decode_block_handler,
    "decodetransaction": decode_transaction_handler,
    "generateaddress": generate_address_handler,
    "recover": recover_handler,
    "sha3": sha3_handler,
    "sign": sign_handler,
}


def main():
    parser = ArgumentParser(
        description="Blockchain helper tools",
        usage=help_message
    )
    parser.add_argument("command", help="Subcommand to run")
    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)
    args = parser.parse_args([sys.argv[1]])
    if args.command not in handlers:
        print("Unrecognized command")
        parser.print_help()
        exit(1)
    handlers[args.command]()
