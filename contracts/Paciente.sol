// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

/**
 * @title Paciente
 * @dev Store & retrieve value in a variable
 */
contract Paciente {
    
    struct infos {
    string dados;
    string cid;
    }

    address private _owner;
    infos[] prontuarios;
    infos private info;
    mapping(address => bool) public whitelist;

    constructor() {
        _owner = msg.sender;
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

    function isMember(address _member) public view returns(bool){
        return whitelist[_member];
    }

    //Somente a administracao pode adicionar acesso
    function addMember(address _member) onlyBy(_owner) public {
         require(
            !isMember(_member),
            "Address is member already."
        );

        whitelist[_member] = true;
        //emit MemberAdded(_member);
    }

    //Paciente pode remover
    function removeMember(address _member) onlyBy(_owner) public {
        {
        delete whitelist[_member];
        //emit MemberRemoved(_member);
        }
    }

    //Membros podem adicionar prontuarios
    function add(string memory _dados, string memory _cid) public {
        require(
            isMember(msg.sender),
            "Not member of whitelist."
        );
        info=infos(_dados,_cid);
        prontuarios.push(info);
    }

    //Paciente pode acessar prontuarios
    function get() public onlyBy(_owner) view returns(infos[] memory) {
        return prontuarios;
    }

}
