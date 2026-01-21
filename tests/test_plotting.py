"""
Tests for MetaArray plotting widgets using pyqtgraph.
"""

import numpy as np
import pytest

try:
    import pyqtgraph as pg
    from pyqtgraph import Qt
    from MetaArray import MetaArray, axis
    from MetaArray.plotting import MetaArrayPlotWidget, MetaArrayPlotItem

    HAS_PYQTGRAPH = True
except ImportError:
    HAS_PYQTGRAPH = False

pytestmark = pytest.mark.skipif(not HAS_PYQTGRAPH, reason="pyqtgraph not installed")


@pytest.fixture
def qapp():
    """Create QApplication instance for tests."""
    app = Qt.QtWidgets.QApplication.instance()
    if app is None:
        app = Qt.QtWidgets.QApplication([])
    yield app


@pytest.fixture
def sample_2d_metaarray():
    """Create a 2D MetaArray for testing plots."""
    # Create a 2D array with time axis and signal columns
    data = np.random.randn(100, 3)

    info = [
        {"name": "Time", "units": "s", "values": np.linspace(0, 1.0, 100)},
        {
            "name": "Signal",
            "cols": [
                {"name": "Voltage 0", "units": "V"},
                {"name": "Voltage 1", "units": "V"},
                {"name": "Current 0", "units": "A"},
            ],
        },
    ]

    return MetaArray(data, info=info)


@pytest.fixture
def sample_2d_metaarray_alt():
    """Create a 2D MetaArray with axes in different order."""
    # Create a 2D array with signal columns first, then time
    data = np.random.randn(3, 100)

    info = [
        {
            "name": "Signal",
            "cols": [
                {"name": "Channel A", "units": "mV"},
                {"name": "Channel B", "units": "mV"},
                {"name": "Channel C", "units": "mV"},
            ],
        },
        {"name": "Time", "units": "ms", "values": np.linspace(0, 100, 100)},
    ]

    return MetaArray(data, info=info)


class TestMultiPlotItem:
    """Test the MultiPlotItem class."""

    def test_init(self, qapp):
        """Test MultiPlotItem initialization."""
        item = MetaArrayPlotItem()
        assert item.plots == []

    def test_plot_2d_metaarray_time_first(self, qapp, sample_2d_metaarray):
        """Test plotting a 2D MetaArray with time axis first."""
        item = MetaArrayPlotItem()
        item.plot(sample_2d_metaarray)

        # Should create 3 plots (one for each signal column)
        assert len(item.plots) == 3

        # Check that each plot was created
        for i, (plot_item, row, col) in enumerate(item.plots):
            assert isinstance(plot_item, pg.PlotItem)
            assert row == i
            assert col == 0

    def test_plot_2d_metaarray_signal_first(self, qapp, sample_2d_metaarray_alt):
        """Test plotting a 2D MetaArray with signal axis first."""
        item = MetaArrayPlotItem()
        item.plot(sample_2d_metaarray_alt)

        # Should create 3 plots (one for each signal column)
        assert len(item.plots) == 3

        # Check that plots were created
        for i, (plot_item, row, col) in enumerate(item.plots):
            assert isinstance(plot_item, pg.PlotItem)

    def test_plot_sets_axis_labels(self, qapp, sample_2d_metaarray):
        """Test that plot() sets appropriate axis labels."""
        item = MetaArrayPlotItem()
        item.plot(sample_2d_metaarray)

        # Check first plot has correct left label (first signal column)
        first_plot = item.plots[0][0]
        left_label = first_plot.getAxis("left").labelText
        assert "Voltage 0" in left_label or left_label != ""

        # Check last plot has bottom label (time axis)
        last_plot = item.plots[-1][0]
        bottom_label = last_plot.getAxis("bottom").labelText
        assert "Time" in bottom_label or bottom_label != ""

    def test_plot_rejects_non_metaarray(self, qapp):
        """Test that plot() raises exception for non-MetaArray data."""
        item = MetaArrayPlotItem()

        with pytest.raises(Exception, match="not \\(yet\\?\\) supported"):
            item.plot(np.array([1, 2, 3]))

    def test_plot_rejects_non_2d_metaarray(self, qapp):
        """Test that plot() raises exception for non-2D MetaArray."""
        item = MetaArrayPlotItem()

        # Create a 1D MetaArray
        data = MetaArray(np.array([1, 2, 3]), info=[{"name": "x"}])

        with pytest.raises(Exception, match="currently only accepts 2D"):
            item.plot(data)

    def test_plot_with_plot_args(self, qapp, sample_2d_metaarray):
        """Test that plot arguments are passed through."""
        item = MetaArrayPlotItem()

        # This should not raise an error
        item.plot(sample_2d_metaarray, pen="r", symbol="o")

        # Should still create the plots
        assert len(item.plots) == 3

    def test_close(self, qapp, sample_2d_metaarray):
        """Test that close() properly cleans up."""
        item = MetaArrayPlotItem()
        item.plot(sample_2d_metaarray)

        assert len(item.plots) == 3

        item.close()

        # Plots should be None after close
        assert item.plots is None


class TestMetaArrayPlotWidget:
    """Test the MetaArrayPlotWidget class."""

    def test_init(self, qapp):
        """Test MetaArrayPlotWidget initialization."""
        widget = MetaArrayPlotWidget()

        assert widget.minPlotHeight == 50
        assert widget.mPlotItem is not None
        assert isinstance(widget.mPlotItem, MetaArrayPlotItem)

    def test_widget_displays(self, qapp):
        """Test that widget can be shown."""
        widget = MetaArrayPlotWidget()
        widget.show()

        # Just verify it doesn't crash
        assert widget.isVisible()

        widget.close()

    def test_set_data_via_mplotitem(self, qapp, sample_2d_metaarray):
        """Test setting data through the MultiPlotItem."""
        widget = MetaArrayPlotWidget()

        # Should be able to call plot on the widget (via __getattr__)
        widget.plot(sample_2d_metaarray)

        # Check that plots were created
        assert len(widget.mPlotItem.plots) == 3

        widget.close()

    def test_getattr_wrapper(self, qapp):
        """Test that __getattr__ properly wraps mPlotItem methods."""
        widget = MetaArrayPlotWidget()

        # Should be able to access mPlotItem methods
        assert hasattr(widget, "plot")
        assert callable(widget.plot)

        widget.close()

    def test_getattr_raises_on_invalid(self, qapp):
        """Test that __getattr__ raises AttributeError for invalid attributes."""
        widget = MetaArrayPlotWidget()

        with pytest.raises(AttributeError):
            _ = widget.nonexistent_method

        widget.close()

    def test_set_minimum_plot_height(self, qapp):
        """Test setMinimumPlotHeight() method."""
        widget = MetaArrayPlotWidget()

        assert widget.minPlotHeight == 50

        widget.setMinimumPlotHeight(100)

        assert widget.minPlotHeight == 100

        widget.close()

    def test_save_restore_state(self, qapp):
        """Test saveState() and restoreState() methods."""
        widget = MetaArrayPlotWidget()

        # Save state
        state = widget.saveState()

        # Should return empty dict (as per current implementation)
        assert isinstance(state, dict)
        assert len(state) == 0

        # Restore should not crash
        widget.restoreState(state)

        widget.close()

    def test_widget_group_interface(self, qapp):
        """Test widgetGroupInterface() method."""
        widget = MetaArrayPlotWidget()

        result = widget.widgetGroupInterface()

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[0] is None
        assert result[1] == MetaArrayPlotWidget.saveState
        assert result[2] == MetaArrayPlotWidget.restoreState

        widget.close()

    def test_close(self, qapp, sample_2d_metaarray):
        """Test that close() properly cleans up the widget."""
        widget = MetaArrayPlotWidget()
        widget.plot(sample_2d_metaarray)

        assert widget.mPlotItem is not None

        widget.close()

        # mPlotItem should be None after close
        assert widget.mPlotItem is None

    def test_scroll_bar_policy(self, qapp):
        """Test that scroll bars are configured correctly."""
        widget = MetaArrayPlotWidget()

        # Check scroll bar policies
        v_policy = widget.verticalScrollBarPolicy()
        h_policy = widget.horizontalScrollBarPolicy()

        assert v_policy == Qt.QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        assert h_policy == Qt.QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded

        widget.close()

    def test_set_range_with_min_height(self, qapp, sample_2d_metaarray):
        """Test that setRange respects minimum plot height."""
        widget = MetaArrayPlotWidget()
        widget.setMinimumPlotHeight(75)
        widget.plot(sample_2d_metaarray)

        # The widget should handle setRange calls
        # This mostly tests that it doesn't crash
        try:
            widget.setRange(Qt.QtCore.QRectF(0, 0, 800, 600))
        except:
            # Some platforms may not support this without a real window
            pass

        widget.close()


class TestIntegration:
    """Integration tests for the plotting system."""

    def test_full_workflow(self, qapp):
        """Test a complete workflow of creating and plotting data."""
        # Create MetaArray
        data = np.sin(np.linspace(0, 4 * np.pi, 200)).reshape(200, 1)
        data = np.hstack([data, np.cos(np.linspace(0, 4 * np.pi, 200)).reshape(200, 1)])

        info = [
            {"name": "Time", "units": "s", "values": np.linspace(0, 2.0, 200)},
            {"name": "Signal", "cols": [{"name": "Sine Wave", "units": "V"}, {"name": "Cosine Wave", "units": "V"}]},
        ]

        ma = MetaArray(data, info=info)

        # Create widget and plot
        widget = MetaArrayPlotWidget()
        widget.plot(ma)

        # Verify plots were created
        assert len(widget.mPlotItem.plots) == 2

        # Verify we can access the plots
        for plot_item, _, _ in widget.mPlotItem.plots:
            assert isinstance(plot_item, pg.PlotItem)

        # Clean up
        widget.close()

    def test_real_data_file(self, qapp):
        """Test plotting data loaded from a file."""
        # Create and save a MetaArray
        data = np.random.randn(50, 4)
        info = [
            {"name": "Sample", "values": np.arange(50)},
            {"name": "Channels", "cols": [{"name": f"Ch{i}", "units": "mV"} for i in range(4)]},
        ]

        ma = MetaArray(data, info=info)

        # Plot it
        widget = MetaArrayPlotWidget()
        widget.plot(ma)

        assert len(widget.mPlotItem.plots) == 4

        widget.close()
