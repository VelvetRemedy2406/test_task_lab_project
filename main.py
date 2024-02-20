import time
import tkinter as tk
import threading
import pexpect
import re


def InteractivBaresip(number):
    p = pexpect.spawn('baresip')
    p.expect('ready.')
    p.sendline('/help')

    p.expect('/vidsrc')

    commands = list(p.before.decode('utf-8').split('\r\n'))[2:]

    for cmd in commands:
        res = re.search(r'[Ss]ystem.[Ii]nfo', cmd)
        if res:
            break
    time.sleep(2)
    p.sendline(cmd.split()[0])
    for i in range(4):
        p.expect('\r\n')

    p.sendline('/quit')

    p.expect(pexpect.EOF)

    ans = p.before.decode('utf-8')
    ans = ans[:ans.find('/qu') - 5].replace('\r', '')
    if RunBaresipCallback.stop_event[number].is_set():
        bare_sip_text[number].delete(1.0, tk.END)
        bare_sip_text[number].insert(1.0, ans)


def SetActiveCallback():
    ac.set("App is active")


def RunBaresipCallback(number):
    if not hasattr(RunBaresipCallback, 'stop_event'):
        RunBaresipCallback.stop_event = [threading.Event(), threading.Event()]
    if RunBaresipCallback.stop_event[number].is_set():
        RunBaresipCallback.stop_event[number].clear()
        bare_sip_button[number].config(text='Run baresip')
    else:
        bare_sip_button[number].config(text='Stop baresip')
        RunBaresipCallback.stop_event[number].set()
        backend = threading.Thread(target=lambda: InteractivBaresip(number), name="daemon-thread", daemon=True)
        backend.start()


def createCommand(SomeFunction, i):
    return lambda: SomeFunction(i)


root = tk.Tk()
root.title("Test task")
root.geometry("400x800")
ac = tk.StringVar()
is_active_entry = tk.Entry(root, textvariable=ac)
is_active_entry.grid(column=1, row=3)
is_active_button = tk.Button(text='Check', command=SetActiveCallback)
is_active_button.grid(column=3, row=3)

bare_sip_text = []
bare_sip_button = []
for i in range(2):
    bare_sip_text.append(tk.Text(root, width=35, height=20))
    bare_sip_text[i].grid(column=1, row=i + 1)
    bare_sip_button.append(tk.Button(text='Run baresip', command=createCommand(RunBaresipCallback, i)))
    bare_sip_button[i].grid(column=3, row=i + 1)

root.mainloop()
