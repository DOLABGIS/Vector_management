<template>
	<div id="map">
    <select-layer class="mapselect" :map="map"></select-layer>
    <openfile v-if="isShow" id='openfile'></openfile>
   <div  id="info-box" >
		<v-card tile class="quarkgis-layer-panel" color="#4a5064">
			<div class="quarkgis-layer-panel-title">
			<span>Layers</span>
			</div>
			<v-divider></v-divider>
			<div class="quarkgis-layer-panel-toolbar">
			<v-toolbar flat color="#4a5064" dense height="40">
				<div class="quarkgis-layer-panel-toolbar-btns">


				<v-btn x-small icon :disabled="enableVisible" @click="setVisibility">
					<v-icon>{{ isVisible ? "mdi-eye-off" : "mdi-eye"}}</v-icon>
				</v-btn>
				<v-btn x-small icon :disabled="enableDelete" @click="deleteLayer">
					<v-icon>mdi-delete-outline</v-icon>
				</v-btn>
				<v-btn x-small icon @click="switchSelectionMode">
					<v-icon>{{ enableSelect ? "mdi-cursor-default-outline" : "mdi-cursor-default" }}</v-icon>
				</v-btn>
				<v-btn x-small icon @click="switchQueryMode">
					<v-icon>{{ enableQuery ? "mdi-database-search-outline" : "mdi-database-search" }}</v-icon>
				</v-btn>
				<v-btn x-small icon>
					<v-icon>mdi-filter</v-icon>
				</v-btn>
				</div>
				<v-divider vertical></v-divider>
				<div class="quarkgis-layer-panel-toolbar-layer-info">
				<v-btn text x-small>{{visibleLayerNumber}}/{{layerNumber}} <v-icon x-small>mdi-filter</v-icon></v-btn>
				</div>
			</v-toolbar>
			<v-divider></v-divider>
			</div>
			<div class="quarkgis-layer-panel-layers">
			<v-list dense>
				<v-list-item-group
					v-model="selectedItem"
					color="primary"
				>
				<v-list-item
					v-for="(item, i) in items"
					:key="i"
					color="primary"
				>
					<v-list-item-icon>
					<v-icon>mdi-layers</v-icon>
					</v-list-item-icon>
					<v-list-item-content>
					<v-list-item-title v-text="item.name"></v-list-item-title>
					</v-list-item-content>
				</v-list-item>
				</v-list-item-group>
			</v-list>
			</div>
		</v-card>
		</div>
		<el-row class="opebutton">
			<el-button type="primary" @click="drawPolygon()">绘制区域</el-button>
			<el-button type="primary" @click="drawPoint()">绘制中心点</el-button>
			<el-button type="danger" @click="delectDraw()">删除绘制</el-button>
            <el-button type="saveDraw" @click="saveDraw()">保存绘制</el-button>
		</el-row>
	</div>
</template>
<script>
import mapBoxGl from 'mapbox-gl'
import {
	CircleMode,
	DragCircleMode,
	DirectMode,
	SimpleSelectMode
} from 'mapbox-gl-draw-circle'
import MapboxDraw from '@mapbox/mapbox-gl-draw'
import 'mapbox-gl/dist/mapbox-gl.css'
import SelectLayer from '../components/MapBox/SelectLayer'
import turf from 'turf'
import mapSources from './MapBox/modules/mapstyles'
import Openfile from './upload.vue'
import axios from 'axios';
import Bus from '../assets/bus'
import { MapboxExportControl, Size, PageOrientation, Format, DPI} from "@watergis/mapbox-gl-export";
import '@watergis/mapbox-gl-export/css/styles.css';
export default {
	data() {
		return {
            isShow:false,
            map: null,
            draw: null,
            layer:[],
            enableAddData: false,
            enableEdit: false,
            enableVisible: false,
            isVisible: 'none',
            isEditable: false,
            enableDelete: false,
            enableSelect: true,
            enableQuery: false,
            openDataSourceDialog: false,
            saveEditingDialog: false,
            tab: null,
            databases: ["PostgreSql", "SQL Server", "MySQL", "ORACLE"],
            webServiceType: ["WMTS", "WMS", "WFS"],
            serverType: ["carmentaserver", "geoserver", "mapserver", "qgis"],
            layerName: "",
            selectedWebService: "",
            webServiceUrl: "",
            selectedServerType: "geoserver",
            timeout: 1000,
            snackbar: false,
            text: "",
            color: "teal",
            wmsLayers: "",
            wmtsLayer: "0",
            selectedItem: 0,
            items: [],
            userFiles: ["All"],
            selectedUserLayer: "",
            geometryType: ["Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", "MultiPolygon", "GeometryCollection"],
            layerFields: [],
            fieldName: "",
            dataType: ["integer", "double", "character varying(255)"],
            selectedDataType: "",
            newLayerName: "",
            selectedGeometryType: "",
            layerNumber: 0,
            visibleLayerNumber: 0,
            singleClickSelect: undefined,
            modify: undefined,
            draw: undefined,
            snap: undefined,
            isPropertiesPanelVisible: false,
            selectedFeatureProperties: [],
            addedFeatures: [],
            modifiedFeatures: {}
		}
	},
  components: {
		'select-layer': SelectLayer,
		'Openfile': Openfile,
    },
	created() {
     Bus.$on('send',(val)=>{
            this.isShow = val

        })
      Bus.$on('geojson',(val)=>{
        this.layer.push(val)
        // this.init(val);
        this.upload(val);      
        })  
  },
	mounted() {
		this.init(false)
	},
	methods: {
		init() {
			mapBoxGl.accessToken =
				'pk.eyJ1IjoibWFwYm94bWF4IiwiYSI6ImNqbnY4MHM3azA2ZmkzdnBnMThvNzRoZ28ifQ.IffqPZGkhcdPjnZ2dmSO6w'
			this.map = new mapBoxGl.Map({
				container: 'map',
				style: {
					version: 8,
					glyphs: 'mapbox://fonts/mapbox/{fontstack}/{range}.pbf',
					sources: {
						source_tdtvec_tiles:
							mapSources.baseMapUrl.source_tdtvec_tiles,
						source_tdtcva_tiles:
							mapSources.baseMapUrl.source_tdtcva_tiles
					},
					layers: [
						mapSources.baseLayerConfig.tdtvec_tiles,
						mapSources.baseLayerConfig.tdtcva_tiles
					]
				},
				center: [114.356, 30.624],
				zoom: 8,
				minZoom: 5,
				maxZoom: 17
				// pitch: 40,
				// bearing: 1
			})

      this.items= this.toList();
      // console.log(this.items);
			this.map.addControl(new mapBoxGl.NavigationControl(), 'top-right')
			this.map.addControl(
				new mapBoxGl.ScaleControl({ maxWidth: 80, unit: 'metric' }),
				'bottom-right'
			)
			this.map.addControl(
				new mapBoxGl.FullscreenControl({
					container: document.querySelector('map')
				}),
				'top-right'
			)
// create control with specified options
      this.map.addControl(new MapboxExportControl({
          PageSize: Size.A3,
          PageOrientation: PageOrientation.Portrait,
          Format: Format.PNG,
          DPI: DPI[96],
          Crosshair: true,
          PrintableArea: true
      }), 'top-right');
			this.draw = new MapboxDraw({
				displayControlsDefault: false,
				controls: {
					polygon: true,
					point: true,
					trash: true
				}
			})

			this.map.addControl(this.draw)
      //       this.map.on('draw.update', this.updateArea)
      // this.map.on('draw.create', this.updateArea);
      // this.map.on('draw.delete', this.updateArea);
        },
    upload(val){
    axios.get('api/uploadshp').then((response)=>{
        var polys=response.data;
        console.log(response.data);
        this.map.on('load',() => {
          this.map.addLayer({
            'id': val,
            'type': 'fill',
            'source': {
              'type':'geojson',
              'data':polys
            },
            'layout': {},
            'paint': {
            'fill-color': '#088',
            'fill-opacity': 0.8
          }
          });
        console.log('fis',this.map.getStyle());
        });
      });
      this.toList();
    },
    toList() {
			let layerList = [];
      this.map.on('load', () => {
        // console.log(this.map.getStyle());
			this.map.getStyle().layers.forEach(layer => {
				layerList.push({
					name: layer['id'],
					layer: layer,
					visible: true,
					editable: true
				});
			});
      });
			layerList.reverse();
			console.log(layerList);
			return layerList;
			},
      // 设置图层可见性
		setVisibility() {
      const visibility = this.map.getLayoutProperty(
        this.items[this.selectedItem].layer.id,
        'visibility'
        ); 

      if(visibility=='visibility'){
        this.map.setLayoutProperty(this.items[this.selectedItem].layer.id,'visibility','none');
        this.items[this.selectedItem].visible = 'none';
      }
      else{
        this.map.setLayoutProperty(this.items[this.selectedItem].layer.id,'visibility','visibility');
        this.items[this.selectedItem].visible = 'visibility';
      }
			const visibleLayers = this.items.filter(item => item.visible === 'visibility');
			this.visibleLayerNumber = visibleLayers.length;
		},
		//删除图层
		deleteLayer() {
			this.map.removeLayer(this.items[this.selectedItem].layer);
			this.items.splice(this.selectedItem, 1);
			this.refreshItems();
		},
		refreshItems() {
			this.items = this.map.toList();
			this.layerNumber = this.items.length;
			this.visibleLayerNumber = this.items.length;
		},
		switchSelectionMode() {
			this.enableSelect = !this.enableSelect;
			console.log("Selection Mode - ", this.enableSelect);
			if (this.enableSelect) {
				this.enableSelection();
			} else {
				this.removeSelection();
			}
		},
		//切换查询模式
		switchQueryMode() {
			if (this.enableSelect) {
				this.enableQuery = !this.enableQuery;
				if (this.enableQuery) {
				this.$refs.MapComponent.enableQueryProperties();
				} else {
				this.$refs.MapComponent.removeQueryProperties();
				}
			} else {
				this.enableQuery = false;
			}
		},
		enableSelection() {
			this.singleClickSelect = new Select();
			this.map.addInteraction(this.singleClickSelect);
			console.log("Enable Selection");
		},
		removeSelection() {
			if (this.singleClickSelect) {
				this.map.removeInteraction(this.singleClickSelect);
			}
			console.log("Remove Selection");
		},
		enableEditing(selectedLayer, selectedLayerType = "") {
			// if (this.singleClickSelect) {
			//   this.modify = new Modify({
			//     features: this.singleClickSelect.getFeatures()
			//   });
			//   this.map.addInteraction(this.modify);
			// }
			let vectorSource = selectedLayer.getSource();
			this.modify = new Modify({
				features: this.singleClickSelect.getFeatures()
			});
			this.map.addInteraction(this.modify);
			this.modify.on("modifyend", (e) => {
				let feature = e.features.item(0).clone();
				let id = feature.getProperties()["id"];
				console.log(feature.getProperties());
				this.modifiedFeatures[id] = feature;
				console.info("modified features: ", this.modifiedFeatures);
			});
			let geomType = "";
			if (selectedLayer.getSource().getFeatures()[0] !== undefined) {
				const geometry =  selectedLayer.getSource().getFeatures()[0].getGeometry();
				geomType = geometry.constructor.name;
			}  else {
				geomType = selectedLayerType;
			}

			console.info(geomType);
			this.draw = new Draw({
				source: vectorSource,
				type: geomType
			});
			this.map.addInteraction(this.draw);
			this.draw.on("drawend", (e) => {
				this.addedFeatures.push(e.feature);
			});
			this.snap = new Snap({
				source: vectorSource
			});
			this.map.addInteraction(this.snap);
			console.log("Enable Editing");
		},
		saveEditingAutomaticallyByTimeInterval() {
		// TODO
		},
		saveEditing(modifiedLayerName, modifiedLayerObject) {
		let features = modifiedLayerObject.getSource().getFeatures();
		console.log("modified layername ", modifiedLayerName, " geometry number: ", features.length, " features: ", features);
		const data = new GeoJSON().writeFeaturesObject(features, {
			featureProjection: getProjection("EPSG:3857")
		});
		console.info("generated geojson ", data);
		this.$postJson(`/data/postTrueJson?filename=${modifiedLayerName}&apikey=${getLocalStorage("jwt_token")}`, data).then(() => {
			console.info("Save Data Successfully!");
		}).catch(() => {
			console.warn("Error: Fail to save data.")
		});
		// this.$postJson(`/postgis/insertJDBC?table=${modifiedLayerName}`, data).then(() => {
		//   console.info("Save Data Successfully!");
		// }).catch(() => {
		//   console.warn("Error: Fail to save data.")
		// });
		},
		saveAddEditing(modifiedLayerName) {
		console.info(this.addedFeatures);
		if (this.addedFeatures.length > 0) {
			const addedData = new GeoJSON().writeFeaturesObject(this.addedFeatures, {
			featureProjection: getProjection("EPSG:3857")
			});
			const features = {
			"features": addedData["features"]
			}
			console.info(features);
			this.$postJson(`/postgis/insertJDBC?table=${modifiedLayerName}`, features).then(() => {
			console.info("Save Data Successfully!");
			}).catch(() => {
			console.warn("Error: Fail to save data.")
			});
		}
		console.log("modified features number: ", Object.keys(this.modifiedFeatures).length);
		if (Object.keys(this.modifiedFeatures).length > 0) {
			Object.keys(this.modifiedFeatures).forEach((id) => {
			const modifiedData = this.modifiedFeatures[id].getProperties();
			delete modifiedData.id;
			delete modifiedData.geometry;
			const modifiedGeometry = new GeoJSON().writeGeometryObject(this.modifiedFeatures[id].getGeometry(), {
				featureProjection: getProjection("EPSG:3857")
			});
			modifiedData["geometry"] = modifiedGeometry;
			console.info(JSON.stringify(modifiedData));
			this.$postJson(`/postgis/updateJDBC?table=${modifiedLayerName}&where=id=${id}`, modifiedData).then(() => {
				console.info("Save Data Successfully!");
			}).catch(() => {
				console.warn("Error: Fail to save data.")
			});
			})
			this.modifiedFeatures = {};
		}
		},
		removeEditing() {
		if (this.modify) {
			this.map.removeInteraction(this.modify);
		}
		if (this.draw) {
			this.map.removeInteraction(this.draw);
		}
		if (this.snap) {
			this.map.removeInteraction(this.snap);
		}
		console.log("Remove Editing");
		},
		enableQueryProperties() {
		console.info("Enable Query");
		if (this.singleClickSelect) {
			this.singleClickSelect.on('select', (e) => {
			if (this.selectedFeatureProperties) {
				this.selectedFeatureProperties = [];
			}
			const feature = e.selected[0];
			if (feature) {
				console.info("Got Selected Features! ", feature)
				this.isPropertiesPanelVisible = true;
				Object.getOwnPropertyNames(feature.getProperties()).forEach(key => {
				key = key.toString();
				if (key !== "geometry") {
					const value = feature.getProperties()[key] || "null";
					this.selectedFeatureProperties.push({
					id: shortid(),
					name: key,
					value: value
					});
				}
				});
			} else {
				console.warn("Nothing Selected!");
				this.isPropertiesPanelVisible = false;
			}
			});
		}
		},
		removeQueryProperties() {
		console.info("Remove Query Properties")
		this.isPropertiesPanelVisible = false;
		},
        // 开始绘制区域
		drawPolygon: function() {
            this.draw.changeMode('draw_polygon');
        },
        // 标记中心点
        drawPoint: function(){
            this.draw.changeMode('draw_point');
        },
        // 删除
        delectDraw: function(){
            this.draw.deleteAll()
        },
            updateArea (e) {
      this.rawArea = null;
      var featureNum = this.mapOptions.draw.getAll().features.length;
      if (featureNum === 0) {
        this.positions = [];
      } else  {
        if(this.mapOptions.draw.getAll().features.length) {
            
            for(var i=0;i<this.mapOptions.draw.getAll().features.length;i++){
          let geometry = this.mapOptions.draw.getAll().features[i].geometry
          switch(geometry.type) {
            case 'Point':
              this.markers.position = [{lng: geometry.coordinates[0], lat: geometry.coordinates[1]}];
              break;
            case 'LineString':
              this.positions = geometry.coordinates.map(p => ({lng: p[0], lat: p[1]}));
              break;
            case 'Polygon':
              if(geometry.coordinates.length) {
                let temp = geometry.coordinates[0];
                this.polygons = temp.map(p => ({lng: p[0], lat: p[1]})).filter((_, i) => temp.length - 1 != i);
              } else {
                 this.polygons  = [];
              }
              break;
            default:
              break;
          }}
        } else {
          this.positions = [];
        }
      } 
    },
	},
  watch:{
      positions: function () {
      this.mapOptions.draw.deleteAll();
      const drawId = 'calculate-polygon';
      if (this.positions.length === 0) {
        return;
      } else if (this.positions.length === 1) {
        this.mapOptions.draw.add({ 
          id: drawId,
          type: 'Feature',
          properties: {},
          geometry: { type: 'Point', coordinates: [this.positions[0].lng, this.positions[0].lat] }
        })
      } else if (this.positions.length === 2) {
        this.mapOptions.draw.add({ 
          id: drawId,
          type: 'Feature',
          properties: {},
          geometry: { type: 'LineString', coordinates: this.positions.map(p => [p.lng, p.lat]) }
        }) 
      } else {
        this.mapOptions.draw.add({ 
          id: drawId,
          type: 'Feature',
          properties: {},
          geometry: { type: 'Polygon', coordinates: [
            [...this.positions.map(p => [p.lng, p.lat]), [this.positions[0].lng, this.positions[0].lat]]
          ] }
        });
        this.rawArea = Math.round(turf.area(this.mapOptions.draw.getAll()) * 100) / 100;
      }
    },
    a:{
    handler:function(val){
      // console.log(val);
    }
  }
  },
  computed: {
 
}
}
</script>

<style scoped>
/* @import url('https://api.mapbox.com/mapbox-gl-js/v1.9.1/mapbox-gl.css'); */
@import url('https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-draw/v1.0.9/mapbox-gl-draw.css');
#map {
	/* position: absolute; */
	left: 0;
	top: 0;
	text-align: left;
	width: 100%;
	height: 100%;
    cursor: ne-resize
}

.opebutton {
	position: absolute;
	top: 3%;
	right: 20%;
	z-index: 2;
}
.quarkgis-layer-panel {
	position: absolute;
	top: 15%;
	left: 10%;
	height: 40%;
	z-index: 1000;
	overflow: auto;
}

.quarkgis-layer-panel-title {
  height: 40px;
  width: 100%;
  line-height: 40px;
  font-weight: bold;
}

.quarkgis-layer-panel-title > span {
  margin-left: 15px;
  color: #fff;
}

.quarkgis-layer-panel-toolbar {
  width: 100%;
}

.quarkgis-layer-panel-toolbar-btns {
  float: left;
  width: 190px;
  display: flex;
  justify-content: space-around;
}

.quarkgis-layer-panel-toolbar-layer-info {
  width: 66px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quarkgis-layer-panel-layers {
  overflow: auto;
  width: 100%;
  height: calc(100% - 82px);
}
</style>