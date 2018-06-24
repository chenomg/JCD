#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
# =============================================================================
#      FileName: JCDown.py
#          Desc: download images from forum such as 蜂鸟 and 贴吧
#        Author: Jase Chen
#         Email: xxmm@live.cn
#      HomePage: https://jase.im/
#       Version: 0.0.1
#       License: GPLv2
#    LastChange: 2018-06-04 08:52:42
#       History:
# =============================================================================
'''

import wx
import basewin
import requests
import re
from lxml import html
import os
from io import StringIO
import JYoutube
import threading
from time import sleep
import re


class MainWindow(basewin.baseMainWindow):
    def init_main_window(self):
        self.JCDown = JYoutube.JYoutube()
        self.url = ''
        self.localDir = ''
        self.status = 5 * ['']
        self.statusBar.SetStatusWidths([90, 90, 130, 190, 100])
        self.status_thread()
        self.Stream_listCtrl.InsertColumn(0, 'Format')
        self.Stream_listCtrl.InsertColumn(1, 'Description')
        self.Stream_listCtrl.InsertItem(0, 'Hello')
        self.Stream_listCtrl.InsertItem(0, 'World!')
        # self.Stream_listCtrl.SetItem(0, 0, 'hello')
        # self.Stream_listCtrl.SetItem(0, 1, 'world!')

    def baseMainWindowOnClose(self, event):
        self.Destroy()

    def get_image_links(self):
        # 图片地址
        img_list = []
        headers = {
            'user-agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
        }
        r = requests.get(self.url, headers=headers)
        selector = html.fromstring(r.text)
        for sel in selector.xpath(
                '//div[starts-with(@class, "d_post_content j_d_post_content")]'
        ):
            for img in sel.xpath("img/@src"):
                img_list.append(img)
        return img_list

    def download_img(self, img_urls, path=os.getcwd()):
        # 首先检查是否有图片
        if not img_urls:
            print('Image not found!')
        else:
            for img in img_urls:
                # 图片保存名字
                file_name = re.findall(r'\/([\d\w]+\.jpg)', img)
                if file_name:
                    # 二进制写入图片
                    with open(os.path.join(path, file_name[0]), 'wb') as f:
                        f.write(requests.get(img).content)
            print('Download done...')

    def image_urls_input(self):
        urls_list = []
        for url in StringIO(self.image_urls_textCtrl.GetValue()).readlines():
            urls_list.append(url)
        return urls_list

    def image_local_location(self):
        return self.image_local_dirPicker.GetPath()

    def image_download_buttonOnButtonClick(self, event):
        urls = self.image_urls_input()
        local = self.image_local_location()
        print(self.is_individual())

    def set_format(self):
        try:
            format_id_index = self.select_stream_index()
            print(self.stream_formatID_list)
            format_id = self.stream_formatID_list[format_id_index]
            print('Download: ' + format_id)
            if format_id:
                self.JCDown.set_format(format_id)
            else:
                self.JCDown.set_format('best')
        except:
            print('已选择默认格式：best')

    def set_proxy(self):
        if self.proxy_checkBox.GetValue():
            proxy = self.proxy_textCtrl.GetValue()
        else:
            proxy = ''
        self.JCDown.set_proxy(proxy)

    def is_individual(self):
        return self.image_save_individual_checkBox.GetValue()

    def fetch_buttonOnButtonClick(self, event):
        if not self.video_url_textCtrl.GetValue():
            self.JCDown.status[0] = 'Check'
            print('Input Check...')
        else:
            self.url = self.video_url_textCtrl.GetValue()
            self.JCDown.set_url(self.url)
            self.set_proxy()
            self.JCDown.status[0] = 'Fetch_Wait'
            self.JCDown.fetch()
            self.show_stream_list_thread()

    def download_buttonOnButtonClick(self, event):
        if not self.video_url_textCtrl.GetValue(
        ) or not self.save_local_dirPicker.Path:
            self.JCDown.status[0] = 'Check'
            print('Input Check...')
        else:
            self.url = self.video_url_textCtrl.GetValue()
            self.localDir = self.save_local_dirPicker.Path
            self.JCDown.set_url(self.url)
            self.JCDown.set_localDir(self.localDir)
            self.set_proxy()
            self.set_format()
            self.JCDown.status[0] = 'Download_Wait'
            self.JCDown.download()

    def stop_buttonOnButtonClick(self, event):
        self.JCDown.stop()

    def setStatus(self):
        try:
            while True:
                if self.JCDown.status[0] == 'Downloading':
                    self.download_button.Enable(False)
                    self.stop_button.Enable(True)
                    self.status[0] = '下载中 -->'
                    self.status[1:] = self.JCDown.status[1:]
                elif self.JCDown.status[0] == 'Done':
                    self.download_button.Enable(True)
                    self.stop_button.Enable(False)
                    self.fetch_button.Enable(True)
                    self.status[0] = '完成'
                    self.status[1:] = self.JCDown.status[1:]
                elif self.JCDown.status[0] == 'Error':
                    self.download_button.Enable(True)
                    self.stop_button.Enable(False)
                    self.fetch_button.Enable(True)
                    self.status[0] = '错误!'
                    self.status[1:] = self.JCDown.status[1:]
                elif self.JCDown.status[0] == 'Download_Wait':
                    self.download_button.Enable(False)
                    self.stop_button.Enable(False)
                    self.fetch_button.Enable(True)
                    self.status[0] = '即将开始下载'
                    self.status[1:] = self.JCDown.status[1:]
                elif self.JCDown.status[0] == 'Check':
                    self.download_button.Enable(True)
                    self.stop_button.Enable(False)
                    self.fetch_button.Enable(True)
                    self.status[0] = '检查输入!'
                    self.status[1:] = self.JCDown.status[1:]
                elif self.JCDown.status[0] == '':
                    self.download_button.Enable(True)
                    self.stop_button.Enable(False)
                    self.fetch_button.Enable(True)
                    self.status[0] = ''
                    self.status[1:] = self.JCDown.status[1:]
                elif self.JCDown.status[0] == 'Pause':
                    self.download_button.Enable(True)
                    self.stop_button.Enable(False)
                    self.fetch_button.Enable(True)
                    self.status[0] = '已暂停!'
                    self.status[1:] = self.JCDown.status[1:]
                elif self.JCDown.status[0] == 'Fetch_Wait':
                    self.fetch_button.Enable(False)
                    self.status[0] = '获取列表中~'
                elif self.JCDown.status[0] == 'Fetch_Error':
                    self.fetch_button.Enable(True)
                    self.status[0] = '获取列表失败！'
                elif self.JCDown.status[0] == 'Fetch_Done':
                    self.fetch_button.Enable(True)
                    self.status[0] = '获取列表成功！'
                self.statusBar.SetStatusText(self.status[0])
                self.statusBar.SetStatusText(self.status[1], 1)
                self.statusBar.SetStatusText(self.status[2], 2)
                self.statusBar.SetStatusText(self.status[3], 3)
                self.statusBar.SetStatusText(self.status[4], 4)
                sleep(0.1)
        except:
            pass

    def status_thread(self):
        status_thread = threading.Thread(target=self.setStatus, daemon=True)
        status_thread.start()

    def show_stream_list(self):
        self.Stream_listBox.Clear()
        self.JCDown.ft_thread.join()
        self.stream_formatID_list = ['']
        # print(self.JCDown.stream_list)
        try:
            self.Stream_listBox.Append(self.JCDown.stream_list[1])
            for item in self.JCDown.stream_list[2:]:
                self.Stream_listBox.InsertItems([item], 0)
            for item_id in self.JCDown.stream_format_list[:0:-1]:
                self.stream_formatID_list.append(item_id)
            self.Stream_listBox.InsertItems([self.JCDown.stream_list[0]], 0)
            self.stream_formatID_list[0] = 'best'
            self.Stream_listBox.SetSelection(1)
        except:
            print('Error in: show_stream_list')

    def show_stream_list_thread(self):
        show_stream_list_thread = threading.Thread(
            target=self.show_stream_list, daemon=True)
        show_stream_list_thread.start()

    def select_stream_index(self):
        format_ID = self.Stream_listBox.GetSelection()
        return int(format_ID)

    def Stream_listBoxOnListBox(self, event):
        format_ID = self.Stream_listBox.GetSelections()
        print('you select: ' + str(format_ID))

    def need_merge(self):
        if self.merge_VideoAndSound_checkBox.GetValue():
            return True
        else:
            return False

    def get_large_image_links(self):
        pass

    def exit_menuItemOnMenuSelection(self, event):
        wx.CallAfter(self.Destroy)

    def next_link(self):
        pass

    def rule_menuItemOnMenuSelection(self, event):
        # 设置对话框，网页抓取时xpath设置
        basewin.rule_Dialog(self).Show()

    def about_menuItemOnMenuSelection(self, event):
        # 关于本程序
        about_program = '''本程序用来下载：
    *YouTube以及其他国内外主流视频网站的视频

本程序基于youtube_dl开发
Email: xxmm@live.cn
Created by Jase Chen'''
        wx.MessageBox(about_program, 'About', wx.OK | wx.ICON_INFORMATION)


def main():
    app = wx.App()
    main_win = MainWindow(None)
    main_win.init_main_window()
    main_win.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
