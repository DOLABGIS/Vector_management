<template>
	<div id="map">
    <select-layer class="mapselect" :map="map"></select-layer>
    <openfile v-if="isShow" id='openfile'></openfile>
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
        this.init(val);
              
        })  
  },
	mounted() {
		this.init(false)
	},
	methods: {
		init(a) {
			mapBoxGl.accessToken =
				'pk.eyJ1IjoibWFwYm94bWF4IiwiYSI6ImNqbnY4MHM3azA2ZmkzdnBnMThvNzRoZ28ifQ.IffqPZGkhcdPjnZ2dmSO6w'
			this.map = new mapBoxGl.Map({
				container: 'map',
				style: {
					version: 8,
					// "glyphs": "../../static/fonts/{fontstack}/{range}.pbf", // 本地化字体
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
      if(a!=false){
            axios.get('api/uploadshp').then((response)=>{
        var polys=response.data;
         
        console.log(polys);
        this.map.on('load',() => {
          this.map.addLayer({
            'id': a,
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
        });
      });
      }
			// map.addControl(new this.mbgl.GeolocateControl({ positionOptions: { enableHighAccuracy: true }, trackUserLocation: true }), 'top-left');
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
    upload(){
    axios.get('api/uploadshp').then((response)=>{
        var polys=response.data;
         
        console.log(response.data);
        this.map.on('load',() => {
          this.map.addLayer({
            'id': 'objectlayer',
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
        });
      });
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
</style>