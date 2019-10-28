"""储存一些跨文件的常量，方便统一修改"""
child_flows_key = "child_flows:{}"
# flow_id, 值为list系列化后的str类型:缓存子流程信息

cache_key = "cache:{}"
# device_id, 值为dict系列化后str类型：缓存流程信息

unknown_key = "unknown:{}"
# device_id, 值为int类型：缓存无法回答的次数

crontab_key = "crontab:{}-{}"
# device_id, 值为dict系列化后str类型：定时任务缓存

robot_info_key = "robot_info:{}"
# device_id, 值为dict：机器人信息缓存

broadcast_key = "broadcast:{}"
# device_id： 华东学院送站广播信息缓存
staff_key = "way_staff_{}:{}"
# subsystem_id, staff_id, 值为set(接管device_id1,device_id2...)：员工信息+接管的机器id

log_key = "log:{}"
# session_id, 值为list:问答日志缓存

# user_key = "user:{}"
# device_id： 用户信息缓存

status_key = "device_status:{}:{}"
# subsystem_id, device_id, 值为dict： 设备状态缓存

stop_resp = ["幸好有你,差点停不下来了", "好的", "您还有别的吩咐吗", "哦"]

FMT = "%Y-%m-%d %H:%M:%S"
log_name_keep_alive = "keep_alive"
log_name_main = "main"
log_name_timer = "timer"
log_name_socketio = "socketio"

sep = "|"
comm = "way_common_subsystem"  # 公共子系统
em = '<span class="yellowFont">{}</span>'
css = """<div class="simpleSent"><div class="simplecount">
<div class="commaleft"></div>
{}
<div class="commaright"></div>
</div></div>"""

noun_cache_key = "noun:{}"
# 名词缓存键值 key=noun:{device_id}; 值格式为字符串 json.dump([['北京','天安门'],['太阳'],['西瓜']]) 列表最后一个最新
