"""Collect existing credentials on this computer without showing or committing them."""
import argparse
import getpass
import os
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default='.local/social.env')
    args = parser.parse_args()
    target = Path(args.out)
    if target.exists() or target.is_symlink():
        print('Configuration already exists; preserved. Edit it privately if needed.')
        return 1
    values = {'INSTAGRAM_HANDLE': 'mirabilis_on'}
    try:
        # getpass refuses to echo secrets on supported local terminals.
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('error', getpass.GetPassWarning)
            values['GEMINI_API_KEY'] = getpass.getpass('Existing Gemini API key (blank to skip): ')
            values['INSTAGRAM_ACCESS_TOKEN'] = getpass.getpass('Instagram Login access token (blank to skip): ')
        values['INSTAGRAM_USER_ID'] = input('Instagram professional account numeric ID (blank to skip): ').strip()
        values['INSTAGRAM_GRAPH_VERSION'] = input('Supported Meta API version, e.g. v25.0 (blank to skip): ').strip()
        if values['INSTAGRAM_USER_ID'] and not values['INSTAGRAM_USER_ID'].isdigit():
            raise ValueError('Invalid account ID')
        if values['INSTAGRAM_GRAPH_VERSION'] and not re.fullmatch(r'v\d+\.0', values['INSTAGRAM_GRAPH_VERSION']):
            raise ValueError('Invalid API version')
        if any('\n' in v or '\r' in v for v in values.values()):
            raise ValueError('Multiline credentials are not supported')
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
            handle.write(''.join(f'{k}={v}\n' for k, v in values.items() if v))
        print(f'Configuration saved privately: {target}. Never share or commit it.')
        return 0
    except (OSError, EOFError, ValueError, getpass.GetPassWarning):
        print('Configuration not completed. Use a local interactive terminal; secrets were not printed.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
