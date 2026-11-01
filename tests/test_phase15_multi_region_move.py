"""Repeated Move Original on separate areas of one layer must be non-destructive."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_move_two_different_regions_then_revisit_first_without_frames():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **kw: True
    try:
        source = Image.new('RGBA', (128, 128))
        source.putpixel((5, 5), (250, 40, 10, 170))
        source.putpixel((20, 20), (10, 100, 250, 210))
        window.model.import_part('one asset', source)
        window.assets.addItem('one asset')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        animation = window.anim.currentText()
        count = len(window.model.animations.get(animation, []))
        for x, y, dx in ((5, 5, 3), (20, 20, -4), (8, 5, 2)):
            window.slimer_paint(x, y, False)
            window.slimer_finish_selecting()
            window.slimer_dx.setValue(dx)
            window.slimer_apply_move_to_pose()
            assert window.slimer_selection is None or window.slimer_selection.mask.getbbox() is None
            assert window.model.render().getpixel((x, y))[3] == 0
            assert len(window.model.animations.get(animation, [])) == count
        final = window.model.render()
        assert final.getpixel((10, 5)) == (250, 40, 10, 170)
        assert final.getpixel((16, 20)) == (10, 100, 250, 210)
        assert sum(p['name'] == 'Slimer pose overlay' for p in window.model.parts) == 1
    finally:
        window.close()
