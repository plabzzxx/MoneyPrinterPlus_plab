# PLAB NOTE

## note
【plabmark】为一些特殊的标记

## commit：
- V0 拉取后首次提交 添加plabnote
- V1.0 进行了本地测试（批量发布功能），修改了快手发布按钮的元素定位，现测试可用
- V1.1 增加简要的项目解读
- V1.2 备份了03_auto_publish copy.py 下一步将开始对原项目修改，当前还未做任何其他修改
- V1.3 实现自动批量上传。实现了对指定文件夹内的全部视频自动上传到快手 修改了03_auto_publish 和services\publisher\publish_video.py
- V1.4 完善可批量上传的功能，目前只支持快手。


# 启动
1.以debug模式启动chrome 
chrome --remote-debugging-port=9222
2.运行
streamlit run gui.py
3. 端口占用问题，如果遇到 "Port 8501 is already in use" 错误，可以通过以下方法解决：
netstat -ano | findstr 8501
taskkill /F /PID <PID>

