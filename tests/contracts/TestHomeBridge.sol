pragma solidity ^0.8.0;


contract TestHomeBridge {

    event Confirmation(
        bytes32 transferHash,
        bytes32 transactionHash,
        uint256 amount,
        address recipient,
        address indexed validator
    );
    event TransferCompleted(
        bytes32 transferHash,
        bytes32 transactionHash,
        uint256 amount,
        address recipient,
        bool coinTransferSuccessful
    );

    function emitConfirmation(
        bytes32 transferHash,
        bytes32 transactionHash,
        uint256 amount,
        address recipient,
        address validator) public {
        emit Confirmation(transferHash, transactionHash, amount, recipient, validator);
    }

    function emitTransferCompleted(
        bytes32 transferHash,
        bytes32 transactionHash,
        uint256 amount,
        address recipient
        ) public {
        emit TransferCompleted(transferHash, transactionHash, amount, recipient, true);
    }
}

// SPDX-License-Identifier: MIT
