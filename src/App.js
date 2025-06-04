import { React, useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  LayersControl,
  useMapEvents,
  ScaleControl,
  Polyline,
  Polygon,
} from "react-leaflet";
import VectorTileLayer from "react-esri-leaflet/plugins/VectorTileLayer";
import { Icon } from "leaflet";
import { Link } from "react-router-dom";
import axios from "axios";
import Button from "react-bootstrap/Button";
import 'mapbox-gl/dist/mapbox-gl.css';


// Local Components
import MainToolModeButtons from "./components/MainToolModeButtons";
import IdMode from "./components/IdMode";
import EvalMode from "./components/EvalMode";
import { DisclaimerPopup, LoadingMessageIdMode, LoadingMessageEvalMode, ServerErrorPopup, InvalidLocationPopup, InvalidLandmassPopup } from "./components/PopupModals";

// Local Assets
import netlLogo from "./media/NETL_Square_GREEN_E.png";
import doeLogo from "./media/DOE_Logo_Color.png";
import discoverLogo from "./media/discover.jpg";

global.Buffer = require("buffer").Buffer;
let end=[0,0]
let shptyp = "";

/**
 * Primary App component that renders all other components and contains topmost level of state
 * @returns {JSX.element} Entire main page functionality 
 */
export default function MyApp() {
  // the polygons / lines that are drawn on the map for each mode, stored as a list of coords
  const [evalModePolygon, setEvalModePolygon] = useState([]);
  const [idModePolygon, setIdModePolygon] = useState([]);

  // toggles display of loading message modals for each mode
  const [isLoadingIdMode, setIsLoadingIdMode] = useState(false);
  const [isLoadingEvalMode, setIsLoadingEvalMode] = useState(false);

  // state of commpletion for processing of each main mode
  const [evalModeDone, setEvalModeDone] = useState("");
  const [idModeDone, setIdModeDone] = useState("");

  // display the catch-all server error Modal
  const [showServerError, setShowServerError] = useState(false);

  // what location?
  const [location, setLocation] = useState("");

  // files for upload mode
  const [files, setFiles] = useState([]);

  // state for the tool's main mode: "id" or "eval"
  const [mainMode, setMainMode] = useState("id");

  // state for sub-mode of Id Mode: "route" or "rail"
  const [idMode, setIdMode] = useState("route");

  // whether each point is in the main US landmass or Alaska
  const [startLandmass, setStartLandmass] = useState("");
  const [endLandmass, setEndLandmass] = useState("");

  // I think this displays the 'both points need to be in the US or AK' modal
  const [invalidPoint, setInvalidPoint] = useState(false);
  const [invalidLandmass, setInvalidLandmass] = useState(false);

  // used only for tile layer testing UI to test layers with. keep for posterity
  const [showTileLayer, setShowTileLayer] = useState(false);
  const [tileLayer, setTileLayer] = useState(null);
  const [showLayerChecked, setShowLayerChecked] = useState(false);

  // initial state is where markers are rendered before user selection 
  const [startMarkerRenderCoords, setStartMarkerRenderCoords] = useState([0, 0]); // given to Marker leaflet component to draw marker pos on the map
  const [destMarkerRenderCoords, setDestMarkerRenderCoords] = useState([0, 0]);

  // right now, marker coord data and data used for processing are seperate because they were before refactor
  const [startCoords, setStartCoords] = useState([null, null]);
  const [destCoords, setDestCoords] = useState([null, null]);

  // map markers
  const startMarkerIcon = new Icon({
    iconUrl: "https://cdn-icons-png.flaticon.com/512/447/447031.png",
    iconSize: [30, 30],
  });
  const destMarkerIcon = new Icon({
    iconUrl: require("./media/red_marker.png"),
    iconSize: [30, 30],
  });

  /**
   * The main functionality of Eval Mode, run an uploaded polygon through the ml analyzation code, draw it on the map, and generate a pdf report.
   * 
   * @param {*} event 
   */
  function evaluateCorridor(event) {
    event.preventDefault();
    setEvalModeDone(false);
    setIsLoadingEvalMode(true);
    setIsLoadingIdMode(false);
    let urlfile = "";
    const formData = new FormData();
    files.forEach((file, index) => {
      formData.append(`file${index}`, file);
    });

    if (global.electronmode === true) {
      urlfile = "http://127.0.0.1:5000/uploads";
    } else {
      urlfile = "/uploads";
    }
    axios
      .post(urlfile, formData)
      .then((response) => {
        setEvalModePolygon(response.data["array"]);
        shptyp = response.data["typ"];
        console.log(response);
        console.log(response.data);
        setEvalModeDone(true);
        setIsLoadingEvalMode(false);
      })
      .catch((err) => {
        setIsLoadingEvalMode(false);
        console.warn(err);
      });
  }

  /**
   * The main functionality of Id Mode, generate a route based on start and dest user input. 
   * Draw the route on the map, and create a shapefile of it and a corresponding pdf report for user download.
   */
  function generatePipeline() {
    let urlpipe = "";

    // check if both points are in the same landmass (mainland USA or Alaska)
    if (endLandmass !== startLandmass && endLandmass !== "" && startLandmass !== "") {
      setInvalidLandmass(true);
    } else {

      setIdModeDone(false);
      setIsLoadingIdMode(true);
      setIsLoadingEvalMode(false);
      if (global.electronmode === true) {
        urlpipe = "http://127.0.0.1:5000/token";
      } else {
        urlpipe = "/token";
      }

      console.log(
        "Sending start " +
          startCoords[0] +
          ", " +
          startCoords[1] +
          " and end " +
          destCoords[0] +
          ", " +
          destCoords[1] +
          " to backend"
      );
      axios({
        method: "POST",
        url: urlpipe,
        data: { s: startCoords, e: destCoords, mode: idMode },
      })
        .then((response) => {
          setIdModePolygon(response.data["route"]);
          console.log("Got line data");
          setIdModeDone(true);
          setIsLoadingIdMode(false);
        })
        .catch((error) => {
          if (error.response) {
            console.log(
              "Error with Generate Pipeline. Points are invalid or other logic error."
            );
            console.log(error.response);
            console.log(error.response.status);
            console.log(error.response.headers);
          }
          setIsLoadingIdMode(false);
          setShowServerError(true);
        });
    }
  }

  /**
   * Handler for clicking the documentation button, opens documentation in a browser window.
   */
  function openDocs() {
    let urldoc = "";

    if (global.electronmode === true) {
      urldoc = "http://127.0.0.1:5000/help";
    } else {
      urldoc = "/help";
    }
    axios({
      method: "POST",

      url: urldoc,
    }).catch((error) => {
      if (error.response) {
        console.log("Error requesting help documentation");
      }
    });

    /// Alt version for quick testing without fetching
    //  window.open("documentation/_build/html/index.html", "helpWindow", "noreferrer")
  }

  /**
   * Generic download hanlder that handles downloads based on file extension
   * 
   * @param {string} extension - The file extension you want the handler to consider
   */
  function handleDownload(extension) {
    let url_dl = "";
    if (global.electronmode === true) {
      url_dl = "http://127.0.0.1:5000/download_report";
    } else {
      url_dl = "/download_report";
    }
    // const response = await axios.post(url_dl, { extension }, { responseType: 'blob' });

    axios({
      method: "POST",
      url: url_dl,
      responseType: "blob",
      data: { extension: extension },
    })
      .then((response) => {
        const url = window.URL.createObjectURL(response.data);
        const a = document.createElement("a");
        a.href = url;

        let fname = "report_results";
        const contentDisposition = response.headers.get("Content-Disposition");
        if (contentDisposition && contentDisposition.indexOf("filename") > -1) {
          fname = contentDisposition
            .split("filename=")[1]
            .split(";")[0]
            .trim()
            .replace(/"/g, "");
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
  }

  /**
   * Zip-specific download handler
   */
  function handleZIPDownload() {
    handleDownload(".zip");
  }

  /**
   * Component to draw the line on the map for Id Mode
   * @returns {JSX.Element} - The line element
   */
  function ShowIdModeLine() {
    const LIME_OPTIONS = { color: "lime" };
    if (idModeDone) {
      return <Polyline pathOptions={LIME_OPTIONS} positions={idModePolygon} />;
    }
  }

  /**
   * Component to draw the line or polygon element on the map for Eval Mode 
   * @returns {JSX.Element} The line or polygon element
   */
  function ShowEvalModeShape() {
    const PURPLE_OPTIONS = { color: "purple" };
    if (evalModeDone) {
      if (shptyp === "Polygon") {
        return (
          <Polygon pathOptions={PURPLE_OPTIONS} positions={evalModePolygon} />
        );
      } else if (shptyp === "LineString") {
        return (
          <Polyline pathOptions={PURPLE_OPTIONS} positions={evalModePolygon} />
        );
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
  };

  /**
   * Sets uploaded files to a files variable in state 
   * @param {*} event 
   */
  function handleMultipleChange(event) {
    setFiles([...event.target.files]);
  }

  /**
   * Start marker component drawn on map at position held in startMarkerRenderCoords 
   * @returns {JSX.element} - The marker icon
   */
  const StartMarkers = () => {
    // handleClick basically
    const map = useMapEvents({
      click(e) {
        if (mainMode === "id") {
          if (location === "start") {
            let s1 = e.latlng["lat"];
            let s2 = e.latlng["lng"];

            let pt =
              "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=" +
              s1 +
              "&lon=" +
              s2;

            axios({
              method: "GET",
              url: pt,
            })
              .then((response) => {
                let startdata = response.data["address"];

                console.log(startdata);

                if (
                  startdata === undefined ||
                  startdata["state"] === "Hawaii" ||
                  startdata["country"] !== "United States"
                ) {
                  setInvalidPoint(true);
                } else {
                  if (startdata["state"] === "Alaska") {
                    setStartLandmass("Alaska");
                  } else {
                    setStartLandmass("US");
                  }

                  setStartCoords([s1, s2]);
                  console.log("Start from click: [" + s1 + ", " + s2 + "]");

                  setStartMarkerRenderCoords([
                    e.latlng["lat"],
                    e.latlng["lng"],
                  ]);
                }
              })
              .catch((error) => {
                if (error.response) {
                  console.log(error.response);
                  console.log(error.response.status);
                  console.log(error.response.headers);
                }
              });
          }
        }
      },
    });

    if (mainMode === "id") {
      return (
        <Marker position={startMarkerRenderCoords} icon={startMarkerIcon}>
          <Popup>
            Start Location ({0},{0})
          </Popup>
        </Marker>
      );
    } else if (mainMode === "eval") {
      return (
        <Marker position={[0, 0]} icon={startMarkerIcon}>
          <Popup>
            Start Location ({0}, {0})
          </Popup>
        </Marker>
      );
    }
  };

  /**
   * Destination marker component drawn on map at position held in destMarkerRenderCoords
   * @returns {JSX.element} - The marker object with icon
   */
  const EndMarkers = () => {
    const maps = useMapEvents({
      click(f) {
        if (mainMode === "id") {
          if (location === "end") {
            let e1 = f.latlng["lat"];
            let e2 = f.latlng["lng"];

            let pt2 =
              "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=" +
              e1 +
              "&lon=" +
              e2;

            axios({
              method: "GET",
              url: pt2,
            })
              .then((response) => {
                let enddata = response.data["address"];

                if (
                  enddata === undefined ||
                  enddata["state"] === "Hawaii" ||
                  enddata["country"] !== "United States"
                ) {
                  setInvalidPoint(true);
                } else {
                  if (enddata["state"] === "Alaska") {
                    setEndLandmass("Alaska");
                  } else {
                    setEndLandmass("US");
                  }

                  setDestCoords([f.latlng["lat"], f.latlng["lng"]]);
                  setDestMarkerRenderCoords([f.latlng["lat"], f.latlng["lng"]]);
                  end[0] = f.latlng["lat"];
                  end[1] = f.latlng["lng"];
                }
              })
              .catch((error) => {
                if (error.response) {
                  console.log(error.response);
                  console.log(error.response.status);
                  console.log(error.response.headers);
                }
              });
          }
        }
      },
    });

    if (mainMode === "id") {
      return (
        <Marker position={destMarkerRenderCoords} icon={destMarkerIcon}>
          <Popup>
            End Location ({end[0].toFixed(6)}, {end[1].toFixed(6)})
          </Popup>
        </Marker>
      );
    } else if (mainMode === "eval") {
      return (
        <Marker position={[0, 0]} icon={destMarkerIcon}>
          <Popup>
            End Location ({0}, {0})
          </Popup>
        </Marker>
      );
    }
  };

  /**
   * Component containing main function and download button for Id Mode
   * @returns {JSX.element} - Both buttons, the Generate Pipeline button and the corresponding Download button
   */
  function GenAndDownloadButtons() {
    return (
      <div>
        <p>
          <Button id="submit-btn" type="button" onClick={generatePipeline}>
            {" "}
            Generate Pipeline{" "}
          </Button>
        </p>

        <p>
          <Button onClick={handleZIPDownload}>
            <i className="fas fa-download" />
            Download Report and Shapefile
          </Button>
        </p>
        <br />
      </div>
    );
  }

  /**
   * Component for page header
   * @returns {JSX.element} - Header for page that contains appropriate icons and Help Documentation button
   */
  const Header = () => {
    return (
      <div className="header">
        <img src={netlLogo} width={50} height={50} alt="NETL Logo" />
        <img src={doeLogo} height={50} alt="DOE Logo" />
        <img src={discoverLogo} width={120} height={50} alt="Discover Logo" />
        <h1>Smart CO2 Transport-Routing Tool</h1>
        <div id="docButton">
          <Button onClick={openDocs}>Help Documentation</Button>
        </div>
      </div>
    );
  };

  /**
   * Component for page footer
   * @returns {JSX.element} - Footer that contains link to full disclaimer, opened in new tab or window
   */
  function Footer() {
    return (
      <p>
        <Link to="https://www.netl.doe.gov/home/disclaimer">Disclaimer</Link>
      </p>
    );
  }


  const overlays = {
    '<img class="layers" src=intermodal.png  width={10} height={10} alt="Discover Logo" /><p class="layerstext">Intermodal facilities</p>': (
      <VectorTileLayer url='https://arcgis.netl.doe.gov/server/rest/services/Hosted/Intermodal_Freight_Facilities_Flat/VectorTileServer' /> 
    ),
    '<img class="layers" src=public.png  width={10} height={10} alt="Discover Logo" /><p class="layerstext">Public infrastructure/HCAs</p>': (
      <VectorTileLayer url='https://arcgis.netl.doe.gov/server/rest/services/Hosted/Public_Infrastructure_Vector_Tile_Flat/VectorTileServer' /> 
    ),
    '<img class="layers" src=natural.png  width={10} height={10} alt="Discover Logo" /><p class="layerstext">Natural gas pipelines</p>': (
      <VectorTileLayer url='https://arcgis.netl.doe.gov/server/rest/services/Hosted/Natural_Gas_Pipelines/VectorTileServer' /> 
    ),
    '<img class="layers" src=hydrocarbon.png  width={10} height={10} alt="Discover Logo" /><p class="layerstext">Hydrocarbon pipelines</p>': (
      <VectorTileLayer url='https://arcgis.netl.doe.gov/server/rest/services/Hosted/Hydrocarbon_Pipelines_Flat/VectorTileServer' /> 
    ),
    '<img class="layers" src=frost.png  width={10} height={10} alt="Discover Logo" /><p class="layerstext">Frost Action Potential (High)</p>': (
      <VectorTileLayer url='https://arcgis.netl.doe.gov/server/rest/services/Hosted/Dissolved_Frost_Action_High_Flat_v2/VectorTileServer' /> 
    ),
    '<img class="layers" src=corrosion.png  width={10} height={10} alt="Discover Logo" /><p class="layerstext">Corrosion Potential</p>': (
      <VectorTileLayer url='https://arcgis.netl.doe.gov/server/rest/services/Hosted/Dissolved_Soil_Steel_Corrosion_Potential_v2/VectorTileServer' /> 
    ),
  };

  // Main return block for App
  return (
    <div>
      {/*Initial popup */}
      <DisclaimerPopup/>

      {/*Hidden by default popups*/}
      <InvalidLandmassPopup invalidLandmass={invalidLandmass} setInvalidLandmass={setInvalidLandmass} />
      <InvalidLocationPopup invalidPoint={invalidPoint} setInvalidPoint={setInvalidPoint}/> 
      <ServerErrorPopup showServerError={showServerError} setShowServerError={setShowServerError} />
      <LoadingMessageEvalMode isLoadingEvalMode={isLoadingEvalMode}/>
      <LoadingMessageIdMode isLoadingIdMode={isLoadingIdMode}/>

      {/*Regular page*/}
      <Header />

      <MapContainer center={[39.8283, -98.5795]} zoom={5}>
        {/* <VectorTileLayerTestWrapper tileLayer={ tileLayer } showTileLayer={ showTileLayer }/> */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <LayersControl position="topright">

        {Object.entries(overlays).map(([name, layer]) => (
          <LayersControl.Overlay key={name} name={name}>
            {layer}
          </LayersControl.Overlay>
        ))}
        
        </LayersControl>

        <StartMarkers />
        <EndMarkers />
        <ScaleControl position="bottomright" />
        <ShowIdModeLine />
        <ShowEvalModeShape />
      </MapContainer>

      <MainToolModeButtons
        setBtnGroupState={setMainMode}
        btntxt1={"Identify Route"}
        btntxt2={"Evaluate Corridor"}
        setEvalModePolygon={setEvalModePolygon}
        setIdModePolygon={setIdModePolygon}
      />
      {mainMode === "id" ? (
        <IdMode
          location={location}
          setLocation={setLocation}
          setInvalidPoint={setInvalidPoint}
          setStartLandmass={setStartLandmass}
          setEndLandmass={setEndLandmass}
          setBtnGroupState={setIdMode}
          btntxt1={"Pipeline Mode"}
          btntxt2={"Railway Mode"}
          toolMode={mainMode}
          setStartMarkerRenderCoords={setStartMarkerRenderCoords}
          setDestMarkerRenderCoords={setDestMarkerRenderCoords}
          setStartCoords={setStartCoords}
          setDestCoords={setDestCoords}
        />
      ) : null}

      {mainMode === "id" ? <GenAndDownloadButtons /> : null}

      {mainMode === "eval" ? (
        <EvalMode
          evaluateCorridor={evaluateCorridor}
          handleMultipleChange={handleMultipleChange}
          handleDownload={handleDownload}
        />
      ) : null}
      <Footer />
    </div>
  );
}
