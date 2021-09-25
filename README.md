# blockchain_implementation

Dexter owns the most famous coffee shop of his town and has plenty of friends who often come by his shop. He uses logbooks to store the transaction data. As his shop is very famous, he often runs out of logbooks. Some of Dexter's friends have access to his shop and they would often remove/edit their transactions from the logbook which would make him lose money. Dexter recently heard about blockchain technology and is wondering how he can use it in his business so that he can continue his work more efficiently. 

Help Dexter to create his own Blockchain with the following functionalities (2 points for each feature) :
1.Dexter has information regarding all the available blocks.
2.None of Dexter's friends should be able to edit the added transactions.
3.Timestamp of each transaction is readily available.
4.Dexter should have all the information regarding the completed transactions.



## Instructions to run: 
Clone the repo and then install the dependencies using 
```
pip install -r requirements.txt
``
In the ```config_peers.py``` add the peers you wish to have while running the network. By default we have some peers added to file like:
peers = {'http://127.0.0.1:5000/', 'http://127.0.0.1:5001/'}
```
 store all url's running on the network here in string format, so that they can communicate
for example: 'http://127.0.0.1:5000/'
peers = {'http://127.0.0.1:5000/', 'http://127.0.0.1:5001/'}
```
The wallet.py file is used to generate a public key and a private key pair for so that anyone can make a transaction against the private key and Dexter can verify the transaction using the public key and private key pair.

The current public key and private key are contained in the wallet_keys.txt file. You can use it to make transactions
Now to run, open two terminals and navigate both to repo. Use following commands to run instances of our application:   
For the first instance on port 5000:
```
set FLASK_APP=main.py

flask run --port 5000 --debugger --reload
```   
For the second instance on port 5001:   
```
set FLASK_APP=main.py

flask run --port 5001 --debugger --reload
```
Now we will have two instances running on http://localhost:5000 and http://localhost:5001.   
![index](https://user-images.githubusercontent.com/30752980/110203144-67feaa00-7e92-11eb-90f5-3a81a91153af.png)

After starting both the instances, you can make a transaction by filling in both the private key and public key


After making the transactions, they are put in the unverified_transactions which you can check using  http://localhost:5001/unverified_transactions

After the transactions has been put in unverified_transactions, they can be mined by http://localhost:5001/mine_transactions through which Dexter can verify the transactions by first validating the signature on the blocks and then creating a hash of the block with the appropriate difficulty which then gets added to the blockchain

After all the transactions have been mined and verified, Dexter can view them using  http://localhost:5001/blockchain which will show all the blocks of transactions
