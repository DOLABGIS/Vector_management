<template>
  <v-card id ="properties-panel" v-show="visible">
    <v-card-title>
      <v-text-field
        v-model="search"
        append-icon="mdi-magnify"
        label="Search"
        single-line
        hide-details
      ></v-text-field>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="desserts"
      :search="search"
    ></v-data-table>
  </v-card>
</template>
<script>
  export default {
      props: ["properties", "visible","titles"],
    data () {
      return {
        search: '',
        headers: [
          {
            text: 'gid',value: 'gid'
           
          },
          { text: 'name', value: 'name' },
          { text: 'value', value: 'value' },
        ],
        desserts: [
          {
              'gid':1,
              'name':"江夏区",
              'value': 0.3116
          },
                    {
              'gid':2,
              'name':"汉阳区",
              'value': 0.5458
          },
                    {
              'gid':3,
              'name':"武昌区",
              'value': 0.9321
          },
            {
              'gid':4,
              'name':"硚口区",
              'value': 0.7613
          },
            {
              'gid':5,
              'name':"江汉区",
              'value': 1.0
          },
            {
              'gid':6,
              'name':"青山区",
              'value': 0.3983
          },
            {
              'gid':7,
              'name':"蔡甸区",
              'value': 0.2577
          },
          {
              'gid':8,
              'name':"洪山区",
              'value': 0.6493
          },
          {
              'gid':12,
              'name':"黄陂区",
              'value': 0.3166
          },
          {
              'gid':9,
              'name':"江岸区",
              'value': 0.8714
          },
          {
              'gid':10,
              'name':"东西湖区",
              'value': 0.4083
          },
          {
              'gid':11,
              'name':"新洲区",
              'value': 0.7613
          },
        ],
      }
    },
  }
</script>
<style scoped>
#properties-panel {
  width: 400px;
  height: 500px;
  right: 20px;
  top: 10%;
  overflow: auto;
  z-index: 600;
  position: absolute;
  scroll-behavior: auto;
}
</style>