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
- V1.5 批量上传的功能增加支持视频号。
- V1.6 测试视频生成成功1。测试条件：chattts 本地api，关闭字幕，关闭转场效果。（字幕和转场效果会报错，后续排查）
- V1.7 增加本地日志。视频号批量发布失败的文件会被记录logs/publish_errors.log---【未git】
- V1.7.1 日常备份
- V1.8 增加了视频号等待上传完成的功能
- V1.9 视频号的 标题 限制16个字符，多余则截取前16
- V1.9.1 优化了视频号上传的元素渲染等待时间


# 启动
0.切换conda - alpha

1.以debug模式启动chrome 
chrome --remote-debugging-port=9222
2.运行
streamlit run gui.py
3. 端口占用问题，如果遇到 "Port 8501 is already in use" 错误，可以通过以下方法解决：
netstat -ano | findstr 8501
taskkill /F /PID <PID>


