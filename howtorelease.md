# Creating the Release Files

1. Install [PyInstaller](https://www.pyinstaller.org/)
2. Run `pyinstaller TTSCards.spec`. For Linux, use `TTSCards_Linux.spec`.
3. The release files will be in the `dist` folder
4. Repeat for each OS you wish to release on
5. For Windows, open `release/WindowsSetupScript.iss` with Inno Setup and compile the script to generate an installer
6. For Linux, copy the file in `./assets/ttscards_mark.png` to `./dist/TTSCards/assets/ttscards_mark.png`.
