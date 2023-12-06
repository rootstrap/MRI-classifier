import os
import sys
import subprocess
import shutil
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count

count = 0

def plot_middle(data, slice_no=None):
    if not slice_no:
        slice_no = data.shape[-1] // 2
    plt.figure()
    plt.imshow(data[..., slice_no], cmap="gray")
    plt.show()
    return

def registration(src_path, dst_path, ref_path):
    command = ["flirt", "-in", src_path, "-ref", ref_path, "-out", dst_path,
               "-bins", "256", "-cost", "corratio", "-searchrx", "-90", "90",
               "-searchry", "-90", "90", "-searchrz", "-90", "90", "-dof", "12",
               "-interp", "spline"]
    subprocess.call(command, stdout=open(os.devnull, "r"),
                    stderr=subprocess.STDOUT)
    return

def orient2std(src_path, dst_path):
    command = ["fslreorient2std", src_path, dst_path]
    subprocess.call(command)

    return

def create_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    return

def unwarp_main(arg, **kwarg):
    return main(*arg, **kwarg)

def main(src_path, dst_path, ref_path):
    print("Registration on: ", src_path)
    try:
        orient2std(src_path, dst_path)
        registration(dst_path, dst_path, ref_path)
    except RuntimeError:
        print("\tFalied on: ", src_path)
    return 

current_directory = os.getcwd()
parent_directory = os.path.dirname(current_directory)
data_dir = os.path.join(parent_directory, 'data')

data_src_dir = os.path.join(data_dir, 'ADNI')
data_dst_dir = os.path.join(data_dir, 'ADNIReg')
data_labels = ['AD', 'CN', 'MCI']

if not os.path.exists(data_dst_dir):
    create_dir(data_dst_dir)
else:
    shutil.rmtree(data_dst_dir)
    create_dir(data_dst_dir)

ref_path = os.path.join(parent_directory, 'altas', "name of MNI152 file")

data_src_paths, data_dst_paths = [], []
for label in data_labels:
    src_label_dir = os.path.join(data_src_dir, label)
    dst_label_dir = os.path.join(data_dst_dir, label)
    if not os.path.exists(dst_label_dir):
        create_dir(dst_label_dir)
    else:
        if len(os.listdir(dst_label_dir))>0:
            cont = input("DESTINTATION FOLDER IS NOT EMPTY!!!!! CHECK IF YOUR ARE RUNNING THE CORRECT FILE. Do you want to continue (Y/N)?").upper()
            while cont != "Y" and cont != "N":
                cont = input("Invalid input. Please enter Y for yes and N for no. Do you want to continue (Y/N)?").upper()
            if cont == "N":
                exit(1)
            else:
                shutil.rmtree(dst_label_dir)
                create_dir(dst_label_dir)
        else:    
            shutil.rmtree(dst_label_dir)
            create_dir(dst_label_dir)
    for subject in os.listdir(src_label_dir):
        data_src_paths.append(os.path.join(src_label_dir, subject))
        data_dst_paths.append(os.path.join(dst_label_dir, subject))

# Test
#main(data_src_paths[0], data_dst_paths[0], ref_path)

if __name__ =='__main__':
    # Multi-processing
    paras = zip(data_src_paths, data_dst_paths,
                [ref_path] * len(data_src_paths))
    pool = Pool(processes=cpu_count())
    pool.map(unwarp_main, paras)

    pool.close()
    pool.join()