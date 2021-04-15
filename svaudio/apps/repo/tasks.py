from datetime import datetime
from hashlib import sha256
from os import chmod, fdopen, unlink
from pathlib import Path
from shutil import move
from tempfile import mkstemp

import requests
from pytz import utc
from rv.api import Project, Synth, read_sunvox_file

from config import celery_app

from . import models as m


@celery_app.task()
def start_fetch(fetch_id: int):
    print(f"{fetch_id=}")
    fetch = m.Fetch.objects.get(id=fetch_id)
    fetch.started_at = datetime.now(tz=utc)
    fetch.save()
    location = fetch.location
    url = location.url
    fd, temp_name = mkstemp(prefix="svaudio", text=False)
    with fdopen(fd, "w+b") as f, requests.get(url, stream=True) as r:
        r.raise_for_status()
        h = sha256()
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
            h.update(chunk)
        f.flush()
        size = f.tell()
        f.seek(0)
        magic = f.read(4)
        file_type = {
            b"SVOX": m.File.FileType.PROJECT,
            b"SSYN": m.File.FileType.MODULE,
        }.get(magic)
        if not file_type:
            unlink(temp_name)
            fetch.finished_at = datetime.now(tz=utc)
            fetch.success = False
            fetch.save()
            return
        digest = h.hexdigest()
        file = m.File.objects.filter(hash=digest).first()
        if not file:
            file = m.File.objects.create(
                hash=digest,
                file_type=file_type,
                size=size,
                cached_at=datetime.now(tz=utc),
            )
            dest_path: Path = file.filesystem_path()
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            move(temp_name, dest_path)
            chmod(dest_path, 0o644)
        else:
            unlink(temp_name)
        fetch.finished_at = datetime.now(tz=utc)
        fetch.success = True
        fetch.file = file
        fetch.save()
        location.last_good_fetch = fetch
        location.most_recent_file = file
        location.save()
        if file_type == m.File.FileType.PROJECT:
            project = m.Project.objects.filter(file=file).first()
            if not project:
                f.seek(0)
                sunvox_obj = read_sunvox_file(f)
                assert isinstance(sunvox_obj, Project)
                m.Project.objects.get_or_create(file=file, name=sunvox_obj.name)
        elif file_type == m.File.FileType.MODULE:
            module = m.Module.objects.filter(file=file).first()
            if not module:
                f.seek(0)
                sunvox_obj = read_sunvox_file(f)
                assert isinstance(sunvox_obj, Synth)
                m.Module.objects.get_or_create(file=file, name=sunvox_obj.module.name)
