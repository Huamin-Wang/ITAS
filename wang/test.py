import threading
import time
# 共享资源：工具箱，这里用一个变量表示工具的数量
toolbox = 10
# 创建锁，就像给工具箱加了一把锁
lock = threading.Lock()


def worker(name):
    global toolbox
    for _ in range(5):
        flag=1
        lock.acquire()
        if toolbox > 0:  # 检查工具箱里是否还有工具
            toolbox -= 1  # 从工具箱里拿一个工具
            print(f"{name} 拿了一个工具，工具箱里还剩下 {toolbox} 个工具")
            if name == "工人1":
                lock.release()
                time.sleep(2)
                flag=0
        else:
            print(f"{name} 发现工具箱空了，无法拿到工具")
        if flag==1:
            lock.release()
        return name   # 这个name怎么接收





# 创建线程对象，代表不同的工人
t1 = threading.Thread(target=worker, args=("工人1",))
t2 = threading.Thread(target=worker, args=("工人2",))
t3 = threading.Thread(target=worker, args=("工人3",))


# 启动线程
t1.start()
t2.start()
t3.start()


# 等待线程完成
t1.join()
t2.join()
t3.join()