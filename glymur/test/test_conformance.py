"""
These tests deal with JPX/JP2/J2K images in the format-corpus repository.
"""
# R0904:  Not too many methods in unittest.
# pylint: disable=R0904

# E1101:  assertWarns introduced in python 3.2
# pylint: disable=E1101

import os
from os.path import join
import re
import sys
import tempfile
import unittest

import glymur
from glymur import Jp2k

try:
    FORMAT_CORPUS_DATA_ROOT = os.environ['FORMAT_CORPUS_DATA_ROOT']
except KeyError:
    FORMAT_CORPUS_DATA_ROOT = None

try:
    OPJ_DATA_ROOT = os.environ['OPJ_DATA_ROOT']
except KeyError:
    OPJ_DATA_ROOT = None


@unittest.skipIf(sys.hexversion < 0x03020000,
                 "Requires features introduced in 3.2 (assertWarns)")
class TestSuiteConformance(unittest.TestCase):
    """Test suite for conformance."""

    def setUp(self):
        self.j2kfile = glymur.data.goodstuff()

    def tearDown(self):
        pass

    @unittest.skipIf(re.match(r"""1\.[0123]""",
                              glymur.version.openjpeg_version) is not None,
                     "Needs 1.3+ to catch this.")
    def test_truncated_eoc(self):
        """Has one byte shaved off of EOC marker."""
        with open(self.j2kfile, 'rb') as ifile:
            data = ifile.read()
            with tempfile.NamedTemporaryFile(suffix='.j2k') as ofile:
                ofile.write(data[:-1])
                ofile.flush()

                j2k = Jp2k(ofile.name)
                with self.assertWarns(UserWarning):
                    codestream = j2k.get_codestream(header_only=False)

                # The last segment is truncated, so there should not be an EOC
                # marker.
                self.assertNotEqual(codestream.segment[-1].marker_id, 'EOC')

                # The codestream is not as long as claimed.
                with self.assertRaises(OSError):
                    j2k.read(rlevel=-1)

    def test_truncated_5000(self):
        """File is missing last 5000 bytes."""
        with open(self.j2kfile, 'rb') as ifile:
            data = ifile.read()
            with tempfile.NamedTemporaryFile(suffix='.j2k') as ofile:
                ofile.write(data[:-5000])
                ofile.flush()

                j2k = Jp2k(ofile.name)
                with self.assertWarns(UserWarning):
                    codestream = j2k.get_codestream(header_only=False)

                # The last segment is truncated, so there should not be an EOC
                # marker.
                self.assertNotEqual(codestream.segment[-1].marker_id, 'EOC')
        
                # The codestream is not as long as claimed.
                with self.assertRaises(OSError):
                    j2k.read(rlevel=-1)


@unittest.skipIf(FORMAT_CORPUS_DATA_ROOT is None,
                 "FORMAT_CORPUS_DATA_ROOT environment variable not set")
@unittest.skipIf(sys.hexversion < 0x03020000,
                 "Requires features introduced in 3.2 (assertWarns)")
class TestSuiteFormatCorpus(unittest.TestCase):
    """Test suite for files in format corpus repository."""

    def test_balloon_trunc3(self):
        """Most of last tile is missing."""
        jfile = os.path.join(FORMAT_CORPUS_DATA_ROOT,
                             'jp2k-test/byteCorruption/balloon_trunc3.jp2')
        j2k = Jp2k(jfile)
        with self.assertWarns(UserWarning):
            codestream = j2k.get_codestream(header_only=False)

        # The last segment is truncated, so there should not be an EOC marker.
        self.assertNotEqual(codestream.segment[-1].marker_id, 'EOC')

        # Should error out, it does not.
        #with self.assertRaises(OSError):
        #    j2k.read(rlevel=-1)

    def test_jp2_brand_any_icc_profile(self):
        """If 'jp2 ', then the method cannot be any icc profile."""
        jfile = os.path.join(FORMAT_CORPUS_DATA_ROOT,
                             'jp2k-test', 'icc',
                             'balloon_eciRGBv2_ps_adobeplugin.jpf')
        with self.assertWarns(UserWarning):
            Jp2k(jfile)

    def test_jp2_brand_iccpr_mult_colr(self):
        """Has colr box, one that conforms, one that does not."""

        # Wrong 'brand' field; contains two versions of ICC profile: one
        # embedded using "Any ICC" method; other embedded using "Restricted
        # ICC" method, with description ("Modified eciRGB v2") and profileClass
        # ("Input Device") changed relative to original profile.
        jfile = join(FORMAT_CORPUS_DATA_ROOT, 'jp2k-test', 'icc',
                     'balloon_eciRGBv2_ps_adobeplugin_jp2compatible.jpf')
        with self.assertWarns(UserWarning):
            Jp2k(jfile)


@unittest.skipIf(OPJ_DATA_ROOT is None,
                 "OPJ_DATA_ROOT environment variable not set")
@unittest.skipIf(sys.hexversion < 0x03020000,
                 "Requires features introduced in 3.2 (assertWarns)")
class TestSuiteOpj(unittest.TestCase):
    """Test suite for files in openjpeg repository."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_jp2_brand_any_icc_profile(self):
        """If 'jp2 ', then the method cannot be any icc profile."""
        filename = os.path.join(OPJ_DATA_ROOT,
                                'input/nonregression/text_GBR.jp2')
        with self.assertWarns(UserWarning):
            Jp2k(filename)

if __name__ == "__main__":
    unittest.main()
