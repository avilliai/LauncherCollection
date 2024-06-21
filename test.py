# -*- coding: utf-8 -*-
import logging
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import tkinter as tk
import threading

import colorlog
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
class TkinterTextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        # 移除ANSI转义序列
        msg = re.sub(r'\x1b\[[0-9;]*m', '', msg)
        self.text_widget.after(0, self.update_text_widget, msg, record.levelno)

    def update_text_widget(self, msg, levelno):
        # 根据日志级别设置颜色
        log_color = {
            logging.DEBUG: 'grey',
            logging.INFO: 'black',
            logging.WARNING: 'orange',
            logging.ERROR: 'red',
            logging.CRITICAL: 'purple',
        }.get(levelno, 'black')
        self.text_widget.configure(state='normal')
        self.text_widget.tag_config(str(levelno), foreground=log_color)
        self.text_widget.insert(tk.END, msg + '\n', str(levelno))
        self.text_widget.configure(state='disabled')
        self.text_widget.see(tk.END)  # 自动滚动到文本末尾

def newLogger(text_widget):
    # 创建一个logger对象
    logger = logging.getLogger("villia")
    logger.setLevel(logging.DEBUG)  # 设置日志级别为DEBUG
    logger.propagate = False

    # 创建一个格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                                            log_colors={
                                                                'DEBUG': 'white',
                                                                'INFO': 'cyan',
                                                                'WARNING': 'yellow',
                                                                'ERROR': 'red',
                                                                'CRITICAL': 'bold_red',
                                                            }))
    logger.addHandler(console_handler)

    # Tkinter文本组件日志处理器
    text_handler = TkinterTextHandler(text_widget)
    text_handler.setFormatter(formatter)
    logger.addHandler(text_handler)

    return logger



class CommandFrame(ttk.Frame):
    def __init__(self, master=None, cmd=None, cwd=None):
        super().__init__(master)
        self.cmd = cmd
        self.cwd = cwd
        self.process = None
        self.keep_alive = True
        self.cmd_output = tk.Text(self)
        self.cmd_output.pack(side="bottom", fill=tk.BOTH, expand=True)
        # 在这里传入文本组件创建logger
        self.logger = newLogger(self.cmd_output)
    def create_miraipage(self):
        self.run_btn = ttk.Button(self,bootstyle="info")
        self.run_btn["text"] = "启动Mirai"
        self.run_btn["command"] = self.start_cmd_thread
        self.run_btn.pack(side="bottom")
        self.cmd_output = tk.Text(self)
        self.cmd_output.pack(side="bottom")
    def create_manyanapage(self):
        self.run_btn = ttk.Button(self,bootstyle="info")
        self.run_btn["text"] = "启动Manyana"
        self.run_btn["command"] = self.start_cmd_thread
        self.run_btn.pack(side="top")
        self.cmd_output = tk.Text(self)
        self.cmd_output.pack(side="top")
    def create_overgflowPage(self):
        self.run_btn = ttk.Button(self, bootstyle="info")
        self.run_btn["text"] = "启动overflow"
        self.run_btn["command"] = self.start_cmd_thread
        self.run_btn.pack(side="top")
        self.cmd_output = tk.Text(self)
        self.cmd_output.pack(side="top")
    def start_cmd_thread(self):
        cmd_thread = threading.Thread(target=self.run_cmd, daemon=True)
        cmd_thread.start()
        return cmd_thread

    def run_cmd(self):
        # 创建一个日志记录器实例
        logger = logging.getLogger("villia")
        while self.keep_alive:
            # 开启子进程，捕获其标准输出和标准错误
            self.process = subprocess.Popen(self.cmd, shell=True, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            # 循环读取输出
            while True:
                output = self.process.stdout.readline()
                if output == '' and self.process.poll() is not None:
                    break
                if output:
                    logger.info(output.strip())  # 将输出发送到日志记录器
            self.process.communicate()

            if not self.keep_alive:
                # 如果keep_alive被设置为False，不再重启进程，退出方法
                break

            self.killself()

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
        self.clone_btn["text"] = "搭建"
        self.clone_btn["command"] = self.git_clone
        self.clone_btn.pack(side="top", pady=10) # 添加间隔

        self.pull_btn = ttk.Button(self)
        self.pull_btn["text"] = "更新"
        self.pull_btn["command"] = self.git_pull
        self.pull_btn.pack(side="top", pady=10) # 添加间隔

        self.setup_btn = ttk.Button(self)
        self.setup_btn["text"] = "不知道"
        self.setup_btn["command"] = self.python_setup
        self.setup_btn.pack(side="top", pady=10) # 添加间隔

        self.echo_btn = ttk.Button(self)
        self.echo_btn["text"] = "不知道"
        self.echo_btn["command"] = self.echo_hello
        self.echo_btn.pack(side="top", pady=10) # 添加间隔

    def git_clone(self):
        logger.info("首先需要的是配置环境，按任意键开始部署环境，按1跳过,跳过后将开始获取bot代码")
        if input("在这里输入：") != "1":
            evvir()
        else:
            logger.info("你似乎并不想部署环境，这可能影响bot的正常运作。如果你知道自己在做什么，那就让我们继续吧")
        logger.info("好的，下面让我们获取bot的代码，按任意键开始，按1跳过")
        if input("在这里输入") != "1":
            botCodeGet()
        else:
            logger.warning("你跳过了bot代码拉取，接下来我们将为你启动mirai")

    def git_pull(self):
        logger.info("接下来将为您更新bot代码，如出现运行问题请使用Manyana/更新脚本.bat 进行更新。")
        p311 = subprocess.Popen(["更新脚本.bat"], shell=True, cwd="Manyana")
        p311.communicate()

        time.sleep(1)

    def python_setup(self):
        subprocess.Popen("python setUp.py", shell=True)

    def echo_hello(self):
        subprocess.Popen("echo hello", shell=True)
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
            self.frame2.cmd_output.config(width=self.master.winfo_width(), height=self.master.winfo_height())
        except:
            pass
        try:
            self.frame21.cmd_output.config(width=self.master.winfo_width(), height=self.master.winfo_height())
        except:
            pass
    def create_widgets(self):
        notebook = ttk.Notebook(self,style="info")
        if os.path.exists("Manyana/config.json"):
            self.frame41 = YamlPage(notebook, yaml_file='Manyana/config.json')
            notebook.add(self.frame41, text='基本设置')
        self.frame1 = CommandFrame(notebook, cmd='java -jar mcl.jar', cwd="./miraiBot")
        self.frame1.create_miraipage()
        notebook.add(self.frame1, text='mirai')
        self.frame2 = CommandFrame(notebook, cmd='启动脚本.bat', cwd="./Manyana")
        self.frame2.create_manyanapage()

        if os.path.isdir("./overflow"):
            self.frame21 = CommandFrame(notebook, cmd='start.bat', cwd="./overflow")
            self.frame21.create_overgflowPage()
            notebook.add(self.frame21, text='overflow')

        notebook.add(self.frame2, text='Manyana')
        self.frame3 = GitFrame(notebook)
        notebook.add(self.frame3, text='工具页')
        # 在Application类的create_widgets方法中添加新页面
        if os.path.exists("Manyana/config/api.yaml"):
            self.frame4 = YamlPage(notebook, yaml_file='Manyana/config/api.yaml')
            notebook.add(self.frame4, text='外部api设置')
        if os.path.exists("Manyana/config/settings.yaml"):
            self.frame5 = YamlPage(notebook, yaml_file='Manyana/config/settings.yaml')
            notebook.add(self.frame5, text='bot设置')
        notebook.pack(expand=1, fill='both')
        #底部小组件
        self.status_bar = StatusBar(self.master)
        self.status_bar.pack(side='bottom', fill='x')
        self.status_bar.update_status()
    def on_closing(self):
        print("closing")
        self.frame1.keep_alive = False
        self.frame2.keep_alive = False
        self.frame21.keep_alive = False
        self.frame1.killself()
        self.frame2.killself()
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
        canvas = tk.Canvas(main_frame)
        self.canvas = canvas
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
        self.frame = tk.Frame(canvas)
        self.frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.frame, anchor="nw")
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
def evvir():
    messagebox.showinfo("Message", "如需搭建请确保使用管理员模式运行本程序")
    messagebox.showinfo("Message", "首先我们需要安装必要的环境,正在获取必要的软件目录接下来的操作，请在小黑窗完成")
    logger.info("下面是bot运行所需要的软件，它们被放置在了environments文件夹下。你需要安装它们以保证bot的正常运作。别担心，这很简单")
    logger.info("你可能已经安装过了它们中的一些软件，那么这部分软件就可以不用安装。")
    logger.info("==========================")
    logger.info("让我们开始安装java吧，按任意键开始。如果你的java版本已经是17，输入1以跳过")
    logger.info("接下来你只需要默认选择下一步即可")
    if input("在这里输入：") != "1":
        subprocess.Popen(["environments/jdk-17_windows-x64_bin.exe"])
    else:
        pass
    logger.info("==========================")
    logger.info("下一步让我们安装python，按任意键开始。如果你的python版本已经是3.9，输入1以跳过")
    logger.warning("请注意，在打开python安装程序后，一定要勾选add to path。其余全部默认即可。")
    if input("在这里输入：") != "1":
        subprocess.Popen(["environments/python-3.9.0-amd64.exe"])
    else:
        pass
    logger.info("==========================")
    logger.info("下一步让我们安装git，按任意键开始,输入1以跳过")
    logger.info("通过git，你可以获取到最新的Manyana")
    logger.info("接下来你只需要默认选择下一步即可")
    if input("在这里输入：") != "1":
        subprocess.Popen(["environments/Git-2.39.0.2-64-bit.exe"])
    else:
        pass
    logger.info("很好，我们即将完成环境的配置了")
    logger.info("==========================")
    logger.info("下一步让我们安装vc_redist，按任意键开始,输入1以跳过")
    logger.info("为bot运行提供更加底层的代码支持")
    if input("在这里输入：") != "1":
        subprocess.Popen(["environments/vc_redist.x64.exe"])
    else:
        pass
    logger.info("恭喜你完成了基本的环境安装。请将environments文件夹下的mirai-login-solver-sakura-0.0.10.apk安装到你的手机")
def botCodeGet():
    logger.info("如果你有代理，请在下方输入它运行的端口，没有就回车，这不是必须的设置。clash一般输入7890，ssr一般输入1080，v2ray一般是10809，如果没有或者不知道这是什么东西，请按下回车以跳过")
    proxy1 = input("你的代理运行端口(没有就直接回车)：")
    if proxy1 != "1" and proxy1!="":
        os.system("git config --global http.proxy http://127.0.0.1:" + proxy1)
        os.system("git config --global https.proxy https://127.0.0.1:" + proxy1)
    else:
        if proxy1=="":
            os.system("git config --global --unset http.proxy")
            os.system("git config --global --unset https.proxy")
    logger.info("让我们拉取代码吧，按1跳过")
    sp=input("在这里输入:")
    if sp!="1":
        logger.info("选择clone源()：\n1 git源\n2 镜像源(建议使用这个)")
        sfsff=input("选择clone源(输入数字)：")
        os.system("git config --global core.compression 0")
        if sfsff=="1":
            result = os.popen("git clone --depth 1 https://github.com/avilliai/Manyana.git")
        else:
            result = os.popen("git clone --depth 1 https://gh-proxy.com/https://github.com/avilliai/Manyana")

        print(result.read())
        if "fatal" in result or "error" in result:
            # 命令出错
            logger.error("命令执行失败，请稍后重试")
        else:
            # 命令成功
            logger.info("命令执行成功")
            if os.path.exists("vits/voiceModel/nene/1374_epochsm.pth"):
                pass
            else:
                try:
                    shutil.move("1374_epochsm.pth","Manyana/vits/voiceModel/nene/1374_epochsm.pth", copy_function=shutil.copy2)
                except:
                    logger.error("请检查Manyana/vits/voiceModel/nene文件夹或根目录中是否存在.pth文件(必要)，如.pth文件丢失请重新解压")

    if os.path.exists("./Manyana/main.py"):
        logger.info("接下来是最重要的一步，请确保你已经拉取到了bot代码，安装bot所需python环境。如果你遇到问题，请在我们的用户群628763673反馈。")
        logger.info("输入1跳过：")
        gfgdf=input("在这里输入：")
        if gfgdf!="1":
            logger.info("接下来安装依赖，如果出现问题，请使用Manyana/一键部署脚本.bat 手动部署")
            p31 = subprocess.Popen(["一键部署脚本.bat"], shell=True, cwd="Manyana")
            p31.communicate()
        else:
            logger.info("卡住了？没关系，关掉，重新启动launcher，填写【基本设置】后启动Mirai或overflow，接着启动Manyana就能用了")

    else:
        logger.error("你似乎没有成功获取到代码，要再试一次吗")
        sfsdf=input("按任意键继续，输入1跳过：")
        if sfsdf!="1":
            botCodeGet()
        else:
            pass
def newLogger1():
    # 创建一个logger对象
    logger = logging.getLogger("simple logger")
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
logger=newLogger1()
logger.info("starting")
logger.info("欢迎使用，项目地址和文档：https://github.com/avilliai/Manyana")
root = tk.Tk()
root.title("ManyanaLauncherUI")
app = Application(master=root)
app.mainloop()
