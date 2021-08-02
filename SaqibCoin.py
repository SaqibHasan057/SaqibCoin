import hashlib
import datetime
from flask import Flask,request,json
import requests

class Block:

    def __init__(self,index,timestamp,data,previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculateHash()


    def calculateHash(self):
        fn = hashlib.sha256()
        s = str(self.index)+str(self.timestamp)+str(self.data)+str(self.previous_hash)
        s = s.encode("utf-8")
        fn.update(s)
        return fn.hexdigest()


def create_genesis_block():
    genesis_block = Block(0,datetime.datetime.now(),{"proof_of_work":1,"transactions":None},"0")
    return genesis_block


def new_block(last_block,data):
    new_index = last_block.index + 1
    new_timestamp = datetime.datetime.now()
    previous_hash = last_block.hash

    return Block(new_index,new_timestamp,data,previous_hash)


def create_data(proof_of_work,transactions):
    data = {
        'proof_of_work':proof_of_work,
        'transactions':transactions
    }

    return data

def updateBlockchain(block):
    Blockchain.append(block)
    global Tail
    Tail = Blockchain[-1]



Blockchain = []
Blockchain.append(create_genesis_block())
this_nodes_transactions = []
peer_nodes = []
miner_address = "q3nf394hjg-random-miner-address-34nf3i4nflkn3oi"




##Server Functions
node = Flask(__name__)


@node.route("/transaction",methods=['POST'])
def transaction():
    if request.method=="POST":
        print(request)
        new_transaction = request.get_json()
        print(new_transaction)
        this_nodes_transactions.append(new_transaction)

        print("New Transaction!!")
        print("From:",new_transaction['from'])
        print("To:",new_transaction['to'])
        print("Amount:",new_transaction['amount'])
        print("\n")

        return "Transaction submission successful\n"


def proofOfWork(last_proof):
    incrementor = last_proof+1

    while(not(incrementor%9==0 and incrementor%last_proof==0)):
        incrementor+=1

    return incrementor


@node.route("/mine",methods=['GET'])
def mine():
    last_block = Blockchain[-1]
    last_proof_of_work = last_block.data['proof_of_work']

    new_proof_of_work = proofOfWork(last_proof_of_work)

    new_transaction = {"from":"network","to":miner_address,"amount":1}

    this_nodes_transactions.append(new_transaction)

    new_block_data = {"proof_of_work":new_proof_of_work,"transactions":list(this_nodes_transactions)}

    new_block = Block(last_block.index+1,datetime.datetime.now(),new_block_data,last_block.previous_hash)
    this_nodes_transactions.clear()
    Blockchain.append(new_block)

    return json.dumps(
        {
            "index":str(new_block.index),
            "timestamp":str(new_block.timestamp),
            "data":new_block.data,
            "previous_hash":new_block.previous_hash,
            "current_hash":new_block.hash
        }
    ) + "\n"


@node.route("/blocks",methods=["GET"])
def get_blocks():
    chain_to_send = []

    for x in Blockchain:
        block = {
            "index":str(x.index),
            "timestamp":str(x.timestamp),
            "data":x.data,
            "hash":x.hash
        }

        chain_to_send.append(block)

    return json.dumps(chain_to_send)

def find_new_chains():
    other_chains = []

    for node_url in peer_nodes:
        block = requests.get(node_url+"/blocks").content
        block = json.loads(block)
        other_chains.append(block)

    return other_chains

def consensus():
    other_chains = find_new_chains()

    global Blockchain

    longest_chain = Blockchain

    for chain in other_chains:
        if len(longest_chain)<len(chain):
            longest_chain = chain


    Blockchain = longest_chain




if __name__== "__main__":
    print(Blockchain)
    node.run()