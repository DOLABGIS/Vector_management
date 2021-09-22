<template>
  <div>
map

</div>
</template>

<script>
import Vue from 'vue';
import { fetchData } from '../api/index';
import _ from "lodash";
import Grid from '../components/common/Grid';
import LineECharts from '@/components/dashboard/LineECharts';
export default {
    name: 'dashboard',
    destroyed() {
        this.searchEventBus.$off();
    },
    data() {
        this.searchEventBus = new Vue();
        return {
            name: localStorage.getItem('ms_username'),
            collapse: false,
            dateSelectList: ['今天','昨天','过去7天','过去30天','本周','上周','本月','上月'],     // 可选日期列表
            mediaAccountList: ['媒体账号1','媒体账号2','媒体账号3','媒体账号4'],    // 媒体账号列表
            applicationList: ['应用1','应用2','应用3','应用4','应用5'],    // 应用列表
            mediaTypeList: ['今日头条','广点通','快手'],     // 媒体类型列表
            
            searchForm:{     // 今日头条和效果总览的查询参数
                date: "",
                date2: "",
                mediaAccount: "",
                application: "",
                mediaType: ""
            },
            searchFormTop:{    // TOP广告和TOP创意的查询参数
                applicationTop: "",    // TOP广告
                mediaTypeTop: "",
                dateTop: "",
                applicationTop2: "",   // TOP创意
                mediaTypeTop2: "",
                dateTop2: "",
            },
            columnTopAd: [    // TOP广告的数据表格
            {
                title: "计划名称",
                key: "planName",
                minWidth: 220,
                tooltip: true
            },
            {
                title: "消耗",
                key: "expend",
                tooltip: true,
                minWidth: 100,
            },
            {
                title: "消耗变化率",
                key: "expendRate",
                minWidth: 100,
                tooltip: true,
            },
            {
                title: "转化数",
                key: "TransformNumber",
                minWidth: 100,
                tooltip: true,
            },
            {
                title: "转化率",
                key: "TransformRate",
                minWidth: 100,
                tooltip: true,
            },
        ],
        columnTopIdea:[    // TOP创意的数据表格

        ],
        };
    },
    components: {
        Vue,
        Grid,
        LineECharts
    },
    created() {
        
    },
    computed: {
        role() {
            return this.name === 'admin' ? '超级管理员' : '普通用户';
        }
    },
    methods: {
        //获取页码及每页条数
        currentPage(val){
        this.current = val;
        },
        pageSize(val){
        this.pageNum = val;
        },
        changeSort() {},
        selectionChange() {},
        changeDate() {
            const now = new Date().getTime();
            this.data.forEach((item, index) => {
                const date = new Date(now - (6 - index) * 86400000);
                item.name = `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`;
            });
        },
        setColor(dataVal){
            if(dataVal > 0){
                return 'overview-list-trend-up';
            }else{
                return 'overview-list-trend-down';
            }
        }
    }
};
</script>


<style scoped>
.el-row {
    margin-bottom: 20px;
}

/* 卡片标题字体的样式 */
.clearfix{
    padding-left: 5px;
    font-size: 22px;
    font-weight: 800;
}
/* 四个彩色卡片的相关样式 */
.colorCardsBody{
    padding: 18px 40px;
}
.colorCardsBody span{
    font-size: 16px;
    color: #515a6e;
}
.colorCardsBody p{
    font-family: Roboto-Medium !important;
    padding-top: 15px;
    font-size: 18px;
    font-weight: 800;
}
/* 数据总览区域的整体样式设置 */
.dataOverview{
    padding: 0 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
/* 数据总览里的每一条信息项 */
.overview-list-item {
    padding: 0 25px;
    border-left: 1px solid rgba(220,222,226,.5);
    flex: 1;
}
.overview-list-item:first-child {
    border: none;
}
/* 数据总览里每条信息项的文本部分 */
.overview-list-text {
    color: #515a6e;
    font-size: 14px;
    margin-bottom: 24px;
}
.overview-list-count {
    color: #17233d;
    font-weight: 700;
    margin-bottom: 16px;
    font-size: 16px;
}
.overview-list-trend-up {
    font-size: 14px;
    color: blue;
}
.overview-list-trend-down {
    font-size: 14px;
    color: red;
}
.programmaticBatchBtn{    /* 程序化批量的按钮样式 */
    float: right;
    padding: 4px 11px 3px 11px;
    margin-left: 20px;
    margin-right: 50px;
    font-size: 14px;
    color: rgb(255, 255, 255);
    background-color: rgb(0, 182, 151);
}
.programmaticBatchBtn img{     /* 程序化批量按钮上的动图标 */
    width: 24px;
    display: inline-block;
    vertical-align: middle;    /* 让该图标在 Y 轴上居中 */
}
.search-form{      /* 日期筛选控件的样式 */
    display: inline;
    margin-left: 20px;
    margin-right: 8px;
    float: right;
}
.search-form span,.search-form-2 span{    /* 筛选控件的前面字体样式 */
    margin-right: 10px;
    font-weight: 700;
}
.search-form-2{      /* “效果总览” 卡片里的筛选控件定位设置 */
    margin-top:30px;
    margin-bottom: -40px;
    margin-left: 30px;
}
.blankContent{    /* TOP 创意卡片底部空白部分，为了和 TOP 广告底部对齐 */
    width: auto;
    height: 40px;
}
</style>
