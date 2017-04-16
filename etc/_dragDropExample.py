import wx

class tempLine(object):
    def __init__(self, x0, y0):
        self.x0, self.y0 = x0, y0
        self.x1, self.y1 = x0, y0

    def update_endPoint(self, x1, y1):
        self.x1, self.y1 = x1, y1

    def draw(self, gc):
        gc.SetPen(wx.Pen(wx.BLACK, 5))
        gc.DrawLines([(self.x0, self.y0), (self.x1, self.y1)])
        gc.DrawRectangle(100, 100, 150, 150)


class DragPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.SetBackgroundColour(wx.WHITE)


        (self.fixed_x, self.fixed_y), self.isLeftDown = (0, 0), False
        # event binding
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        # prepare stock objects.
        self.default_pen = self.create_pen(wx.BLACK, 1)
        self.default_font = self.create_font(8, wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.aLine = None

    def create_pen(self, color, width):
        return wx.Pen(color, width)

    def create_font(self, size, family, style, weight):
        return wx.Font(size, family, style, weight)

    # def OnSize(self, e):
    #     w, h = self.GetSize()
    #     w, h = max(100, w), max(100, h)
    #     self.mem_buffer = wx.EmptyBitmap(w, h, 32)
    #     self.RefreshGC(False)

    def OnPaint(self, _):
        wx.BufferedPaintDC(self, self.mem_buffer)

    def RefreshGC(self, update=True):
        mdc = wx.MemoryDC(self.mem_buffer)
        mdc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        mdc.Clear()
        gc = wx.GraphicsContext.Create(mdc)
        gc.SetPen(self.default_pen)
        gc.SetFont(self.default_font, wx.BLACK)
        self.OnDraw(gc)

        self.Refresh(False)

    def OnDraw(self, gc):
        gc.DrawLines([(0, 0), (10,10)])
        gc.DrawRectangle(10, 10, 10, 10)
        if self.aLine:
            self.aLine.draw(gc)

    def OnLeftDown(self, e):
        self.isLeftDown, self.fixed_x, self.fixed_y = True, e.GetX(), e.GetY()
        self.aLine = tempLine(self.fixed_x, self.fixed_y)
        self.SetFocus()
        self.CaptureMouse()

    def OnMotion(self, e):
        if self.isLeftDown:
            cur_x, cur_y = e.GetX(), e.GetY()
            self.aLine.update_endPoint(cur_x, cur_y)
            print self.aLine.x0, self.aLine.x1
            self.RefreshGC()

    def OnLeftUp(self, _):
        if self.isLeftDown:
            self.isLeftDown = False
            self.ReleaseMouse()



class TestFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "DragAndDrop", size=(640,480), pos=(100, 100))
        DragPanel(self)


if __name__ == '__main__':
    app = wx.App(False)
    frame = TestFrame(None)
    frame.Show(True)
    app.MainLoop()