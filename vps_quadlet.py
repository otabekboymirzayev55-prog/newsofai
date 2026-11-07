"""Patch only the supported existing Telegram Quadlet; never read credentials."""
import json
import os
from pathlib import Path
import re
import sys
import tempfile


def inspect(text):
    sections = list(re.finditer(r'^\[([^\]\r\n]+)\][ \t]*$', text, re.M))
    containers = [i for i, match in enumerate(sections) if match[1] == 'Container']
    if len(containers) != 1:
        raise ValueError('Expected exactly one Container section')
    index = containers[0]
    start = sections[index].end()
    end = sections[index + 1].start() if index + 1 < len(sections) else len(text)
    body = text[start:end]
    def values(key):
        return re.findall(r'^' + key + r'=(.+)$', body, re.M)
    images, envs, names = values('Image'), values('EnvironmentFile'), values('ContainerName')
    if len(images) != 1 or len(envs) != 1 or names != ['newsofai']:
        raise ValueError('Unsupported existing image, env file or container name')
    if not envs[0].startswith('/') or not any(re.search(r':/data(?::[^\s]+)?$', v) for v in values('Volume')):
        raise ValueError('Expected an absolute env path and retained /data volume')
    if '\\\n' in body:
        raise ValueError('Inspect multiline container settings before upgrading')
    return {'image': images[0], 'env': envs[0], 'container': names[0]}, start, end


def patch(text, image):
    if not re.fullmatch(r'localhost/newsofai:editorial-[0-9a-f]{12}', image):
        raise ValueError('Unexpected replacement image')
    _, start, end = inspect(text)
    body = re.sub(r'^Image=.+$', 'Image=' + image, text[start:end], count=1, flags=re.M)
    # Put this value after all existing environment directives. Podman --env
    # overrides env-file values; later duplicate --env values take precedence.
    body = body.rstrip('\n') + '\nEnvironment=POST_INTERVAL_HOURS=1.5\n\n'
    return text[:start] + body + text[end:]


def replace(path, text):
    path = Path(path)
    stat = path.stat()
    fd, name = tempfile.mkstemp(prefix='.newsofai-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as file:
            file.write(text)
            file.flush()
            os.fsync(file.fileno())
        os.chown(name, stat.st_uid, stat.st_gid)
        os.chmod(name, stat.st_mode & 0o777)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


if __name__ == '__main__':
    action, unit, target = sys.argv[1:]
    text = Path(unit).read_text()
    if action == 'inspect':
        config, _, _ = inspect(text)
        if not Path(config['env']).is_file():
            raise SystemExit('Existing env file missing. No changes made.')
        Path(target).write_text(json.dumps(config))
    elif action == 'patch':
        replace(unit, patch(text, target))
    else:
        raise SystemExit('Unknown action')
