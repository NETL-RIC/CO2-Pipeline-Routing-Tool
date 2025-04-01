/*
    04/01/2025 
    UI for non-devs to test different vector tile layers, used at the end of EY24 mainly by Cat and Lucy.
    Currently not in the tool, but could be useful in the future.

    To re-enable, Vector...Wrapper will need to be instantiated inside the MapContainer component in App.js, as well as
    Vector...TestInputs will need to be instantiated anywhere inside the main UI section of App.js, like above <MainModeButtons/> for example

*/

import { React, useState } from 'react';
import VectorTileLayer from "react-esri-leaflet/plugins/VectorTileLayer";

export function VectorTileLayerTestWrapper( tileLayer, showTileLayer ) {
        return showTileLayer ?
        <VectorTileLayer 
          url={tileLayer}
        /> : null
  }

export function VectorTileLayerTestInputs ( tileLayer, setTileLayer, showTileLayer, setShowTileLayer, showLayerChecked, setShowLayerChecked ){
  function LayerButtons() {
    function handleTileLayer(){
      showTileLayer ? setShowTileLayer(false) : setShowTileLayer(true);
      !showTileLayer ? setShowTileLayer(true) : setShowTileLayer(false);
      setShowLayerChecked(!showLayerChecked);
    }
    return (
      <div>
        <input type="checkbox"
        checked={showLayerChecked}
        name="tile-layer"
        id="tile-layer-on"
        value="on"
        disabled={tileLayer===null}
        onChange={handleTileLayer}/>

        <label htmlFor="tile-layer-on">Show/Hide Tile Layer</label>
      </div>
    );
  }

  function LayerInput(){
    const [inputValue, setInputValue] = useState(null)

    function saveLayer(e){
      e.preventDefault();
      if (inputValue !== null){
        setTileLayer(inputValue)
      }
    }

    function resetLayer(){
      setTileLayer(null);
      // also hide the tile layer because the url will be null 
      setShowTileLayer(false);
      setShowLayerChecked(false);
    }

    const mystyle = {
      padding: "10px",
    }

    return(
      <div style={mystyle}>
        <label>
          Enter tile layer URL: <input name="layerInput" onChange={(e) => setInputValue(e.target.value)} />
        </label>
        <button onClick={saveLayer}>Save to Variable</button>
        <button onClick={resetLayer}>Clear Variable and Hide Tile Layer</button>
      </div>
    )
  }

  return(
    <>
        <LayerInput/>
        <LayerButtons tileLayer={ tileLayer }/>
    </>
  )
}

