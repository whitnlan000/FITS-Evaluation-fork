from xxsubtype import bench

from Astro import *
from readheader import *

#File Picker:
import tkinter as tk
from tkinter import filedialog, ttk

single_path = None
before_bin_stack_path = None
single_noise = None
single_frame_noise = None

def file_picker():
    root = tk.Tk()
    root.withdraw()

    path = filedialog.askopenfilename(
        title = "Select file",
        filetypes = (("Fit Files", "*.fit *.fits"), ("All Files", "*.*")),
    )
    return path

def select_file_before():
    global select_var_1
    global before_bin_stack_path
    file_path = file_picker()

    print("Selected file: ", file_path)

    before_bin_stack_path = file_path
    if file_path:
        select_var_1.set("Select Stack\nLoaded at "+file_path)


def select_file_after():
    global select_var_2
    global single_path
    file_path = file_picker()
    # after_bin_stack_path = 'images/NGC7000_120s_200Gain_Stacked_AfterBinning.fit'
    single_path = file_path

    if file_path:
        select_var_2.set("Select Single\nLoaded at "+file_path)

def run():
    global before_bin_stack_path
    global single_path
    global single_frame_noise
    global single_noise
    global out_var

    single_out = analyze_fits(single_path)
    single_noise = single_out[0]

    before_bin_results = analyze_fits(file_path=before_bin_stack_path, is_stack=True, single_frame_noise=single_noise)

    out_var.set("\nStack\n"+("\n".join(before_bin_results[1]))+"\n\nSingle\n"+("\n".join(single_out[1])))
    # print(before_bin_results)


    #analyze_stack(before_bin_stack_path)


#Create Window
main_root = tk.Tk()
style = ttk.Style()

#Add Run Button
run_button = ttk.Button(main_root, text="Run", command=run, style='Clam.TButton')

#Pack Run Button
run_button.pack(pady=1)

#Add Select Buttons
select_var_1 = tk.StringVar()
select_var_1.set("Select Stack")

select_var_2 = tk.StringVar()
select_var_2.set("Select Single")

select_1_button = ttk.Button(main_root, text="Select Stack", command=select_file_before, style='Clam.TButton', textvariable=select_var_1)
select_2_button = ttk.Button(main_root, text="Select Single", command=select_file_after, style='Clam.TButton', textvariable=select_var_2)

#Pack Select Buttons
select_2_button.pack(pady=1)
select_1_button.pack(pady=1)

#Add Output
out_var = tk.StringVar()
out_label = tk.Label(main_root, textvariable=out_var)

#Pack Output
out_label.pack(pady=1)

#Mainloop
print(style.theme_names())

style.theme_use("classic")
main_root.mainloop()
