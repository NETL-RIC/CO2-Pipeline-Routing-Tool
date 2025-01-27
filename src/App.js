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

import netlLogo from "./NETL_Square_GREEN_E.png";
import doeLogo from "./DOE_Logo_Color.png";
import discoverLogo from "./discover.jpg";
import bilLogo from "./BIL.png"

global.Buffer = require('buffer').Buffer;

// visualizes Id mode line
let linevals = []

// visualizes Evalulate mode polygon
let shpvals = []

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

  const customIcon1 = new Icon({
    iconUrl: "https://cdn-icons-png.flaticon.com/512/447/447031.png",
    iconSize: [30,30]
  })

  const customIcon2 = new Icon({
    iconUrl: require("./placeholder.png"),
    iconSize: [30,30]
  })

  const [isLoadingIdMode, setIsLoadingIdMode] = useState(false)
  const [isLoadingEvalMode, setIsLoadingEvalMode] = useState(false)
  const [finished2, setFinished2] = useState('')
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
      shpvals = response.data['array']
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

  const [pipeshow, setpipeloc] = useState(false);
  const [finished, setFinished] = useState('')
  const [showServerError, setShowServerError] = useState(false);
  const [endloc, setEndloc] = useState('')

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
      linevals = response.data['route']
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
      urldoc = 'http://127.00.1:5000/help'
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
     console.log("trying documentation open")
     window.open("documentation/_build/html/index.html", "helpWindow", "noreferrer")
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
  function ShowPipeline(){
    if (finished){
    console.log("Returning line data as Polyline for map")
    console.log("Line array in front end: ")
    console.log(linevals)
    return <Polyline pathOptions={LIME_OPTIONS} positions={linevals} />
    }
  }

  // Displays line or polygon onto map from Eval Mode output
  function Showshp(){
    if (finished2){
      if (shptyp === 'Polygon'){
        return <Polygon pathOptions={PURPLE_OPTIONS} positions={shpvals} />
      }
      else if (shptyp === 'LineString'){
        return <Polyline pathOptions={PURPLE_OPTIONS} positions={shpvals} />
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


  const [location, setLocation] = useState("")
  const onOptionChange = e => {
    setLocation(e.target.value)
    console.log(location)
  }

  const [files, setFiles] = useState([]);
  function handleMultipleChange(event) {
    setFiles([...event.target.files]);
  } 

  const [show, setShowloc] = useState(false);
  const [srcLat, setSrcLat] = useState('')
  const [srcLon, setSrcLon] = useState('')
  const [updateSrcLat, setUpdateSrcLat] = useState(srcLat)
  const [updateSrcLon, setupdateSrcLon] = useState(srcLon)
  // Handle START point click
  const HandleClick1 = () => {
    laststart = 0
    let stlat = Number(srcLat)
    let stlon = Number(srcLon)

    let pt2 = "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat="+stlat+"&lon="+stlon;

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
        setUpdateSrcLat(srcLat)
        setupdateSrcLon(srcLon)
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

  const [destLat, setDestLat] = useState('')
  const [destLon, setDestLon] = useState('')
  const [updateDestLat, setupdateDestLat] = useState(destLat)
  const [updateDestLon, setupdateDestLon] = useState(destLon)
  // Handle END point click
  const HandleClick2 = () =>{
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

        if(enddata['state'] === "Alaska"){
          setEndloc('Alaska')
        }else{
          setEndloc('US')
        }
        setupdateDestLat(destLat)
        setupdateDestLon(destLon)
        end[0] = Number(destLat)
        end[1] = Number(destLon)
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

  let colors1 = [
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

  let colors2 = [
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

  //----------------------------------------------SUPPORTING COMPONENTS----------------------------
  const [startloc, setStartloc] = useState('')
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
  
  const [value1, setValue1] = useState('Select known CCS project as start location')
  // Dropdown component for start point
  function DropdownStart() {
    laststart = 1
    return (
      <DropdownList
        containerClassName='dropdown'
        data={colors1}
        datakey = 'id'
        textField='name'
        value={value1}
        onChange={value1 => setValue1(value1)}
        disabled={uploaz!=="points"}
      />
    )
  }

  const [value2, setValue2] = useState('Select known CCS project as destination location')
  // Dropdown component for start point
  function DropdownEnd() {

    lastend = 1

    return (
      <DropdownList
        containerClassName='dropdown'
        data={colors2}
        datakey = 'id'
        textField='name'
        value={value2}
        onChange={value2 => setValue2(value2)}
        disabled={uploaz!=="points"}
      />
    )
  }

  function AddStartLoc() {
    return(
      <div>
        <h4>Add Start Location in World Geodetic System WGS 1984(WGS 84)</h4>

        <p> 
          Latitude:   <input type="number" name="myInput1"  onChange={handleChangeSrcLat} value={srcLat} disabled={uploaz!=="points"}/> 
          Longitude:  <input type="number" name="myInput2"  onChange={handleChangeSrcLon} value={srcLon} disabled={uploaz!=="points"}/>  
          <Button size="sm" onClick={HandleClick1} disabled={uploaz!=="points"}> Save Start </Button >                      
        </p> 
        <div><DropdownStart/></div>
      </div>
    )
  }

  function AddEndLoc() {
    return(
      <div>
        <h4>Add End Location in WGS84</h4>

        <p> 
          Latitude:   <input type="number" name="myInput3" onChange={handleChangeDestLat} value={destLat} disabled={uploaz!=="points"}/> 
          Longitude:  <input type="number" name="myInput4" onChange={handleChangeDestLon} value={destLon} disabled={uploaz!=="points"}/>
          <Button size="sm"  onClick={HandleClick2} disabled={uploaz!=="points"}> Save Destination </Button >            
        </p>
        <div><DropdownEnd/></div>
      </div>
    )
  }

  function IdModeBtns() {
    return(
      <div>
        <p>
          <Button id="gen-btn" type="button" onClick={generatePipeline} disabled={uploaz!=="points"}> Generate Pipeline </Button>
        </p>

        <p><a href={zip_file} target="_blank" rel="noopener noreferrer" download>
          <Button disabled={uploaz!=="points"}>
            <i className="fas fa-download"/>
            Download Report and Shapefile
          </Button>
        </a></p>
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

  const [idMode, setIdMode] = useState("")
  const onIdModeChange = e => {
    // If there is a visualized polygon from Eval mode, clear it
    shpvals = []

    setFinished(false)      //needed in idModeChange?
    const newMode = e.target.value;
    setIdMode(newMode)
    console.log(e.target.value + ' mode set.')

  }
  function IdModeSelector() {
    return(
      <div>
        <input type="radio"
        name="route"
        value="route"
        id="route"
        checked={idMode==="route"}
        onChange={onIdModeChange}
        disabled={uploaz!=="points"}/>
        <label id="idModeRadioText" htmlFor="route">Use ML Routing</label>

        <input type="radio"
        name="rail"
        value="rail"
        id="rail"
        checked={idMode==="rail"}
        onChange={onIdModeChange}
        disabled={uploaz!=="points"}/>
        <label id="idModeRadioText" htmlFor="rail">Use Railways</label>
      </div>
    )
  }

  const [uploaz, setUploaz] = useState("")
  const onModeChange = e => {
    // If there is a visualized polygon from Eval mode, clear it
    shpvals = []

    setFinished(false)
    setUploaz(e.target.value)
    console.log("onModeChange " + uploaz)
  }

  function ModeSelector() {
    return (
      <div>
        <input type="radio"
        name="selectpoints"
        value="points"
        id="points"
        checked={uploaz=== "points"}
        onChange={onModeChange}/>
        <label id="modeRadioText" htmlFor="points">Identify Route</label>

        <input type="radio"
        name="selectpoints"
        value="upld"
        id="upld"
        checked={uploaz=== "upld"}
        onChange={onModeChange}/>
        <label id="modeRadioText" htmlFor="upld">Evaluate Corridor</label>
      </div>
    )
  }

  // When used in a react component, the 'x files selected / no files uploaded' text doesn't change
  function EvalMode(){
    return(
      <div>
      <form onSubmit={evaluateCorridor} disabled={uploaz!=="upld"}>
        <h4> Upload Shapefiles</h4>
        <input type="file" multiple onChange={handleMultipleChange} disabled={uploaz!=="upld"} />
        <button type="submit" disabled={uploaz!=="upld"}>Evaluate</button>
      </form>
      <br></br>
      <p><a href={pdf_file} target="_blank" rel="noopener noreferrer" download>
        <Button disabled={uploaz!=="upld"}>
          <i className="fas fa-download"/>
          Download Report
        </Button>
      </a></p>
      <br/>
    </div>
    )
  }


  const [showTileLayer, setShowTileLayer] = useState(false);
  /*const [tileLayer, setTileLayer] = useState('https://arcgis.netl.doe.gov/server/rest/services/Hosted/CO2_Locate_Public_Wells_Ver_1_Cache/VectorTileServer')*/
  const [tileLayer, setTileLayer] = useState(null)
  function VectorTileLayerWrapper() {
        return showTileLayer ?
        <VectorTileLayer 
          url={tileLayer}
        /> : null
  }


  const [showLayerChecked, setShowLayerChecked] = useState(false);
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
        <ShowPipeline/>
        <Showshp/>
      </MapContainer>

      <LayerInput/>
      <LayerButtons tileLayer={tileLayer}/>

      <ModeSelector/>
      <IdModeSelector/>
      
      <div>
        <input type="radio" 
        name="location" 
        value="start" 
        id="start" 
        checked={location === "start"} 
        onChange={onOptionChange}
        disabled={uploaz!=="points"}/>
        <label htmlFor="start">Start</label>

        <input type="radio" 
        name="location" 
        value="end" 
        id="end" 
        checked={location === "end"} 
        onChange={onOptionChange}
        disabled={uploaz!=="points"}/>
        <label htmlFor="end">End</label>
      </div>

      <div>
        <h4>Add Start Location in World Geodetic System WGS 1984(WGS 84)</h4>

        <p> 
          Latitude:   <input type="number" name="myInput1"  onChange={handleChangeSrcLat} value={srcLat} disabled={uploaz!=="points"}/> 
          Longitude:  <input type="number" name="myInput2"  onChange={handleChangeSrcLon} value={srcLon} disabled={uploaz!=="points"}/>  
          <Button size="sm" onClick={HandleClick1} disabled={uploaz!=="points"}> Save Start </Button >                      
        </p> 
        <div><DropdownStart/></div>
      </div>

      <div>
        <h4>Add End Location in WGS84</h4>

        <p> 
          Latitude:   <input type="number" name="myInput3" onChange={handleChangeDestLat} value={destLat} disabled={uploaz!=="points"}/> 
          Longitude:  <input type="number" name="myInput4" onChange={handleChangeDestLon} value={destLon} disabled={uploaz!=="points"}/>
          <Button size="sm"  onClick={HandleClick2} disabled={uploaz!=="points"}> Save Destination </Button >            
        </p>
        <div><DropdownEnd/></div>
      </div>

      <br></br>
      <IdModeBtns/>
      <div>
        <form onSubmit={evaluateCorridor} disabled={uploaz!=="upld"}>
          <h4> Upload Shapefiles</h4>
          <input type="file" multiple onChange={handleMultipleChange} disabled={uploaz!=="upld"} />
          <button type="submit" disabled={uploaz!=="upld"}>Evaluate</button>
        </form>
        <br></br>
        <p><a href={pdf_file} target="_blank" rel="noopener noreferrer" download>
          <Button disabled={uploaz!=="upld"}>
            <i className="fas fa-download"/>
            Download Report
          </Button>
        </a></p>
        <br/>
      </div>
      <Footer/>
    </div>
  )
}