# install

create or activate venv and install requirements

## create or/and activate venv
```
python -m venv venv
source venv/bin/activate
```

## install reqs
```
pip install -r requirements.txt
```
or
```
pip install bip-utils coincurve
```

# how to run
```bash
python bip.py --mnemonic "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
```

or for testnet

```bash
python bip.py --mnemonic "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about" --testnet
```
