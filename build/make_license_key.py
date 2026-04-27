"""Dev-side license key generator.

Customer sends their Machine ID (visible in the Activate dialog).
Run: python make_license_key.py <MACHINE_ID>
Output: 16-hex license key formatted XXXX-XXXX-XXXX-XXXX.

Set VEO_LICENSE_SECRET to the same value used at build time.
"""
import hashlib
import hmac
import os
import sys


def expected_key(mid: str) -> str:
    secret = os.environ.get(
        "VEO_LICENSE_SECRET",
        "veo-pipeline-pro-2026:truong-hoa:0345431884",
    ).encode()
    digest = hmac.new(secret, mid.encode(), hashlib.sha256).hexdigest().upper()
    short = digest[:16]
    return "-".join(short[i:i + 4] for i in range(0, 16, 4))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_license_key.py <MACHINE_ID>")
        sys.exit(1)
    mid = sys.argv[1].strip().upper()
    print(expected_key(mid))
