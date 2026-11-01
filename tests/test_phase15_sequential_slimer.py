"""Phase 15: repeated Slimer edits must not create timeline frames implicitly."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_two_sequential_copy_moves_reuse_one_overlay_without_frames():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        source = Image.new('RGBA', (128, 128))
        source.putpixel((5, 5), (255, 0, 0, 255))
        source.putpixel((10, 10), (0, 0, 255, 255))
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(False)
        animation = window.anim.currentText()
        before_frames = len(window.model.animations.get(animation, []))
        for x, y, dx in ((5, 5, 2), (10, 10, 3)):
            window.slimer_paint(x, y, False)
            window.slimer_finish_selecting()
            window.slimer_dx.setValue(dx)
            window.slimer_apply_move_to_pose()
            assert len(window.model.animations.get(animation, [])) == before_frames
            assert not window.canvas.slimer_transform_mode
        assert sum(p['name'] == 'Slimer pose overlay' for p in window.model.parts) == 1
        overlay = next(p['image'] for p in window.model.parts if p['name'] == 'Slimer pose overlay')
        assert overlay.getpixel((7, 5)) == (255, 0, 0, 255)
        assert overlay.getpixel((13, 10)) == (0, 0, 255, 255)
        assert source.getpixel((5, 5)) == (255, 0, 0, 255)
    finally:
        window.close()


def test_two_sequential_move_original_then_place_frame():
    """Windows regression: second Apply Move and Place Frame without disabling Slimer."""
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        source = Image.new('RGBA', (128, 128))
        source.putpixel((5, 5), (255, 0, 0, 255))
        source.putpixel((10, 10), (0, 0, 255, 255))
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        animation = window.anim.currentText()
        initial_frames = len(window.model.animations.get(animation, []))
        for x, y, dx in ((5, 5, 2), (10, 10, 3)):
            window.slimer_paint(x, y, False)
            window.slimer_finish_selecting()
            window.slimer_dx.setValue(dx)
            assert window.slimer_apply_move_to_pose(), window.status.text()
            assert not window.canvas.slimer_transform_mode
            assert len(window.model.animations.get(animation, [])) == initial_frames
        rendered = window.model.render()
        assert rendered.getpixel((5, 5))[3] == 0
        assert rendered.getpixel((10, 10))[3] == 0
        assert rendered.getpixel((7, 5)) == (255, 0, 0, 255)
        assert rendered.getpixel((13, 10)) == (0, 0, 255, 255)
        assert window.slimer_place_frame(), window.status.text()
        assert len(window.model.animations[animation]) == initial_frames + 1
        assert window.model.render().getpixel((7, 5)) == (255, 0, 0, 255)
    finally:
        window.close()


def test_place_frame_with_unfinished_slimer_highlight_is_nondestructive():
    """Place Frame must work without disabling Slimer or committing an unfinished move."""
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        source = Image.new('RGBA', (128, 128))
        source.putpixel((5, 5), (255, 0, 0, 255))
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        animation = window.anim.currentText()
        before = len(window.model.animations.get(animation, []))
        window.slimer_paint(5, 5, False)  # still highlighting; no Finish Selecting
        assert not window.canvas.slimer_transform_mode
        assert window.slimer_place_frame(), window.status.text()
        assert len(window.model.animations[animation]) == before + 1
        assert window.model.render().getpixel((5, 5)) == (255, 0, 0, 255)
    finally:
        window.close()
