/**
 * Component for the logic in 'Identify Route' mode
 */
import { React } from 'react';
import axios from "axios";
import Button from 'react-bootstrap/Button';
import { DropdownList } from "react-widgets";

import RouteOrRailButtons from './RouteOrRailButtons';

let prevstart = 'Select known CCS project as start location'
let prevend = 'Select known CCS project as destination location'
let a = true;
const LIME_OPTIONS = { color: 'lime' }
const PURPLE_OPTIONS = { color: 'purple' }
let shptyp = ''
let ccsSitesLarge = [
{ id: [39.87, -88.89], name: 'Illinois Industrial Carbon Capture and Storage Project'},
{ id: [45, -85], name: 'MRCSP Development Phase - Michigan Basin Project' },
{ id: [35, -98], name: 'PurdySho-Vel-Tum EOR Project'},
{ id: [30, -101], name: 'Val Verde NG Plants'},
{ id: [39.863, -88.913], name: 'Illinois Industrial Carbon Capture and Storage'},
{ id: [37.106767, -100.7977], name: 'Arkalon'},
{ id: [37.959112, -100.83676], name: 'Bonanza BioEnergy'},
{ id: [37.047329, -95.604094], name: 'Coffeyville Plant'},
{ id: [45.113, -84.652], name: 'Core Energy CO2-EOR'},
{ id: [46.8839, -102.3157], name: 'Red Trail'},
{ id: [36.378636, -97.762739], name: 'Enid Fertilizer'},
{ id: [29.866, -93.967], name: 'Air Products Port Arthur Facility'},
{ id: [30.3718, -101.8449], name: 'Terrell Gas Processing'},
{ id: [31.009, -88.025], name: 'SECARB Development Phase - Citronelle Project'},
{ id: [37.536, -105.104], name: 'Oakdale NG Processing'},
{ id: [40.530, -89.682], name: 'NRG Powerton Station'},
{ id: [38.272, -89.668], name: 'Prairie State Energy Campus'},
{ id: [37.046, -95.604], name: 'CO2 Capture from Coffeyville Fertilizer Plant'},
{ id: [37.7903, -84.7144], name: 'EW Brown Generating Station'},
{ id: [39.594529, -78.745292], name: 'AES Warrior Run'},
{ id: [42.0916, -71.48352], name: 'Bellingham Cogeneration Facility'},
{ id: [47.3727, -101.15679], name: 'Great River Energy'},
{ id: [40.90214, -82.03784], name: 'Touchstone Bioconversion Pilot Plant'},
{ id: [36.37858, -97.76379], name: 'Purdy Sho-Vel-Tum EOR Project'},
{ id: [29.86493, -93.966697], name: 'Air Products and Chemicals Inc. CCS Project'},
{ id: [31, -103], name: 'Century Plant Gas Processing'},
{ id: [33.216456, -97.772382], name: 'Mitchell Energy Bridgeport Plant'},
{ id: [29.47678, -95.637769], name: 'W.A. Parish Post-Combustion CO2 Capture and Sequestration Project'},
{ id: [39.501027, -112.581819], name: 'Intermountain Power Agency'},
{ id: [42.535541, -87.903483], name: 'We Energies Pleasant Prairie Field Pilot'},
{ id: [35.760591, -117.379211], name: 'Searles Valley Minerals'},
{ id: [41.88568, -110.0926], name: 'Shute Creek Plant'},
{ id: [30.692226, -88.042569], name: 'Fuel Cell Carbon Capture Pilot Plant'},
{ id: [31.01124, -88.024597], name: 'Linde/BASF FEED'},
{ id: [33.2343, -86.4836], name: 'National Carbon Capture Center (NCCC)'},
{ id: [33.417905, -111.928358], name: 'Center for Negative Carbon Emissions'},
{ id: [35.27444, -119.32301], name: 'Elk Hills CCS'},
{ id: [37.510632, -121.997288], name: 'Membrane Technology & Research, Inc.'},
{ id: [37.458009, -122.175774], name: 'SRI International Post-combustion Sorbent'},
{ id: [39.79121, -105.137092], name: 'TDA Research Post-combustion'},
{ id: [39.791215, -105.136744], name: 'TDA Research Pre-combustion'},
{ id: [31.006474, -88.008697], name: 'Gas Technology Institute'},
{ id: [40.116306, -88.243522], name: 'Linde/Illinois'},
{ id: [38.24935, -89.75296], name: 'Prairie State Generating Station CCS'},
{ id: [37.106778, -100.799611], name: 'Arkalon Bioethanol'},
{ id: [37.958806, -100.836556], name: 'Bonanza Bioethanol'},
{ id: [37.050663, -95.604763], name: 'Coffeyville Fertilizer'},
{ id: [38.03501, -84.504821], name: 'University of Kentucky Center for Applied Energy Research'},
{ id: [38.03501, -84.504821], name: 'University of Kentucky Research Foundation'},
{ id: [30.218533, -91.052119], name: 'PCS Nitrogen'},
{ id: [39.594529, -78.745292], name: 'Warrior Run'},
{ id: [45.1, -84.65], name: 'Core Energy'},
{ id: [41.0809508, -101.1433768], name: 'Gerald Gentleman Coal Power Plant'},
{ id: [40.764619, -73.971056], name: 'Global Thermostat'},
{ id: [40.71217, -74.007155], name: 'Infinitree'},
{ id: [35.905909, -78.863898], name: 'Research Triangle Institute'},
{ id: [47.11495, -101.1725], name: 'Project Tundra'},
{ id: [47.9198, -97.0605], name: 'University of North Dakota Energy and Environmental Research Center'},
{ id: [35.194006, -94.646982], name: 'Shady Point'},
{ id: [29.865806, -93.967361], name: 'Air Products Steam Methane Reformer'},
{ id: [30.608764, -102.57876], name: 'Century Plant'},
{ id: [29.646611, -95.055917], name: 'NET Power'},
{ id: [33.63559, -96.60902], name: 'Panda Energy Fund'},
{ id: [29.477964, -95.635209], name: 'Petra Nova'},
{ id: [29.477964, -95.635209], name: 'Petra Nova'},
{ id: [32.972554, -102.74361], name: 'University of Texas'},
{ id: [44.388212, -105.459617], name: 'Dry Fork Power Plant CCS'},
{ id: [43.280518, -107.6022], name: 'Lost Cabin'},
{ id: [44.388212, -105.45961], name: 'Wyoming Integrated Test Center'},
{ id: [47.361953, -101.838103], name: 'Great Plains Synfuel Plant'},
];
let ccsSitesSmall = [
{ id: [39.87, -88.89], name: 'Illinois Industrial Carbon Capture and Storage Project'},
{ id: [43, -106], name: 'LINC Energy - Wyoming EOR'},
{ id: [45, -85], name: 'MRCSP Development Phase - Michigan Basin Project' },
{ id: [35, -98], name: 'PurdySho-Vel-Tum EOR Project'},
{ id: [40, -109], name: 'Rangely-Webber EOR'},
{ id: [42, -109], name: 'Salt CreekMonellSussex Unit EOR'},
{ id: [36, -101], name: 'SWP Development Phase - Farnsworth Unit Ochiltree Project'},
{ id: [30, -101], name: 'Val Verde NG Plants'},
{ id: [31, -102], name: 'Yates Oil Field EOR Operations'},
];

function StartEndButtons( {location, setLocation} ){

  const onOptionChange = e => {
    setLocation(e.target.value)
    console.log(location)
  }
    return(
      <div>
      <input type="radio" 
      name="location" 
      value="start" 
      id="start" 
      checked={location === "start"} 
      onChange={onOptionChange}
      />
      <label htmlFor="start">Start</label>

      <input type="radio" 
      name="location" 
      value="end" 
      id="end" 
      checked={location === "end"} 
      onChange={onOptionChange}
      />
      <label htmlFor="end">End</label>
      </div>
    )
}

function StartEndDetails( {value1, setValue1, value2, setValue2, 
  setShowloc, setEndloc, srcLat, 
  srcLon, destLat, destLon, setUpdateSrcLat, 
  setupdateSrcLon, setupdateDestLat, setupdateDestLon, setSrcLat, setSrcLon, setDestLat, setDestLon,
  setStartMarkerRenderCoords, setDestMarkerRenderCoords,
  setStartCoords, setDestCoords,
  start,
  end, laststart, lastend
  } ){

  // Dropdown component for start point
  function DropdownStart() {
    laststart = 1
    function onChange(ccsSite){
      setStartMarkerRenderCoords(ccsSite.id)
      setValue1(ccsSite)
      setStartCoords(ccsSite.id)
    }
    return (
      <DropdownList
        containerClassName='dropdown'
        data={ccsSitesLarge}
        datakey = 'id'
        textField='name'
        value={value1}
        onChange={onChange}
      />
    )
  }

  // Dropdown component for end point
  function DropdownEnd() {
    lastend = 1
    function onChange(ccsSite){
      setDestMarkerRenderCoords(ccsSite.id)
      debugger;
      setValue2(ccsSite)
      setDestCoords(ccsSite.id)
    }
    return (
      <DropdownList
        containerClassName='dropdown'
        data={ccsSitesSmall}
        datakey = 'id'
        textField='name'
        value={value2}
        onChange={onChange}
      />
    )
  }

  // Handler for clicking on the map to set the Start marker
  const saveStartBtnClick = () => {
    console.log('Save Start clicked')
    laststart = 0
    let stlat = Number(srcLat)
    let stlon = Number(srcLon)

    let pt2 = "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat="+stlat+"&lon="+stlon;

    axios({
      method: "GET",
      url: pt2,
    })

    .then((response) => {

      let pointAddress = response.data['address']
      // error catch for 200 from serer (resopnse, not error) but error is contained in response
      if(response.data.error){
        console.error('Bad response from axios request with start data with Lat ' + stlat + ' and Lon ' + stlon)
        console.error(response.data.error)
      } else {
        console.log(response.data)
      }
      // if invalid point
      if((pointAddress === undefined) || (pointAddress["state"] === "Hawaii") || (pointAddress["country"] !== "United States")){
        // brings up the 'select a valid point in the US' modal
        setShowloc(true)
      // if valid point
      }else{

        // State for checking that both points are in the same landmass
        if(pointAddress['state'] === "Alaska"){
          setEndloc('Alaska')
        }else{
          setEndloc('US')
        }
        setUpdateSrcLat(srcLat)
        setupdateSrcLon(srcLon)

        const newStartCoords = [Number(srcLat), Number(srcLon)]
        console.log(newStartCoords)
        setStartMarkerRenderCoords(newStartCoords)
        // 'start' and 'end' are the data actually send to the backend
        setStartCoords([Number(srcLat), Number(srcLon)])
        start[0] = Number(srcLat)
        start[1] = Number(srcLon)
      }

    }).catch((error) => {
      if (error.response) {
        console.log(error.response)
        console.log(error.response.status)
        console.log(error.response.headers)
        }
    })
  }

  // Handler for setting the End/Dest point by clicking on the map
  const saveDestBtnClick = () =>{
    lastend = 0
    let dtlat = Number(destLat)
    let dtlon = Number(destLon)

    let pt3 = "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat="+dtlat+"&lon="+dtlon;

    axios({
      method: "GET",
      url: pt3,
    })
    .then((response) => {
      let enddata = response.data['address']

      if((enddata === undefined) || (enddata["state"] === "Hawaii") || (enddata["country"] !== "United States")){
        setShowloc(true)

      }else{

        // State for checking that both points are in the same landmass
        if(enddata['state'] === "Alaska"){
          setEndloc('Alaska')
        }else{
          setEndloc('US')
        }
        setupdateDestLat(destLat)
        setupdateDestLon(destLon)
        // 'start' and 'end' are the data actually send to the backend
        end[0] = Number(destLat)
        end[1] = Number(destLon)
        const newDestCoords = [Number(destLat), Number(destLon)]
        console.log(newDestCoords)
        setDestMarkerRenderCoords(newDestCoords)
        setDestCoords([Number(destLat), Number(destLon)])

      }

    }).catch((error) => {
      if (error.response) {
        console.log(error.response)
        console.log(error.response.status)
        console.log(error.response.headers)
        }
    })
  }

  const handleChangeSrcLat = (event) =>{
    setSrcLat(event.target.value)
  }

  const handleChangeSrcLon = (event) =>{
    setSrcLon(event.target.value)
  }

  const handleChangeDestLat = (event) => {
    setDestLat(event.target.value)
  }

  const handleChangeDestLon = (event) => {
    setDestLon(event.target.value)
  }

return(
    <div>
    <div>
        <h4>Add Start Location in World Geodetic System WGS 1984 (WGS 84)</h4>
        <p> 
        Latitude:   <input type="number" name="myInput1"  onChange={handleChangeSrcLat} value={srcLat}/> 
        Longitude:  <input type="number" name="myInput2"  onChange={handleChangeSrcLon} value={srcLon}/>  
        <Button size="sm" onClick={saveStartBtnClick}> Save Start </Button >                      
        </p> 
        <div><DropdownStart/></div>
    </div>

    <div>
        <h4>Add End Location in WGS84</h4>
        <p> 
        Latitude:   <input type="number" name="myInput3" onChange={handleChangeDestLat} value={destLat}/> 
        Longitude:  <input type="number" name="myInput4" onChange={handleChangeDestLon} value={destLon}/>
        <Button size="sm"  onClick={saveDestBtnClick}> Save Destination </Button >            
        </p>
        <div><DropdownEnd/></div>
    </div>
    </div>
)
}

export default function IdMode( {location, setLocation, value1, setValue1, value2, 
  setValue2, setShowLoc, setEndLoc, setBtnGroupState, 
  btntxt1, btntxt2, toolMode, srcLat, srcLon, destLat, 
  destLon, setUpdateSrcLat, setupdateSrcLon, setupdateDestLat, 
  setupdateDestLon, setSrcLat, setSrcLon, setDestLat, setDestLon,
  setStartMarkerRenderCoords, start, end, laststart, lastend,
  setStartCoords, setDestCoords, setDestMarkerRenderCoords} ){
    return(
        <div>
            <RouteOrRailButtons setBtnGroupState={setBtnGroupState} btntxt1={btntxt1} btntxt2={btntxt2} toolMode={toolMode}/>
            <StartEndButtons location={location} setLocation={setLocation}/>
            <StartEndDetails 
              value1={value1} setValue1={setValue1} 
              value2={value2} setValue2={setValue2} 
              srcLat={ srcLat } setSrcLat={ setSrcLat }
              setShowloc={setShowLoc} setEndloc={setEndLoc}
              srcLon={srcLon} setSrcLon={setSrcLon} 
              destLat={destLat} setDestLat={ setDestLat }
              destLon={destLon} setDestLon={setDestLon} 
              setUpdateSrcLat={setUpdateSrcLat} 
              setupdateSrcLon={setupdateSrcLon} 
              setupdateDestLat={setupdateDestLat} 
              setupdateDestLon={setupdateDestLon} 
              setStartMarkerRenderCoords = { setStartMarkerRenderCoords }
              setDestMarkerRenderCoords = { setDestMarkerRenderCoords }
              start={start}
              end={end}
              laststart={ laststart } lastend={ lastend }
              setStartCoords={ setStartCoords } setDestCoords = { setDestCoords }
            />
            <br></br>
        </div>
    )
}