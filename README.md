# iAppGone

**iAppGone** is a command-line tool for macOS that allows you to list and uninstall applications from different sources like `/Applications`, Homebrew, and the App Store. It helps you reclaim disk space by completely removing applications and their associated artifacts.

## Features

- List all installed applications.
- Uninstall a specific application.
- Uninstall multiple applications by providing their index numbers.
- Supports applications installed via `/Applications`, Homebrew, and the App Store.
- Removes associated artifacts such as caches, preferences, and logs.

## Requirements

- Python 3

## Installation

```bash
pip install iAppGone
```
or
```
pip install pandas tabulate colorama
git clone https://github.com/h4rithd/iAppGone.git
cd iAppGone
sudo python3 iAppGone.py -l
```

## Usage
### List all installed applications:
```bash
sudo python3 iAppGone.py -l
```

### Uninstall a specific application:
```bash
sudo python3 iAppGone.py -u AppName
```
Replace AppName with the name of the application you want to uninstall.

### Uninstall multiple applications by index numbers:
```bash
sudo python3 iAppGone.py -m 1,2,4
```
Replace 1,2,4 with the index numbers of the applications you want to uninstall, separated by commas.

### Options
```
-l, --list: List all installed applications.
-u, --app: Uninstall a specific application by name.
-m, --multi: Uninstall multiple applications by index numbers.
```

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.



