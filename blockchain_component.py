from hashlib import sha256
from datetime import datetime
from ecdsa import SigningKey, SECP256k1, VerifyingKey
import json
import requests
from flask import request

class Block:
	def __init__(self, index, block_timestamp, transactions, prev_hash, proof_of_work=0):
		self.index = index
		self.block_timestamp = block_timestamp
		self.transactions = transactions
		self.prev_hash = prev_hash
		self.proof_of_work = proof_of_work

	# hash of complete block along with the proof of work using sha256.
	@property 
	def hash(self):
		block_string = str(self.index) + str(self.block_timestamp) + str(self.transactions) + str(self.prev_hash) + str(self.proof_of_work)
		return sha256(block_string.encode()).hexdigest()


class Blockchain:
	def __init__(self):
		#hash should start with this no. of zeros for proof_of_work
		self.zeros_difficulty = 4
		self.unverified_transactions = []
		self.chain = []
		self.genesis_block() #genesis block will be created with initialization.

	# genesis block is the first block in a blockchain, its prev_hash would be 0
	def genesis_block(self):
		g_block = Block(0, str(0), [], 0, 0)
		self.chain.append(g_block)

	@property 
	def last_block(self):
		if self.chain:
			return self.chain[-1]
		else:
			return False
	
	# the block should have valid prev_hash and valid proof_of_work to be added in blockchain.
	def add_block(self, block):
		if self.last_block and self.last_block.hash == block.prev_hash:
			if self.is_valid_proof(block):
				self.chain.append(block)
				return True
		return False

	def mine(self):
		'''this adds all unverified transactions into a block first and
			finds valid proof_of_work for that block in order to 
			add it to blockchain'''
		if not self.unverified_transactions:
			return False
		else:
			# to consider only valid transaction by verifying signature.
			for transaction in self.unverified_transactions:
				if not self.is_valid_transaction(transaction): 
					self.unverified_transactions.remove(transaction) 

			new_block = Block(index= self.last_block.index + 1, block_timestamp= str(datetime.now()), 
						transactions= self.unverified_transactions, prev_hash= self.last_block.hash)

			#Calulates proof_of_work
			while not new_block.hash.startswith('0' * self.zeros_difficulty):
				new_block.proof_of_work += 1

			self.add_block(new_block)
			self.unverified_transactions = [] 
			return new_block
			return True

	# to verify signature of transaction.
	def is_valid_transaction(self, transaction_dict):
		signature = transaction_dict['signature']
		signature = bytes.fromhex(signature) #converting hex string back to bytes to be able to verify.
		public_key = transaction_dict['message']['from_addr']
		public_key = VerifyingKey.from_string(bytes.fromhex(public_key), curve=SECP256k1) #getting public key in bytes from public key in hex string format.
		msg = json.dumps(transaction_dict['message']).encode() #converting msg back in bytes format.
		if public_key.verify(signature, msg):
			return True
		return False

	# checking if block hash(calculated with proof_of_work) starts with given no. of zeros_difficulty
	def is_valid_proof(self, block):
		if block.hash.startswith('0' * self.zeros_difficulty):
			return True

	# announce block to other peers
	def announce_block(self, peers, block_obj):
		for peer in peers:
			if peer != request.host_url:
				response = requests.post(peer+'add_block', json= block_obj.__dict__)

	def generate_signature(self, readable_sk, msg):
		# msg is just a transaction dict.
		# converting from readable format to SigningKey object.
		sk = SigningKey.from_string(bytes.fromhex(readable_sk), curve=SECP256k1)
		msg = json.dumps(msg).encode() #to convert msg dict to bytes like object
		return sk.sign(msg)

	def announce_transaction(self, peers, transaction_dict):
		for peer in peers:
			response = requests.post(peer+'add_transaction', json= transaction_dict)
