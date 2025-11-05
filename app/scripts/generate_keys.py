"""
RSA Key Generation Script for JWT Authentication.

Generates a 2048-bit RSA key pair and outputs as base64-encoded PEM strings
suitable for storing in environment variables.

Usage:
    python -m app.scripts.generate_keys

Output:
    Base64-encoded private and public keys to copy into .env file
"""
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


def generate_rsa_keys():
    """Generate RSA key pair and return base64-encoded PEM strings."""
    print("=" * 70)
    print("RSA Key Pair Generation for JWT Authentication")
    print("=" * 70)
    print("\nGenerating 2048-bit RSA key pair...")
    
    # Generate RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Serialize private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Generate public key from private key
    public_key = private_key.public_key()
    
    # Serialize public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Encode to base64 for environment variables
    private_b64 = base64.b64encode(private_pem).decode('utf-8')
    public_b64 = base64.b64encode(public_pem).decode('utf-8')
    
    print("✓ Keys generated successfully!\n")
    print("=" * 70)
    print("Add the following to your .env file:")
    print("=" * 70)
    print()
    print(f"JWT_PRIVATE_KEY={private_b64}")
    print()
    print(f"JWT_PUBLIC_KEY={public_b64}")
    print()
    print("=" * 70)
    print("⚠️  SECURITY WARNINGS:")
    print("=" * 70)
    print("1. Keep JWT_PRIVATE_KEY secret - NEVER commit to version control")
    print("2. JWT_PUBLIC_KEY can be safely shared")
    print("3. Rotate keys periodically in production")
    print("4. Use secrets management in production (AWS Secrets Manager, etc.)")
    print("=" * 70)


if __name__ == "__main__":
    generate_rsa_keys()
