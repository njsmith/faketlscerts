# -*- coding: utf-8 -*-

import argparse
import os
import trustme
import sys

# Python 2/3 annoyingness
try:
    unicode
except NameError:  # pragma: no cover
    unicode = str


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="trustme")
    parser.add_argument(
        "-d",
        "--dir",
        default=os.getcwd(),
        help="Directory where certificates and keys are written to. Defaults to cwd.",
    )
    parser.add_argument(
        "-i",
        "--identities",
        nargs="*",
        default=("localhost", "127.0.0.1", "::1"),
        help="Identities for the certificate. Defaults to 'localhost 127.0.0.1 ::1'.",
    )
    parser.add_argument(
        "--common-name",
        nargs=1,
        default=None,
        help="Also sets the deprecated 'commonName' field for all relevant identities.",
    )
    parser.add_argument(
        "--key-size",
        type=int,
        default=2048,
        help="Key size of the certificate generated. Defaults to 2048.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Doesn't print out helpful information for humans.",
    )

    args = parser.parse_args(argv)
    cert_dir = args.dir
    identities = [unicode(identity) for identity in args.identities]
    common_name = unicode(args.common_name[0]) if args.common_name else None
    key_size = args.key_size
    quiet = args.quiet

    if not os.path.isdir(cert_dir):
        raise ValueError("--dir={} is not a directory".format(cert_dir))
    if len(identities) < 1:
        raise ValueError("Must include at least one identity")

    # Generate the CA certificate
    trustme._KEY_SIZE = key_size
    ca = trustme.CA()
    cert = ca.issue_cert(*identities, common_name=common_name)

    # Write the certificate and private key the server should use
    server_key = os.path.join(cert_dir, "server.key")
    server_cert = os.path.join(cert_dir, "server.pem")
    cert.private_key_pem.write_to_path(path=server_key)
    with open(server_cert, mode="w") as f:
        f.truncate()
    for blob in cert.cert_chain_pems:
        blob.write_to_path(path=server_cert, append=True)

    # Write the certificate the client should trust
    client_cert = os.path.join(cert_dir, "client.pem")
    ca.cert_pem.write_to_path(path=client_cert)

    if not quiet:
        idents = "', '".join(identities)
        print("Generated a certificate for '{}'".format(idents))
        print("Configure your server to use the following files:")
        print("  cert={}".format(server_cert))
        print("  key={}".format(server_key))
        print("Configure your client to use the following files:")
        print("  cert={}".format(client_cert))
