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
      :headers="titles"
      :items="properties"
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