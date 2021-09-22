<template>
<div class="wrapper">
<!-- 页面头部部分 -->
    <div class="header">
        <div class="logo">矢量数据管理</div>
        <!-- 水平一级菜单 -->
        <div style="float:left;">
            <!-- <el-menu :default-active="toIndex()" mode="horizontal" @select="handleSelect">
            <template v-for="item in items">
                <el-menu-item :index="item.index" :key="item.index">
                <template slot="title">
                    <span slot="title">{{ item.title }}</span>
                </template>
                </el-menu-item>
            </template>
            </el-menu> -->
            <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" @select="handleSelect">
  <el-submenu index="1">
    <template slot="title">文件</template>
    <el-menu-item index="1-1">打开文件</el-menu-item>
    <el-menu-item index="1-2">保存文件</el-menu-item>
    <el-menu-item index="1-3">导出文件</el-menu-item>
    <!-- <el-submenu index="2-4">
      <template slot="title">选项4</template>
      <el-menu-item index="2-4-1">选项1</el-menu-item>
      <el-menu-item index="2-4-2">选项2</el-menu-item>
      <el-menu-item index="2-4-3">选项3</el-menu-item>
    </el-submenu> -->
  </el-submenu>
    <el-submenu index="2">
    <template slot="title">矢量数据编辑</template>
    <el-menu-item index="2-1">开始编辑</el-menu-item>
    <el-menu-item index="2-2">停止编辑</el-menu-item>
  </el-submenu>
      <el-submenu index="3">
    <template slot="title">数据管理</template>
    <el-menu-item index="3-1">1</el-menu-item>
    <el-menu-item index="3-2">2</el-menu-item>
  </el-submenu>
</el-menu>

        </div>

        <div class="header-right">
            <div class="header-user-con">
                <!-- 用户头像 -->
                <div class="user-avator"><img src="../../assets/img/img.jpg" /></div>
                <!-- 用户名下拉菜单 -->
                <el-dropdown class="user-name" trigger="click" @command="handleCommand">
                    <span class="el-dropdown-link">
                        {{ username }}
                        <i class="el-icon-caret-bottom"></i>
                    </span>
                    <el-dropdown-menu slot="dropdown">
                        <el-dropdown-item disabled>修改密码</el-dropdown-item>
                        <el-dropdown-item command="loginout">退出登录</el-dropdown-item>
                    </el-dropdown-menu>
                </el-dropdown>
            </div>
        </div>
    </div>
    
    <!-- 页面左侧二级菜单栏，和主体内容区域部分 -->
    <el-main>
        <router-view></router-view>
    </el-main>

</div>
</template>

<script>
export default {
    data() {
        return {
            items: [    // 水平一级菜单栏的菜单
                { index: 'Home', title: '打开文件' },
                {  title: '一级菜单1' },
                {  title: '一级菜单2' },
                {  title: '一级菜单3' },
                {  title: '管理员权限' },
            ]
        }
    },
    computed: {
        username() {
            let username = localStorage.getItem('ms_username');
            return username ? username : this.name;
        }
    },
    methods:{
        // 根据路径绑定到对应的一级菜单，防止页面刷新重新跳回第一个
        toIndex() {
            return this.$route.path.split('/')[1];
        },
        // 切换菜单栏
        handleSelect(index) {
            this.$router.push('/' + index);
        },
        // 用户名下拉菜单选择事件
        handleCommand(command) {
            if (command == 'loginout') {
                localStorage.removeItem('ms_username');
                this.$router.push('/login');
            }
        }
    }
}
</script>

<style scoped>
.wrapper {
    width: 100%;
    height: 100%;
    background: #f0f0f0;
}
.header {
    position: relative;
    box-sizing: border-box;
    width: 100%;
    height: 70px;
    font-size: 22px;
}
.header .logo {
    float: left;
    margin-left: 60px;
    margin-top: 17.5px;
    height: 29px;
    width: 160px;
    vertical-align: middle;
}
/* --------------- 用户头像区域的样式 ---------------- */
.header-right {
    float: right;
    padding-right: 50px;
}
.header-user-con {
    display: flex;
    height: 70px;
    align-items: center;
}
.user-avator {
    margin-left: 20px;
}
.user-avator img {
    display: block;
    width: 40px;
    height: 40px;
    border-radius: 50%;
}
.user-name {
    margin-left: 10px;
}
.el-dropdown-link {
    cursor: pointer;
}
.el-dropdown-menu__item {
    text-align: center;
}
/* --------------- 水平一级菜单栏的样式--------------------- */
.el-menu.el-menu--horizontal {
    border-bottom: none !important;
    float: left;
    margin-left: 50px;
}
.el-menu--horizontal > .el-menu-item.is-active {
    border-bottom: 2px solid #409eff;
    color: #3989fa;
    font-weight: 700;
}
.el-menu--horizontal > .el-menu-item {
    font-size: 16px;
    margin: 0 15px;
    color: black;
}
</style>