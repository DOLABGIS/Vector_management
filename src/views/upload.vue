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
    export default {
        name: "Config",
        data(){
            return{
                file:{}
            }
        },
        methods:{
            config() {
                const name=this.file.name
                console.log(this.filePath);
                const extension=name.split('.')[1]
                //console.log(extension)
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
                                    return source.read().then(log);
                                }))
                            .catch(error => console.error(error.stack));
                    }
                    Bus.$emit('send',false);
                    Bus.$emit('geojson',name.split('.')[0]);

                }

            },
            cancer(){
                    Bus.$emit('send',false);

            },
            handleRemove(file, fileList) {
                //console.log(file, fileList);
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
