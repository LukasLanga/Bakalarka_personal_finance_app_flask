import os
from pathlib import Path

def _get_kb_certs():
    """Helper function to get the absolute paths for KB certificates and verify they exist."""
    app_dir = Path(__file__).resolve().parent.parent
    cert_filename = Path(os.environ.get('KB_CERT_PATH', '')).name
    key_filename = Path(os.environ.get('KB_KEY_PATH', '')).name

    cert_path = app_dir / 'certs' / cert_filename
    key_path = app_dir / 'certs' / key_filename

    if not cert_path.is_file():
        raise FileNotFoundError(f"Certificate file not found at path: {cert_path}")
    if not key_path.is_file():
        raise FileNotFoundError(f"Key file not found at path: {key_path}")
        
    return (str(cert_path), str(key_path))
