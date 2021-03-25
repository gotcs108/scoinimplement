import hashlib
import datetime
import backend

from flask import Flask
from flask import request

import json

miner_address = "...a3"


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hashblock()

    def hashblock(self):
        sha = hashlib.sha256()
        sha.update((str(self.index) + str(self.timestamp) + str(
            self.data) + str(self.previous_hash)).encode())
        return sha.hexdigest()


def create_genesis_block():
    return Block(0, datetime.datetime.now(),
                 {"proof-of-work": 9, "transactions": None}, "0")


blockchain = [create_genesis_block()]


def proof_of_work(last_proof):
    incrementer = last_proof + 1
    while not (incrementer % 9 == 0 and incrementer % last_proof == 0):
        incrementer += 1
    return incrementer


node = Flask(__name__)
transaction_list_this_node = []


@node.route('/blocks', methods=['GET'])
def get_blocks():
    chain_to_send = blockchain[:]
    # JSON needs dictionary object. Convert
    for i in range(len(chain_to_send)):
        block = chain_to_send[i]
        chain_to_send[i] = {
            "index": block.index,
            "timestamp": str(block.timestamp),
            "data": block.data,
            "hash": block.hash,
        }
    chain_to_send = json.dumps(chain_to_send)
    return json.dumps(chain_to_send)


other_chains = []


def find_other_chains():
    other_chain_urls = []
    for node_url in other_chain_urls:
        block = request.get(node_url + "/blocks").content
        block = json.loads(block)
        other_chains.append(block)
    return other_chains


def consensus():
    longest_chain = blockchain
    for chain in other_chains:
        if longest_chain < chain.len():
            longest_chain = chain
    return longest_chain

@node.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain[len(blockchain) - 1]
    last_proof = last_block.data['proof-of-work']

    proof = proof_of_work(last_proof)
    transaction_list_this_node.append({"from": "network", "to": miner_address,
                                       "amount": 1})

    new_block_index = last_block.index + 1
    new_block_timestamp = datetime.datetime.now()
    last_block_hash = last_block.hash
    new_block_data = {
        "proof-of-work": proof,
        "transactions": list(transaction_list_this_node)
    }
    transaction_list_this_node[:] = []
    mined_block = Block(
        new_block_index,
        new_block_timestamp,
        new_block_data,
        last_block_hash
    )

    blockchain.append(mined_block)

    return json.dumps({
        "index": mined_block.index,
        "timestamp": str(mined_block.timestamp),
        "data": mined_block.data,
        "hash": mined_block.hash
    }) + "\n"


# Add a URL rule.
@node.route('/transaction', methods=['POST'])
def transaction():
    if request.method == "POST":
        new_transaction = request.get_json()
        transaction_list_this_node.append(new_transaction)
        print("New Transaction")
        print("FROM: {}".format(new_transaction['from']))
        print("TO: {}".format(new_transaction['to']))
        print("AMOUNT: {}".format(new_transaction['amount']))
        return "Submitted Transaction Successfully\n"


node.run()
