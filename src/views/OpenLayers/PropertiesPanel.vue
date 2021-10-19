<template>
  <div id="properties-panel" v-show="visible">
    <div class= "layer-panel-title">
      <span>属性表</span>
    </div>
    <v-simple-table dense fixed-header style="color=#4a5064; height: 500px;">
      <template v-slot:default>
        <thead>
        <tr>
          <th v-for="title in titles" :key="title" >
            {{title}}
          </th>
          <th></th>
          <th></th>
        </tr>
        </thead>
        <tbody>
          <tr v-for="property in properties" :key="property">
            <!-- <td>{{ property.name }}</td>
            <td>{{ property.value.toString() }}</td> -->
            <td v-for="val in property" :key="val">
              {{val}}
            </td>
            <td @click="delete_data">
              删除
            </td>
            <td @click="modify_data">
              修改
            </td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </div>
</template>

<script>
export default {
  name: "PropertiesPanel",
  props: ["properties", "visible","titles"],
  methods:{
    delete_data(){

    },
    modify_data(){

    }
  }
}
</script>

<style scoped>
#properties-panel {
  width: 350px;
  max-width: 350px;
  height: 500px;
  right: 20px;
  top: 10%;
  overflow: auto;
  z-index: 600;
  position: absolute;
  scroll-behavior: auto;
  background-color: #4a5064;
}
.layer-panel-title {
  height: 40px;
  width: 100%;
  line-height: 40px;
  font-weight: bold;
}
.layer-panel-title > span {
  margin-left: 15px;
  color: #fff;
}

</style>