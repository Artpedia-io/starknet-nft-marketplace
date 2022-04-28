# cairo-marketplace
Cairo contracts used in `Artpedia` exchange and demo-ERC721 used for testing

## Overview

Artpedia is a ERC721(NFT) Exchange


## Dependencies

Tested on OSX Monterey 12.3.1

* [python3](https://www.python.org/downloads/release/python-368/) tested with version [3.9.5](https://www.python.org/downloads/release/python-395/)
* [nile](https://github.com/OpenZeppelin/nile) - tested with version [0.6.1](https://github.com/OpenZeppelin/nile/releases/tag/v0.6.1)


Exchange contracts are compiled using [nile 0.6.1](https://github.com/OpenZeppelin/nile)


## Setup

Create a [virtualenv](https://docs.python.org/3/library/venv.html) and activate it:

Using `venv`
```sh
python3 -m venv env
source env/bin/activate
```

Using `conda`
conda create -n {ENV_NAME} 3.9.5



Install `nile`:

```sh
pip install cairo-nile
```

Use `nile` to quickly set up your development environment:

```sh
nile init
...
✨  Cairo successfully installed!
...
✅ Dependencies successfully installed
🗄  Creating project directory tree
⛵️ Nile project ready! Try running:
```
This command creates the project directory structure and installs `cairo-lang`, `starknet-devnet`, `pytest`, and `pytest-asyncio` for you. The template includes a makefile to build the project (`make build`) and run tests (`make test`).
