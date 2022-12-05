import json
import hashlib
from operator import itemgetter

from flask import Flask, render_template
from time import time
from uuid import uuid4


class Blockchain(object):
    difficulty_level = "0000"

    def __init__(self):
        self.chain = []
        self.current_transaction = []
        genesis_Hash = self.Block_Hash("genesis_block")
        self.append_block(
            Previous_block_hash=genesis_Hash,
            nonce=self.PoW(0, genesis_Hash, [])
        )

    # Hash the block
    def Block_Hash(self, block):
        # json.dumps covert the Python Object into JSON String
        blockEncoder = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(blockEncoder).hexdigest()

    # Proof of Work
    def PoW(self, index, Previous_block_hash, transactions):
        nonce = 0
        time1 = time()
        while self.validate_proof(index, Previous_block_hash,
                                  transactions, nonce) is False:
            nonce += 1
            print(nonce)
        time_total = time() - time1
        print(time_total)
        print(nonce)
        return nonce

    # Makes sure the PoW is correct
    def validate_proof(self, index, Previous_block_hash, transactions, nonce):
        data = f'{index},{Previous_block_hash},{transactions},{nonce}'.encode()
        hash_data = hashlib.sha256(data).hexdigest()
        return hash_data[:len(self.difficulty_level)] == self.difficulty_level

    # add the block to the chain
    def append_block(self, nonce, Previous_block_hash):
        block = {
            'index': len(self.chain),
            'transactions': self.current_transaction,
            'timestamp': time(),
            'nonce': nonce,
            'Previous_block_hash': Previous_block_hash
        }
        self.current_transaction = []
        self.chain.append(block)
        return block

    # add the vote to the block
    def add_vote(self, sender, voter_ID, amount):
        self.current_transaction.append({
            'amount': amount,
            'voter_ID': voter_ID,
            'sender': sender
        })
        return self.last_block['index'] + 1

    # return the last block in the block chain
    @property
    def last_block(self):
        return self.chain[-1]

    # Counts all the votes that have occurred for each candidate
    @property
    def all_blocks(self):
        temp = list(filter(lambda transactions: transactions['transactions'], self.chain))
        temp2 = list(map(itemgetter('transactions'), temp))
        vote1 = 0
        vote2 = 0
        for i in temp2:
            vote = list(map(itemgetter('amount'), i))
            vote = int(vote[0])
            if vote == 1:
                vote1 += 1
            elif vote == 2:
                vote2 += 1

        return vote1, vote2

    # Checks the voter ID to see if they already voted
    @property
    def check_vote_status(self):
        temp = list(filter(lambda transactions: transactions['transactions'], self.chain))
        temp2 = list(map(itemgetter('transactions'), temp))
        for i in temp2:
            voted = list(map(itemgetter('voter_ID'), i))
            if voted == list(map(itemgetter('voter_ID'), i)):
                print("you have already voted")
                return True

        return False


# Flask , #routes
app = Flask(__name__, template_folder="templates")
blockchain = Blockchain()
node_identifier = str(uuid4()).replace('-', "")


# routes ####################################################################################
@app.route('/blockchain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return render_template("blockchain.html", data=response)


@app.route('/', methods=['GET'])
def vote_page():
    return render_template("vote.html")


@app.route('/candidate1', methods=['GET'])
def add_vote_candidate1():
    if not blockchain.check_vote_status:
        blockchain.add_vote(
            sender="0",
            voter_ID=node_identifier,
            amount=1
        )
        last_block_hash = blockchain.Block_Hash(blockchain.last_block)
        index = len(blockchain.chain)
        nonce = blockchain.PoW(index, last_block_hash, blockchain.current_transaction)
        block = blockchain.append_block(nonce, last_block_hash)
        response = {
            'message': "new block has been added",
            'index': block['index'],
            'hash_of_previous_block': block['Previous_block_hash'],
            'nonce': block['nonce'],
            'transaction': block['transactions']
        }
        return render_template("Candidate1vote.html"), response
    else:
        return render_template("AlreadyVoted.html")


@app.route('/candidate2', methods=['GET'])
def add_vote_candidate2():
    if not blockchain.check_vote_status:
        blockchain.add_vote(
            sender="0",
            voter_ID=node_identifier,
            amount=2
        )
        last_block_hash = blockchain.Block_Hash(blockchain.last_block)
        index = len(blockchain.chain)
        nonce = blockchain.PoW(index, last_block_hash, blockchain.current_transaction)
        block = blockchain.append_block(nonce, last_block_hash)
        response = {
            'message': "new block has been added",
            'index': block['index'],
            'hash_of_previous_block': block['Previous_block_hash'],
            'nonce': block['nonce'],
            'transaction': block['transactions']
        }
        return render_template("Candidate2vote.html"), response
    else:
        return render_template("AlreadyVoted.html")


@app.route('/results', methods=['GET'])
def results():
    vote1, vote2 = blockchain.all_blocks
    response = {
        'vote1': vote1,
        'vote2': vote2
    }
    return render_template("results.html", data=response)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=int(8000))
