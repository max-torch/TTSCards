# TTSCards

An application that converts cards in Tabletop Simulator into printable pdf files

## Creating the Release Files

1. Install [PyInstaller](https://www.pyinstaller.org/)
2. Run `pyinstaller TTSCards.spec`
3. The release files will be in the `dist` folder
4. Create an `assets` folder in `dist` and copy `ttscards_app_icon.ico` into it
5. Repeat for each OS you wish to release on
6. For Windows, open `release/WindowsSetupScript.iss` with Inno Setup and compile the script to generate an installer
