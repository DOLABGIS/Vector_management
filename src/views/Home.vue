<template>
<v-app  >
	<div id="olmap" ref="olmap" style="width: 100%; height: 100%;">
		<!-- <panel>
		</panel> -->
		<div  id="info-box" >
			
		<!-- <download  v-if="true" id='downfile'>> </download> -->
		<openfile v-if="isShow" id='openfile'></openfile>
		<v-card tile class="layer-panel" color="#4a5064" draggable="true">
			<div class="layer-panel-title">
			<span>图层</span>
			</div>
			<v-divider></v-divider>
			<div class="layer-panel-toolbar">
			<v-toolbar flat color="#4a5064" dense height="40">
				<div class="layer-panel-toolbar-btns">
					<el-tooltip class="item" effect="dark" content="显示" placement="bottom-start">
						<v-btn x-small icon :disabled="enableVisible" @click="setVisibility" >
							<v-icon>{{ isVisible ? "mdi-eye-off" : "mdi-eye"}}</v-icon>
						</v-btn>
					</el-tooltip>
					<el-tooltip class="item" effect="dark" content="删除" placement="bottom-start">
						<v-btn x-small icon :disabled="enableDelete" @click="deleteLayer">
							<v-icon>mdi-delete-outline</v-icon>
						</v-btn>
					</el-tooltip>
					<el-tooltip class="item" effect="dark" content="选择" placement="bottom-start">
						<v-btn x-small icon @click="switchSelectionMode">
							<v-icon>{{ enableSelect ? "mdi-cursor-default-outline" : "mdi-cursor-default" }}</v-icon>
						</v-btn>
					</el-tooltip>
					<el-tooltip class="item" effect="dark" content="属性" placement="bottom-start">
						<v-btn x-small icon @click="switchQueryMode">
							<v-icon>{{ enableQuery ? "mdi-database-search-outline" : "mdi-database-search" }}</v-icon>
						</v-btn>
					</el-tooltip>
					<el-tooltip class="item" effect="dark" content="查询" placement="bottom-start">
						<v-btn x-small icon @click="querysql">
							<v-icon>{{"mdi-magnify"}}</v-icon>
						</v-btn>
					</el-tooltip>
					<el-tooltip class="item" effect="dark" content="下载" placement="bottom-start">
						<v-btn x-small icon @click="downloadshp">
							<v-icon>{{ "mdi-download"  }}</v-icon>
						</v-btn>
					</el-tooltip>
				<v-btn x-small icon>
					<v-icon>mdi-filter</v-icon>
				</v-btn>
				</div>
				<v-divider vertical></v-divider>
				<div class="layer-panel-toolbar-layer-info">
				<v-btn text x-small>{{visibleLayerNumber}}/{{layerNumber}} <v-icon x-small>mdi-filter</v-icon></v-btn>
				</div>
			</v-toolbar>
			<v-divider></v-divider>
			</div>
			<div class="layer-panel-layers">
			<v-list dense  color="#4a5064" >
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
		<el-row :gutter="20">
			<el-col :span="6">
				<div class="grid-content bg-purple"></div>
			</el-col>
			<el-col :span="6" :offset="6">
				<div class="grid-content bg-purple"></div>
			</el-col>
		</el-row>
		<el-select class="mapselect" v-model="value" placeholder="切换地图底图" @change="changeBaseMap(value)">
			<el-option-group v-for="group in options" :key="group.label" :label="group.label">
				<el-option
					v-for="item in group.options"
					:key="item.value"
					:label="item.label"
					:value="item.value"
				></el-option>
			</el-option-group>
		</el-select>

		<el-select class="geometryType" v-model="value1" placeholder="选择绘制类型" @change="selectGeometry(value1)">
            <el-option
                v-for="item in geometryType"
                :key="item.value"
                :label="item.label"
                :value="item.value"
            ></el-option>
		</el-select>
		<el-select class="algorithmType" v-model="value2" placeholder="多边形算法" @change="selectalgrithm(value2)">
            <el-option
                v-for="item in algorithmType"
                :key="item.value"
                :label="item.label"
                :value="item.value"
            ></el-option>
		</el-select>
		<el-row class="opebutton">
			<el-button type="primary" @click="startDraw()">开始绘制</el-button>
			<el-button type="endDraw" @click="endDraw()">结束绘制</el-button>
			<el-button type="saveDraw" @click="saveDraw()">保存绘制</el-button>
			<el-button type="delectDraw" @click="delectDraw()">删除绘制</el-button>
			<el-button type="danger" @click="editDraw()">编辑绘制</el-button>
		</el-row>
		<!-- <testpanel :visible="isPropertiesPanelVisible" :properties="selectedFeatureProperties" :titles="title"></testpanel> -->
		<propertiPanel   :visible="isPropertiesPanelVisible"
                                  :properties="selectedFeatureProperties"
								  :titles="title"></propertiPanel>
		<!-- <el-checkbox class="isedit" v-model="checked">启用WFS编辑</el-checkbox> -->

	</div>
	</v-app>
</template>

<script>
import Map from 'ol/Map'
import View from 'ol/View'
import { Draw, Modify, Snap, Select,DragBox} from 'ol/interaction'
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer'
import { OSM, TileArcGISRest, Vector as VectorSource } from 'ol/source'
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style'
import XYZ from 'ol/source/XYZ'
import { transform } from 'ol/proj'
import mapSources from './OpenLayers/modules/maplist'
import propertiPanel from './OpenLayers/PropertiesPanel.vue'
import testpanel from './OpenLayers/testpanel.vue'
import Bus from '../assets/bus'
import GeoJSON from "ol/format/GeoJSON"
import shortid from 'shortid'
import jsondata from '../../src/assets/data/wuhan.json'
import axios from 'axios'
import Openfile from './upload.vue'
import download from './download.vue'
import {getArea, getLength} from 'ol/sphere';
import {platformModifierKeyOnly} from 'ol/events/condition';
// import panel from '../panel.vue'
export default {
	components: {propertiPanel,testpanel,Openfile,download},
	data() {
		return {
			checked: false,
			openDataSourceDialog:true,
			isShow:false,
			layerName: "",
			selectedItem: 0,
      		items: [],
			geometryType: [
				{
					value: 'Point',
					label: 'Point'
				},
				{
					value: 'LineString',
					label: 'LineString'
				},
				{
					value: 'Polygon',
					label: 'Polygon'
				},
				{
					value: 'Circle',
					label: 'Circle'
				}
			],
			algorithmType:[
				{
					value:'Convexity',
					label:'多边形凹凸性'
				},
				{
					value:'getposition',
					label:'点与多边形关系'
				},
				{
					value:'isvalid',
					label:'多边形是否自相交'
				},
				{
					value:'Area',
					label:'多边形面积'
				}
			],
			options: mapSources.basemapLabel,
			value: '',
			value1: '',
			value2:'',
			googledz: mapSources.googledz,
			googledx: mapSources.googledx,
			googlewx: mapSources.googlewx,
			tdtdz: mapSources.tdtdz,
			tdtlabeldz: mapSources.tdtlabeldz,
			tdtwx: mapSources.tdtwx,
			tdtlabelwx: mapSources.tdtlabelwx,
			baidudz: mapSources.baidudz,
			baiduwx: mapSources.baiduwx,
			baidulabelwx: mapSources.baidulabelwx,
			gaodedz: mapSources.gaodedz,
			gaodewx: mapSources.gaodewx,
			gaodelabelwx: mapSources.gaodelabelwx,
			qqmapdz: mapSources.qqmapdz,
			qqmapdx: mapSources.qqmapdx,
			qqmaplabledx: mapSources.qqmaplabledx,
			qqmapwx: mapSources.qqmapwx,
			qqmaplablewx: mapSources.qqmaplablewx,
			geoqcs: mapSources.geoqcs,
			geoqns: mapSources.geoqns,
			geoqhs: mapSources.geoqhs,
			geoqlh: mapSources.geoqlh,
			proj: 'EPSG:4326', //定义wgs84地图坐标系
			proj_m: 'EPSG:3857', //定义墨卡托地图坐标系
			map: null,
			mapLayer: null,
			mapLayerlabel: null,
			source: null,
			vector: null,
			draw: null,
			snap: null,
			singleClickSelect: undefined,
			layerNumber: 0,
      		visibleLayerNumber: 0,
			isPropertiesPanelVisible: false,
			selectedFeatureProperties: [],
			addedFeatures: [],
      		modifiedFeatures: {},
			selectedtype:'Polygon',
			selectedalgorithm:'',
			enableAddData: false,
			enableEdit: false,
			enableVisible: false,
			isVisible: false,
			isEditable: false,
			enableDelete: false,
			enableSelect: false,
			enableQuery: false,
			openDataSourceDialog: false,
			saveEditingDialog: false,
			properties:null,
			title:null,
			vectorla:null,
			propertylayer:null,
			querylayer:null
		}
	},
	created() {
		Bus.$on('send',(val)=>{
				this.isShow = val

			})
		Bus.$on('download',(val)=>{
			// $refs.file.click();
			})	
		Bus.$on('geojson',(val)=>{
			var vectorlayer  = new VectorLayer({
				title:val.layername,
				source:new VectorSource({
					features: new GeoJSON().readFeatures(val.data,{
    					featureProjection:"EPSG:3857"
					})
				}),
				projection: this.proj_m,
				zIndex:10,
				style: new Style({
					fill: new Fill({
						color: 'rgba(30, 144, 255, 0.3)'
					}),
					stroke: new Stroke({
						color: '#1E90FF',
						width: 2
					}),
					image: new CircleStyle({
				      radius: 4,
				      fill: new Fill({
				        color: '#1E90FF',
				      }),
				    }),
				})
			})
			this.map.addLayer(vectorlayer);
			this.items = this.toList();
			}) 
		//this.createMap()
	},
	mounted() {
		this.initMap();
		Bus.$on('delete_item',(val)=>{
			this.map.getLayers().forEach(function (layer) {
			if ( layer.get('title') === val.layername) {
				// layersToRemove.push(layer);
				console.log('layer',val.data[val.layername][0]);
				layer.getSource().clear();
				var features = (new GeoJSON()).readFeatures(val.data[val.layername][0], {featureProjection:"EPSG:3857"});
				layer.getSource().addFeatures(features);
				layer.getSource().refresh()
			}
		});
			})
	},
	methods: {
		querysql(){
				this.$prompt('请输入sql语句', '提示', {
          		confirmButtonText: '确定',
          		cancelButtonText: '取消',
        		}).then(({ value }) => {

				axios.post('api/query',{'sql':value }).then((response)=>{
					if(response.data!=0){
				// 返回符合查询条件的table，格式和查询图层的属性表一样（attr_table)
					this.map.removeLayer(this.querylayer)
					this.querylayer  = new VectorLayer({
						source:new VectorSource({
						features: new GeoJSON().readFeatures(response.data.geojson,{
							featureProjection:"EPSG:3857"
						})
						}),
						projection: this.proj_m,
						zIndex:10,
						style: new Style({
						fill: new Fill({
							color: 'rgba(220, 220, 170,0.8)'
						}),
						stroke: new Stroke({
							color: 'rgba(220, 220, 170, 1)',
							width: 2
						}),
						image: new CircleStyle({
					      radius: 4,
					      fill: new Fill({
					        color: 'rgba(220, 220, 170, 1)',
					      }),
					    }),
					})
						})
				this.map.addLayer(this.querylayer);		
				console.log(response.data);
				this.isPropertiesPanelVisible = true;
				this.selectedFeatureProperties = response.data.attr_table['content']
				this.title=response.data.attr_table['title']
				this.title.push({ text: 'Actions', value: 'actions', sortable: false })
				Bus.$emit('header', this.title);
				Bus.$emit('item', this.selectedFeatureProperties);
				Bus.$emit('layername', this.items[this.selectedItem].name);						
					}

				});
        		});
		},
		downloadshp(){
                var element = document.createElement('a');
				var name =this.items[this.selectedItem].name +'.json'
				let features = this.items[this.selectedItem].layer.getSource().getFeatures()
				var newForm = new GeoJSON();
				var featColl = newForm.writeFeaturesObject(features);
				console.log(featColl);
				element.setAttribute('href', 'data:text/plain;charset=utf-8,'+encodeURIComponent(JSON.stringify(featColl)));
                element.setAttribute('download', name);
                document.body.appendChild(element);
                element.click();
				document.body.removeChild(element); //下载完成移除元素
		},
		initMap: function() {
			//初始化map对象

			this.map = new Map({
				target: 'olmap',
				projection: this.proj,
				//interactions: ol.interaction.defaults().extend([mapDragInteraction]),
				view: new View({
					center: transform(
						[114.356, 30.624],
						this.proj,
						this.proj_m
					),
					zoom: 8
				})
			})

			//初始化地图图层
			this.mapLayer = new TileLayer({
				title: "OpenStreetMap",
				source: this.tdtdz,
				projection: this.proj_m
			})
			//初始化标签图层
			this.mapLayerlabel = new TileLayer({
				title: "label",
				source: this.tdtlabeldz,
				projection: this.proj_m
			})
			this.map.addLayer(this.mapLayer)
			this.map.addLayer(this.mapLayerlabel)
			axios.get('api/initial').then(response=>{
				var layers = response.data;

				for (var item in layers)
				{
					console.log(layers[item]);
					if(layers[item].features!=null) {
						var vector_layer  = new VectorLayer({
						title:item,
						source:new VectorSource({
						features: new GeoJSON().readFeatures(layers[item],{
							featureProjection:"EPSG:3857"
						})
						}),
						projection: this.proj_m,
						zIndex:10,
						style: new Style({
						fill: new Fill({
							color: 'rgba(30, 144, 255, 0.3)'
						}),
						stroke: new Stroke({
							color: '#1E90FF',
							width: 2
						}),
						image: new CircleStyle({
					      radius: 4,
					      fill: new Fill({
					        color: '#1E90FF',
					      }),
					    }),
					})
						})
					this.map.addLayer(vector_layer)
					
					}
					else{
						var vector_layer  = new VectorLayer({
						title:item,
						source:new VectorSource(),
						projection: this.proj_m,
						zIndex:10,
						style: new Style({
						fill: new Fill({
							color: 'rgba(30, 144, 255, 0.3)'
						}),
						stroke: new Stroke({
							color: '#1E90FF',
							width: 2
						}),
						image: new CircleStyle({
					      radius: 4,
					      fill: new Fill({
					        color: '#1E90FF',
					      }),
					    }),
					})
						})
					this.map.addLayer(vector_layer)
					}
				}
//将图层加载到地图对象

			// this.map.addLayer(this.vectorla)

			let layerList = [];
			this.map.getLayers().forEach(layer => {
				layerList.push({
					name: layer.get("title"),
					layer: layer,
					visible: true,
					editable: true
				});
			});
			console.log(layerList);
			layerList.reverse();
			this.items = layerList;
			this.layerNumber = this.items.length;
    		this.visibleLayerNumber = this.items.length;

			});
			
		},
		/******************地图切换方法***************/
		changeBaseMap: function(value) {
			this.map.removeLayer(this.mapLayer)
			this.map.removeLayer(this.mapLayerlabel)
			switch (value) {
				case 'googledz':
					this.mapLayer = new TileLayer({
						source: this.googledz,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					break
				case 'googledx':
					this.mapLayer = new TileLayer({
						source: this.googledx,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					break
				case 'googlewx':
					this.mapLayer = new TileLayer({
						source: this.googlewx,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					break
				case 'tdtdz':
					this.mapLayer = new TileLayer({
						source: this.tdtdz,
						projection: this.proj
					})
					this.mapLayerlabel = new TileLayer({
						source: this.tdtlabeldz,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					this.map.addLayer(this.mapLayerlabel)
					break
				case 'tdtwx':
					this.mapLayer = new TileLayer({
						source: this.tdtwx,
						projection: this.proj
					})
					this.mapLayerlabel = new TileLayer({
						source: this.tdtlabelwx,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					this.map.addLayer(this.mapLayerlabel)
					break
				case 'gaodedz':
					this.mapLayer = new TileLayer({
						source: this.gaodedz,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					break
				case 'gaodewx':
					this.mapLayer = new TileLayer({
						source: this.gaodewx,
						projection: this.proj
					})
					this.mapLayerlabel = new TileLayer({
						source: this.gaodelabelwx,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					this.map.addLayer(this.mapLayerlabel)
					break
				case 'baidudz':
					this.mapLayer = new TileLayer({
						source: this.baidudz,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					break
				case 'baiduwx':
					this.mapLayer = new TileLayer({
						source: this.baiduwx,
						projection: this.proj
					})
					this.mapLayerlabel = new TileLayer({
						source: this.baidulabelwx,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					this.map.addLayer(this.mapLayerlabel)
					break
				case 'qqmapdz':
					this.mapLayer = new TileLayer({
						source: this.qqmapdz,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					break
				case 'qqmapdx':
					this.mapLayer = new TileLayer({
						source: this.qqmapdx,
						projection: this.proj
					})
					this.mapLayerlabel = new TileLayer({
						source: this.qqmaplabledx,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					this.map.addLayer(this.mapLayerlabel)
					break
				case 'qqmapwx':
					this.mapLayer = new TileLayer({
						source: this.qqmapwx,
						projection: this.proj
					})
					this.mapLayerlabel = new TileLayer({
						source: this.qqmaplablewx,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					this.map.addLayer(this.mapLayerlabel)
					break
				case 'geoqcs':
					this.mapLayer = new TileLayer({
						source: this.geoqcs,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					break
				case 'geoqns':
					this.mapLayer = new TileLayer({
						source: this.geoqns,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					break
				case 'geoqhs':
					this.mapLayer = new TileLayer({
						source: this.geoqhs,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					break
				case 'geoqlh':
					this.mapLayer = new TileLayer({
						source: this.geoqlh,
						projection: this.proj
					})
					this.map.addLayer(this.mapLayer)
					break
			}
		},
		/******************选择绘制类型**************/
		selectGeometry: function(value) {
			switch (value) {
				case 'Point':
					this.selectedtype ='Point';
					break
				case 'LineString':
					this.selectedtype ='LineString';
					break
				case 'Polygon':
					this.selectedtype ='Polygon';
					break
				case 'Circle':
					this.selectedtype ='Circle';
					break
			}
			console.log(this.draw);
		},
		selectalgrithm: function(value) {
			this.map.removeEventListener('singleclick');
			switch (value) {
				case 'Convexity':
					this.selectedalgorithm ='Convexity';
					break
				case 'getposition':
					this.selectedalgorithm ='getposition';
					break
				case 'isvalid':
					this.selectedalgorithm ='isvalid';
					break	
				case 'Area':
					this.selectedalgorithm ='Area';
					break
			}
			console.log(this.draw);
		},
		// modifyInteraction
		wfsEdit: function() {
			let modify = new Modify({
				source: this.source
			})
			this.map.addInteraction(modify)
		},

		addInteractions: function(value) {
			this.draw = new Draw({
				source: this.source,
				style: new Style({
					stroke: new Stroke({
						color: '#1E90FF',
						lineDash: [2,4,6,8],
						width: 2
					})
				}),
				type: value
			})
			console.log(this.draw);
			this.map.addInteraction(this.draw)
			this.snap = new Snap({
				source: this.source
			})
			this.map.addInteraction(this.snap)
		},

		selectInteraction: function(){
			let select = new Select({
				source: this.source
			})
			this.map.addInteraction(select)
		},
		// 设置图层可见性
		setVisibility() {
			console.log(this.isVisible);
			this.items[this.selectedItem].layer.setVisible(this.isVisible);
			this.items[this.selectedItem].visible = this.isVisible;
			this.isVisible = !this.isVisible;
			const visibleLayers = this.items.filter(item => item.visible === true);
			this.visibleLayerNumber = visibleLayers.length;
		},
		//删除图层
		deleteLayer() {
			console.log(this.selectedItem);

			axios.post('api/drop',{'layer':this.items[this.selectedItem].name }).then((response)=>{
					if(response.data!="0")
					{
						this.$message({
                			message: "删除成功",
                			type: "success"
              			});
					}
					else{

						this.$message({
                			message: "图层不存在",
                			type: "error"
              			});

					}				
				});
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
			// if (this.enableSelect) {
				this.enableQuery = !this.enableQuery;
				if (this.enableQuery) {
				this.enableQueryProperties();
				} else {
				this.removeQueryProperties();
				}
			// } else {
			// 	this.enableQuery = false;
			// }
		},
		enableSelection() {
			this.singleClickSelect = new Select();
			this.map.addInteraction(this.singleClickSelect);
			console.log("Enable Selection");
			if (this.singleClickSelect) {
				console.log(this.singleClickSelect);
				this.singleClickSelect.on('select', (e) => {
				if (this.selectedFeatureProperties) {
					this.selectedFeatureProperties = [];
				}
				const feature = e.selected[0];
				console.log(feature);
				if (feature) {
					console.info("Got Selected Features! ", feature)
					this.isPropertiesPanelVisible = true;
					// Object.getOwnPropertyNames(feature.getProperties()).forEach(key => {
					// key = key.toString();
					// if (key !== "geometry" && key !== "childrenNum"&& key!== "parent") {
					// 	const value = feature.getProperties()[key] || "null";
					// 	console.log(value);
					// 	this.selectedFeatureProperties[0].key = value;
					// }

					// });
					var item={};
					for (var fea in feature.values_){
						fea = fea.toString();
						if(fea!=='geometry'){
						console.log(feature.values_[fea]);

							item[fea] = feature.values_[fea];
						}
					}
					// var newfeature = feature.values_
					// delete newfeature.geometry //true
					console.log('selectedFeatureProperties',item);
					Bus.$emit('item',[item]);
				} else {
					console.warn("Nothing Selected!");
					this.isPropertiesPanelVisible = false;
				}
				});
			}
			const dragBox = new DragBox({
				condition: platformModifierKeyOnly,
				});

			this.map.addInteraction(dragBox);
			dragBox.on('boxend', (e) => {
				// features that intersect the box geometry are added to the
				// collection of selected features

				// if the view is not obliquely rotated the box geometry and
				// its extent are equalivalent so intersecting features can
				// be added directly to the collection
				const rotation = this.map.getView().getRotation();
				const oblique = rotation % (Math.PI / 2) !== 0;
				const candidateFeatures = oblique ? [] : selectedFeatures;
				const extent = dragBox.getGeometry().getExtent();
				const feature = e.selected[0];
				console.log(feature);
				// vectorSource.forEachFeatureIntersectingExtent(extent, function (feature) {
				// 	candidateFeatures.push(feature);
				// });

				// // when the view is obliquely rotated the box extent will
				// // exceed its geometry so both the box and the candidate
				// // feature geometries are rotated around a common anchor
				// // to confirm that, with the box geometry aligned with its
				// // extent, the geometries intersect
				// if (oblique) {
				// 	const anchor = [0, 0];
				// 	const geometry = dragBox.getGeometry().clone();
				// 	geometry.rotate(-rotation, anchor);
				// 	const extent = geometry.getExtent();
				// 	candidateFeatures.forEach(function (feature) {
				// 	const geometry = feature.getGeometry().clone();
				// 	geometry.rotate(-rotation, anchor);
				// 	if (geometry.intersectsExtent(extent)) {
				// 		selectedFeatures.push(feature);
				// 	}
				// 	});
				// }
				});

				// clear selection when drawing a new box and when clicking on the map
				dragBox.on('boxstart', function () {
				selectedFeatures.clear();
				});

		},
		removeSelection() {
			if (this.singleClickSelect) {
				this.map.removeInteraction(this.singleClickSelect);
			}
			console.log("Remove Selection");
			},
		enableEditing(selectedLayer, selectedLayerType = "") {
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
			// console.log(this.items[this.selectedItem].name);
			axios.post('api/attr_table',{'file_name':this.items[this.selectedItem].name}).then((response)=>{
				console.log(response.data);
				if(response.data!="0"){
				this.isPropertiesPanelVisible = true;
				this.selectedFeatureProperties = response.data['content']
				this.title=response.data['title']
				this.title.push({ text: 'Actions', value: 'actions', sortable: false })
				Bus.$emit('header', this.title);
				Bus.$emit('item', this.selectedFeatureProperties);
				Bus.$emit('layername', this.items[this.selectedItem].name);
				console.log('title',this.selectedFeatureProperties);
				}
				else{
					this.$message({
                			message: "没有属性表",
                			type: "error"
              		});
				}
			}).catch(res=>{
			this.$message({
                			message: "查询错误",
                			type: "error"
              			});
			});
			if (this.singleClickSelect) {
				console.log(this.singleClickSelect);
				this.singleClickSelect.on('select', (e) => {
				console.log('aa');
				if (this.selectedFeatureProperties) {
					this.selectedFeatureProperties = [];
				}
				console.log(e.selected);
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
		// 开始绘制
		startDraw: function() {
			if(this.draw == null){
			this.source = new VectorSource()
			this.vector = new VectorLayer({
				source: this.source,
				style: new Style({
					fill: new Fill({
						color: 'rgba(30, 144, 255, 0.3)'
					}),
					stroke: new Stroke({
						color: '#1E90FF',
						width: 2
					}),
					image: new CircleStyle({
				      radius: 4,
				      fill: new Fill({
				        color: '#1E90FF',
				      }),
				    }),
				})
			})
			this.map.addLayer(this.vector)
			this.wfsEdit()
			if(this.selectedtype=='Point'){
				this.addInteractions('Point');
				
			}
			else if(this.selectedtype=='LineString'){
				this.addInteractions('LineString');
				
			}
			else if(this.selectedtype=='Polygon'){
				this.addInteractions('Polygon');
				
			}
			else if(this.selectedtype=='Circle'){
				this.addInteractions('Circle');
				
			}
			}
			
			// this.addInteractions('Polygon')
		},
		// 结束绘制
		endDraw: function() {
			if (this.draw) {
				this.map.removeInteraction(this.draw)
				this.map.removeInteraction(this.snap)
				this.draw = null
				this.snap = null
			}
			if(this.selectedalgorithm !=''){
				if(this.selectedalgorithm=='Convexity'){
					var features = this.source.getFeatures();
					var coord = features[0].getGeometry().getCoordinates();
					console.log(coord[0]);
					axios.post('api/Convexity',{'polygon':coord[0]}).then((response)=>{
						console.log(response.data);
						if (response.data =='True' ){
							this.$message({
                			message: "凹多边形",
              			});
						}
						if (response.data =='False' ){
							this.$message({
                			message: "凸多边形",
              			});
						}
					});
				}
				if(this.selectedalgorithm=='getposition'){
					var features = this.source.getFeatures();
					var coord = features[0].getGeometry().getCoordinates();
					this.map.on('singleclick',function(evt){
						console.log(evt.coordinate);
						axios.post('api/getposition',{'polygon':coord[0],'point':evt.coordinate}).then((response)=>{
						console.log(response.data);
						if (response.data ==-1 ){
						// 	this.$message({
                		// 	message: "点在多边形上",
              			// });
						  alert("点在多边形上");
						  
						}
						else if (response.data ==1 ){
						// 	this.$message({
                		// 	message: "点在多边形外",
              			// });
						  alert("点在多边形外");

						}
						else if (response.data ==0 ){
						// 	this.$message({
                		// 	message: "点在多边形内",
              			// });
						  alert("点在多边形内");
						}
					});
					})
					
				}
				if(this.selectedalgorithm=='isvalid'){
					var features = this.source.getFeatures();
					var coord = features[0].getGeometry().getCoordinates();
					console.log(coord);
						axios.post('api/isvalid',{'polygon':coord[0]}).then((response)=>{
						console.log(response.data);
						if (response.data =='-1' ){
							this.$message({
                			message: "多边形自相交",
              			});
						//   alert("多边形自相交");
						}
						else if (response.data =='1' ){
							this.$message({
                			message: "多边形有效",
              			});
						//   alert("多边形有效");
						}
					})
					
				}
				if(this.selectedalgorithm=='Area'){
					var features = this.source.getFeatures();
					var coord = features[0].getGeometry().getCoordinates();
					console.log(getArea(features[0].getGeometry()));
					axios.post('api/cal_polygonarea',{'polygon':coord[0]}).then((response)=>{
						console.log(response.data['area']);
						this.$message({
                			message: '多边形面积为：'+response.data['area']+'平方公里',
              			});
					});
				}
			}
		},
		// 保存绘制
		saveDraw: function() {
			if (this.draw) {
				this.map.removeInteraction(this.draw)
				this.map.removeInteraction(this.snap)
				this.draw = null
				this.snap = null
			}
			if (this.vector) {
				this.$prompt('请输入图层名', '提示', {
          		confirmButtonText: '确定',
          		cancelButtonText: '取消',
        		}).then(({ value }) => {

					this.map.removeLayer(this.vector)
         			this.layerName = value;
					this.vector.values_.title =value;
					this.map.addLayer(this.vector);
					this.items = this.toList();
					this.endDraw();
					let features = this.source.getFeatures()
					var newForm = new GeoJSON();
					console.log(features);
					// let trans_feature = []
					// if (features.length > 0) {
					// 	for (var j = 0; j < features.length; j++) {
					// 		// 将3857坐标转换为4326坐标
					// 		let geo = features[j].getGeometry().transform(this.proj_m, this.proj)
					// 		trans_feature.push(geo);
					// 	}
					// }
					// console.log('trans',features);
					var featColl = newForm.writeFeaturesObject(features);
					axios.post('api/uploadgeojson',{'data':featColl,'name':this.layerName }).then((response)=>{
						// if(response.data=='1'){
						// this.$message({
                		// 	message: "保存成功",
                		// 	type: "success"
              			// });
						// }
						// else if(response.data=='0'){
						// this.$message({
                		// 	message: "图层名重复",
                		// 	type: "error"
              			// });
						// }
					});
        		});

			}
			this.draw = null
			this.snap = null
		},
		// 删除绘制
		delectDraw: function() {
			if (this.draw) {
				this.map.removeInteraction(this.draw)
				this.map.removeInteraction(this.snap)
			}
			if (this.vector) {
				this.vector.getSource().clear()
				this.map.removeLayer(this.vector)
			}
			this.draw = null
			this.snap = null	
		},
		// 编辑绘制
		editDraw: function(){
			this.map.removeInteraction(this.draw)
			this.draw = null
			this.selectInteraction()
		},
		toList() {
			let layerList = [];
			console.log('tolist');
			this.map.getLayers().forEach(layer => {
				layerList.push({
					name: layer.get("title"),
					layer: layer,
					visible: true,
					editable: true
				});
			});
			layerList.reverse();
			console.log(layerList);
			return layerList;
			}
	},
	watch:{
		selectedItem: {
			handler(newValue) {
				this.isVisible = !this.items[newValue].visible;
			},
			deep: true
    },
	selectedtype: function(newVal, oldVal) {
			if(this.draw){
            this.endDraw();
			this.addInteractions(newVal);

			}
        }
	}
}
</script>

<style scoped>
#olmap {
	position: relative;
	z-index: 1;
	width: 500px;
}
.mapselect {
	position: absolute;
	top: 3%;
	right: 2%;
	z-index: 2;
}
.geometryType {
	position: absolute;
	top: 3%;
	left: 10%;
	z-index: 2;
	width:150px;
}
.algorithmType {
	position: absolute;
	top: 3%;
	left: 22%;
	z-index: 2;
	width:150px;
}
.opebutton {
	position: absolute;
	top: 3%;
	right: 20%;
	z-index: 2;
}
.isedit {
	position: absolute;
	top: 4%;
	right: 30%;
	z-index: 2;
}

.layer-panel {
	position: absolute;
	top: 15%;
	left: 10%;
	height: 40%;
	z-index: 1000;
	overflow: auto;
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

.layer-panel-toolbar {
  width: 100%;
}

.layer-panel-toolbar-btns {
  float: left;
  width: 190px;
  display: flex;
  justify-content: space-around;
}

.layer-panel-toolbar-layer-info {
  width: 66px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.layer-panel-layers {
  overflow: auto;
  width: 100%;
  height: calc(100% - 82px);
}
</style>
