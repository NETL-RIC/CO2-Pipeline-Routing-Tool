import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

export default function EvalMode ( {evaluateCorridor, handleMultipleChange, handlePDFDownload} ){
    return(
        <div>
            <h4> Upload Shapefiles</h4>
            <form id="eval-form" onSubmit={evaluateCorridor}>
                <Form.Group controlId="formFileMultiple" className="mb-3">
                    <Form.Label>Select one or more files to contribute to the shapefile used for corridor evaluation</Form.Label>
                    <Form.Control type="file" multiple onChange={ handleMultipleChange } />
                </Form.Group>
                <Button id="submit-btn" type="submit">Evaluate</Button>
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