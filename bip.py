#!/usr/bin/env python3
"""
derive_with_bip_utils.py

Usage:
  python3 derive_with_bip_utils.py \
    --mnemonic "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about" \
    --passphrase "" \
    --count 20 \
    [--testnet]

Outputs:
 - master xprv/xpub
 - account xprv/xpub for m/44'/0'/0' m/49'/0'/0' m/84'/0'/0' m/86'/0'/0'
 - first N external (change=0) child pubkeys + addresses per account.

Security: run only on an offline machine for real seeds.
"""

import argparse
from bip_utils import (
    Bip39SeedGenerator,
    Bip44, Bip44Coins,
    Bip49, Bip49Coins,
    Bip84, Bip84Coins,
    Bip86, Bip86Coins,
    Bip44Changes,
)

def derive_account_info(bip_obj, account_idx: int, count: int, hrp: str):
    """
    bip_obj is the BipX object returned by BipXX.FromSeed(seed, BipXXCoins.BITCOIN)
    that represents the master.
    We'll derive: Account(account_idx), Change(EXTERNAL), AddressIndex(i)
    """
    # Derive account node (m/...'/account_idx')
    acct = bip_obj.Purpose().Coin().Account(account_idx)

    # Extended keys for the account (xprv/xpub)
    acct_xprv = acct.PrivateKey().ToExtended()
    acct_xpub = acct.PublicKey().ToExtended()

    # external chain (change = 0)
    ext_chain = acct.Change(Bip44Changes.CHAIN_EXT)

    children = []
    for i in range(count):
        addr_ctx = ext_chain.AddressIndex(i)
        pub_hex = addr_ctx.PublicKey().RawCompressed().ToHex()
        addr_str = addr_ctx.PublicKey().ToAddress()    # uses appropriate encoding for the Bip class
        children.append((i, pub_hex, addr_str))

    return acct_xprv, acct_xpub, children

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mnemonic", required=True, help="BIP39 mnemonic (wrap in quotes)")
    ap.add_argument("--passphrase", default="", help="Optional BIP39 passphrase")
    ap.add_argument("--count", type=int, default=20, help="Number of child addresses to derive (default 20)")
    ap.add_argument("--testnet", action="store_true", help="Use testnet coins/addresses")
    args = ap.parse_args()

    # seed
    seed_bytes = Bip39SeedGenerator(args.mnemonic).Generate(args.passphrase)

    # Choose coin enums depending on mainnet/testnet
    if args.testnet:
        # bip_utils enums for testnet: usually *_TESTNET variants exist; fall back to bitcoin testnet coin enums where defined
        # We'll use the BTC testnet coin enums available in bip_utils
        bip44_coin = Bip44Coins.BITCOIN_TESTNET  # bip_utils historically uses the same coin enum and outputs testnet addresses if network param used when encoding
        bip49_coin = Bip49Coins.BITCOIN_TESTNET
        bip84_coin = Bip84Coins.BITCOIN_TESTNET
        bip86_coin = Bip86Coins.BITCOIN_TESTNET
        hrp = "tb"
    else:
        bip44_coin = Bip44Coins.BITCOIN
        bip49_coin = Bip49Coins.BITCOIN
        bip84_coin = Bip84Coins.BITCOIN
        bip86_coin = Bip86Coins.BITCOIN
        hrp = "bc"

    # Build Bip objects from seed
    bip44_mst = Bip44.FromSeed(seed_bytes, bip44_coin)
    bip49_mst = Bip49.FromSeed(seed_bytes, bip49_coin)
    bip84_mst = Bip84.FromSeed(seed_bytes, bip84_coin)
    bip86_mst = Bip86.FromSeed(seed_bytes, bip86_coin)

    # Print master extended keys (BIP32)
    # bip_utils allows getting master keys via MasterPrivateKey / MasterPublicKey
    print("\n=== MASTER (BIP32) ===")
    try:
        print("MASTER XPRV:", bip44_mst.MasterPrivateKey().ToExtended())
        print("MASTER XPUB:", bip44_mst.MasterPublicKey().ToExtended())
    except Exception:
        # fallback if methods differ in versions
        print("MASTER (no ToExtended available) — check bip_utils version")

    # Accounts to derive (account 0)
    # coin_type is 0 for mainnet, 1 for testnet (BIP44 standard)
    coin_type = 1 if args.testnet else 0
    accounts = {
        f"BIP44  m/44'/{coin_type}'/0' (P2PKH)": bip44_mst,
        f"BIP49  m/49'/{coin_type}'/0' (P2SH-P2WPKH)": bip49_mst,
        f"BIP84  m/84'/{coin_type}'/0' (P2WPKH)": bip84_mst,
        f"BIP86  m/86'/{coin_type}'/0' (P2TR)": bip86_mst,
    }

    for label, bip_obj in accounts.items():
        print(f"\n=== {label} ===")
        acct_xprv, acct_xpub, children = derive_account_info(bip_obj, account_idx=0, count=args.count, hrp=hrp)
        print("Account xprv:", acct_xprv)
        print("Account xpub:", acct_xpub)
        print(f"First {args.count} external children (index, pub_compressed_hex, address):")
        for idx, pub_hex, addr in children:
            print(f"  [{idx:02d}] {pub_hex}  {addr}")

    print("\nDone.")

if __name__ == '__main__':
    main()

