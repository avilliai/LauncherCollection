# -*- coding: utf-8 -*-
import logging
import os
import shutil
import signal
import subprocess
import sys
import time
import tkinter as tk
import threading

import colorlog
import ttkbootstrap
import yaml
from tkinter import ttk, messagebox
from tkinter import BooleanVar, Checkbutton
import psutil
import ruamel.yaml
from ruamel.yaml import CommentToken
from ttkbootstrap import style
'''global mans
global mirais
mans=None
mirais=None'''

from ruamel.yaml import YAML
# 创建一个YAML对象来加载和存储YAML数据
yaml = YAML()

def merge_dicts(old, new):
    for k, v in old.items():
        # 如果值是一个字典，并且键在新的yaml文件中，那么我们就递归地更新键值对
        if isinstance(v, dict) and k in new and isinstance(new[k], dict):
            merge_dicts(v, new[k])
        # 如果键在新的yaml文件中，我们就更新它的值
        elif k in new:
            logger.info("更新key"+str(k)+" value"+str(v))
            new[k] = v

def conflict_file_dealter(file_old='old_aiReply.yaml', file_new='new_aiReply.yaml'):
    # 加载旧的YAML文件
    with open(file_old, 'r',encoding="utf-8") as file:
        old_data = yaml.load(file)

    # 加载新的YAML文件
    with open(file_new, 'r',encoding="utf-8") as file:
        new_data = yaml.load(file)

    # 遍历旧的YAML数据并更新新的YAML数据中的相应值
    merge_dicts(old_data, new_data)

    # 把新的YAML数据保存到新的文件中
    with open(file_new, 'w',encoding="utf-8") as file:
        yaml.dump(new_data, file)
def newLogger():
    # 创建一个logger对象
    logger = logging.getLogger("villia")
    # 设置日志级别为DEBUG，这样可以输出所有级别的日志
    logger.setLevel(logging.DEBUG)
    # 创建一个StreamHandler对象，用于输出日志到控制台
    console_handler = logging.StreamHandler()
    # 设置控制台输出的日志格式和颜色
    logger.propagate = False
    console_format = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_colors = {
        'DEBUG': 'white',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
    console_formatter = colorlog.ColoredFormatter(console_format, log_colors=console_colors)
    console_handler.setFormatter(console_formatter)
    # 将控制台处理器添加到logger对象中
    logger.addHandler(console_handler)
    return logger



class CommandFrame(ttk.Frame):
    def __init__(self, master=None, cmd=None, cwd=None):
        super().__init__(master)
        self.cmd = cmd
        self.cwd = cwd
        self.process = None
        self.keep_alive=True

    def create_bingdraw(self):
        self.run_btn = ttk.Button(self,bootstyle="info")
        self.run_btn["text"] = "启动bing ai绘画"
        self.run_btn["command"] = self.start_cmd_thread
        self.run_btn.pack(side="top")
        self.cmd_output = tk.Text(self)
        self.cmd_output.pack(side="top")
    def create_petunia(self):
        self.run_btn = ttk.Button(self, bootstyle="info")
        self.run_btn["text"] = "启动Petunia"
        self.run_btn["command"] = self.start_cmd_thread
        self.run_btn.pack(side="top")
        self.cmd_output = tk.Text(self)
        self.cmd_output.pack(side="top")
    def start_cmd_thread(self):
        cmd_thread = threading.Thread(target=self.run_cmd, daemon=True)
        cmd_thread.start()
        return cmd_thread

    def run_cmd(self):
        #global mans,mirais
        while self.keep_alive:

            self.process = subprocess.Popen(self.cmd, shell=True,cwd=self.cwd)
            if not self.keep_alive:
                # 如果keep_alive被设置为False，不再重启进程，退出方法
                break
            self.process.communicate()
            self.killself()
            print("killself")

    def killself(self):
        print(self.process)
        if self.process is not None:
            pid = self.process.pid
            try:
                # 尝试终止主进程
                self.process.terminate()
                self.process.wait(timeout=5)  # 等待进程终止
            except subprocess.TimeoutExpired:
                print("主进程终止超时，尝试强制终止")
                self.process.kill()
            except Exception as e:
                print(f"终止主进程时发生错误: {e}")

            try:
                # 终止所有子进程
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                for child in children:
                    child.kill()
                parent.kill()
            except psutil.NoSuchProcess:
                print("进程已经不存在")
            except Exception as e:
                print(f"终止子进程时发生错误: {e}")

class GitFrame(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        self.clone_btn = ttk.Button(self)
        self.clone_btn["text"] = "处理冲突文件"
        self.clone_btn["command"] = self.git_clone
        self.clone_btn.pack(side="top", pady=10) # 添加间隔


    def git_clone(self):
        logger.info("首先需要的是配置环境，按任意键开始部署环境，按1跳过,跳过后将开始获取bot代码")
        messagebox.showinfo("Message", "确保已经将旧的 settings.yaml 和 bing_dalle3_config.yaml 放置在oldConfig文件夹下！")
        if os.path.exists("oldConfig/settings.yaml"):
            conflict_file_dealter("oldConfig/settings.yaml","settings.yaml")
        if os.path.exists("oldConfig/bing_dalle3_config.yaml"):
            conflict_file_dealter("oldConfig/bing_dalle3_config.yaml", "bing_dalle3_config.yaml")
        messagebox.showinfo("Message", "请关闭并重启UI")
        sys.exit()

class InfoWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.label = tk.Label(self, text="")
        self.label.pack()

    def update_text(self, text):
        self.label.config(text=text)
class Application(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        # 让master窗口随着窗口的最大化而变大
        self.master.geometry('800x600')  # 设置master窗口的初始大小，可以修改
        self.master.bind("<Configure>", self.update_size)  # 当窗口大小改变时触发我们下面定义的update_size函数
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.pack()
        self.create_widgets()

    def update_size(self, event=None):
        # 这个函数在窗口大小改变时被触发，会更新master窗口中Text的大小
        try:
            self.frame1.cmd_output.config(width=self.master.winfo_width(), height=self.master.winfo_height())
        except:
            pass
        try:
            self.frame21.cmd_output.config(width=self.master.winfo_width(), height=self.master.winfo_height())
        except:
            pass
    def create_widgets(self):
        notebook = ttk.Notebook(self,style="info")

        self.frame21 = CommandFrame(notebook, cmd='main2.exe')
        self.frame21.create_petunia()
        notebook.add(self.frame21, text='Petunia')

        self.frame1 = CommandFrame(notebook, cmd='bing_image_creator.exe')
        self.frame1.create_bingdraw()
        notebook.add(self.frame1, text='bingai绘画')

        self.frame3 = GitFrame(notebook)
        notebook.add(self.frame3, text='工具页')
        # 在Application类的create_widgets方法中添加新页面
        if os.path.exists("bing_dalle3_config.yaml"):
            self.frame6 = YamlPage(notebook, yaml_file='bing_dalle3_config.yaml')
            notebook.add(self.frame6, text='bing ai绘画必要配置项')
        if os.path.exists("settings.yaml"):
            self.frame5 = YamlPage(notebook, yaml_file='settings.yaml')
            notebook.add(self.frame5, text='bot设置')
        notebook.pack(expand=1, fill='both')
        #底部小组件
        self.status_bar = StatusBar(self.master)
        self.status_bar.pack(side='bottom', fill='x')
        self.status_bar.update_status()
    def on_closing(self):
        print("closing")
        self.frame1.keep_alive = False
        self.frame1.killself()
        self.frame21.keep_alive = False
        self.frame21.killself()
        try:
            root.destroy()
        except Exception as e:
            print(e)
        try:
            sys.exit()
        except Exception as e:
            print(e)
class YamlPage(ttk.Frame):
    def __init__(self, master=None, yaml_file=None):
        super().__init__(master)
        self.created=list([0])
        self.yaml_file = yaml_file
        self.yaml = ruamel.yaml.YAML()
        self.values = {}
        self.comments = {}
        self.vars = {}

        self.load_yaml()
        self.datas = self.load_yaml()
        self.childrenkeys = []
        # 创建一个frame作为canvas和scrollbars的容器
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # 创建一个滚动的canvas
        self.canvas = tk.Canvas(main_frame)
        self.canvas.grid(row=0, column=0, sticky="nsew")  # 注意这里使用grid布局

        # 为canvas添加纵向和横向滚动条
        ttk.Scrollbar(main_frame, command=self.canvas.yview).grid(row=0, column=1, sticky="ns")

        ttk.Scrollbar(main_frame, command=self.canvas.xview, orient='horizontal').grid(row=1, column=0, sticky="ew")
        '''y_scrollbar = tk.Scrollbar(self, command=canvas.yview)
        y_scrollbar.pack(side="right", fill="y")

        x_scrollbar = tk.Scrollbar(self, command=canvas.xview, orient='horizontal')
        x_scrollbar.pack(side="bottom", fill="x",)'''
        main_frame.grid_columnconfigure(0, weight=1)  # 让canvas列宽可变
        main_frame.grid_rowconfigure(0, weight=1)  # 让canvas行高可变
        self.frame = tk.Frame(self.canvas)
        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        #canvas.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # 计算最长的键长度
        self.max_key_length = max(len(key) for key in self.values.keys())

        # 创建控件，固定每个Entry的宽度为最长键的长度

        # 创建控件
        self.create_widgets(self.values, self.frame)


    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*event.delta/120), "units")

    def load_yaml(self):
        with open(self.yaml_file, 'r', encoding="utf-8") as file:
            yml = self.yaml.load(file)
            self.comments=self.recursively_parse_comments(yml)

            return yml

    def recursively_parse_comments(self,mapping, comments={}, parent_key=""):
        # 遍历yaml结构的每个键
        for key, value in mapping.items():
            self.values[key] = value
            current_key = f"{parent_key}.{key}" if parent_key else key
            comment_info = mapping.ca.items.get(key)
            if comment_info:
                comments[current_key] = comment_info[2]
            else:
                comments[current_key]=CommentToken('', 0,0)
            # 如果键的值是一个嵌套结构，则递归地对这个值进行处理
            if isinstance(value, dict):
                self.recursively_parse_comments(value, comments, current_key)
        return comments

    def create_widgets(self, dictionary,parent,pk=""):
        #print(dictionary)
        #print(self.comments)
        #print("========")
        for key, value in dictionary.items():
            #print("读取" + str(key) + " " + str(value))
            #print("===================")
            if isinstance(value, dict):
                if key in self.created:
                    continue
                #print("传递" + str(key) + " " + str(value))
                frame = ttk.Labelframe(parent, text=key)
                if key=="default" or key=="自定义":
                    self.created.append(key)
                frame.pack(side='top', fill='x', padx=5, pady=5, expand=True)
                if pk!="":
                    k=pk+"."+key
                else:
                    k=key
                self.create_widgets(value, frame,k)
            else:
                #input("输入以继续")
                frame = ttk.Frame(parent)
                frame.pack(side='top', fill='x', padx=5, pady=5)
                if key in self.datas or pk+"."+key in self.comments:
                    ttk.Label(frame, text=key, width=self.max_key_length).pack(side='left')
                var = tk.StringVar()
                var.set(value)
                self.vars[key] = var
                var.trace_add("write",
                              lambda name, index, mode, var=var, key=key, frame=parent: self.update_value(self.datas,var, key,
                                                                                                          frame))
                if key in self.datas.keys() or pk+"."+key in self.comments:
                    if isinstance(value, list):  # 如果值是列表
                        key2=key
                        for idx, item in enumerate(value):
                            # 创建一个字符串变量来存储列表项
                            item_var = tk.StringVar()
                            # 设置初始值为列表中的值
                            item_var.set(item)
                            # 添加输入框，并将输入框与变量关联起来
                            ttk.Entry(frame, textvariable=item_var, width=self.max_key_length).pack(side='left',
                                                                                                    fill='x')
                            # 如果列表项的值更改，则更新字典中相应的值
                            item_var.trace_add("write", lambda name, index, mode, var=item_var, key=key, idx=idx, cur_key=key: self.update_list_value(var, cur_key, idx))

                        # 创建一个按钮，用于添加新的列表项
                        add_button = ttk.Button(frame, text="添加", command=lambda k=key2: self.add_list_value(k))
                        add_button.pack(side='left')
                    #print(pk+"."+key)
                    elif isinstance(value, bool):  # 如果值是布尔值，添加一个复选框
                        var = tk.BooleanVar()  # 创建一个BooleanVar
                        var.set(value)  # 设置其初始状态与YAML文件中的值相同
                        chk = tk.Checkbutton(frame, variable=var, onvalue=True, offvalue=False)
                        chk.pack(side='left', fill='x')
                        var.trace_add("write",
                                      lambda name, index, mode, var=var, key=key, frame=parent: self.update_value(self.datas,var,
                                                                                                                  key,
                                                                                                                  frame))
                    else:  # 否则，添加一个输入框
                        ttk.Entry(frame, textvariable=var, width=self.max_key_length).pack(side='left', fill='x')
                    #ttk.Entry(frame, textvariable=var,width=self.max_key_length).pack(side='left', fill='x')
                #ttk.Entry(frame, textvariable=var, width=20).pack(side='left', fill='x', expand=True)
                #ttk.Label(frame, text=" " + self.comments.get(full_key, "没有找到注释")).pack(side='right')

                #print(key,self.comments.get(key).value)
                #print(self.childrenkeys)
                if pk!="":
                    #print("pk= "+pk)
                    if pk+"."+key in self.comments:
                        #print("pk列有注释"+pk+"."+key)

                        ttk.Label(frame, text=" " + self.comments.get(pk+"."+key).value).pack(side='left')
                    else:
                        if key in self.datas.keys() or pk + "." + key in self.comments:

                            ttk.Label(frame, text=" 没有对应注释").pack(side='left')
                        else:
                            pass
                        #ttk.Label(frame, text=" 没有对应注释").pack(side='left')
                        #print("pk列无注释" + pk + "." + key)
                else:
                    if key in self.comments:
                        #print("1:"+key)
                        ttk.Label(frame, text=" " + self.comments.get(key).value).pack(side='left')
                    else:
                        if key in self.datas.keys() or pk + "." + key in self.comments:

                            ttk.Label(frame, text=" 没有对应注释").pack(side='left')
                        else:
                            pass
                        #print("2:" + key)

    def add_list_value(self, target_key):
        #print(target_key)
        for key, value in self.datas.items():
            if key == target_key and isinstance(value, list):  # 找到了目标键，且它是一个列表
                # 向列表中添加一个新的项，值为"xxx"
                value.append("xxx")
                self.datas[key]=value
                #print(self.datas)

        # 保存更改到 yaml 文件
        self.save_yaml()
        for widget in self.frame.winfo_children():
            widget.destroy()
        # 重新创建列表项的输入框
        self.create_widgets(self.values, self.frame)
        self.frame.update()
    def update_list_value(self, new_value, target_key, target_index):
        for key, value in self.datas.items():
            if key == target_key and isinstance(value, list):  # 找到了目标键，且它是一个列表
                new_val = new_value.get()  # 获取新值
                if new_val:  # 如果新值不为空
                    # 就更新列表中对应索引的值
                    value[target_index] = new_val
                else:  # 如果新值为空
                    # 删除该元素
                    del value[target_index]

        # 保存更改到 yaml 文件
        self.save_yaml()
        for widget in self.frame.winfo_children():
            widget.destroy()
        # 重新创建列表项的输入框
        self.create_widgets(self.values, self.frame)
        self.frame.update()
    def update_value(self,dc,new_value,target_key,frame):
        dictionary=dc
        #print(new_value.get())

        for key in dictionary.keys():
            if isinstance(dictionary[key], dict):  # 如果值是一个字典，就需要递归处理
                self.update_value(dictionary[key], new_value,target_key,frame)
            elif key == target_key:  # 找到了目标键，就更新它的值
                var=new_value
                if type(var.get()) == bool:
                    var1 = var.get()
                else:
                    try:
                        var1 = int(var.get())
                    except:
                        var1 = var.get()
                dictionary[key] = var1

        self.datas = dictionary
        # Save the changes to yaml file
        self.save_yaml()

    def find_keys_recursively(self, frame):
        widget = frame.master
        keys = []
        while True:
            if isinstance(widget, ttk.Labelframe):
                keys.append(widget["text"])
                widget = widget.master
            else:
                break
        keys.reverse()
        return keys
    def save_yaml(self):
        #print(self.datas)
        with open(self.yaml_file, "w", encoding="utf-8") as file:
            self.yaml.dump(self.datas, file)

    '''def update_value(self, var, key):
        self.datas[key] = var.get()
        self.save_yaml()'''

class StatusBar(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()
        self.START_TIME=time.time()
    def create_widgets(self):
        self.uptime_text = tk.StringVar()
        self.memory_text = tk.StringVar()
        self.uptime_label = ttk.Label(self, textvariable=self.uptime_text)
        self.uptime_label.pack(side="left")
        self.memory_label = ttk.Label(self, textvariable=self.memory_text)
        self.memory_label.pack(side="left")

    def update_status(self):
        uptime = time.time() - self.START_TIME
        m, s = divmod(uptime, 60)
        h, m = divmod(m, 60)
        readable_uptime = "%02d:%02d:%02d" % (h, m, s)
        self.uptime_text.set("已运行时间: " + readable_uptime)
        #self.memory_text.set("    Memory usage: " + str(psutil.virtual_memory().percent))
        self.after(1000, self.update_status)  # 更新状态每秒


logger=newLogger()
logger.info("starting")
logger.info("欢迎使用，项目地址和文档：https://github.com/avilliai/Manyana")
styl = ttkbootstrap.Style(theme='morph')
# 使用style创建主窗口
root = styl.master
root.title("launcher")

# 创建你的应用程序...
app = Application(master=root)  # 确保你的Application类能够接收master作为参数
app.mainloop()
