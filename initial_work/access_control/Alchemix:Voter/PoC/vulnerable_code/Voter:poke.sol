function poke(uint256 _tokenId) public {
    //...//
        _vote(_tokenId, _poolVote, _weights, _boost); //internal _vote is called 
    }
function _vote(uint256 _tokenId, address[] memory _poolVote, uint256[] memory _weights, uint256 _boost) internal {
      //...
        IFluxToken(FLUX).accrueFlux(_tokenId);  // flux is accrued here
        uint256 totalPower = (IVotingEscrow(veALCX).balanceOfToken(_tokenId) + _boost);
}