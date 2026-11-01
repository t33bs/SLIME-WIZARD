"""Phase 15 regression: repeatedly reposition the same pixels in one pose.

This GUI integration contract is deliberately not marked xfail: a rejected
second/third Move Original must fail the release gate until actually fixed.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_move_original_reposition_same_pixel_repeatedly_then_place_frame():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **k: True
    try:
        source = Image.new('RGBA', (128, 128))
        color = (244, 89, 33, 180)
        source.putpixel((5, 5), color)
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        animation = window.anim.currentText()
        initial_frames = len(window.model.animations.get(animation, []))
        for x in (5, 7, 9, 11):
            window.slimer_paint(x, 5, False)
            window.slimer_finish_selecting()
            window.slimer_dx.setValue(2)
            window.slimer_apply_move_to_pose()
            assert not window.canvas.slimer_transform_mode, 'Apply Move must finish selection'
            assert window.slimer_selection is not None, 'Slimer must remain ready for the next highlight'
            assert window.slimer_selection.mask.getbbox() is None, 'Apply Move must clear highlighted pixels'
            assert window.slimer_selection.source.tobytes() == window.model.render().tobytes(), 'Next highlight must sample the updated working pose'
            assert window.model.render().getpixel((x, 5))[3] == 0, 'Source pixel not cleared'
            assert window.model.render().getpixel((x + 2, 5)) == color, 'Moved pixel lost/altered'
            assert len(window.model.animations.get(animation, [])) == initial_frames
        assert sum(p['name'] == 'Slimer pose overlay' for p in window.model.parts) == 1
        window.slimer_place_frame()
        assert len(window.model.animations.get(animation, [])) == initial_frames + 1
        assert window.model.render().getpixel((13, 5)) == color
    finally:
        window.close()
