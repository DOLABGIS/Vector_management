<template>
  <div id="properties-panel" v-show="visible">
  <v-data-table
    :headers="headers"
    :items="desserts"
    sort-by="calories"
    class="elevation-1"
    item-key="name"
    :search="search"
  >
    <template v-slot:top>
      <v-toolbar
        flat
      >
        <v-toolbar-title>Properties
        </v-toolbar-title>
        <v-card-title>
      <v-spacer></v-spacer>
      <v-divider
          class="mx-4"
          inset
          vertical
        ></v-divider>
      <v-text-field
        v-model="search"
        append-icon="mdi-magnify"
        label="Search"
        single-line
        hide-details
      ></v-text-field>
    </v-card-title>
        
        <v-spacer></v-spacer>
        <v-dialog
          v-model="dialog"
          max-width="500px"
        >
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              color="black"
              dark
              class="mb-2"
              v-bind="attrs"
              v-on="on"
            >
              New Item
            </v-btn>
          </template>
          <v-card>
            <v-card-title>
              <span class="text-h5">
                {{ formTitle }}
                </span>
            </v-card-title>

            <v-card-text>
              <v-container>
                <v-row>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-text-field
                    v-for="(val,key) in editedItem"
                      :key="key"
                      :label="key"
                    v-model="editedItem[key]"
                    ></v-text-field>
                  </v-col>
                  <!-- <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                  <v-text-field
                      label="name"
                      v-model="editedItem.gid"
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    md="4"
                  >
                  <v-text-field
                      label="value"
                      v-model="editedItem.dist1"
                    ></v-text-field>
                  </v-col> -->
                </v-row>
              </v-container>
            </v-card-text>

            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                color="blue darken-1"
                text
                @click="close"
              >
                Cancel
              </v-btn>
              <v-btn
                color="blue darken-1"
                text
                @click="save"
              >
                Save
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
        <v-dialog v-model="dialogDelete" max-width="500px">
          <v-card>
            <v-card-title class="text-h5">Are you sure you want to delete this item?</v-card-title>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="blue darken-1" text @click="closeDelete">Cancel</v-btn>
              <v-btn color="blue darken-1" text @click="deleteItemConfirm">OK</v-btn>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-toolbar>
    </template>
    <template v-slot:item.actions="{ item }">
      <v-icon
        small
        class="mr-2"
        @click="editItem(item)"
      >
        mdi-pencil
      </v-icon>
      <v-icon
        small
        @click="deleteItem(item)"
      >
        mdi-delete
      </v-icon>
    </template>
    <template v-slot:no-data>
      <v-btn
        color="primary"
        @click="initialize"
      >
        Reset
      </v-btn>
    </template>
  </v-data-table>
  </div>
</template>

<script>
import axios from 'axios'
import Bus from '../../assets/bus'
export default {
  name: "PropertiesPanel",
  props: ["visible"],
 data: () => ({
      dialog: false,
      search:'',
      dialogDelete: false,
      layername:'',
      headers: [],
      properties:[],
      desserts: [],
      editedIndex: -1,
      editedItem: {

      },
      defaultItem: {

      },
    }),
    computed: {
      formTitle () {
        return this.editedIndex === -1 ? 'New Item' : 'Edit Item'
      },
    },

    watch: {
      dialog (val) {
        val || this.close()
      },
      dialogDelete (val) {
        val || this.closeDelete()
      },
    },
    created () {
      Bus.$on('header',(val)=>{
				this.headers = val
			})
      Bus.$on('item',(val1)=>{
        console.log('PropertiesPanel Rogar!',val1);
				this.desserts = val1
        if(val1.length>0){
          for(var key in val1[0]){
              if(typeof(val1[0][key]) == 'number'){
                this.defaultItem[key] =0
              }
              if(typeof(val1[0][key]) == 'string'){
                this.defaultItem[key] =''
              }
          }
        }
        this.editedItem = this.defaultItem;
			})
      Bus.$on('layername',(val1)=>{
				this.layername = val1
			})
      this.initialize()
    },
    methods: {
      initialize () {
        
      },
      editItem (item) {

        this.editedIndex = this.desserts.indexOf(item)
        this.editedItem = Object.assign({}, item)
        console.log('item',this.editedItem);
        this.dialog = true
      },
      deleteItem (item) {
        this.editedIndex = this.desserts.indexOf(item)
        this.editedItem = Object.assign({}, item)
        this.dialogDelete = true
      },
      deleteItemConfirm () {
        axios.post('api/delete',{'layer':this.layername,'gid':this.desserts[this.editedIndex].gid}).then((response)=>{
          // delete成功返回"1"，否则返回0
          if(response.data!="0"){
            Bus.$emit('delete_item',{'layername':this.layername,'data':response.data});
          }
			  }).catch(res=>{
			  this.$message({
                			message: "删除失败",
                			type: "error"
        });
			});
        this.desserts.splice(this.editedIndex, 1);
        this.closeDelete();
        // Bus.$emit('editedIndex', this.desserts[this.editedIndex].protein);

      },
      close () {
        this.dialog = false
        this.$nextTick(() => {
          this.editedItem = Object.assign({}, this.defaultItem)
          this.editedIndex = -1
        })
      },
      closeDelete () {
        this.dialogDelete = false
        this.$nextTick(() => {
          this.editedItem = Object.assign({}, this.defaultItem)
          this.editedIndex = -1
        })
      },
      save () {
        if (this.editedIndex > -1) {
          Object.assign(this.desserts[this.editedIndex], this.editedItem)
          axios.post('api/update',{'layer':this.layername,'content':this.desserts[this.editedIndex]}).then((response)=>{
          // update成功返回"1"，否则返回0
			    }).catch(res=>{
			  this.$message({
                			message: "更新失败",
                			type: "error"
        });})
        } else {
          // new item
          // Bus.$emit('newitem',{'layername':this.layername,'item':this.editedItem})
          axios.post('api/insert',{'layer':this.layername,'content':this.editedItem}).then((response)=>{
          // update成功返回"1"，否则返回0
			    }).catch(res=>{
			  this.$message({
                			message: "插入失败",
                			type: "error"
        });})
          this.desserts.push(this.editedItem)

        }
        this.close()
      },
    },
    }
</script>

<style scoped>
#properties-panel {
  width: 40%;
  max-width: 70%;
  right: 0px;
  top: 10%;
  overflow: auto;
  z-index: 600;
  position: absolute;
  scroll-behavior: auto;
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