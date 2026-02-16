from tkinter import *
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import zipfile
import sys
from PIL import Image
from pathlib import Path
import send2trash

#主窗口
root = TkinterDnD.Tk()
root.title("漫画压缩器")
root.geometry("1280x720")
root.resizable(False,False)

#全局参数
bPNG = BooleanVar()
sZOOM = StringVar()
sZOOM.set("A")
bZOOM_01 = BooleanVar()
bZOOM_02 = BooleanVar()
bZOOM_03 = BooleanVar()
sZOOM_11 = StringVar(value="33177600")
sZOOM_12 = StringVar(value="0.25")
sZOOM_21 = StringVar(value="12441600")
sZOOM_22 = StringVar(value="0.3")
sZOOM_31 = StringVar(value="8294400")
sZOOM_32 = StringVar(value="0.5")
sDrop = StringVar(value="拖放文件到此处")
sPath = ""
sTemp = ""
sTempAfter = ""
sTempZIP = ""

#删除临时文件
def move_to_trash(file_path):
    """
    将文件移动到回收站（确保使用send2trash）
    """
    try:
        send2trash.send2trash(str(file_path))
        return True
    except Exception as e:
        print(f"移动到回收站失败: {e}")
        return False
        
        
def cleanup_folder_if_tmp_exists(folder_path, tmp_filename="BDZJZ.tmp"):
    """
    检查文件夹中是否存在指定临时文件，如果存在则删除文件夹中所有内容到回收站
    
    Args:
        folder_path (str): 要检查的文件夹路径
        tmp_filename (str): 要检查的临时文件名
    
    Returns:
        bool: 操作是否成功
    """
    folder = Path(folder_path)
    
    # 检查文件夹是否存在
    if not folder.exists():
        print(f"错误: 文件夹 '{folder_path}' 不存在")
        return False
    
    if not folder.is_dir():
        print(f"错误: '{folder_path}' 不是一个文件夹")
        return False
    
    # 检查临时文件是否存在
    tmp_file = folder / tmp_filename
    if not tmp_file.exists():
        print(f"文件 '{tmp_filename}' 不存在，不执行任何操作")
        return True
    
    print(f"检测到文件 '{tmp_filename}'，开始清理文件夹...")
    
    # 删除文件夹中的所有内容
    success_count = 0
    fail_count = 0
    
    try:
        # 遍历文件夹中的所有项目
        for item in folder.iterdir():
            # 跳过临时文件本身
            if item.name == tmp_filename:
                continue
                
            try:
                if move_to_trash(item):
                    print(f"已移至回收站: {item.name}")
                    success_count += 1
                else:
                    print(f"删除失败: {item.name}")
                    fail_count += 1
            except Exception as e:
                print(f"删除出错 {item.name}: {e}")
                fail_count += 1
        
        # 最后删除临时文件
        try:
            if move_to_trash(tmp_file):
                print(f"已移至回收站: {tmp_filename}")
                success_count += 1
            else:
                print(f"删除临时文件失败: {tmp_filename}")
                fail_count += 1
        except Exception as e:
            print(f"删除临时文件出错: {e}")
            fail_count += 1
            
    except Exception as e:
        print(f"遍历文件夹时出错: {e}")
        return False
    
    print(f"清理完成! 成功: {success_count} 个, 失败: {fail_count} 个")
    return fail_count == 0

#打包ZIP
def pack_folder_except_tmp(source_folder,output_folder, output_zip, exclude_file="BDZJZ.tmp"):
    """
    将文件夹中的所有文件打包成ZIP，排除指定文件
    
    Args:
        source_folder (str): 源文件夹路径
        output_zip (str): 输出ZIP文件路径
        exclude_file (str): 要排除的文件名
    """
    source_path = Path(source_folder)
    
   
    # 创建ZIP文件
    with zipfile.ZipFile(os.path.join(output_folder,output_zip), 'w', zipfile.ZIP_DEFLATED) as zipf:
        packed_files = []
        
        # 遍历文件夹中的所有文件
        for file_path in source_path.rglob('*'):
            if file_path.is_file():
                # 检查是否是要排除的文件
                if file_path.name != exclude_file:
                    # 计算相对于源文件夹的路径
                    arcname = file_path.relative_to(source_path)
                    zipf.write(file_path, arcname)
                    packed_files.append(str(arcname))
                    print(f"已添加: {arcname}")
                else:
                    print(f"已跳过: {file_path.name}")
    
    return packed_files


#压缩图片
def fcompress_images(input_folder, output_folder, quality=75):
    """
    压缩指定文件夹中的图片文件为指定质量的JPEG格式
    
    Args:
        input_folder (str): 输入文件夹路径
        output_folder (str): 输出文件夹路径
        quality (int): JPEG压缩质量(1-100)
    """
    # 支持的图片格式
    supported_formats = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
    
    # 统计处理结果
    processed_count = 0
    error_count = 0
    
    print(f"开始处理图片...")
    print(f"输入文件夹: {input_folder}")
    print(f"输出文件夹: {output_folder}")
    print(f"压缩质量: {quality}")
    print("-" * 50)
    
    # 遍历输入文件夹中的所有文件
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            # 获取文件扩展名并转换为小写
            file_extension = Path(file).suffix.lower()
            
            # 检查是否为支持的图片格式
            if file_extension in supported_formats:
                input_path = os.path.join(root, file)
                # 保持相对路径结构
                relative_path = os.path.relpath(input_path, input_folder)
                output_path = os.path.join(output_folder, relative_path)
                
                # 更改输出文件扩展名为.jpg
                output_path = Path(output_path).with_suffix('.jpg')
                
                # 创建输出文件的目录结构
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    # 打开并转换图片
                    with Image.open(input_path) as img:
                        # 转换为RGB模式(去除透明度)
                        if img.mode in ('RGBA', 'LA', 'P'):
                            # 创建白色背景
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # 保存为JPEG格式
                        img.save(output_path, 'JPEG', quality=quality, optimize=True)
                        print(f"✓ 已处理: {file} -> {output_path.name}")
                        processed_count += 1
                        
                        with open(os.path.join(output_folder,"BDZJZ.tmp"), 'w') as f:
                            pass  # 创建空文件    
                        
                except Exception as e:
                    print(f"✗ 处理失败: {file} - {str(e)}")
                    error_count += 1
    
    print("-" * 50)
    print(f"处理完成!")
    print(f"成功处理: {processed_count} 个文件")
    print(f"处理失败: {error_count} 个文件")


#解压ZIP临时文件夹
def fExtractZIP(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        print(f"文件已解压到: {extract_to}")
        
        
#开始按钮
def fStartCompress():
    sPath = os.path.dirname(sDrop.get())
    os.chdir(sPath)
    # sTemp = os.path.join(sPath,"Temp")
    # sTempAfter = os.path.join(sPath,"TempAfter")
    # sTempZIP = os.path.join(sPath,"TempZIP")
    sTemp = os.path.join(r"D:\Python","Temp")
    sTempAfter = os.path.join(r"D:\Python","TempAfter")
    sTempZIP = os.path.join(r"D:\Python","TempZIP")
    if not os.path.exists(sTemp):
        os.makedirs(sTemp)
    if not os.path.exists(sTempAfter):
        os.makedirs(sTempAfter)        
    if not os.path.exists(sTempZIP):
        os.makedirs(sTempZIP)                 
        
    with open(os.path.join(sTemp,"BDZJZ.tmp"), 'w') as f:
        pass  # 创建空文件    
        
    fExtractZIP(sDrop.get(),sTemp)
    
    fcompress_images(sTemp,sTempAfter,75)
    
    pack_folder_except_tmp(sTempAfter,sTempZIP,os.path.basename(sDrop.get()))
    #print(sPath,bPNG.get())
    cleanup_folder_if_tmp_exists(sTemp)
    cleanup_folder_if_tmp_exists(sTempAfter)

btnStart = Button(root,text="开始压缩",command=fStartCompress).pack(anchor="nw",padx=20,pady=20)

#选项是否PNG压缩成JPG
Checkbutton(root,text="将PNG压缩成JPG",variable=bPNG).pack(anchor="nw",padx=20,pady=10)

#文件拖放部分

def on_drop( event):
    """处理文件拖放"""
    tmpData = event.data
    #带空格的路径前后会有花括号，土办法处理
    if tmpData.startswith('{') and tmpData.endswith('}'):
        tmpData = tmpData[1:-1]
    sDrop.set(os.path.normpath(tmpData))

lblDrop = Entry(root,textvariable=sDrop,relief="groove")
lblDrop.place(x=550,y=10,width=700,height=300)
lblDrop.drop_target_register(DND_FILES)
lblDrop.dnd_bind('<<Drop>>', on_drop)



#长宽压缩选项
Radiobutton(root,text="不压缩大小",variable=sZOOM,value="A").pack(anchor="nw",padx=20,pady=1)
Radiobutton(root,text="压缩一半",variable=sZOOM,value="B").pack(anchor="nw",padx=20,pady=1)
Radiobutton(root,text="压缩1/3",variable=sZOOM,value="C").pack(anchor="nw",padx=20,pady=1)
Radiobutton(root,text="自适应算法:（从上往下Else，不勾或者不满足则不压缩）",variable=sZOOM,value="D").pack(anchor="nw",padx=20,pady=1)

frame_01 = Frame(root)
frame_01.pack(anchor="nw",padx=30,pady=1)

frame_02 = Frame(root)
frame_02.pack(anchor="nw",padx=30,pady=1)

frame_03 = Frame(root)
frame_03.pack(anchor="nw",padx=30,pady=1)

Checkbutton(frame_01,text="  当 宽 x 高 >  ",variable=bZOOM_01).pack(side="left",padx=1,pady=1)
Entry(frame_01,textvariable=sZOOM_11).pack(side="left",padx=1,pady=1)
Label(frame_01,text="时，缩放比例").pack(side="left",padx=1,pady=1)
Entry(frame_01,textvariable=sZOOM_12).pack(side="left",padx=1,pady=1)

Checkbutton(frame_02,text="  当 宽 x 高 >  ",variable=bZOOM_02).pack(side="left",padx=1,pady=1)
Entry(frame_02,textvariable=sZOOM_21).pack(side="left",padx=1,pady=1)
Label(frame_02,text="时，缩放比例").pack(side="left",padx=1,pady=1)
Entry(frame_02,textvariable=sZOOM_22).pack(side="left",padx=1,pady=1)

Checkbutton(frame_03,text="  当 宽 x 高 >  ",variable=bZOOM_03).pack(side="left",padx=1,pady=1)
Entry(frame_03,textvariable=sZOOM_31).pack(side="left",padx=1,pady=1)
Label(frame_03,text="时，缩放比例").pack(side="left",padx=1,pady=1)
Entry(frame_03,textvariable=sZOOM_32).pack(side="left",padx=1,pady=1)

#Radiobutton(root,text="当宽>3840时",variable=sZOOM,value="F").pack(anchor="nw",padx=30,pady=1)
#Radiobutton(root,text="当高>3840时",variable=sZOOM,value="G").pack(anchor="nw",padx=30,pady=1)

mainloop()