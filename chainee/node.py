from argparse import ArgumentParser
from configparser import ConfigParser
import json
import os
import sys
import traceback
from chainee.blockchain import Blockchain
from chainee.block import Block

intro_message = """
   _____ _    _          _____ _   _ ______ ______
  / ____| |  | |   /\\   |_   _| \\ | |  ____|  ____|
 | |    | |__| |  /  \\    | | |  \\| | |__  | |__
 | |    |  __  | / /\\ \\   | | | . ` |  __| |  __|
 | |____| |  | |/ ____ \\ _| |_| |\\  | |____| |____
  \\_____|_|  |_/_/    \\_\\_____|_| \\_|______|______|

Type in 'help' for list of available commands"""

help_message = """List of commands:
getaccount <adddress>   Prints balance and nonce
getblock <hash>         Prints content of a block
getblockcount           Prints number of blocks in chain
getblockhash <index>    Prints hash of a block by index
getinfo                 Prints info about blockchain state
gettransaction <id>     Prints content of transaction
help                    Prints help
stop                    Stops node
submitblock <data>      Pushes block into chain"""


def get_account_handler(blockchain, args):
    print({
        "balance": blockchain.get_balance(args[0]),
        "nonce": blockchain.get_nonce(args[0]),
    })


def get_block_handler(blockchain, args):
    print(json.dumps(blockchain.get_block(args[0]).to_dict(), indent=4))


def get_block_count_handler(blockchain, args):
    print(blockchain.block_count)


def get_block_hash_handler(blockchain, args):
    print(blockchain.get_block_hash(int(args[0])))


def get_info_handler(blockchain, args):
    print("not implemented")


def get_transaction_handler(blockchain, args):
    print(json.dumps(blockchain.get_transaction(args[0]).to_dict(), indent=4))


def help_handler(blockchain, args):
    print(help_message)


def stop_handler(blockchain, args):
    blockchain.save()
    exit(0)


def submit_block_handler(blockchain, args):
    block = Block.deserialize(bytes.fromhex(args[0]))
    blockchain.add_block(block)


commands = {
    "getaccount": get_account_handler,
    "getblock": get_block_handler,
    "getblockcount": get_block_count_handler,
    "getblockhash": get_block_hash_handler,
    "getinfo": get_info_handler,
    "gettransaction": get_transaction_handler,
    "help": help_handler,
    "stop": stop_handler,
    "submitblock": submit_block_handler,
}


def main():
    arg_parser = ArgumentParser(
        description="Blockchain node",
        usage="chainee-node",
    )
    arg_parser.add_argument("-datadir", type=str, help="Path to data directory", default=".")
    arg_parser.add_argument("--debug", nargs="?", const=True, default=False)
    if len(sys.argv) > 1:
        args = arg_parser.parse_args([sys.argv[1]])
    else:
        args = arg_parser.parse_args([])

    config_parser = ConfigParser()
    try:
        with open(os.path.join(args.datadir, "chainee.conf")) as stream:
            config_parser.read_string("[DEFAULT]\n" + stream.read())
    except IOError:
        print("Config in data dir not found. Quitting...")
        exit(1)
    config = {}
    for key in config_parser["DEFAULT"]:
        config[key] = config_parser["DEFAULT"][key]

    blockchain = Blockchain({
        "datadir": os.path.abspath(args.datadir),
    })
    blockchain.load()
    if blockchain.block_count < 1:
        blockchain.add_block(Block(
            0,
            "0" * 64,
            config["genesisbenficiary"],
            2 ** 32 - 1,
            int(config["genesistimestamp"]),
            0,
        ))

    print(intro_message)
    while True:
        print("> ", end="")
        command = input().split(" ")
        base = command[0].lower()
        if base not in commands:
            print("Unrecognized command")
            continue
        try:
            commands[base](blockchain, command[1:])
        except Exception as e:
            print(str(e))
            if args.debug:
                traceback.print_tb(e.__traceback__)
