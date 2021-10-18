<template>
  <div id="properties-panel" v-show="visible">
    <v-simple-table dense fixed-header height="500px">
      <template v-slot:default>
        <thead>
        <tr>
          <th >
            Name
          </th>
          <th >
            Value
          </th>
        </tr>
        </thead>
        <tbody>
          <tr v-for="property in properties" :key="property.id">
            <td>{{ property.name }}</td>
            <td>{{ property.value.toString() }}</td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </div>
</template>

<script>
export default {
  name: "PropertiesPanel",
  props: ["properties", "visible"]
}
</script>

<style scoped>
#properties-panel {
  width: 300px;
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
</style>