"""Apply Move reports success only after an actual working-pose commit."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_apply_move_reports_failure_then_success_and_does_not_create_frame():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **kw: True
    try:
        image = Image.new('RGBA', (128, 128))
        image.putpixel((4, 4), (255, 80, 10, 180))
        window.model.import_part('source', image)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        animation = window.anim.currentText()
        initial_frames = len(window.model.animations.get(animation, []))
        assert window.slimer_apply_move_to_pose() is False
        window.slimer_paint(4, 4, False)
        assert window.slimer_apply_move_to_pose() is False  # Finish Selecting required
        window.slimer_finish_selecting()
        window.slimer_dx.setValue(2)
        assert window.slimer_apply_move_to_pose() is True
        assert window.model.render().getpixel((4, 4))[3] == 0
        assert window.model.render().getpixel((6, 4)) == (255, 80, 10, 180)
        assert len(window.model.animations.get(animation, [])) == initial_frames
        assert window.slimer_apply_move_to_pose() is False  # completed selection cleared
    finally:
        window.close()
