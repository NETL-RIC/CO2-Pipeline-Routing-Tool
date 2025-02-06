export default function Controller(){
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
  const [idMode, setIdMode] = useState("")



  const [uploaz, setUploaz] = useState("")
  const [showTileLayer, setShowTileLayer] = useState(false);
  /*const [tileLayer, setTileLayer] = useState('https://arcgis.netl.doe.gov/server/rest/services/Hosted/CO2_Locate_Public_Wells_Ver_1_Cache/VectorTileServer')*/
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

}