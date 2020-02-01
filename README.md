<div align="left">
  <img src="https://raw.githubusercontent.com/Vetrovec/chainee/master/artwork/chainee.png" alt="chainee">
</div>

# chainee: Blockchain implementation

Chainee is semester programming task turned into passion project. It is not overbloated with unnecessary dependencies. Strong inspiration for this project was Ethereum.

## Installation and Usage

*This project requires Python 3.6+*

To install this project you must first clone it and then run following command in the working directory:
```
$ pip3 install .
```
After installation, commands *chainee-node* and *chainee-tools* become available.

The *chainee-node* command requires to be either run in directory containing *chainee.conf* file or to be pointed into such directory with *-datadir* argument.

## Example

The example below shows how you can create new block step by step. Let's assume you have the node running with the default configuration and you haven't added any blocks yet.

First we need to generate a new address where we are going to send the funds from genesis block to. You can use different seed or no seed at all.
```
$ chainee-tools generateaddress -seed=example
{
    "address": "b751bfbcd968a0d5836a48b68e28f62c886f50dc",
    "private_key": "70983d692f648185febe6d6fa607630ae68649f7e6fc45b94680096c06e4fadb",
    "pub_key": "..."
}
```

After that we can create the transaction saying to move the funds. Transaction nonce represents how many transactions have already been sent from an address, so setting nonce to 0 means this is going to be genesis beneficiary's first transaction.
```
$ chainee-tools createtransaction -nonce=0 \
	-out='{"b751bfbcd968a0d5836a48b68e28f62c886f50dc":1}' \
	-private_key=685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe
000001b751bfbcd9...
```

Now we need to put the transaction into new block, but to create new block you must know hash of its parent. Open node console and get hash of the first block.
```
> getblockhash 0
7af2b9ea10e70309822bc8a865fbd3a8ecacc0ad8918c0145166fba4a4765f48
```
Now we can use the hash and also the previously created transaction to create a new block.
```
$ chainee-tools createblock -number=1 \
	-parent="7af2b9ea10e70309822bc8a865fbd3a8ecacc0ad8918c0145166fba4a4765f48" \
	-beneficiary="b751bfbcd968a0d5836a48b68e28f62c886f50dc" \
	-target=0 -nonce=0 \
	000001b751bfbcd968a0d5836a48b68e28f62c886f50dc0100000000000000f03597bae1731280c28fa6eea783df89c38b622444d90bda3f22c44e8564dfb608dbcb38796f4c9bfd6577f5180f18b7160183a0facfed8df47a906d25efea3a01
010000007af2b9ea...
```
And finally we have to put the block we just created onto blockchain.
```
> submitblock 010000007af2b9ea10e70309822bc8a865fbd3a8ecacc0ad8918c0145166fba4a4765f48b751bfbcd968a0d5836a48b68e28f62c886f50dc91fa6413789b5e95971421ae7309e11b1e0484b7ecee3905dcdd816d660b2f4c000000003363355e0000000001006000000001b751bfbcd968a0d5836a48b68e28f62c886f50dc0100000000000000f03597bae1731280c28fa6eea783df89c38b622444d90bda3f22c44e8564dfb608dbcb38796f4c9bfd6577f5180f18b7160183a0facfed8df47a906d25efea3a01
```

To test if the new block was processed, you can do the following to see the data on blockchain. The hash of the new block should be different in your blockchain.
```
> getblockcount
2
> getblockhash 1
e32119c323e18f203c50614f602561d19d817cea9cdc70b61979736051888239
> getblock e32119c323e18f203c50614f602561d19d817cea9cdc70b61979736051888239
{
    "number": 1,
    ...
}
```

## To Do

* **State trie**

	Account state is stored in dictionary structure and not in tree structure. Dictionary data structures are not ideal for this, because calculating state root hash in a scalable way is a problem. The data structure should be changed and block header should contain state root in the future.

* **Improve indexing**

	Only data stored on hard disk are raw serialized blocks. All indexes are rebuilt after each node startup.

* **Transaction memory pool**

	Before adding any network protocol, transaction memory pool should be implemented.

* **Consensus mechanism**

	Absence of Proof-of-Work (or any other system) might seem like a core concept missing in this implementation; and it is. But other blockchain concepts can function without it and also there is no way to keep decentralized consensus at the moment anyway due to lack of network interface. However it's something that's expected to be added later on, block header already has a field reserved for PoW target.

* **Network interface**

	This could be standard JSON-RPC, REST API, custom P2P protocol or any combination of those. There is no way for nodes to communicate with each other or even for any remote access at the moment.

* **Scripting for transactions**

	Same way Bitcoin has Script or Ethereum has EVM, it would be nice adding more capabilities to transactions other than simple value transfer from one account to other accounts.

* **Improve code quality**

	As of right now, parts of the project were rushed and not properly debugged/audited. Also it would be nice to add more comments and more tests.

## License

[MIT](LICENSE)
