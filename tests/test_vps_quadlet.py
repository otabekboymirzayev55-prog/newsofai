import unittest
from vps_quadlet import inspect, patch


class UpgradeTests(unittest.TestCase):
    original = '''[Unit]
Description=Existing publisher
[Container]
Image=localhost/newsofai:old
ContainerName=newsofai
EnvironmentFile=/etc/newsofai/bot.env
Environment="POST_INTERVAL_HOURS=2" "OTHER=keep this"
Volume=newsofai-data:/data:Z
Volume=/opt/assets:/assets:ro
[Service]
Restart=always
[Install]
WantedBy=multi-user.target
'''

    def test_upgrade_retains_env_volumes_and_other_service_settings(self):
        new = patch(self.original, 'localhost/newsofai:editorial-012345abcdef')
        for line in self.original.splitlines():
            if not line.startswith('Image='):
                self.assertIn(line + '\n', new)
        self.assertNotIn('Image=localhost/newsofai:old', new)
        self.assertLess(new.index('OTHER=keep this'), new.index('Environment=POST_INTERVAL_HOURS=1.5'))
        self.assertLess(new.index('Environment=POST_INTERVAL_HOURS=1.5'), new.index('[Service]'))
        self.assertEqual(inspect(new)[0]['env'], '/etc/newsofai/bot.env')

    def test_unsupported_installations_are_rejected_before_patch(self):
        for text in [self.original.replace(':/data:Z', ':/database'),
                     self.original.replace('ContainerName=newsofai', 'ContainerName=other'),
                     self.original + '\n[Container]\nImage=other\n',
                     self.original.replace('Image=localhost/newsofai:old', 'Image=a\nImage=b')]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                patch(text, 'localhost/newsofai:editorial-012345abcdef')

    def test_caller_cannot_inject_a_quadlet_directive_via_image(self):
        with self.assertRaises(ValueError):
            patch(self.original, 'localhost/newsofai:tag\nEnvironment=INJECTED=yes')


if __name__ == '__main__':
    unittest.main()
