"""Exercise the existing asset table against real staged Slimer assets (Windows/Qt)."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_existing_table_transforms_each_new_slimer_layer_without_editing_source():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **kw: True
    try:
        source = Image.new('RGBA', (128, 128))
        for x in (8, 18, 28):
            source.putpixel((x, 8), (255, 0, 0, 255))
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(False)
        created = []
        for number, x in enumerate((8, 18, 28), 1):
            window.slimer_paint(x, 8, False)
            assert window.slimer_create_editable_layer(), window.status.text()
            pending = window._slimer_pending_part
            assert window.model.parts[window.selected] is pending
            window.x.setValue(number * 3)
            window.y.setValue(number * 4)
            window.angle.setValue(number * 10)
            assert pending['x'] == number * 3
            assert pending['y'] == number * 4
            assert window.model.angles[window.selected] == number * 10
            # Selecting the original asset cannot mutate the frozen source
            # while a destination is waiting for Apply Move.
            window.assets.setCurrentRow(0)
            old_x = window.model.parts[0]['x']
            window.x.setValue(old_x + 9)
            assert window.model.parts[0]['x'] == old_x
            window.assets.setCurrentRow(len(window.model.parts) - 1)
            assert window.slimer_apply_move_to_pose(), window.status.text()
            created.append(pending)
        assert len({id(p) for p in created}) == 3
        assert all(any(p is q for q in window.model.parts) for p in created)
        assert [p['x'] for p in created] == [3, 6, 9]
        assert [p['y'] for p in created] == [4, 8, 12]
    finally:
        window.close()
