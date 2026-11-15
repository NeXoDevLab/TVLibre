import copy
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from test_tvlibre import FakeTV
from tvlibre import core, diagnostics, launcher
from tvlibre.adb import ADB, TVLibreError
from tvlibre.cli import main


class AutomaticTV(FakeTV):
    def __init__(self, interrupt=False):
        super().__init__()
        self.values['secure'].pop('enabled_accessibility_services')
        self.values['secure']['accessibility_enabled'] = '0'
        self.interrupt = interrupt

    def shell(self, *args):
        value = super().shell(*args)
        if args[0] == 'settings' and 'enabled_accessibility_services' in args:
            self.values['secure']['accessibility_enabled'] = '1' if self.values['secure'].get('enabled_accessibility_services') else '0'
            if self.interrupt:
                self.interrupt = False
                raise TVLibreError('Corte después del efecto automático de Android')
        return value


class Updates(unittest.TestCase):
    def test_accessibility_automatic_change_roundtrip(self):
        tv = AutomaticTV()
        before = copy.deepcopy(tv.values)
        with tempfile.TemporaryDirectory() as folder:
            path = core.apply(tv, launcher.activation_plan(tv), folder)
            data = core.read_json(path)
            self.assertTrue(core.verify(tv, data)['ok'])
            self.assertTrue(next(o for o in data['operations'] if o.get('key') == 'accessibility_enabled')['observed_system_effect'])
            core.restore(tv, data, path)
            self.assertEqual(tv.values, before)

    def test_cut_after_service_write_restores_automatic_flag(self):
        tv = AutomaticTV(interrupt=True)
        before = copy.deepcopy(tv.values)
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(TVLibreError):
                core.apply(tv, launcher.activation_plan(tv), folder)
            path = next(Path(folder).glob('*/backup.json'))
            core.restore(tv, core.read_json(path), path)
            self.assertEqual(tv.values, before)

    def test_pairing_component_is_never_disabled_even_in_old_plans(self):
        tv = FakeTV()
        tv.states['com.amazon.storm.lightning.tutorial'] = 0
        plan = core.make_plan(tv)
        self.assertNotIn('com.amazon.storm.lightning.tutorial', [o.get('package') for o in plan['operations']])
        plan['operations'].append({'kind':'package','package':'com.amazon.storm.lightning.tutorial','before':0,'after':3})
        with self.assertRaises(TVLibreError):
            core.apply(tv, plan)
        self.assertEqual(tv.mutations, [])

    def test_repair_is_explicit_and_reversible(self):
        tv = FakeTV()
        tv.states['com.amazon.storm.lightning.tutorial'] = 3
        tv.states['com.amazon.firebat'] = 3
        plan = core.repair_plan(tv, ['com.amazon.storm.lightning.tutorial'])
        with tempfile.TemporaryDirectory() as folder:
            path = core.apply(tv, plan, folder)
            self.assertEqual(tv.states['com.amazon.storm.lightning.tutorial'], 1)
            self.assertEqual(tv.states['com.amazon.firebat'], 3)
            core.restore(tv, core.read_json(path), path)
            self.assertEqual(tv.states['com.amazon.storm.lightning.tutorial'], 3)
        with self.assertRaises(TVLibreError):
            core.repair_plan(tv, ['com.example.unknown'])

    def test_backup_discovery_ignores_address_but_not_identity_or_firmware(self):
        tv = FakeTV()
        with tempfile.TemporaryDirectory() as folder:
            a = Path(folder)/'old-ip'; a.mkdir()
            data = {**core.make_plan(tv), 'status':'applied','operations':[]}
            (a/'backup.json').write_text(json.dumps(data))
            self.assertTrue(diagnostics.backups(folder, tv.device())[0]['restorable_journal'])
            tv.info['build'] = 'NEW'
            self.assertFalse(diagnostics.backups(folder, tv.device())[0]['same_firmware_and_user'])
            tv.info['identity'] = 'different'
            self.assertEqual(diagnostics.backups(folder, tv.device()), [])

    def test_analysis_is_offline_and_keeps_unknown_packages_unknown(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'inventory.json'
            p.write_text(json.dumps({'packages':['com.example.unknown','com.amazon.firebat'],'disabled':['package:com.amazon.firebat']}))
            with patch('tvlibre.cli.ADB') as adb, patch('sys.stdout',new_callable=io.StringIO) as stdout:
                self.assertEqual(main(['analyze','--inventory',str(p)]),0)
                data=json.loads(stdout.getvalue())
                self.assertEqual(data['protected_disabled'],['com.amazon.firebat'])
                self.assertEqual(data['unknown_packages'],['com.example.unknown'])
                adb.assert_not_called()

    def test_server_selection_never_changes_device(self):
        with patch('shutil.which',return_value='/test/adb'),patch('subprocess.run') as run:
            run.return_value=subprocess.CompletedProcess([],0,'ok','')
            ADB('192.0.2.4:5555',server_port=5038).shell('getprop','ro.product.model')
            self.assertEqual(run.call_args.args[0][:6],['/test/adb','-P','5038','-s','192.0.2.4:5555','shell'])
            with self.assertRaises(TVLibreError):ADB('192.0.2.4',server_port=0)

    def test_existing_partial_download_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'app.apk';partial=Path(folder)/'app.apk.part';partial.write_bytes(b'previous')
            with patch.object(launcher,'catalog',return_value=[{'id':'test','sha256':'0'*64,'apk_url':'https://example.invalid/app'}]):
                with self.assertRaises(FileExistsError):launcher.download('test',target)
            self.assertEqual(partial.read_bytes(),b'previous')

    def test_historical_cleanup_can_be_restored_but_not_applied(self):
        tv=FakeTV();pkg='com.amazon.storm.lightning.tutorial';tv.states[pkg]=3
        document={**core.make_plan(tv),'status':'applied','operations':[{'kind':'package','package':pkg,'before':0,'after':3,'attempted':True,'applied':True}]}
        with self.assertRaises(TVLibreError):core.validate(document)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'backup.json'
            core.restore(tv,document,path)
            self.assertEqual(tv.states[pkg],0)

    def test_network_failure_removes_only_our_partial(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'app.apk'
            with patch.object(launcher,'catalog',return_value=[{'id':'x','sha256':'0'*64,'apk_url':'https://example.invalid/app'}]),patch('urllib.request.urlopen',side_effect=OSError('offline')):
                with self.assertRaises(OSError):launcher.download('x',p)
            self.assertFalse(p.with_suffix('.apk.part').exists())

    def test_target_created_during_download_is_not_overwritten(self):
        import hashlib
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'app.apk'
            def response(*args,**kwargs):
                p.write_bytes(b'user-file')
                return io.BytesIO(b'apk')
            with patch.object(launcher,'catalog',return_value=[{'id':'x','sha256':hashlib.sha256(b'apk').hexdigest(),'apk_url':'https://example.invalid/app'}]),patch('urllib.request.urlopen',side_effect=response):
                with self.assertRaises(FileExistsError):launcher.download('x',p)
            self.assertEqual(p.read_bytes(),b'user-file')
            self.assertFalse(p.with_suffix('.apk.part').exists())

    def test_nul_is_refused_before_transport(self):
        with patch('shutil.which',return_value='/test/adb'),patch('subprocess.run') as run:
            with self.assertRaises(TVLibreError):ADB('192.0.2.4').shell('echo','bad\0data')
            run.assert_not_called()
