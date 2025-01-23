import json
from web3 import Web3
from eth_account import Account

from elections.models import Election
from nextgenvoting import settings
from celery import shared_task

from voting.models import Blockchain_Vote

# need to send this to constant somewhere
rpc_url = "https://polygon-rpc.com"


#@shared_task(bind=True, max_retries=3, default_retry_delay=30)
@shared_task
def cast_vote_async(bc_voteId, vote_data):

    bc_vote = Blockchain_Vote.objects.get(id=bc_voteId)

    try:
        # initialize BlockchainManager
        bc_manager = BlockchainManager()

        # send the vote to the blockchain
        tx_receipt = bc_manager.sendVote(bc_vote.id, vote_data)

        if tx_receipt:
            print(f"Transaction successful for vote_id {bc_vote.id}: {tx_receipt}")
            bc_vote.status = bc_vote.COMPLETE
            bc_vote.save()
            return {"status": "success", "transaction_receipt": tx_receipt}
        else:
            print(f"Transaction failed for vote_id {bc_vote.id}")
            bc_vote.vote_data = vote_data
            bc_vote.status = bc_vote.FAILED
            bc_vote.save()

    except Exception as e:
        print(f"An error occurred while processing vote_id {bc_vote.id}: {e}")






class BlockchainManager:
    def __init__(self):

        self.web3 = Web3(Web3.HTTPProvider(rpc_url))

        # get abi from json file
        with open('algorithms/abi.json') as f:
            self.contract_abi = json.load(f)

        self.contract_address = settings.CONTRACT_ADDRESS
        self.private_key = settings.PRIVATE_KEY
        self.account = Account.from_key(self.private_key)
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.contract_abi)


    def getVote(self, voterId):
        try:
            return self.contract.functions.retrieveVote(str(voterId)).call()

        except:
            print("")
            return None

    def sendVote(self, voter_id, vote_data):
        try:
            # the transaction
            transaction = self.contract.functions.storeVote(
                str(voter_id),
                str(vote_data)
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price
            })

            # sign the transaction with private key
            signed_tx = self.web3.eth.account.sign_transaction(transaction, self.private_key)

            # send the transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # wait for the transaction to finish
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            return tx_receipt

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
