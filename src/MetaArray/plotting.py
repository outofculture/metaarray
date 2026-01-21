try:
    import pyqtgraph as pg
    from pyqtgraph import Qt, GraphicsView
except ImportError:
    raise ImportError("MetaArray plotting requires pyqtgraph: pip install pyqtgraph")


class MetaArrayPlotWidget(pg.GraphicsView):
    """Widget implementing a :class:`~pyqtgraph.GraphicsView` with a single
    :class:`~pyqtgraph.MultiPlotItem` inside."""

    def __init__(self, parent=None):
        self.minPlotHeight = 50
        self.mPlotItem = MetaArrayPlotItem()
        super().__init__(parent)
        self.enableMouse(False)
        self.setCentralItem(self.mPlotItem)
        # Explicitly wrap methods from mPlotItem
        # for m in ['setData']:
        # setattr(self, m, getattr(self.mPlotItem, m))
        self.setVerticalScrollBarPolicy(Qt.QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def __getattr__(self, attr):  # implicitly wrap methods from plotItem
        if hasattr(self.mPlotItem, attr):
            m = getattr(self.mPlotItem, attr)
            if hasattr(m, '__call__'):
                return m
        raise AttributeError(attr)

    def setMinimumPlotHeight(self, minimum):
        """Set the minimum height for each sub-plot displayed.

        If the total height of all plots is greater than the height of the
        widget, then a scroll bar will appear to provide access to the entire
        set of plots.

        Added in version 0.9.9
        """
        self.minPlotHeight = minimum
        self.resizeEvent(None)

    def widgetGroupInterface(self):
        return None, MetaArrayPlotWidget.saveState, MetaArrayPlotWidget.restoreState

    def saveState(self):
        return {}
        # return self.plotItem.saveState()

    def restoreState(self, state):
        pass
        # return self.plotItem.restoreState(state)

    def close(self):
        self.mPlotItem.close()
        self.mPlotItem = None
        self.setParent(None)
        GraphicsView.close(self)

    def setRange(self, *args, **kwds):
        GraphicsView.setRange(self, *args, **kwds)
        if self.centralWidget is not None:
            r = self.range
            minHeight = len(self.mPlotItem.plots) * self.minPlotHeight
            if r.height() < minHeight:
                r.setHeight(minHeight)
                r.setWidth(r.width() - self.verticalScrollBar().width())
            self.centralWidget.setGeometry(r)

    def resizeEvent(self, ev):
        if self.closed:
            return
        if self.autoPixelRange:
            self.range = Qt.QtCore.QRectF(0, 0, self.size().width(), self.size().height())
        # we do this because some subclasses like to redefine setRange in an incompatible way.
        MetaArrayPlotWidget.setRange(self, self.range, padding=0, disableAutoPixel=False)
        self.updateMatrix()


class MetaArrayPlotItem(pg.GraphicsLayout):
    """
    :class:`~pyqtgraph.GraphicsLayout` that automatically generates a grid of
    plots from a MetaArray.

    .. seealso:: :class:`~pyqtgraph.MultiPlotWidget`: Widget containing a MultiPlotItem
    """

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.plots = []

    def plot(self, data, **plotArgs):
        """Plot the data from a MetaArray with each array column as a separate
        :class:`~pyqtgraph.PlotItem`.

        Axis labels are automatically extracted from the array info.

        ``plotArgs`` are passed to :meth:`PlotItem.plot
        <pyqtgraph.PlotItem.plot>`.
        """
        # self.layout.clear()

        if hasattr(data, 'implements') and data.implements('MetaArray'):
            if data.ndim != 2:
                raise Exception("MultiPlot currently only accepts 2D MetaArray.")
            ic = data.infoCopy()
            ax = 0
            for i in [0, 1]:
                if 'cols' in ic[i]:
                    ax = i
                    break
            # print "Plotting using axis %d as columns (%d plots)" % (ax, data.shape[ax])
            for i in range(data.shape[ax]):
                pi = self.addPlot()
                self.nextRow()
                sl = [slice(None)] * 2
                sl[ax] = i
                pi.plot(data[tuple(sl)], **plotArgs)
                # self.layout.addItem(pi, i, 0)
                self.plots.append((pi, i, 0))
                info = ic[ax]['cols'][i]
                title = info.get('title', info.get('name', None))
                units = info.get('units', None)
                pi.setLabel('left', text=title, units=units)
            info = ic[1 - ax]
            title = info.get('title', info.get('name', None))
            units = info.get('units', None)
            pi.setLabel('bottom', text=title, units=units)
        else:
            raise Exception("Data type %s not (yet?) supported for MultiPlot." % type(data))

    def close(self):
        if self.plots is not None:
            for p in self.plots:
                try:
                    p[0].close()
                except (AttributeError, RuntimeError):
                    # Item may not be in scene or already closed
                    pass
            self.plots = None
        try:
            self.clear()
        except (AttributeError, RuntimeError):
            # Layout may not be in scene
            pass
