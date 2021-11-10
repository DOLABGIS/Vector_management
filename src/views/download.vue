<template>
    <div class="download_demo">
        <el-form ref="form" :model="form" label-width="120px" style="width: 50%">
      <el-form-item label="保存至文件夹">
        <input type="file" id="file" hidden @change="fileChange" webkitdirectory>
        <el-input placeholder="请输入内容" v-model="imgSavePath" class="input-with-select">
          <el-button slot="append" icon="el-icon-folder" type="success" @click="btnChange"></el-button>
        </el-input>
      </el-form-item>
    </el-form>

    </div>
</template>
<script>
import Bus from '../assets/bus'
export default {
        name: "download",
        data() {
    return {
     
        imgSavePath: ''
    }
  },
  methods: {
    fileChange(e) {
      try {
        const fu = document.getElementById('file')
        if (fu == null) return
        this.imgSavePath = fu.files[0].path
        console.log(fu.files[0].path)
      } catch (error) {
        console.debug('choice file err:', error)
      }
    },
    btnChange() {
      var file = document.getElementById('file')
      file.click()
    }
  }

    }
</script>

<style scoped>
    .download_demo{
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