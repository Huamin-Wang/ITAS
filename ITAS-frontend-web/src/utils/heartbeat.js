import { heartbeat } from "@/http/api";

class HeartbeatService {
    constructor() {
        this.intervalId = null;
        this.intervalTime = 20 * 60 * 1000;
        this.endpoint = '/heartbeat';
        this.isRunning = false;
    }

    // 检查用户是否已登录
    checkLoginStatus() {
        const userInfo = localStorage.getItem('userInfo');
        return !!(userInfo && userInfo !== 'null' && userInfo !== 'undefined' && userInfo !== '{}');
    }

    // 初始化方法 - 在应用启动时调用
    init() {
        // 检查当前登录状态，如果已登录则自动启动
        if (this.checkLoginStatus()) {
            console.log('🔍 检测到用户已登录，自动启动心跳服务');
            this.start();
        } else {
            console.log('🔐 用户未登录，等待登录后启动心跳服务');
        }

        // 监听存储变化，当用户信息变化时自动处理
        window.addEventListener('storage', this.handleStorageChange.bind(this));
    }

    // 处理存储变化事件
    handleStorageChange(event) {
        if (event.key === 'userInfo') {
            if (event.newValue && event.newValue !== 'null') {
                // 用户信息被设置，可能是登录了
                if (!this.isRunning) {
                    console.log('🔄 检测到用户登录，启动心跳服务');
                    this.start();
                }
            } else {
                // 用户信息被清除，可能是登出了
                if (this.isRunning) {
                    console.log('🔄 检测到用户登出，停止心跳服务');
                    this.stop();
                }
            }
        }
    }

    start() {
        if (this.isRunning) return;

        console.log('💓 心跳服务启动');
        this.isRunning = true;

        // 立即发送第一次心跳
        this.sendHeartbeat();

        this.intervalId = setInterval(() => {
            if (!this.checkLoginStatus()) {
                console.log('🔐 检测到用户已登出，停止心跳服务');
                this.stop();
                return;
            }
            this.sendHeartbeat();
        }, this.intervalTime);

        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
    }

    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        this.isRunning = false;
        console.log('💔 心跳服务停止');
    }

    async sendHeartbeat() {
        // 发送前再次检查登录状态
        if (!this.checkLoginStatus() || document.hidden) {
            return;
        }

        try {
            const response = await heartbeat();

            if (response.code === 200) {
                console.log('✅ 心跳成功', new Date().toLocaleTimeString());
            } else {
                console.log('🔐 Token 已过期，停止心跳服务');
                this.handleTokenExpired();
            }
        } catch (error) {
            console.error('❌ 心跳请求错误:', error);
        }
    }

    handleVisibilityChange() {
        if (!document.hidden && this.checkLoginStatus()) {
            this.sendHeartbeat();
        }
    }

    handleTokenExpired() {
        this.stop();
        localStorage.removeItem('userInfo');
        window.location.href = '/login';
    }

    // 外部调用的方法：用户登录后手动启动
    onUserLogin() {
        if (!this.isRunning) {
            this.start();
        }
    }

    // 外部调用的方法：用户登出后手动停止
    onUserLogout() {
        this.stop();
    }
}

export default new HeartbeatService();