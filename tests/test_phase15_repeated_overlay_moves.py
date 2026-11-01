"""Regression: repeated Slimer edits must not duplicate or lose artwork."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_move_same_pixel_twice_then_undo_and_redo():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        source = Image.new('RGBA', (128, 128))
        source.putpixel((5, 5), (231, 72, 44, 255))
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        animation = window.anim.currentText()
        initial_frames = len(window.model.animations.get(animation, []))

        for start_x, end_x in ((5, 7), (7, 9)):
            window.slimer_paint(start_x, 5, False)
            window.slimer_finish_selecting()
            window.slimer_dx.setValue(end_x - start_x)
            window.slimer_apply_move_to_pose()
            assert window.slimer_selection is None or window.slimer_selection.mask.getbbox() is None
            rendered = window.model.render()
            assert rendered.getpixel((start_x, 5))[3] == 0
            assert rendered.getpixel((end_x, 5)) == (231, 72, 44, 255)
            assert len(window.model.animations.get(animation, [])) == initial_frames
            assert sum(p['name'] == 'Slimer pose overlay' for p in window.model.parts) == 1

        window.undo()
        assert window.model.render().getpixel((7, 5)) == (231, 72, 44, 255)
        assert window.model.render().getpixel((9, 5))[3] == 0
        window.redo()
        assert window.model.render().getpixel((9, 5)) == (231, 72, 44, 255)
        assert window.model.render().getpixel((7, 5))[3] == 0
    finally:
        window.close()
