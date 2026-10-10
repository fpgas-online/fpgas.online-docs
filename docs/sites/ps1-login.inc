1. Work out the blade's port. It is `1NN22`, where `NN` is the number in the blade's name: `11622` for pi16 at ps1.
2. Connect as `pi` from your own machine. `ssh` prints a banner that holds the password, then asks for it.

   ```console
   $ ssh -p 11622 pi@ps1.fpgas.online
   ```

3. Type the password from the banner. The blade's shell prompt appears, and `sudo` takes the same password.
