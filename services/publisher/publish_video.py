#  Copyright © [2024] 程序那些事
#
#  All rights reserved. This software and associated documentation files (the "Software") are provided for personal and educational use only. Commercial use of the Software is strictly prohibited unless explicit permission is obtained from the author.
#
#  Permission is hereby granted to any person to use, copy, and modify the Software for non-commercial purposes, provided that the following conditions are met:
#
#  1. The original copyright notice and this permission notice must be included in all copies or substantial portions of the Software.
#  2. Modifications, if any, must retain the original copyright information and must not imply that the modified version is an official version of the Software.
#  3. Any distribution of the Software or its modifications must retain the original copyright notice and include this permission notice.
#
#  For commercial use, including but not limited to selling, distributing, or using the Software as part of any commercial product or service, you must obtain explicit authorization from the author.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#  Author: 程序那些事
#  email: flydean@163.com
#  Website: [www.flydean.com](http://www.flydean.com)
#  GitHub: [https://github.com/ddean2009/MoneyPrinterPlus](https://github.com/ddean2009/MoneyPrinterPlus)
#
#  All rights reserved.
#
#

import os
import traceback
import streamlit as st
import logging
from datetime import datetime
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from services.publisher.publisher_common import init_driver
from services.publisher.xiaohongshu_publisher import xiaohongshu_publisher
from services.publisher.douyin_publisher import douyin_publisher
from services.publisher.kuaishou_publisher import kuaishou_publisher
from services.publisher.shipinhao_publisher import shipinhao_publisher
from tools.file_utils import write_to_file, list_files, read_head
from tools.utils import get_must_session_option

last_published_file_name = 'last_published_cn.txt'

all_sites = ['xiaohongshu',
             'douyin',
             'kuaishou',
             'shipinhao',
             ]


def publish_to_platform(platform, driver, video_file, text_file):
    """
    发布到指定平台的封装函数
    """
    try:
        # 读取文本内容并添加文件名(去掉后缀)
        with open(text_file, 'r', encoding='utf-8') as f:
            text_content = f.read().strip()
            temp_text_file = text_file + '.temp'
            # 获取不带后缀的文件名
            filename_without_ext = os.path.splitext(os.path.basename(video_file))[0]
            with open(temp_text_file, 'w', encoding='utf-8') as tf:
                tf.write(f"{text_content} {filename_without_ext}")
            
        globals()[platform + '_publisher'](driver, video_file, temp_text_file)
        # 删除临时文件
        os.remove(temp_text_file)
    except Exception as e:
        print(platform, "got error")
        traceback.print_exc()
        print(e)
    finally:
        # 确保关闭当前标签页
        if driver:
            for handle in driver.window_handles[1:]:
                driver.switch_to.window(handle)
                driver.close()
            driver.switch_to.window(driver.window_handles[0])
    if video_file:
        save_last_published_file_name(os.path.basename(video_file))


def save_last_published_file_name(filename):
    write_to_file(filename, last_published_file_name)

def batch_publish_files():
    """
    批量处理目录下的所有视频文件
    """
    success = 0
    failed = 0
    failed_files = []
    
    # 可配置的延迟时间(秒)【plabmark】
    delay_time = st.session_state.get("video_publish_delay_time", 1)
    
    video_dir = get_must_session_option('video_publish_content_dir', "请设置视频发布内容")
    text_file = get_must_session_option('video_publish_content_text', "请选择要发布的内容文件")
    video_files = list_files(video_dir, '.mp4')
    
    # 按数字顺序排序文件
    def get_file_number(filename):
        # 从文件名中提取数字部分
        name = os.path.splitext(os.path.basename(filename))[0]
        try:
            return int(name)
        except ValueError:
            return filename  # 如果转换失败，返回原文件名
    
    # 对文件列表进行排序
    video_files.sort(key=get_file_number)
    
    if not video_files:
        st.error("所选目录下没有找到视频文件")
        return
    
    total_files = len(video_files)
    for index, video_file in enumerate(video_files):
        current_file = os.path.basename(video_file)
        print(f"\n处理进度: [{index + 1}/{total_files}] 当前文件: {current_file}")
        
        try:
            driver = init_driver()
            
            # 发布到已启用的平台
            if st.session_state.get("video_publish_enable_douyin"):
                publish_to_platform('douyin', driver, video_file, text_file)
            
            if st.session_state.get("video_publish_enable_kuaishou"):
                publish_to_platform('kuaishou', driver, video_file, text_file)
                
            if st.session_state.get("video_publish_enable_xiaohongshu"):
                publish_to_platform('xiaohongshu', driver, video_file, text_file)
                
            if st.session_state.get("video_publish_enable_shipinhao"):
                publish_to_platform('shipinhao', driver, video_file, text_file)
            
            success += 1
            print(f"✓ 处理成功: {current_file}")
            driver.quit()
            
            time.sleep(delay_time)
            
        except Exception as e:
            failed += 1
            failed_files.append(os.path.basename(video_file))
            logging.error(f"处理视频 {video_file} 失败: {str(e)}")
            print(f"✗ 处理失败: {current_file}")
            traceback.print_exc()
        
    # 任务完成后的统计信息
    completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n任务完成！时间: {completion_time}")
    print(f"总计: {total_files} 个文件")
    print(f"成功: {success} 个")
    print(f"失败: {failed} 个")
    
    if failed_files:
        print("\n失败的文件：")
        for f in failed_files:
            print(f"- {f}")
    
    # 记录最后发布的文件
    if video_files:
        save_last_published_file_name(os.path.basename(video_files[-1]))

def publish_file():
    """
    保留原有的单文件发布功能，但改为调用批量处理函数
    """
    batch_publish_files()

def publish_all():
    driver = init_driver()
    video_dir = get_must_session_option('video_publish_content_dir', "请设置视频发布内容")
    video_list = list_files(video_dir, '.mp4')
    text_list = list_files(video_dir, '.txt')
    while True:
        # 选择要发布的内容
        print("选择你要发布的视频,输入序号,A:全部,n-m从n到m:")
        for index, file_name in enumerate(video_list):
            print(str(index) + ":" + os.path.basename(file_name))
        print("上次发布的视频是: " + read_head(last_published_file_name))
        file_choice = input("\n请选择: ")
        print("")
        file_path_list = []
        text_path_list = []

        if file_choice == 'A':
            file_path_list = video_list
            text_path_list = text_list
        elif file_choice.isdigit():
            if len(video_list) > int(file_choice) >= 0:
                file_path_list.append(video_list[int(file_choice)])
                text_path_list.append(text_list[int(file_choice)])
            else:
                print("输入的序号不在范围内")
                continue
        else:
            range_list = file_choice.split('-')
            if len(range_list) == 2:
                start = int(range_list[0])
                end = int(range_list[1])
                if start <= end < len(video_list):
                    file_path_list = video_list[start:end + 1]
                    text_path_list = text_list[start:end + 1]
                else:
                    print("输入的序号不在范围内")
                    continue
            else:
                print("输入的序号不在范围内")
                continue

        while True:
            print("选择你要发布的平台:\n")
            print("1. 全部(小红书,抖音,快手,视频号)")
            print("2. 小红书")
            print("3. 抖音")
            print("4. 快手")
            print("5. 视频号")
            print("0. 退出")

            choice = input("\n请选择: ")
            print("")
            for file_path, text_path in zip(file_path_list, text_path_list):
                if choice == "1":
                    publish_to_platform('xiaohongshu', driver, file_path, text_path)
                    publish_to_platform('douyin', driver, file_path, text_path)
                    publish_to_platform('kuaishou', driver, file_path, text_path)
                    publish_to_platform('shipinhao', driver, file_path, text_path)
                elif choice == "2":
                    publish_to_platform('xiaohongshu', driver, file_path, text_path)
                elif choice == "3":
                    publish_to_platform('douyin', driver, file_path, text_path)

                elif choice == "4":
                    publish_to_platform('kuaishou', driver, file_path, text_path)

                elif choice == "5":
                    publish_to_platform('shipinhao', driver, file_path, text_path)
                else:
                    break
            if choice == "0":
                break


if __name__ == '__main__':
    publish_all()