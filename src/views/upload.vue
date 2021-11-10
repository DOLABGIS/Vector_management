<template>
    <div class="upload_demo">
        <el-upload
                   drag
                   :auto-upload=false
                   action=""
                   accept="shp"
                   :on-preview="handlePreview"
                   :on-remove="handleRemove"
                   :limit="1"
                   :on-change="bind"
                   class=" upload"
        >
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">将shp文件拖到此处，或<em>点击配置</em></div>

            <div class="el-upload__tip" slot="tip">必须是shp文件</div>
        </el-upload>
        <el-button style="margin-left: 10px;" size="small" type="success" @click="config">确定</el-button>
        <el-button style="margin-left: 10px;" size="small" type="danger" @click="cancer">取消</el-button>
    </div>
</template>

<script>
import Bus from '../assets/bus'
import {open} from 'shapefile'
import axios from 'axios'
    export default {
        name: "Config",
        data(){
            return{
                file:{},
                result:null
            }
        },
        methods:{
            config() {
                const name=this.file.name
                const extension=name.split('.')[1]
                if('shp'!==extension){
                    this.$alert('文件不是shp文件！请重新选择文件', {
                        confirmButtonText: '确定'
                    })
                }else {
                    const reader=new FileReader()
                    const  fileData=this.file.raw
                    reader.readAsArrayBuffer(fileData)
                    reader.onload = function(e){
                        open(this.result)
                            .then(source => source.read()
                                .then(function log(result) {
                                    if (result.done) return;
                                    console.log(result.value);
                                    // axios.post('api/uploadgeojson',{'data':result.value,'name':name.split('.')[0] }).then((response)=>{
                                    //     if(response.data=='1'){
                                    //     this.$message({
                                    //         message: "上传成功",
                                    //         type: "success"
                                    //     });
                                    //     }
                                    //     else if(response.data=='0'){
                                    //     this.$message({
                                    //         message: "图层名重复",
                                    //         type: "error"
                                    //     });
                                    //     }
                                    // });
                                    Bus.$emit('send',false);
                                    Bus.$emit('geojson',{'layername':name.split('.')[0],'data':result.value});
                                    return source.read().then(log);
                                }))
                            .catch(error => console.error(error.stack));
                    }
                

                }

            },
            cancer(){
                    Bus.$emit('send',false);

            },
            handleRemove(file, fileList) {
            },
            handlePreview(file) {
                console.log(file);
            },
            bind(files, fileList){
                //绑定文件
                this.file=fileList[0]
                //console.log(this.file)
            }

        }
    }
</script>

<style scoped>
    .upload_demo{
        text-align: center;
        margin-top: 50px;
        position: absolute;
        top: 30%;
        right: 35%;
        z-index: 2;
        background-color: #fff;
    }
    .el-button{
       margin-top: 10px;
       margin-bottom: 10px;
    }
    .upload{
        margin: 10px;
    }
</style>
