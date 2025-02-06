
export default function EvalMode(){
    <div>
        <form onSubmit={evaluateCorridor} disabled={uploaz!=="upld"}>
            <h4> Upload Shapefiles</h4>
            <input type="file" multiple onChange={handleMultipleChange} disabled={uploaz!=="upld"} />
            <button type="submit" disabled={uploaz!=="upld"}>Evaluate</button>
        </form>
        <br></br>
        <p>
            <Button disabled={uploaz!=="upld"} onClick={handlePDFDownload}>
            <i className="fas fa-download"/>
            Download Report
            </Button>
        </p>
        <br/>
    </div>
}