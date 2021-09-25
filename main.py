from flask import Flask, request, jsonify, url_for, render_template
from blockchain_component import Block, Blockchain
from config_peers import peers
from datetime import datetime

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True #to enable pretty printing with jsonify.
app.config['JSON_SORT_KEYS'] = False #to not sort while returning json response.

blockchain = Blockchain()


# to view entire blockchain
@app.route('/blockchain', methods=['GET'])
def display_chain():
	blocks = []
	for each_block in blockchain.chain:
		blocks.append(each_block.__dict__)
	return jsonify({'blockchain': blocks, 
					'chain_length': len(blockchain.chain)})

# to view unconfirmed_transactions list, which can be mined into a block
@app.route('/unverified_transactions', methods= ["GET"])
def display_unverified_transactions():
	return jsonify({
		'unverified_transactions': blockchain.unverified_transactions
		})

# mine and announce block
@app.route('/mine_transactions', methods=['GET'])
def mining():
	mined_block = blockchain.mine()
	if mined_block:
		blockchain.announce_block(peers, mined_block)
		return jsonify({'mined_block': mined_block.__dict__})
	else:
		return "Nothing to mine!!"

# form to create new transaction
@app.route('/', methods= ['GET', 'POST'])
def index():
	if request.method == 'POST':
		return url_for('process_transaction')
	else:
		return render_template('make_transaction.html')

# announced block gets added in blockchain
@app.route('/add_block', methods=['POST'])
def add_block():
	block_data = request.get_json()
	# clearing the blockchain.unconfirmed_transaction after block having those transaction is already mined.
	if block_data['transactions'] == blockchain.unverified_transactions:
		blockchain.unverified_transactions = []

	block = Block(block_data['index'], block_data['block_timestamp'], block_data['transactions'], block_data['prev_hash'], block_data['proof_of_work'])
	added = blockchain.add_block(block)
	if not added:
		return "The block was discarded by the node", 400
	return "Block added to the chain", 201

# announced transaction gets added in unconfirmed_transactions list.
@app.route('/add_transaction', methods= ['POST'])
def add_transaction():
	transaction_dict = request.get_json()
	blockchain.unverified_transactions.append(transaction_dict)
	return "Transaction added to unconfirmed_transactions and is ready to be mined!"

# receives form data from '/', generates signature and announces transaction.
@app.route('/process_transaction', methods= ['POST'])
def process_transaction():
	send_from_addr = request.form.get('pk')
	to_addr = request.form.get('to_addr')
	amount = request.form.get('amount')
	send_to_addr = request.form.get('sk')
	timestamp = str(datetime.now())
	msg = {'transaction_timestamp': timestamp, 'from_addr': send_from_addr, 'to_addr': to_addr, 'amount': amount}
	signature = blockchain.generate_signature(send_to_addr, msg)
	signature = signature.hex() #converting bytes type to hex string, so it will be accepted by json.
	blockchain.announce_transaction(peers, {'message': msg, 'signature': signature})
	return "Transaction has been made!"

# to view peers(all host url's from 'config_peers.py')
@app.route('/peers', methods= ["GET"])
def display_peers():
	return jsonify({
		'peers': str(peers),
		'count': len(peers)
		})

