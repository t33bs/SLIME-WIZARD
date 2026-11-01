"""A fully off-canvas transform must never erase its original pixels."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_offcanvas_move_does_not_erase_or_create_frame():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **k: True
    try:
        source = Image.new('RGBA', (128, 128))
        source.putpixel((5, 5), (240, 50, 30, 160))
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        before = window.model.render().tobytes()
        animation = window.anim.currentText()
        frame_count = len(window.model.animations.get(animation, []))
        window.slimer_paint(5, 5, False)
        window.slimer_finish_selecting()
        window.slimer_dx.setValue(127)
        assert window._slimer_commit(False, into_pose=True) is False
        assert window.model.render().tobytes() == before
        assert len(window.model.animations.get(animation, [])) == frame_count
        assert not any(p['name'] == 'Slimer pose overlay' for p in window.model.parts)
    finally:
        window.close()
