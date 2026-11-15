"""Análisis de inventarios y respaldos, sin modificar el televisor."""

from pathlib import Path
from . import core
from .adb import TVLibreError


def backups(directory, device):
    matches = []
    for path in sorted(Path(directory).rglob('backup.json')):
        try:
            data = core.read_json(path)
            original = data.get('device', {})
            if original.get('identity') != device.get('identity'):
                continue
            compatible = all(original.get(k) == device.get(k) for k in ('model', 'sdk', 'build', 'user'))
            journal = False
            try:
                core.validate(data, historical=True)
                core.require_journal(data)
                journal = True
            except TVLibreError:
                pass
            matches.append({'path': str(path.resolve()), 'purpose': data.get('purpose', data.get('action')),
                            'status': data.get('status'), 'same_firmware_and_user': compatible,
                            'restorable_journal': compatible and journal})
        except (ValueError, AttributeError, OSError, TVLibreError):
            continue
    return matches


def analyze(inventory):
    packages = set(inventory['packages'])
    disabled = {p.removeprefix('package:') for p in inventory.get('disabled', [])}
    candidates = {p['id']: p['reason'] for name in core.PROFILES for p in core.profile(name)['packages']}
    protected = core.protected_packages()
    return {'mode': 'solo lectura, inventario guardado',
            'protected_disabled': sorted(packages & disabled & protected),
            'cleanup_candidates': [{'package': p, 'reason': candidates[p]} for p in sorted(packages & candidates.keys() - protected - disabled)],
            'unknown_packages': sorted(packages - candidates.keys() - protected),
            'note': 'Una coincidencia de lista no demuestra telemetría ni compatibilidad; no habilita ni deshabilita paquetes.'}


def catalog():
    return core.read_json(core.ROOT / 'integrations/devices.json')
