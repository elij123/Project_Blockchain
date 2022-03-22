// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;
import "./utils/cryptography/ECDSA.sol"; //MIT License by OpenZeppelin Library

contract CryptoProject {
    mapping(address => string) miner_mapping;
    mapping(bytes32 => bool) device_mapping;
    mapping(string => bool) M_ID_mapping;
    mapping(string => bool) D_ID_mapping;
    uint256 public flag = 0;
    bytes32 temp_hash;
    address temp_acc;
    bool test;

    function setValueMiner(address _M_addr, string memory _M_ID) public {
        if (
            keccak256(abi.encodePacked(miner_mapping[_M_addr])) ==
            keccak256(abi.encodePacked("")) &&
            !M_ID_mapping[_M_ID]
        ) {
            M_ID_mapping[_M_ID] = true;
            miner_mapping[_M_addr] = _M_ID;
        } else {
            revert("Miner address / Miner ID already registered"); //Replace with feedback to the server
        }
    }

    // function retrieveMiner(address _M_addr)
    //     public
    //     view
    //     returns (string memory)
    // {
    //     return miner_mapping[_M_addr]; //Default value is "" for string
    // }

    function setValueDevice(
        string memory _M_ID,
        string memory _D_ID,
        address _D_addr
    ) public {
        if (!D_ID_mapping[_D_ID] && M_ID_mapping[_M_ID]) {
            bytes32 hash_sample = keccak256(
                abi.encodePacked(_M_ID, _D_ID, _D_addr)
            );
            device_mapping[hash_sample] = true;
        } else {
            revert("Device ID already registered"); //Replace with feedback to the server
        }
    }

    // function retrieveDevice(
    //     string memory _M_ID,
    //     string memory _D_ID,
    //     address _D_addr
    // ) public view returns (bool) {
    //     bytes32 hash_sample = keccak256(
    //         abi.encodePacked(_M_ID, _D_ID, _D_addr)
    //     );
    //     return device_mapping[hash_sample]; //Default value is false for bool
    // }

    function verify(
        bytes memory data,
        bytes memory signature,
        address account
    ) public {
        temp_hash = ECDSA.toEthSignedMessageHash(data);
        temp_acc = ECDSA.recover(temp_hash, signature);
        if (temp_acc == account) {
            test = true;
        } else {
            test = false;
        }
    }

    function status_check() public view returns (bool) {
        return test;
    }
}
