/* 
    *This vulnerability exists in the `PasswordStore::setPassword` function in the `PasswordStore.sol` 
    *file starting on [line 26](https://github.com/Cyfrin/2023-10-PasswordStore/blob/856ed94bfcf1031bf9d13514cb21b591d88ed323/src/PasswordStore.sol#L26).

    *The `setPassword()` function includes no access controls meaning that anyone can call it and modify the password:
*/

/*
     * @notice This function allows only the owner to set a new password.
     * @param newPassword The new password to set.
     */
    function setPassword(string memory newPassword) external {
        s_password = newPassword;
        emit SetNetPassword();
    }