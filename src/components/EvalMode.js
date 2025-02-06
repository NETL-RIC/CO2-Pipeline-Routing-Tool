import Button from 'react-bootstrap/Button';

export default function EvalMode ( {evaluateCorridor, handleMultipleChange, handlePDFDownload} ){
    return(
        <div>
            <form onSubmit={evaluateCorridor}>
                <h4> Upload Shapefiles</h4>
                <input type="file" multiple onChange={handleMultipleChange}/>
                <button type="submit">Evaluate</button>
            </form>
            <br></br>
            <p>
                <Button onClick={handlePDFDownload}>
                <i className="fas fa-download"/>
                Download Report
                </Button>
            </p>
            <br/>
        </div>
    )
}