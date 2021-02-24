from iconservice import *

TAG = 'IkuToken'

class TokenStandard(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def symbol(self) -> str:
        pass

    @abstractmethod
    def balanceOf(self, _owner: Address) -> int:
        pass

    @abstractmethod
    def ownerOf(self, _tokenId: str) -> Address:
        pass

    @abstractmethod
    def getApproved(self, _tokenId: str) -> Address:
        pass

        @abstractmethod
    def approve(self, _to: Address, _tokenId: str):
        pass

    @abstractmethod
    def transfer(self, _to: Address, _tokenId: str):
        pass

    @abstractmethod
    def transferFrom(self, _from: Address, _to: Address, _tokenId: str):
        pass




class IkuToken(IconScoreBase, TokenStandard):

    _TOKEN_OWNER = "token_owner"
    _OWNER_TOKEN_COUNT = "owner_token_list"
    _TOKENS = "tokens"
    _TOKEN_APPROVALS = "token_approvals"
    _TOKEN_ID_LIST = "token_id_list"


    _DISTRIBUTOR_SCORE = "distributor_score"
    _IKU_UPDATE_SCORE = "iku_update_score"

    _ZERO_ADDRESS = Address.from_prefix_and_int(AddressPrefix.EOA, 0)

    @eventlog(indexed=3)
    def Approval(self, _owner: Address, _approved: Address, _tokenId: str):
        pass

    @eventlog(indexed=3)
    def Transfer(self, _from: Address, _to: Address, _tokenId: str):
        pass

    @eventlog(indexed=3)
    def TokenMinted(self, _by: Address, _tokenId: str, _params: str):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._token_owner = DictDB(self._TOKEN_OWNER, db, value_type=Address)
        self._owner_token_count = DictDB(self._OWNER_TOKEN_COUNT, db, value_type=int)
        self._tokens = DictDB(self._TOKENS, db, value_type=str)
        self._token_approvals = DictDB(self._TOKEN_APPROVALS, db, value_type=Address)
        self._token_id_list = ArrayDB(self._TOKEN_ID_LIST, db, value_type=str)

        self._admin_list = ArrayDB(self._ADMIN_LIST, db, value_type=Address)
        self._super_admin = VarDB(self._SUPER_ADMIN, db, value_type=Address)
        self._distributor_score = VarDB(self._DISTRIBUTOR_SCORE, db, value_type=Address)
        self._iku_update_score = VarDB(self._IKU_UPDATE_SCORE, db, value_type=Address)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def name(self) -> str:
        """
        Returns the name of the token.Any name can be given to token
        """
         return "IkuToken"

    @external(readonly=True)
    def symbol(self) -> str:
        """
        Returns the symbol of the token.
        """
        return "IKU"

    @external(readonly=True)
    def balanceOf(self, _owner: Address) -> int:
        """
        Returns the number of NFTs owned by _owner.
        NFTs assigned to the zero address are considered invalid,
        so this function SHOULD throw for queries about the zero address.
        """
        if _owner is None or self._is_zero_address(_owner):
            revert("Balance error: Invalid  address given")
        return self._owner_token_count[_owner]

    @external(readonly=True)
    def ownerOf(self, _tokenId: str) -> Address:
        """
        Returns the owner of an NFT. Throws if _tokenId is not a valid NFT.
        """
        self._id_validity(_tokenId)
        owner = self._token_owner[_tokenId]
        if self._is_zero_address(owner):
            revert("Token id error: Invalid token Id,token is burned")
        return owner

    @external(readonly=True)
    def getApproved(self, _tokenId: str) -> Address:
        """
        Returns the approved address for a single NFT.
        If there is none, returns the zero address.
        Throws if _tokenId is not a valid NFT.
        """
        owner = self.ownerOf(_tokenId)
        if owner is None:
            revert("Token id error: token id invalid ")
        addr = self._token_approvals[_tokenId]
        if addr is None:
            return self._ZERO_ADDRESS
        return addr

    @external
    def approve(self, _to: Address, _tokenId: str):
        """
        Allows _to to change the ownership of _tokenId from your account.
        The zero address indicates there is no approved address.
        Throws unless self.msg.sender is the current NFT owner.
        """
        owner = self.ownerOf(_tokenId)
        if _to == owner:
            revert("Approve error: Cannot approve to yourself.")
        if self.tx.origin == owner or self.msg.sender == owner:
            self._token_approvals[_tokenId] = _to
            self.Approval(owner, _to, _tokenId)
        else:
            revert("Approve error: Cannot approve,you do not own this token")

     @external
    def transfer(self, _to: Address, _tokenId: str):
        """
        Transfers the ownership of your NFT to another address,
        and MUST fire the Transfer event. Throws unless self.msg.sender
        is the current owner. Throws if _to is the zero address.
        Throws if _tokenId is not a valid NFT.
        """
        owner = self.ownerOf(_tokenId)
        if self.ownerOf(_tokenId) is None:
            revert("Transfer error: The token  Id is invalid")
        if self._is_zero_address(_to):
            revert("Transfer error: Cannot transfer to zero address")

        if self.tx.origin == owner or self.msg.sender == owner:
            approved = self.getApproved(_tokenId)
            if approved != _to:
                revert("Transfer error:The transfer of token  is not approved to given address")
            self._transfer(owner, _to, _tokenId)
        else:
            revert("Transfer error: You don't have permission to transfer this NFT")

    @external
    def transferFrom(self, _from: Address, _to: Address, _tokenId: str):
        """
        Transfers the ownership of an NFT from one address to another address,
        and MUST fire the Transfer event. Throws unless self.msg.sender is the
        current owner or the approved address for the NFT. Throws if _from is
        not the current owner. Throws if _to is the zero address. Throws if
        _tokenId is not a valid NFT.
        """
        if self.ownerOf(_tokenId) != self.msg.sender and self._token_approvals[_tokenId] != self.msg.sender:
            revert("Transfer error: You are not authorized to transfer the token")
        if self.ownerOf(_tokenId) != _from:
            revert("Transfer error: Invalid address of the token owner")
        if self._is_zero_address(_to):
            revert("Transfer error: Invalid address of the receiver")
        approved = self.getApproved(_tokenId)
        if approved != _to:
            revert("Transfer error: The transfer of token is not approved to given address")
        self._transfer(_from, _to, _tokenId)

    def _transfer(self, _from: Address, _to: Address, _tokenId: str):
        del self._token_approvals[_tokenId]
        self._token_owner[_tokenId] = _to
        self._owner_token_count[_to] += 1
        self._owner_token_count[_from] -= 1
        self.Transfer(_from, _to, _tokenId)

    @external(readonly=True)
    def current_supply(self) -> int:
        return len(self._token_id_list)

    @external(readonly=True)
    def get_distributor_score(self) -> Address:
        return self._distributor_score.get()

    @external(readonly=True)
    def set_distributor_score(self, _address: Address):
        if self.msg.sender != self.owner:
            revert("distributor score set error:Only contract owner can set ")
        self._distributor_score.set(_address)

    @external(readonly=True)
    def get_iku_update_score(self) -> Address:
        return self._iku_update_score.get()

    @external(readonly=True)
    def set_iku_update_score(self, _address: Address):
        if self.msg.sender != self.owner:
            revert("iku update_score set error:Only contract owner can set ")
        self._iku_update_score.set(_address)

    @external(readonly=True)
    def get_token_list(self) -> list:
        tokens = []
        for i in self._token_id_list:
            tokens.append(i)
        return tokens

    @external(readonly=True)
    def get_token(self, _tokenId: str) -> dict:
        """
        Returns the details of a tokenId
        :param _tokenId: tokenId of the token
        :return: the dict of the attributes of a token
        """
        self._id_validity(_tokenId)
        token_features = json_loads(self._tokens[_tokenId])
        token_features["owner"] = str(self.ownerOf(_tokenId))
        return token_features

    @external(readonly=True)
    def get_tokens_of_owner(self, _owner: Address) -> dict:
        token_list = []
        for _id in self._token_id_list:
            if self._token_owner[_id] == _owner:
                token_list.append(_id)
        return {'tokens': token_list}

    @external
    def _remove_token(self, _tokenId: str):
        top = self._token_id_list.pop()
        if top != _tokenId:
            for i in range(len(self._token_id_list)):
                if self._token_id_list[i] == _tokenId:
                    self._token_id_list[i] = top

    @external
    def burn_token(self, _tokenId: str):
        owner = self.ownerOf(_tokenId)
        if owner != self.msg.sender or self.msg.sender != self.owner:
            revert("Burn error:You cant burn,token don't belong to you")
        self._transfer(owner, self._ZERO_ADDRESS, _tokenId)
        self._remove_token(_tokenId)

    @external
    def mint_token(self, _params: str):
        if self.msg.sender == self.get_distributor_score():
            params = json_loads(_params)
        params["project_id"] = 1
        params["createDate"] = self.now()
        tokenId = str(self.current_supply() + 1) 
        self._token_id_list.put(tokenId)
        self._owner_token_count[self.get_distributor_score()] += 1
        self._token_owner[tokenId] = self.get_distributor_score()
        self._tokens[tokenId] = json_dumps(params)
        self.TokenMinted(self.msg.sender, tokenId, json_dumps(params))

        else:
            revert("Mint error: Only admin can mint new tokens ")

    @external
    def update_token(self, _params: str, _tokenId: str):
        if self.msg.sender == self.get_iku_update_score():
            self._tokens[_tokenId] = _params
        else:
            revert("Update error: You cannot update  ")

    def _id_validity(self, _tokenId: str):
        """
        Checks the validity of tokenId
        :param _tokenId: tokenId to check the validity
        :return: throws error in case tokenId is not valid
        """
        if _tokenId not in self._token_id_list:
            revert("Token id error: No token  with given Id found")

    def _is_zero_address(self, _address: Address) -> bool:
        """
        :param self:
        :param _address:address to check
        :return:True if _address is a zero address
        """
        if _address == self._ZERO_ADDRESS:
            return True
        return False


