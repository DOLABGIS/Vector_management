<template>
    <div class="upload_demo">
        <el-upload
                   drag
                   :auto-upload=false
                   action=""
                   accept="shp"
                   :on-preview="handlePreview"
                   :on-remove="handleRemove"
                   :before-remove="beforeRemove"
                   multiple
                   :on-change="bind"
                   :file-list="fileList"
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
import { OSM, TileArcGISRest, Vector as VectorSource } from 'ol/source'
import {open,read,openDbf} from 'shapefile'
import GeoJSON from "ol/format/GeoJSON"
import axios from 'axios'
    export default {
        name: "Config",
        data(){
            return{
                file:{},
                result:null,
                result2:null,
                fileList:[],
            }
        },
        methods:{
            config() {
                var opts={'shp':null,'dbf':null}
                const reader=new FileReader()
                var index = 0;
                var index2 = 1;
                var layername=''
                console.log(this.file);
                for(var file in this.file){
                    const name=this.file[file].name
                    const extension=name.split('.')[1]
                    if (extension=='shp'){
                        opts.shp= this.file[file] 
                        layername = this.file[file].name.split('.')[0]
                        const  fileData=this.file[file].raw
                        reader.readAsArrayBuffer(fileData)
                        index = file;
                    };
                    if (extension=='dbf'){
                        opts.dbf= this.file[file] 
                        const  fileData=this.file[file].raw
                        index2 = file;
                    };
                    }
                

                var shparray, dbfarray;
                var newfile = this.file[index2].raw;
                var oldfile = this.file[index].raw;
                var finaljson;
                reader.onload = function() {
                read(this.result)
                .then(geoJson => {
                    console.log('1.geoJson',geoJson);
                Bus.$emit('send',false);
                finaljson = geoJson;
                var reader2 = new FileReader();
                var i=0;
                reader2.readAsArrayBuffer(newfile);
                reader2.onload=function(evt){
                    dbfarray = evt.target.result;
                    openDbf(dbfarray, {encoding: "gbk"}).then(source => source.read()
                    .then(function log(result){
                             if (result.done) return;
                            finaljson.features[i++].properties=result.value;
                            // axios.post('api/upload', {'layername':layername,'data':result.value}).then(res => {
                            // console.log(res.data);
                            // })
                            // console.log(feature);
                            return source.read().then(log);
                    })
                  
                    )
                    }
                
                reader2.onloadend = function(evt){
                        axios.post('api/uploadgeojson', {'name':layername,'data':finaljson}).then(res => {
                            console.log(res.data);
                            })
                    Bus.$emit('geojson',{'layername':layername,'data':finaljson});

                }

        //         axios.post('api/upload', {'layername':layername,'data':finaljson.features[0]}).then(res => {
        //         // console.log('finaljson',finaljson.features[0].properties);
        //         console.log(res.data);
        // })
                }
                )}
                // var featurelist = [];
                // var source1 = new VectorSource({
                //     wrapX: false
                // });
                // reader.onload = function(e){
                //     shparray = e.target.result;
                //     console.log('shparray',shparray);
                //     var reader2 = new FileReader();

                //     reader2.readAsArrayBuffer(newfile);
                //     reader2.onload=function(evt){
                //         dbfarray = evt.target.result;
                //         console.log('dbfarray',dbfarray)
                //         open(shparray, dbfarray, {encoding: "gbk"}).then(source => source.read()
                //         .then(function log(result){
                //              if (result.done) return;
                //             var feature = new GeoJSON().readFeature(result.value);
                //             // featurelist.push(feature.values_);
                //             source1.addFeature(feature);
                //             return source.read().then(log);
                //         }
                //         )
                        
                //         )
                //         // open(shparray, dbfarray, {encoding: "gbk"}).then(source => {
                //         //     var feature = new GeoJSON().readFeatures(source);
                //         //     console.log('feature',feature);

                //         // }
                //         // )
                //     }

                //     }
                // console.log('source1',source1.getFeatures());
                // axios.post('api/upload', {'layername':layername,'data':featurelist}).then(res => {
                //     console.log(res.data);
                // })
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
                this.file=fileList
                //console.log(this.file)
            },
            beforeRemove(file, fileList) {
                    return this.$confirm(`确定移除 ${ file.name }？`);
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
