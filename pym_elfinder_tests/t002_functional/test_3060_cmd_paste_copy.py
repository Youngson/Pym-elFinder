import unittest
import os

from pprint import pprint

from .. import lib
from .. import lib_localfilesystem as lfs


class TestCmdPasteCopy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.finder = lib.create_finder()
        cls.fixt = lib.CMD_FIXT['cmd_paste-copy.txt'][0]

    def setUp(self):
        # Create a dir that will be destination of copy
        self.dst_dir = lfs.create_dst_dir()
        # Create some files and a dir tree that will be copied
        lfs.create_src_items(lfs.SOURCE_ITEMS, lfs.DIR)

    def tearDown(self):
        lfs.unlink_dst_items(lfs.SOURCE_ITEMS, self.dst_dir)
        lfs.unlink_dst_dir(self.dst_dir)
        lfs.unlink_src_items(lfs.SOURCE_ITEMS, lfs.DIR)

    def test_001_localfilesystem_copy(self):
        """
        Tests low-level copy of concrete volume driver.
        """
        vol = self.finder.default_volume
        for name in lfs.SOURCE_ITEMS.keys():
            src_path = os.path.join(lfs.DIR, name)
            dst_fullpath = vol._copy(src_path, self.dst_dir, name)
            self.assertEqual(dst_fullpath, os.path.join(self.dst_dir, name))
        lfs.check_src_exists(self, lfs.SOURCE_ITEMS, lfs.DIR)
        lfs.check_dst_exists(self, lfs.SOURCE_ITEMS, self.dst_dir)

    def test_002_volumedriver_copy(self):
        """
        Tests high-level copy of base volume driver.
        """
        vol = self.finder.default_volume
        for name in lfs.SOURCE_ITEMS.keys():
            src_path = os.path.join(lfs.DIR, name)
            dst_fullpath = vol.copy(src_path, self.dst_dir, name)
            self.assertEqual(dst_fullpath, os.path.join(self.dst_dir, name))
        lfs.check_src_exists(self, lfs.SOURCE_ITEMS, lfs.DIR)
        lfs.check_dst_exists(self, lfs.SOURCE_ITEMS, self.dst_dir)

    def test_003_volumedriver_paste(self):
        """
        Tests high-level paste of base volume driver, which calls copy.
        """
        vol = self.finder.default_volume
        dst_hash = vol.encode(self.dst_dir)
        for name in lfs.SOURCE_ITEMS.keys():
            src_path = os.path.join(lfs.DIR, name)
            src_hash = vol.encode(src_path)
            added, removed = vol.paste(vol, src_hash, dst_hash, cut=False)
            # "added" must be a "stat" structure
            self.assertTrue(isinstance(added, dict))
            self.assertEqual(added['name'], name)
            self.assertEqual(removed, None)
        lfs.check_src_exists(self, lfs.SOURCE_ITEMS, lfs.DIR)
        lfs.check_dst_exists(self, lfs.SOURCE_ITEMS, self.dst_dir)

    def test_cmd_paste_copy(self):
        """
        Tests paste command of finder object.

        Does not check the files like the tests above, only the request and
        response.
        """
        req = self.fixt['request']
        r0 = self.fixt['response'] # expected response
       
        cmd, args = lib.prepare_request(req)
        assert cmd == 'paste'
        
        # This throws exception on error
        self.finder.run(cmd, args, debug=True)
        
        r = self.finder.response
        #pprint(r); raise Exception("DIE")
        #pprint(r0); raise Exception("DIE")
        lib.prepare_response(r0, r)

        self.assertEqual(r0.keys(), r.keys())
        del r0['debug']
        del r['debug']
        self.maxDiff = None
        self.assertEqual(r0, r)

