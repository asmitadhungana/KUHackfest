import ast

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import CallTransactionBuilder
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.wallet.wallet import KeyWallet

import config
#Returns a list of recent transactions
def get_transactions():
    call = (
        CallBuilder()
        .from_(wallet.get_address())
        .to(JUNGLE_SCORE_ADDRESS)
        .method("get_results")
        .params({})
        .build()
    )
    result = icon_service.call(call)

    transaction_list = []
    for resultVal in result["result"]:
        transaction_list.append(ast.literal_eval(resultVal))

    return transaction_list

