#!/usr/bin/env python3
from datetime import datetime
from tkinter import Tk, Label, Button, Listbox, Scrollbar, END, \
    HORIZONTAL, VERTICAL, BROWSE, DISABLED, NORMAL

fake_tasks = [
    '#17349 Бэкапы проекта', '#12431 Проверка задач + консультации по проекту',
    '#8195 SEO-оптимизация для публичной части сайта',
    '#17492 Верстка. Страница 403 в стиле сети',
    '#17441 Ошибки на проде 500',
    '#17413 Рефакторинг стиля кода (к стандарту PEP8)',
    '#17216 Созвон и обсуждение',
    '#16535 Уведомление о новом уведомлении',
    '#16373 ДОКУМЕНТАЦИЯ',
    '#14999 Проверить фикстуры юзеров'
]


SHARED_STATE = {
    'start_time': None,
    'tick_id': None,
}


def workon_mode():
    tasks_lst['state'] = DISABLED
    start_btn['state'] = DISABLED
    stop_btn['state'] = NORMAL
    reset_btn['state'] = DISABLED
    options_btn['state'] = DISABLED
    offline_btn['state'] = DISABLED


def idle_mode():
    tasks_lst['state'] = NORMAL
    start_btn['state'] = NORMAL
    stop_btn['state'] = DISABLED
    reset_btn['state'] = NORMAL
    options_btn['state'] = NORMAL
    offline_btn['state'] = NORMAL


def reset_time_tracking():
    spent_time_lbl['text'] = '0:00:00'


def start_time_tracking():
    SHARED_STATE['start_time'] = datetime.utcnow()
    tick()
    workon_mode()


def stop_time_tracking():
    spent_time_lbl.after_cancel(SHARED_STATE['tick_id'])
    idle_mode()


def tick():
    delta_time = datetime.utcnow() - SHARED_STATE['start_time']
    SHARED_STATE['tick_id'] = spent_time_lbl.after(200, tick)
    spent_time_lbl['text'] = str(delta_time).rpartition('.')[0]


def change_task(event):
    tasks_lst.curselection()
    start_btn['state'] = NORMAL


root = Tk()
root.title('wkTime')
root.geometry('210x210-40+80')
root.resizable(False, False)

spent_time_lbl = Label(font='sans 20', text='0:00:00')
spent_time_lbl.grid(
    row=0, column=0, columnspan=3, padx=8, pady=2, ipadx=8, sticky='n')
# spent_time_lbl.after_idle(tick)

start_btn = Button(
    root, command=start_time_tracking, state=DISABLED,
    text='start', width=1, height=1, fg='green', activeforeground='green',
    font='arial 10')
start_btn.grid(row=1, column=0, padx=8, pady=2, ipadx=12, sticky='n')

stop_btn = Button(
    root, command=stop_time_tracking, state=DISABLED,
    text='stop', width=1, height=1, fg='red', activeforeground='red',
    font='arial 10')
stop_btn.grid(row=1, column=1, padx=0, pady=2, ipadx=12, sticky='n')

reset_btn = Button(
    root, command=reset_time_tracking, state=DISABLED,
    text='reset', width=1, height=1, fg='red', activeforeground='red',
    font='arial 10')
reset_btn.grid(row=1, column=2, padx=8, pady=2, ipadx=12, sticky='n')

tasks_lst_x_scrollbar = Scrollbar(root, orient=HORIZONTAL)
tasks_lst_y_scrollbar = Scrollbar(root, orient=VERTICAL)
tasks_lst = Listbox(
    root, height=5, selectmode=BROWSE, exportselection=False,
    xscrollcommand=tasks_lst_x_scrollbar.set,
    yscrollcommand=tasks_lst_y_scrollbar.set)

for task in sorted(fake_tasks):
    tasks_lst.insert(END, task)

tasks_lst.grid(
    row=2, column=0, columnspan=3, padx=0, pady=0, ipadx=14, sticky='n')

tasks_lst_x_scrollbar.config(command=tasks_lst.xview)
tasks_lst_y_scrollbar.config(command=tasks_lst.yview)

tasks_lst_x_scrollbar.grid(
    row=3, column=0, columnspan=3, padx=8, pady=0, ipadx=79, sticky='s')
# tasks_lst_y_scrollbar.grid(
#     row=2, column=3, padx=0, ipady=24, sticky='s')

tasks_lst.bind('<ButtonRelease-1>', change_task)
tasks_lst.select_anchor(1)
options_btn = Button(
    root, text='options', width=1, height=1, fg='black', font='arial 10')
options_btn.grid(row=4, column=0, padx=8, pady=2, ipadx=12, sticky='n')

offline_btn = Button(
    root, text='offline mode', width=1, height=1, fg='black', font='arial 10')
offline_btn.grid(
    row=4, column=1, columnspan=2, padx=0, pady=2, ipadx=42, sticky='n')

root.mainloop()
