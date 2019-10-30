import wx
from mygame_Neat import *


###########################################################################
## Class MyFrame1
###########################################################################

class StartFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"AI simulator", pos=wx.DefaultPosition,
                          size=wx.Size(500, 300), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_panel3 = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.m_panel3.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT))

        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText1 = wx.StaticText(self.m_panel3, wx.ID_ANY, u"PLAY Yourself", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText1.Wrap(-1)
        self.m_staticText1.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT))

        bSizer2.Add(self.m_staticText1, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.TOP, 20)

        self.start_play_button = wx.Button(self.m_panel3, wx.ID_ANY, u"START", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.start_play_button, 0, wx.ALIGN_CENTER, 5)

        self.m_panel3.SetSizer(bSizer2)
        self.m_panel3.Layout()
        bSizer2.Fit(self.m_panel3)
        bSizer1.Add(self.m_panel3, 1, wx.EXPAND | wx.ALL, 0)

        self.m_panel5 = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.m_panel5.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INACTIVECAPTION))
        self.m_panel5.SetMaxSize(wx.Size(3, -1))

        bSizer1.Add(self.m_panel5, 1, wx.EXPAND | wx.ALL, 0)

        self.m_panel4 = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.m_panel4.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT))

        bSizer3 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText2 = wx.StaticText(self.m_panel4, wx.ID_ANY, u"AI simulator", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText2.Wrap(-1)
        bSizer3.Add(self.m_staticText2, 0, wx.ALIGN_CENTER | wx.ALL, 20)

        agent_cb= [u"100 score agent", u"200 score agent", u"500 score agent",
                   u"800 score agent", u"1500 score agent", u"3000 score agent"]
        self.m_comboBox1 = wx.ComboBox(self.m_panel4, wx.ID_ANY, u"100 score agent", wx.DefaultPosition, wx.DefaultSize,
                                       agent_cb, 0)
        self.m_comboBox1.SetSelection(0)
        bSizer3.Add(self.m_comboBox1, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.agent_play_button = wx.Button(self.m_panel4, wx.ID_ANY, u"시작", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer3.Add(self.agent_play_button, 0, wx.ALIGN_CENTER | wx.ALL, 20)

        self.m_panel4.SetSizer(bSizer3)
        self.m_panel4.Layout()
        bSizer3.Fit(self.m_panel4)
        bSizer1.Add(self.m_panel4, 1, wx.EXPAND | wx.ALL, 0)

        self.SetSizer(bSizer1)
        self.Layout()
        self.start_play_button.Bind(wx.EVT_BUTTON,self.play_game)
        self.agent_play_button.Bind(wx.EVT_BUTTON,self.simulate)

        self.Centre(wx.BOTH)
    def play_game(self,evt):
        play_game()
    def simulate(self,evt):
        agent_number = self.m_comboBox1.GetValue()[:-12]
        model_file = "./model_folder/score_"+agent_number+".pickle"
        with open(model_file,'rb') as f :
            model = pickle.load(f)
        See_AI_play(model)

    def __del__(self):
        pass

if  __name__ == "__main__" :
    app = wx.App()
    Start_Frame = StartFrame(None)
    Start_Frame.Show(True)
    app.MainLoop()