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

import re
import sys
import os

import pyperclip
from selenium import webdriver
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import streamlit as st

import time

from config.config import shipinhao_site
from tools.file_utils import read_head, read_file_with_extra_enter


def wait_for_video_upload(driver):
    """等待视频上传完成"""
    try:
        wait = WebDriverWait(driver, 180)  # 3分钟超时
        
        # 首先检查是否直接上传完成（缓存情况）
        try:
            delete_button = driver.find_element(
                By.XPATH, 
                '//div[contains(@class, "finder-tag-wrap")]//div[contains(text(), "删除")]'
            )
            if delete_button.is_displayed():
                print("视频秒传完成")
                return True
        except:
            # 如果没有找到删除按钮，说明需要等待上传
            print("等待视频上传...")
            
            # 等待进度条出现
            try:
                progress_element = wait.until(
                    EC.presence_of_element_located((
                        By.XPATH, 
                        '//div[contains(@class, "upload-progress")]'
                    ))
                )
                print("找到上传进度条")
                
                # 记录开始时间
                start_time = time.time()
                last_progress = None
                
                # 等待上传完成
                while time.time() - start_time < 180:  # 最多等待3分钟
                    try:
                        # 检查删除按钮是否出现（上传完成标志）
                        delete_button = driver.find_element(
                            By.XPATH, 
                            '//div[contains(@class, "finder-tag-wrap")]//div[contains(text(), "删除")]'
                        )
                        if delete_button.is_displayed():
                            print("视频上传完成")
                            return True
                            
                        # 如果还没完成，检查进度
                        current_progress = progress_element.text
                        if current_progress != last_progress:
                            print(f"当前上传进度: {current_progress}")
                            last_progress = current_progress
                            
                    except:
                        # 如果获取进度失败，继续等待
                        pass
                        
                    time.sleep(1)
                    
                print("上传超时")
                return False
                
            except:
                # 如果没有找到进度条，但也没有错误提示，可能是秒传
                try:
                    delete_button = driver.find_element(
                        By.XPATH, 
                        '//div[contains(@class, "finder-tag-wrap")]//div[contains(text(), "删除")]'
                    )
                    if delete_button.is_displayed():
                        print("视频秒传完成")
                        return True
                except:
                    pass
                    
                print("无法确认上传状态")
                return False
                
    except Exception as e:
        print(f"等待视频上传出错: {str(e)}")
        return False


def shipinhao_publisher(driver, video_file, text_file):
    # 打开新标签页并切换到新标签页
    driver.switch_to.new_window('tab')
    driver.get(shipinhao_site)

    # 设置等待
    wait = WebDriverWait(driver, 30)  # 增加初始等待时间到30秒
    
    try:
        # 等待页面初始化完成（等待页面上任意一个特征元素出现）
        wait.until(
            EC.presence_of_element_located((
                By.XPATH, 
                '//div[contains(@class, "post-album-display-wrap")]'
            ))
        )
        print("页面初始化完成")
        
        # 再等待几秒确保页面完全稳定
        time.sleep(5)
        
        # 使用原来的上传按钮定位策略
        file_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
        )
        
        # 检查文件是否存在且可访问
        if not os.path.isfile(video_file):
            raise Exception(f"视频文件不存在: {video_file}")
            
        print(f"开始上传视频: {video_file}")
        file_input.send_keys(video_file)
        print("已触发文件上传")

        # 等待视频上传完成
        if not wait_for_video_upload(driver):
            raise Exception("视频上传失败或超时")
            
        print("视频上传成功，继续后续操作")

        # 设置标题
        title = driver.find_element(By.XPATH, '//input[@placeholder="概括视频主要内容，字数建议6-16个字符"]')
        title_text = read_head(text_file)
        use_common = st.session_state.get('video_publish_use_common_config')
        if use_common:
            common_title = st.session_state.get('video_publish_title_prefix')
        else:
            common_title = st.session_state.get('video_publish_shipinhao_title_prefix')
        # 替换英文标点符号
        title_text = re.sub(r'[.!?,:;"\'\-\(\)]', '', title_text)
        # 替换中文标点符号
        title_text = re.sub(r'[。！？，：、；"\'\-（）]', '', title_text)

        # 标题最多16个字符
        final_title = common_title + title_text
        if len(final_title) > 16:
            final_title = final_title[:16]
            print(f"标题已截断到16字符: {final_title}")
        
        title.send_keys(final_title)
        time.sleep(2)

        # 设置内容
        content = driver.find_element(By.XPATH, '//div[@class="input-editor"]')
        content.click()
        time.sleep(2)
        cmd_ctrl = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL
        # 将要粘贴的文本内容复制到剪贴板
        content_text = read_file_with_extra_enter(text_file)
        pyperclip.copy(content_text)
        action_chains = webdriver.ActionChains(driver)
        # 模拟实际的粘贴操作
        action_chains.key_down(cmd_ctrl).send_keys('v').key_up(cmd_ctrl).perform()
        time.sleep(2)

        # 设置tags
        if use_common:
            tags = st.session_state.get('video_publish_tags')
        else:
            tags = st.session_state.get('video_publish_shipinhao_tags')
        tags = tags.split()
        for tag in tags:
            content.send_keys(' ')
            content.send_keys(tag)
            content.send_keys(' ')
            time.sleep(1)

        # 设置位置
        location_tag = driver.find_element(By.CLASS_NAME,'location-name')
        actions = ActionChains(driver)
        actions.move_to_element(location_tag).click().perform()
        time.sleep(1)
        location_item = driver.find_element(By.XPATH,'//div[@class="location-item-info"]/div[text()="不显示位置"]')
        actions.move_to_element(location_item).click().perform()
        time.sleep(1)

        # 设置合集
        if use_common:
            collection = st.session_state.get('video_publish_collection_name')
        else:
            collection = st.session_state.get('video_publish_shipinhao_collection_name')
        if collection:
            # 等待合集按钮完全渲染
            time.sleep(3)  # 增加等待时间
            
            # 滚动到底部确保元素可见
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            collection_tag = driver.find_element(By.XPATH, '//div[@class="post-album-display-wrap"]/div[text()="选择合集"]')
            actions = ActionChains(driver)
            actions.move_to_element(collection_tag).click().perform()
            time.sleep(3)  # 增加等待时间到3秒，确保下拉菜单完全展开和渲染
            
            collection_to_select = driver.find_element(By.XPATH,
                                                    f'//div[@class="post-album-wrap"]//div[text()="{collection}"]')
            actions.move_to_element(collection_to_select).click().perform()
            time.sleep(2)  # 增加点击后的等待时间

        is_original = st.session_state.get("video_publish_shipinhao_enable_original")

        if is_original:
            # 原创
            original_tag = driver.find_element(By.XPATH, '//div[@class="declare-original-checkbox"]//input[@type="checkbox"]')
            original_tag.click()
            time.sleep(1)
            # original_tag_click = driver.find_element(By.XPATH, '//div[@class="original-type-form"]//dt[contains(text(),"请选择")]')
            # actions.move_to_element(original_tag_click).click().perform()
            # time.sleep(1)
            # original_tag_item = driver.find_element(By.XPATH,
            #                                          '//div[@class="original-type-form"]//span[text()="知识"]')
            # actions.move_to_element(original_tag_item).click().perform()
            # time.sleep(1)
            agree_button = driver.find_element(By.XPATH, '//div[@class="original-proto-wrapper"]//input[@type="checkbox"]')
            agree_button.click()
            time.sleep(1)
            agree_button_click = driver.find_element(By.XPATH,'//button[@type="button" and text()="声明原创"]')
            agree_button_click.click()
            time.sleep(1)

        # 发布
        publish_button = driver.find_element(By.XPATH, '//button[text()="发表"]')
        auto_publish = st.session_state.get('video_publish_auto_publish')
        if auto_publish:
            print("auto publish")
            publish_button.click()
            time.sleep(10)  # 点击发表后等待5秒

    except Exception as e:
        print(f"视频号上传失败: {str(e)}")
        # 尝试截图保存错误现场
        try:
            screenshot_path = f"error_screenshot_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            print(f"错误截图已保存: {screenshot_path}")
        except:
            print("保存错误截图失败")
        raise e
