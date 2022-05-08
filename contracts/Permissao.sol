// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

/**
 * @title Paciente
 * @dev Store & retrieve value in a variable
 */
contract Permissao{
    address private owner;

    //combinacao de chaves para cid
    mapping(string => string[]) public cids;

    constructor(address _paciente) {
        owner = _paciente;
    }

    error Unauthorized();

    /// Function called too early.
    error TooEarly();

    /// Not enough Ether sent with function call.
    error NotEnoughEther();

    modifier onlyBy(address _account) {
        if (msg.sender != _account) revert("Essa conta nao tem permissao");
        _;
    }

    function getPronts(string memory _combinacao) onlyBy(owner) public view returns(string[] memory) {
        return cids[_combinacao];
    }

    function addPront(string memory _combinacao,string memory _cid) onlyBy(owner) public {
        cids[_combinacao].push(_cid);
    
    }

    function removePront(string memory _combinacao,string memory _cid) onlyBy(owner) public {
        require(cids[_combinacao].length>0,
            "Esse Hospital nao tem permissao");
        
        //percorre cids
        for (uint i = 0; i < cids[_combinacao].length; i++) {
            //se cid for igual ao cid que deseja remover -> troca de lugar com o ultimo e pop()
            if(keccak256(bytes(cids[_combinacao][i])) == keccak256(bytes(_cid))){
                cids[_combinacao][i]=cids[_combinacao][cids[_combinacao].length-1];
                cids[_combinacao].pop();
            }
        }
    }

    function get(string memory _combinacao) public view returns(string[] memory){
        return cids[_combinacao];
    }
}
