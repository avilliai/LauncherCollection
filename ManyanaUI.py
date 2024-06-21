import os
import signal
import subprocess
from tkinter import ttk
import tkinter as tk
import threading
from PIL import Image,ImageTk
from tkinter import Tk, Canvas, ttk
class CommandFrame(ttk.Frame):
    def __init__(self, master=None, cmd=None, cwd=None):
        super().__init__(master)
        self.cmd = cmd
        self.cwd = cwd
        self.process = None
        self.create_widgets()
    def create_widgets(self):
        self.run_btn = ttk.Button(self)
        self.run_btn["text"] = "Run Command"
        self.run_btn["command"] = self.start_cmd_thread
        self.run_btn.pack(side="top")
        self.cmd_output = tk.Text(self)
        self.cmd_output.pack(side="top")
    def start_cmd_thread(self):
        cmd_thread = threading.Thread(target=self.run_cmd, daemon=True)
        cmd_thread.start()
        return cmd_thread

    def run_cmd(self):
        keep_alive = True
        while keep_alive:
            self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                            cwd=self.cwd)
            for line in self.process.stdout:
                try:
                    self.cmd_output.insert(tk.END, line.decode('utf-8'))
                except:
                    continue
            # 子进程已经结束，调用 killself 确保子进程已经完全退出
            self.killself()
            # 检查子进程的退出状态
            keep_alive = self.process.returncode != 0
    def killself(self):
        print(self.process)
        try:
            self.process.terminate()
            os.kill(self.process.pid, signal.CTRL_C_EVENT)
        except:
            try:
                os.kill(self.process.pid, signal.CTRL_C_EVENT)
            except:
                pass
class Application(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master


        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.pack()
        self.create_widgets()


    def create_widgets(self):
        # 加载图片
        style = ttk.Style(self.master)
        style.configure('TNotebook', background='#FFFFFF80')  # 半透明背景
        style.configure('TFrame', background='#FFFFFF80')  # 半透明背景

        notebook = ttk.Notebook(self)
        self.frame1 = CommandFrame(notebook, cmd='启动脚本.cmd', cwd="./miraiBot")
        notebook.add(self.frame1, text='mirai')
        cmd2_dir = './Manyana'  # 你需要运行第二个命令的目录
        self.frame2 = CommandFrame(notebook, cmd='启动脚本.cmd', cwd=cmd2_dir)
        notebook.add(self.frame2, text='Manyana')
        notebook.pack(expand=1, fill='both')
    def on_closing(self):
        print("closing")
        self.frame1.killself()
        self.frame2.killself()
        root.destroy()
root = tk.Tk()
app = Application(master=root)
app.mainloop()