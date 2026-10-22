import json
from pathlib import Path
import tempfile
import unittest
from cast_bank import NamedCast,OwnedCastBank
from cast_prior import CastControls


class NamedBankTests(unittest.TestCase):
    def test_reference_name_startup_and_monochrome_selection_and_unknown_guard(self):
        e=Path(__file__).resolve().parent/'evidence'
        # No private binary needed for Standard's actual non-startup fallback.
        bank=OwnedCastBank(Path('/nonexistent-private'),e/'cast-table-selection.json',e/'cast-names.json')
        out=bank.evaluate(NamedCast('Standard'),CastControls(.5,-.5,.5))
        self.assertIsNone(out.lower_indices)
        with self.assertRaises(ValueError):bank.evaluate(NamedCast('guessed-cast'),CastControls(0,0,0))
        with self.assertRaises(ValueError):bank.evaluate(NamedCast('Standard',1),CastControls(0,0,0))

    def test_wrong_build_does_not_inherit_the_matched_table_names(self):
        e=Path(__file__).resolve().parent/'evidence'
        with tempfile.TemporaryDirectory()as t:
            p=Path(t)/'wrong.json';d=json.loads((e/'cast-names.json').read_text());d['build']='24A435';p.write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError,'hardware/build'):
                OwnedCastBank(Path(t),e/'cast-table-selection.json',p)


if __name__=='__main__':unittest.main()
