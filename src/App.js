import { React, useState, useEffect } from 'react';
import { DropdownList } from "react-widgets";
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, ScaleControl, Polyline, Polygon } from "react-leaflet";
import { FeatureLayer} from "react-esri-leaflet";
import VectorTileLayer from "react-esri-leaflet/plugins/VectorTileLayer";
import { Icon } from "leaflet";
import { Link } from 'react-router-dom';
import axios from "axios";
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';

import MainToolModeButtons from "./components/MainToolModeButtons"
import IdMode from './components/IdMode';
import EvalMode from './components/EvalMode';

import netlLogo from "./NETL_Square_GREEN_E.png";
import doeLogo from "./DOE_Logo_Color.png";
import discoverLogo from "./discover.jpg";
import bilLogo from "./BIL.png"

global.Buffer = require('buffer').Buffer;

// visualizes Id mode line


let zip_file = ''
let pdf_file = ''
let start = [0,0]
let laststart = -999
let lastend = -999  
let end = [0,0]
let prevstart = 'Select known CCS project as start location'
let prevend = 'Select known CCS project as destination location'
let a = true;
const LIME_OPTIONS = { color: 'lime' }
const PURPLE_OPTIONS = { color: 'purple' }
let shptyp = ''

export default function MyApp(){

  const [evalModePolygon, setEvalModePolygon] = useState([])
  const [idModePolygon, setIdModePolygon] = useState([])

  const [srcLat, setSrcLat] = useState('')
  const [srcLon, setSrcLon] = useState('')
  const [destLat, setDestLat] = useState('')
  const [destLon, setDestLon] = useState('')
  const [updateSrcLat, setUpdateSrcLat] = useState(srcLat)
  const [updateSrcLon, setupdateSrcLon] = useState(srcLon)
  const [updateDestLat, setupdateDestLat] = useState(destLat)
  const [updateDestLon, setupdateDestLon] = useState(destLon)
  const [show, setShowloc] = useState(false);
  const [endloc, setEndloc] = useState('')
  const [value1, setValue1] = useState('Select known CCS project as start location')
  const [value2, setValue2] = useState('Select known CCS project as destination location')
  const [isLoadingIdMode, setIsLoadingIdMode] = useState(false)
  const [isLoadingEvalMode, setIsLoadingEvalMode] = useState(false)
  const [finished2, setFinished2] = useState('')
  const [pipeshow, setpipeloc] = useState(false);
  const [finished, setFinished] = useState('')
  const [showServerError, setShowServerError] = useState(false);
  const [location, setLocation] = useState("")
  const [files, setFiles] = useState([]);
  const [startloc, setStartloc] = useState('')
  const [idMode, setIdMode] = useState("route")
  const [uploaz, setUploaz] = useState("points")
  const [showTileLayer, setShowTileLayer] = useState(false);
  const [tileLayer, setTileLayer] = useState(null)
  const [showLayerChecked, setShowLayerChecked] = useState(false);
  const customIcon1 = new Icon({
    iconUrl: "https://cdn-icons-png.flaticon.com/512/447/447031.png",
    iconSize: [30,30]
  })
  const customIcon2 = new Icon({
    iconUrl: require("./placeholder.png"),
    iconSize: [30,30]
  })

  
  // 'Evaluate' button (handleMultipleSubmit() formerly)
  function evaluateCorridor(event) {
    event.preventDefault();
    setFinished2(false)
    setIsLoadingEvalMode(true)
    setIsLoadingIdMode(false)
    let urlfile = ''
    const formData = new FormData();
    files.forEach((file, index) => {
      formData.append(`file${index}`, file);
    });
    
    if (global.electronmode === true){
      urlfile = "http://127.0.0.1:5000/uploads"
    }else{
      urlfile = "/uploads"
    }
    axios
    .post(urlfile, formData)
    .then((response) => {
      setEvalModePolygon(response.data['array'])
      shptyp = response.data['typ']
      pdf_file = response.data['pdf']
      console.log(response)
      console.log(response.data)
      setFinished2(true)
      setIsLoadingEvalMode(false)

    })
    .catch((err) => {
      setIsLoadingEvalMode(false)
      console.warn(err)
    });
  }


  // 'Generate Pipeline' button (sendData() formerly)
  function generatePipeline() {

    setFinished(false);
    setIsLoadingIdMode(true);
    setIsLoadingEvalMode(false);
    let urlpipe = ''

    if ((endloc !== startloc) && (endloc !== '' && startloc !== '')){
      setpipeloc(true);

    }else{
    if(global.electronmode === true){
      urlpipe = "http://127.0.0.1:5000/token"
      
    }
    else{
      urlpipe = "/token"
      
    }
    axios({
      method: "POST",
      url: urlpipe, 
      data: {s: start, e:end, mode:idMode}
    })

    .then((response) => {
      setIdModePolygon(response.data['route'])
      zip_file = response.data['zip']
      console.log("Got line data");
      setFinished(true);
      setIsLoadingIdMode(false);

    }).catch((error) => {
      if (error.response) {
        console.log("Error with Generate Pipeline. Points are invalid or other logic error.");
        console.log(error.response);
        console.log(error.response.status);
        console.log(error.response.headers);
        }
        setIsLoadingIdMode(false);
        setShowServerError(true);
    })
  }
  }

  function openDocs(){
    /// THIS VERSION IS FOR ELECTRON BUILD AS SOMETHING IS BLOCKING NEW WINDOWS

    let urldoc = ''

    if(global.electronmode === true){
      urldoc = 'http://127.0.0.1:5000/help'
    }else{
      urldoc = '/help'
    }
    axios({
      method: "POST",

      url: urldoc,

    })
    .catch((error) => {
      if (error.response) {
        console.log("Error requesting help documentation");
      }
    });

    /// THIS VERSION CAN BE USED FOR DEVELOPMENT
    //  console.log("trying documentation open")
    //  window.open("documentation/_build/html/index.html", "helpWindow", "noreferrer")
  }

  function handleDownload(extension) {
    let url_dl = ''
    if(global.electronmode === true){
      url_dl = 'http://127.0.0.1:5000/download_report'
    } else {
      url_dl = '/download_report'
    }
    // const response = await axios.post(url_dl, { extension }, { responseType: 'blob' });
    
    axios({
      method: "POST",
      url: url_dl,
      responseType:'blob',
      data: { extension: extension }
    })
    .then((response) => {

      const url = window.URL.createObjectURL(response.data);
      const a = document.createElement('a');
      a.href = url;
      
      let fname = 'report_results';
      const contentDisposition = response.headers.get('Content-Disposition');
      if (contentDisposition && contentDisposition.indexOf('filename') > -1)
      {
        fname = contentDisposition.split('filename=')[1].split(';')[0].trim().replace(/"/g,"");
      }
      a.download = fname;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    })
    .catch((error) => {
      if (error.response) {
        console.log("Error downloading file");
      }
    });

  };

  function handlePDFDownload() {
    handleDownload('.pdf');
  }
  
  function handleZIPDownload() {
     handleDownload('.zip');
  }

  function DisclaimerPopup() {
    const [showz, setShow] = useState(a);
    a = false;
    const handleClose = () => setShow(a);

      return (
        <>
          <Modal
            dialogClassName="dis-modal"
            show={showz}
            onHide={handleClose}
            backdrop="static"
            keyboard={false}
          >
            <Modal.Header >
              <Modal.Title></Modal.Title>
                <img src={discoverLogo}  width={120} height={50} alt='Discover Logo' />
                <img src={bilLogo} alt='BIL Logo' />
                <img src={netlLogo} width={50} height={50}  alt='NETL Logo' />
                <img src={doeLogo}  alt='DOE Logo' />
            </Modal.Header>
            <div id="disTitle" className="modal-body">
              <label id="disTitleText">
                Disclaimer
              </label>
            </div>
            <Modal.Body>
            This project was funded by the United States Department of Energy, 
            National Energy Technology Laboratory, in part, through a site 
            support contract. Neither the United States Government nor any 
            agency thereof, nor any of their employees, nor the support contractor, 
            nor any of their employees, makes any warranty, express or implied, 
            or assumes any legal liability or responsibility for the accuracy,
             completeness, or usefulness of any information, apparatus, product, 
             or process disclosed, or represents that its use would not infringe 
             privately owned rights.  Reference herein to any specific commercial 
             product, process, or service by trade name, trademark, manufacturer, 
             or otherwise does not necessarily constitute or imply its endorsement, 
             recommendation, or favoring by the United States Government or any agency 
             thereof. The views and opinions of authors expressed herein do not necessarily
              state or reflect those of the United States Government or any agency thereof.
              Parts of this technical effort were performed in support of the National Energy 
            Technology Laboratory's ongoing research under the Energy Data eXchange for 
            Carbon Capture and Storage (EDX4CCS) Field Work Proposal 1025007 by 
            NETL's Research and Innovation Center, including work performed by Leidos
             Research Support Team staff under the RSS contract 326663.00.0.2.00.00.2050.033.0.
            </Modal.Body>
            <Modal.Footer>
              <Button onClick={handleClose}>Understood</Button>
            </Modal.Footer>
          </Modal>
        </>
      );
  }

  // The loading message that apperas when the backend is generating after 'Generate Pipeline' in ID Mode
  function LoadingMessageIdMode() {
    if (isLoadingIdMode) {
      return(
        <>
          <Modal
            show={isLoadingIdMode}
            backdrop="static"
            keyboard={false}
            aria-labelledby="contained-modal-title-vcenter"
          centered
          >
            <Modal.Header>
              <Modal.Title>Loading...</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              Optimizing pipeline corridor, this may take several minutes. Please do not close the webpage, or your progress will be lost.
            </Modal.Body>
            <Modal.Footer>
              This notification will close automatically when optimization has concluded. 
            </Modal.Footer>
          </Modal>
        </>
      );
    }
  }

  // The loading message that apperas when the backend is generating after 'Evaluate' in Eval Mode
  function LoadingMessageEvalMode() {
    if (isLoadingEvalMode) {
      return(
        <>
          <Modal
            show={isLoadingEvalMode}
            backdrop="static"
            keyboard={false}
            aria-labelledby="contained-modal-title-vcenter"
          centered
          >
            <Modal.Header>
              <Modal.Title>Loading...</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              Evaluating uploaded corridor, this may take several minutes. Please do not close the webpage, or your progress will be lost.
            </Modal.Body>
            <Modal.Footer>
              This notification will close automatically when evaluation has concluded. 
            </Modal.Footer>
          </Modal>
        </>
      );
    }
  }

  // Catch-all for invalid points, bad logic issues, etc. In the future should have more specific messages for different server errors
  function ServerErrorPopup(){
    const handleClose = () => setShowServerError(false);
    return(
      <>
        <Modal
          show={showServerError}
          onHide={handleClose}
          backdrop="static"
          keyboard={false}
          aria-labelledby="contained-modal-title-vcenter"
        centered
        >
          <Modal.Header>
            <Modal.Title>Server Error</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            An invalid point location may have been selected, the server may not have been started, or a different server error has occured.
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={handleClose}>Understood</Button>
          </Modal.Footer>
        </Modal>
      </>
    );
  }
    
  // Single selected point is outside of US or AK
  function InvalidLocationPopup() {

    const handleClose = () => setShowloc(false);

    return (
      <>

        <Modal
          show={show}
          onHide={handleClose}
          backdrop="static"
          keyboard={false}
          aria-labelledby="contained-modal-title-vcenter"
        centered
        >
          <Modal.Header>
            <Modal.Title>Invalid Location!</Modal.Title>
          </Modal.Header>
          <Modal.Body>
          Please select a point within the USA or Alaska.
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={handleClose}>Understood</Button>
          </Modal.Footer>
        </Modal>
      </>
    );    
  }
  
  // Both selected points are in different landmasses (US or AK)
  function InvalidPipeline() {
    const handleClose = () => setpipeloc(false);

    return (
      <>
        <Modal
          show={pipeshow}
          onHide={handleClose}
          backdrop="static"
          keyboard={false}
          aria-labelledby="contained-modal-title-vcenter"
        centered
        >
          <Modal.Header>
            <Modal.Title>Invalid Pipeline!</Modal.Title>
          </Modal.Header>
          <Modal.Body>
          Start and end locations must be both in Alaska or both in continental USA.
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={handleClose}>Understood</Button>
          </Modal.Footer>
        </Modal>
      </>
    );    
  }


  // Displays pipeline onto map from ID Mode output
  function ShowIdModeLine(){
    if (finished){
    console.log("Returning line data as Polyline for map")
    console.log("Line array in front end: ")
    console.log(idModePolygon)
    return <Polyline pathOptions={LIME_OPTIONS} positions={idModePolygon} />
    }
  }

  // Displays line or polygon onto map from Eval Mode output
  function ShowEvalModeShape(){
    if (finished2){
      if (shptyp === 'Polygon'){
        return <Polygon pathOptions={PURPLE_OPTIONS} positions={evalModePolygon} />
      }
      else if (shptyp === 'LineString'){
        return <Polyline pathOptions={PURPLE_OPTIONS} positions={evalModePolygon} />
      }
    }
  }

  // creates "are you sure" dialogue box on page refresh
  useEffect(() => {
    window.addEventListener("beforeunload", alertUser);
    return () => {
      window.removeEventListener("beforeunload", alertUser);
    };
  }, []);
  const alertUser = (e) => {
    e.preventDefault();
    e.returnValue = "";
  }


  function handleMultipleChange(event) {
    setFiles([...event.target.files]);
  } 


  // Handle START point click

  //----------------------------------------------SUPPORTING COMPONENTS----------------------------
  // Marker point component
  const StartMarkers = () => {

    if (prevstart !== value1  && laststart === 1){
      prevstart = value1
      laststart = 1
      start[0] = value1['id'][0]
      start[1] = value1['id'][1]
    }

    const initialMarkers= [0,0]
    const [markers, setMarkers] = useState(initialMarkers);
  
    const map = useMapEvents({
      click(e) {
        if(uploaz==="points"){if (location ==='start'){
        let s1 =  e.latlng['lat']
        let s2 = e.latlng['lng']

        let pt = "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat="+s1+"&lon="+s2;
        

        axios({
          method: "GET",
          url: pt,
        })

        .then((response) => {

          let startdata = response.data['address']
          console.log(startdata)

          if((startdata === undefined) ||(startdata["state"] === "Hawaii") || (startdata["country"] !== "United States")){
            setShowloc(true)

          // Need logic to check for NoGo zone... currently just handled by backend serving a general server error
            
          }else{
            if(startdata['state'] === "Alaska"){
              console.log('a')
              setStartloc('Alaska')
            }else{
              setStartloc('US')
              console.log('b')
            }
            
            console.log(startloc)
            console.log(endloc)
            
            
            start[0] = e.latlng['lat']
            start[1] = e.latlng['lng']
            markers.push(e.latlng);
            setMarkers((prevValue) => [...prevValue, e.latlng]);
        }

        }).catch((error) => {
          if (error.response) {
            console.log(error.response)
            console.log(error.response.status)
            console.log(error.response.headers)
            }
        })
        }}
      }
    })
    
    if (uploaz==="points"){
    return (
      <Marker position={[start[0], start[1]]} icon={customIcon1}>
        <Popup>Start Location ({(start[0].toFixed(6))}, {start[1].toFixed(6)})</Popup>
      </Marker>
    ) 
    } else if(uploaz==="upld"){
      return (
        <Marker position={[0, 0]} icon={customIcon1}>
          <Popup>Start Location ({(0)}, {0})</Popup>
        </Marker>
      ) 
    }
  }

  // Marker point component
  const EndMarkers = () => {
   
    if (prevend !== value2 && lastend === 1){
      prevend = value2
      lastend = 1
      end[0] = value2['id'][0]
      end[1] = value2['id'][1]
    }

    const endMarkers= [0,0]
    const [emarkers, seteMarkers] = useState(endMarkers);
  
    const maps = useMapEvents({
      click(f) {
        if(uploaz==="points"){if (location === 'end'){
        let e1 =  f.latlng['lat']
        let e2 = f.latlng['lng']

        let pt2 = "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat="+e1+"&lon="+e2;
       
        axios({
          method: "GET",
          url: pt2,
        })
        .then((response) => {
          let enddata = response.data['address']


          if((enddata === undefined) || (enddata["state"] === "Hawaii") || (enddata["country"] !== "United States")){
            setShowloc(true)

          }else{

            if(enddata['state'] === "Alaska"){
              setEndloc('Alaska')
            }else{
              setEndloc('US')
            }
            
            end[0] = f.latlng['lat']
            end[1] = f.latlng['lng']
            emarkers.push(f.latlng);
            seteMarkers((prevValue) => [...prevValue, f.latlng]);
          
          }
    
        }).catch((error) => {
          if (error.response) {
            console.log(error.response)
            console.log(error.response.status)
            console.log(error.response.headers)
            }
        })
        }}
      }
    })

    if(uploaz === "points"){
    return (
      <Marker position={[end[0], end[1]]} icon={customIcon2}>
        <Popup>End Location ({(end[0].toFixed(6))}, {end[1].toFixed(6)})</Popup>
      </Marker>
    )
    }
    else if(uploaz === "uploads"){
      return (
      <Marker position={[0,0]} icon={customIcon2}>
        <Popup>End Location ({(0)}, {0})</Popup>
      </Marker>
    )}

  }

  function GenAndDownloadButtons() {
    return(
      <div>
        <p>
          <Button id="submit-btn" type="button" onClick={generatePipeline}> Generate Pipeline </Button>
        </p>

        <p>
          <Button onClick={handleZIPDownload}>
            <i className="fas fa-download"/>
            Download Report and Shapefile
          </Button>
        </p>
        <br/>
      </div>
    )
  }

  // ---------------------------------------MAIN COMPONENTS------------------------------------
  const Header = () => {
    return (
      <div className="header">
        <img src={netlLogo} width={50} height={50}  alt='NETL Logo' />
        <img src={doeLogo}  alt='DOE Logo' />
        <img src={discoverLogo}  width={120} height={50} alt='Discover Logo' />
        <h1>Smart CO2 Transport-Routing Tool</h1>
        <div id="docButton">
            <Button onClick={openDocs}>
              Help Documentation
            </Button>
        </div>
      </div>
    );
  };

  function VectorTileLayerWrapper() {
        return showTileLayer ?
        <VectorTileLayer 
          url={tileLayer}
        /> : null
  }


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

  /* default layer */

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


  // Footer node
  function Footer() {
    return (
      <p>
      <img src={bilLogo} alt='BIL Logo' />
      <Link to="https://www.netl.doe.gov/home/disclaimer">Disclaimer</Link>
      </p>
    )
  }


  return(
    <div>
      {/* Utility components */}
      {/*Initial popup */}
      <DisclaimerPopup/>

      {/*Hidden by default popups*/}
      <InvalidLocationPopup/>
      <ServerErrorPopup/>
      <InvalidPipeline/>
      <LoadingMessageEvalMode/>
      <LoadingMessageIdMode/>

      {/*Regular page*/}
      <Header/>

      <MapContainer center={[39.8283, -98.5795]} zoom={5}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <VectorTileLayerWrapper tileLayer={tileLayer}/>
        <StartMarkers/>
        <EndMarkers/>
        <ScaleControl position="bottomright" />
        <ShowIdModeLine/>
        <ShowEvalModeShape/>
      </MapContainer>

      <LayerInput/>
      <LayerButtons tileLayer={tileLayer}/>
      <MainToolModeButtons setBtnGroupState={setUploaz} btntxt1={"Identify Route"} btntxt2={"Evaluate Corridor"} setEvalModePolygon={setEvalModePolygon} setIdModePolygon={setIdModePolygon}/>
      {uploaz === 'points' ? 
      <IdMode 
      location={location} 
      setLocation={setLocation} 
      value1={value1} 
      setValue1={setValue1} 
      value2={value2} 
      setValue2={setValue2} setShowLoc={setShowloc} setEndLoc={setEndloc} setBtnGroupState={setIdMode} 
      btntxt1={"Pipeline Mode"} btntxt2={"Railway Mode"} toolMode={uploaz} 
      srcLat={srcLat} srcLon={srcLon} destLat={destLat} destLon={destLon} setUpdateSrcLat={setUpdateSrcLat} 
      setupdateSrcLon={setupdateSrcLon} setupdateDestLat={setupdateDestLat} setupdateDestLon={setupdateDestLon} 
      setSrcLat={setSrcLat} setSrcLon={setSrcLon} setDestLat={setDestLat} setDestLon={setDestLon}
      /> : null }

      {uploaz==='points' ? 
      <GenAndDownloadButtons
      /> : null}

      {uploaz === 'upld' ? 
      <EvalMode
      evaluateCorridor={evaluateCorridor} handleMultipleChange={handleMultipleChange} handlePDFDownload={handlePDFDownload}
      /> : null}
      <Footer/>
    </div>
  )
}