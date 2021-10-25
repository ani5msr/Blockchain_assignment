import urllib.request
import json
import random
import socket
import redis
import zmq 
from blockchain_component import Block, Blockchain
from collections import defaultdict
from utils import decode_redis, get_own_ip

blockchain = Blockchain()
class Election:
    def __init__(self):
        self.primary_representatives = dict()
        self.fund_addr = ""
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.redis_client.hmset('fund '+self.fund_addr, {'total fund': 00})
        self.this_node_addr = get_own_ip()
        self.stakes_map = dict()
        self.votes_map = dict()
        self.load_election_fund_details()
    # this function will load all the current funds of the elction, which is the share a particular stakeholder has in the blockchain
    def load_election_fund_details(self):
        f = open('electionfund.json', 'r')
        data = json.load(f)
        self.fund_addr = data["address"]
    # this function broadcasts the election to all the nodes in the blockchain using sockets
    def broadcastmessage(message):
        host = '0.0.0.0'
        port = '6010'
        udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpsock.bind((host, port))
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_data = decode_redis(redis_client.hgetall("nodes_map")) # a mapping of the nodes according if they are in a list, a dictionary or in bytes
        for ip_addr, raw_data in redis_data.items():   # this is a loop which iterates through all the IP addresses and broadcasts the vote given to all nodes in blockchain
            data = json.loads(raw_data)
            udpsock.sendto(message.encode('utf-8'),
                           (ip_addr, data["receiver_port"]))
        udpsock.close()

    def scan_election_fund(self):
        txs = blockchain.get_txs_by_addr(self.fund_addr)
        pipe = self.redis_client.pipeline()
        for tx in txs:
            for output in tx.outputs:
                if output.address == self.fund_addr:
                    if tx.inputs > 0:
                        pipe.hincrbyfloat(
                            "stakes_map", tx.inputs[0].address, output.value)
        pipe.execute()
    # this function gets all the stakes of all the nodes present in the blockchain
    def get_stakes(self):
        self.stakes_map = decode_redis(self.redis_client.hgetall("stakes_map"))
    # this function casts the votes 
    def castvote(self, data):
        self.broadcastmessage({
            "command": "voteto",
            "data": data
        })
    # this function elects a delegate according to its stake in the blockchain and selects a representative
    def elect_delegate(self):
        total_stake = 0
        arr = []
        for key, val in self.stakes_map.items():
            total_stake += int(val)
            for i in range(0, int(val)):
                arr.append(key)
        if total_stake == 0:
            return
        select = arr[random.randint(0, total_stake-1)]
        self.votes_map[self.this_node_addr] = select
        self.castvote(json.dumps(
            {"node_addr": self.this_node_addr, "representative": select}))
    # this function casts the vote  by the voter ip address to a voted ip address that can be changed by select
    def vote_to(self):
        # Broadcast the selected node to vote
        self.broadcastmessage(json.dumps(
         {'data': {"voter_addr": self.this_node_addr, "voted_addr": select}, 'command': 'voteto'}))
        context = zmq.Context()
        z2socket = context.socket(zmq.REQ)
        z2socket.connect("tcp://127.0.0.1:5060")
        z2socket.send_string(json.dumps({'data':{"voter_addr":self.this_node_addr, "voted_addr":select},'command': 'voteto'}))
        message = z2socket.recv()
        print(message)
        z2socket.close()

    def add_vote(self, vote):
        self.votes.update(vote)
    # this function counts all the votes voted by all the nodes in the network
    def delegates(self):
        votes_count = defaultdict(int)
        for key, val in self.votes.items():
            votes_count[val] += 1
        votes_count = sorted(votes_count.items(),
                             key=lambda kv: (kv[1], kv[0]))
        dels = []
        if len(votes_count) > 10:
            dels = list(reversed(list(votes_count)))[0:10]
        else:
            dels = list(reversed(list(votes_count)))
        return dels